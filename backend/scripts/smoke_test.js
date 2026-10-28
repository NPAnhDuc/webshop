// Automated CI Smoke Test for Backend Endpoints
const http = require('http');
const crypto = require('crypto');

function scryptHash(password) {
  const salt = crypto.randomBytes(16);
  return `scrypt$${salt.toString('hex')}$${crypto.scryptSync(password, salt, 64).toString('hex')}`;
}

// Throwaway test credentials, generated per run (never real secrets).
const OWNER_PASSWORD = crypto.randomBytes(12).toString('hex');
const WAREHOUSE_PASSWORD = crypto.randomBytes(12).toString('hex');
process.env.NODE_ENV = 'test';
process.env.ADMIN_JWT_SECRET = crypto.randomBytes(48).toString('hex');
process.env.ADMIN_TOTP_SECRET = 'JBSWY3DPEHPK3PXP';
process.env.ADMIN_OWNER_USERNAME = 'admin';
process.env.ADMIN_OWNER_PASSWORD_HASH = scryptHash(OWNER_PASSWORD);
process.env.ADMIN_WAREHOUSE_USERNAME = 'kho';
process.env.ADMIN_WAREHOUSE_PASSWORD_HASH = scryptHash(WAREHOUSE_PASSWORD);
delete process.env.ADMIN_MASTER_OTP;
delete process.env.ADMIN_OTP_DEV_HELPER;
delete process.env.AI_SERVICE_URL;

const { app } = require('../dist/server.js');
const { generateTOTP } = require('../dist/utils/totp.js');

function request(server, method, path, { body, token, origin } = {}) {
  const port = server.address().port;
  return new Promise((resolve, reject) => {
    const payload = body ? JSON.stringify(body) : null;
    const headers = {};
    if (payload) {
      headers['Content-Type'] = 'application/json';
      headers['Content-Length'] = Buffer.byteLength(payload);
    }
    if (token) headers['Authorization'] = `Bearer ${token}`;
    if (origin) headers['Origin'] = origin;
    const req = http.request({ hostname: '127.0.0.1', port, path, method, headers }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, headers: res.headers, body: JSON.parse(data) });
        } catch {
          resolve({ status: res.statusCode, headers: res.headers, body: data });
        }
      });
    });
    req.on('error', reject);
    if (payload) req.write(payload);
    req.end();
  });
}

async function run() {
  console.log('🧪 Starting TechStore Backend API Smoke Tests...');
  const server = app.listen(0, '127.0.0.1', async () => {
    console.log(`[Test Server] Running on ephemeral port ${server.address().port}`);
    let allPassed = true;

    async function check(label, fn) {
      try {
        const ok = await fn();
        if (ok) {
          console.log(`✅ [PASS] ${label}`);
        } else {
          console.error(`❌ [FAIL] ${label}`);
          allPassed = false;
        }
      } catch (e) {
        console.error(`❌ [ERROR] ${label}: ${e.message}`);
        allPassed = false;
      }
    }

    const ok2xx = (res) => res.status >= 200 && res.status < 300 && res.body.success !== false;

    // Public storefront endpoints
    for (const ep of ['/api/products', '/api/categories', '/api/brands', '/api/settings', '/api/promotions']) {
      await check(`GET ${ep} (public)`, async () => ok2xx(await request(server, 'GET', ep)));
    }

    // Admin endpoints reject missing / forged tokens
    const adminEndpoints = [
      ['GET', '/admin/products'],
      ['GET', '/admin/settings'],
      ['GET', '/admin/dashboard/kpis'],
      ['GET', '/admin/inventory'],
      ['GET', '/admin/orders'],
      ['GET', '/admin/documents'],
      ['GET', '/admin/auth/otp-setup'],
      ['POST', '/admin/chat']
    ];
    for (const [method, ep] of adminEndpoints) {
      await check(`${method} ${ep} without token -> 401`, async () => (await request(server, method, ep, { body: {} })).status === 401);
    }
    await check('GET /admin/products with forged token -> 401', async () =>
      (await request(server, 'GET', '/admin/products', { token: 'jwt-token-sec-owner-123' })).status === 401);

    // Login flow
    const login = (body) => request(server, 'POST', '/admin/auth/login', { body });
    await check('Login missing OTP -> 400 requireOtp', async () => {
      const res = await login({ username: 'admin', password: OWNER_PASSWORD });
      return res.status === 400 && res.body.requireOtp === true;
    });
    await check('Login wrong password -> 401', async () =>
      (await login({ username: 'admin', password: 'admin123', otp: generateTOTP() })).status === 401);
    await check('Login wrong OTP -> 401', async () =>
      (await login({ username: 'admin', password: OWNER_PASSWORD, otp: '000000' })).status === 401);
    await check('Old master OTP 888999 no longer accepted -> 401', async () =>
      (await login({ username: 'admin', password: OWNER_PASSWORD, otp: '888999' })).status === 401 || generateTOTP() === '888999');

    let ownerToken = null;
    let warehouseToken = null;
    await check('Owner login with password + TOTP -> 200 JWT', async () => {
      const res = await login({ username: 'admin', password: OWNER_PASSWORD, otp: generateTOTP() });
      ownerToken = res.body.token;
      return res.status === 200 && res.body.user?.role === 'owner' && typeof ownerToken === 'string' && ownerToken.split('.').length === 3;
    });
    await check('Warehouse login with password + TOTP -> 200 JWT', async () => {
      const res = await login({ username: 'kho', password: WAREHOUSE_PASSWORD, otp: generateTOTP() });
      warehouseToken = res.body.token;
      return res.status === 200 && res.body.user?.role === 'warehouse' && !!warehouseToken;
    });

    // Authorized access
    for (const ep of ['/admin/products', '/admin/settings', '/admin/inventory', '/admin/orders']) {
      await check(`GET ${ep} with owner token -> 200`, async () => ok2xx(await request(server, 'GET', ep, { token: ownerToken })));
    }
    await check('GET /admin/inventory with warehouse token -> 200', async () =>
      ok2xx(await request(server, 'GET', '/admin/inventory', { token: warehouseToken })));
    await check('GET /admin/auth/otp-setup with owner token -> 200 without current code', async () => {
      const res = await request(server, 'GET', '/admin/auth/otp-setup', { token: ownerToken });
      return ok2xx(res) && res.body.data.secret && res.body.data.currentDevOtp === undefined && res.body.data.masterOtp === undefined;
    });
    await check('GET /admin/auth/otp-setup with warehouse token -> 403', async () =>
      (await request(server, 'GET', '/admin/auth/otp-setup', { token: warehouseToken })).status === 403);
    await check('POST /admin/chat with warehouse token -> 403', async () =>
      (await request(server, 'POST', '/admin/chat', { token: warehouseToken, body: { query: 'doanh thu' } })).status === 403);
    await check('POST /admin/chat with owner token -> 200', async () =>
      ok2xx(await request(server, 'POST', '/admin/chat', { token: ownerToken, body: { query: 'doanh thu tháng này' } })));
    // TOTP pairing QR: closed unless ADMIN_TOTP_ENROLLMENT=true; wrong passwords count toward the login lockout.
    await check('GET /admin/auth/setup-qr reports enrollment closed', async () =>
      (await request(server, 'GET', '/admin/auth/setup-qr')).body?.data?.enrollmentOpen === false);
    await check('POST /admin/auth/setup-qr while closed -> 403 (no secret)', async () => {
      const res = await request(server, 'POST', '/admin/auth/setup-qr', { body: { username: 'admin', password: OWNER_PASSWORD } });
      return res.status === 403 && !JSON.stringify(res.body).includes(process.env.ADMIN_TOTP_SECRET);
    });
    process.env.ADMIN_TOTP_ENROLLMENT = 'true';
    await check('POST /admin/auth/setup-qr while open -> 200 QR', async () => {
      const res = await request(server, 'POST', '/admin/auth/setup-qr', { body: { username: 'admin', password: OWNER_PASSWORD } });
      return res.status === 200 && String(res.body.data?.qrCodeDataUrl || '').startsWith('data:image/png');
    });
    await check('setup-qr wrong passwords hit the shared lockout -> 429', async () => {
      let last;
      for (let i = 0; i < 12; i++) {
        last = await request(server, 'POST', '/admin/auth/setup-qr', { body: { username: 'admin', password: 'wrong-' + i } });
      }
      const login = await request(server, 'POST', '/admin/auth/login', { body: { username: 'admin', password: OWNER_PASSWORD, otp: generateTOTP() } });
      return last.status === 429 && login.status === 429;
    });
    delete process.env.ADMIN_TOTP_ENROLLMENT;

    // CORS: an arbitrary *.onrender.com site is not trusted; requests without Origin are unaffected.
    await check('CORS rejects https://evil.onrender.com', async () =>
      !(await request(server, 'GET', '/api/categories', { origin: 'https://evil.onrender.com' })).headers['access-control-allow-origin']);

    await check('Tampered owner token -> 401', async () => {
      const [h, p, s] = ownerToken.split('.');
      const forged = Buffer.from(JSON.stringify({ ...JSON.parse(Buffer.from(p, 'base64url').toString()), role: 'owner', sub: 'x' })).toString('base64url');
      return (await request(server, 'GET', '/admin/products', { token: `${h}.${forged}.${s}` })).status === 401;
    });

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
