// Automated CI Smoke Test for Backend Endpoints
const http = require('http');

process.env.NODE_ENV = 'test';
const { app } = require('../dist/server.js');

function checkEndpoint(server, path) {
  const port = server.address().port;
  return new Promise((resolve, reject) => {
    http.get(`http://127.0.0.1:${port}${path}`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            const parsed = JSON.parse(data);
            if (parsed.success !== false) {
              console.log(`✅ [PASS] GET ${path} (HTTP ${res.statusCode})`);
              resolve(true);
            } else {
              console.error(`❌ [FAIL] GET ${path}: success flag is false`);
              reject(new Error(`${path} failed`));
            }
          } catch (e) {
            console.log(`✅ [PASS] GET ${path} (HTTP ${res.statusCode} non-JSON)`);
            resolve(true);
          }
        } else {
          console.error(`❌ [FAIL] GET ${path} returned status ${res.statusCode}`);
          reject(new Error(`Status ${res.statusCode}`));
        }
      });
    }).on('error', (err) => {
      console.error(`❌ [ERROR] GET ${path}: ${err.message}`);
      reject(err);
    });
  });
}

function postJson(server, path, body) {
  const port = server.address().port;
  return new Promise((resolve, reject) => {
    const payload = JSON.stringify(body);
    const req = http.request({
      hostname: '127.0.0.1',
      port,
      path,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload)
      }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, body: JSON.parse(data) });
        } catch {
          resolve({ status: res.statusCode, body: data });
        }
      });
    });
    req.on('error', reject);
    req.write(payload);
    req.end();
  });
}

async function run() {
  console.log('🧪 Starting TechStore Backend API Smoke Tests...');
  const server = app.listen(0, '127.0.0.1', async () => {
    const port = server.address().port;
    console.log(`[Test Server] Running on ephemeral port ${port}`);

    const endpoints = [
      '/api/products',
      '/api/categories',
      '/api/brands',
      '/api/settings',
      '/api/promotions',
      '/admin/products',
      '/admin/settings',
      '/admin/auth/otp-setup'
    ];

    let allPassed = true;
    for (const ep of endpoints) {
      try {
        await checkEndpoint(server, ep);
      } catch (e) {
        allPassed = false;
      }
    }

    // Test 1: Login missing OTP -> HTTP 400 with requireOtp: true
    try {
      const res = await postJson(server, '/admin/auth/login', { username: 'admin', password: 'admin123' });
      if (res.status === 400 && res.body.requireOtp === true) {
        console.log('✅ [PASS] POST /admin/auth/login (Requires OTP gate - HTTP 400)');
      } else {
        console.error('❌ [FAIL] Missing OTP check failed', res);
        allPassed = false;
      }
    } catch (e) {
      console.error('❌ [ERROR] Missing OTP test:', e.message);
      allPassed = false;
    }

    // Test 2: Login wrong OTP -> HTTP 401
    try {
      const res = await postJson(server, '/admin/auth/login', { username: 'admin', password: 'admin123', otp: '000000' });
      if (res.status === 401) {
        console.log('✅ [PASS] POST /admin/auth/login (Rejects invalid OTP - HTTP 401)');
      } else {
        console.error('❌ [FAIL] Wrong OTP check failed', res);
        allPassed = false;
      }
    } catch (e) {
      console.error('❌ [ERROR] Wrong OTP test:', e.message);
      allPassed = false;
    }

    // Test 3: Login valid user + valid Master OTP -> HTTP 200 with token
    try {
      const res = await postJson(server, '/admin/auth/login', { username: 'admin', password: 'admin123', otp: '888999' });
      if (res.status === 200 && res.body.success === true && res.body.token) {
        console.log('✅ [PASS] POST /admin/auth/login (Valid 2FA OTP login - HTTP 200)');
      } else {
        console.error('❌ [FAIL] Valid OTP login failed', res);
        allPassed = false;
      }
    } catch (e) {
      console.error('❌ [ERROR] Valid OTP login test:', e.message);
      allPassed = false;
    }

    server.close(() => {
      if (allPassed) {
        console.log('🎉 All Backend API Smoke Tests & 2FA Auth PASSED!');
        process.exit(0);
      } else {
        console.error('💥 Some API Smoke Tests FAILED!');
        process.exit(1);
      }
    });
  });
}

run();
