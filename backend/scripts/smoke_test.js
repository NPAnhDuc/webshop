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
              console.log(`✅ [PASS] ${path} (HTTP ${res.statusCode})`);
              resolve(true);
            } else {
              console.error(`❌ [FAIL] ${path}: success flag is false`);
              reject(new Error(`${path} failed`));
            }
          } catch (e) {
            console.log(`✅ [PASS] ${path} (HTTP ${res.statusCode} non-JSON)`);
            resolve(true);
          }
        } else {
          console.error(`❌ [FAIL] ${path} returned status ${res.statusCode}`);
          reject(new Error(`Status ${res.statusCode}`));
        }
      });
    }).on('error', (err) => {
      console.error(`❌ [ERROR] ${path}: ${err.message}`);
      reject(err);
    });
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
      '/admin/settings'
    ];

    let allPassed = true;
    for (const ep of endpoints) {
      try {
        await checkEndpoint(server, ep);
      } catch (e) {
        allPassed = false;
      }
    }

    server.close(() => {
      if (allPassed) {
        console.log('🎉 All Backend API Smoke Tests PASSED!');
        process.exit(0);
      } else {
        console.error('💥 Some API Smoke Tests FAILED!');
        process.exit(1);
      }
    });
  });
}

run();
