// Automated CI Smoke Test for Backend Endpoints
const http = require('http');

function checkEndpoint(path) {
  return new Promise((resolve, reject) => {
    http.get(`http://localhost:5000${path}`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            const parsed = JSON.parse(data);
            if (parsed.success) {
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
      await checkEndpoint(ep);
    } catch (e) {
      allPassed = false;
    }
  }

  if (allPassed) {
    console.log('🎉 All Backend API Smoke Tests PASSED!');
    process.exit(0);
  } else {
    console.error('💥 Some API Smoke Tests FAILED!');
    process.exit(1);
  }
}

run();
