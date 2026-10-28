// Usage: node scripts/hash_password.js '<password>'
// Prints a scrypt hash for ADMIN_OWNER_PASSWORD_HASH / ADMIN_WAREHOUSE_PASSWORD_HASH (same format as src/utils/adminAuth.ts).
const crypto = require('crypto');

const password = process.argv[2];
if (!password) {
  console.error("Usage: node scripts/hash_password.js '<password>'");
  process.exit(1);
}
const salt = crypto.randomBytes(16);
const key = crypto.scryptSync(password, salt, 64);
console.log(`scrypt$${salt.toString('hex')}$${key.toString('hex')}`);
