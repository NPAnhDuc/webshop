import crypto from 'crypto';
import jwt from 'jsonwebtoken';
import { Request, Response, NextFunction } from 'express';

export type AdminRole = 'owner' | 'warehouse';

export interface AdminUser {
  id: string;
  name: string;
  role: AdminRole;
  email: string;
}

const IS_PRODUCTION = process.env.NODE_ENV === 'production';
const JWT_SECRET = (process.env.ADMIN_JWT_SECRET || '').trim();
const JWT_EXPIRES_IN = (process.env.ADMIN_JWT_EXPIRES_IN || '2h').trim();
const JWT_ISSUER = 'techstore-backend';
const JWT_AUDIENCE = 'techstore-admin';

// Account profiles are public info; credentials come only from env (scrypt hashes, see scripts/hash_password.js).
const ACCOUNTS: Array<{ user: AdminUser; usernameEnv: string; defaultUsername: string; hashEnv: string }> = [
  {
    user: { id: 'usr-1', name: 'Chị Lan (Chủ Shop)', role: 'owner', email: 'lan.techstore@gmail.com' },
    usernameEnv: 'ADMIN_OWNER_USERNAME',
    defaultUsername: 'admin',
    hashEnv: 'ADMIN_OWNER_PASSWORD_HASH'
  },
  {
    user: { id: 'usr-2', name: 'Anh Tuấn (Nhân Viên Kho)', role: 'warehouse', email: 'tuan.kho@techstore.vn' },
    usernameEnv: 'ADMIN_WAREHOUSE_USERNAME',
    defaultUsername: 'kho',
    hashEnv: 'ADMIN_WAREHOUSE_PASSWORD_HASH'
  }
];

function configuredAccounts() {
  return ACCOUNTS.map(a => ({
    user: a.user,
    username: (process.env[a.usernameEnv] || a.defaultUsername).trim(),
    hash: (process.env[a.hashEnv] || '').trim()
  })).filter(a => a.hash);
}

/** Why admin login is unavailable, or null when it is fully configured. */
export function adminAuthConfigError(): string | null {
  if (JWT_SECRET.length < 32) return 'ADMIN_JWT_SECRET chưa được cấu hình (tối thiểu 32 ký tự).';
  if (IS_PRODUCTION && !process.env.ADMIN_TOTP_SECRET) return 'ADMIN_TOTP_SECRET chưa được cấu hình.';
  if (configuredAccounts().length === 0) return 'Chưa cấu hình ADMIN_OWNER_PASSWORD_HASH / ADMIN_WAREHOUSE_PASSWORD_HASH.';
  return null;
}

/** Hash format: scrypt$<salt hex>$<key hex> */
export function hashPassword(password: string): string {
  const salt = crypto.randomBytes(16);
  const key = crypto.scryptSync(password, salt, 64);
  return `scrypt$${salt.toString('hex')}$${key.toString('hex')}`;
}

function verifyPassword(password: string, stored: string): boolean {
  const [scheme, saltHex, keyHex] = stored.split('$');
  if (scheme !== 'scrypt' || !saltHex || !keyHex) return false;
  const expected = Buffer.from(keyHex, 'hex');
  const actual = crypto.scryptSync(password, Buffer.from(saltHex, 'hex'), expected.length);
  return crypto.timingSafeEqual(actual, expected);
}

function safeEqual(a: string, b: string): boolean {
  const ha = crypto.createHash('sha256').update(a).digest();
  const hb = crypto.createHash('sha256').update(b).digest();
  return crypto.timingSafeEqual(ha, hb);
}

export function verifyAdminCredentials(username: string, password: string): AdminUser | null {
  for (const account of configuredAccounts()) {
    if (safeEqual(username, account.username) && verifyPassword(password, account.hash)) {
      return account.user;
    }
  }
  return null;
}

export function issueAdminToken(user: AdminUser): string {
  return jwt.sign({ name: user.name, role: user.role, email: user.email }, JWT_SECRET, {
    subject: user.id,
    expiresIn: JWT_EXPIRES_IN as jwt.SignOptions['expiresIn'],
    issuer: JWT_ISSUER,
    audience: JWT_AUDIENCE,
    algorithm: 'HS256'
  });
}

function readAdminUser(req: Request): AdminUser | null {
  if (!JWT_SECRET) return null;
  const header = req.headers.authorization || '';
  const match = header.match(/^Bearer\s+(.+)$/i);
  if (!match) return null;
  try {
    const payload = jwt.verify(match[1], JWT_SECRET, {
      issuer: JWT_ISSUER,
      audience: JWT_AUDIENCE,
      algorithms: ['HS256']
    }) as jwt.JwtPayload;
    if (payload.role !== 'owner' && payload.role !== 'warehouse') return null;
    return { id: String(payload.sub), name: payload.name, role: payload.role, email: payload.email };
  } catch {
    return null;
  }
}

/** Rejects requests without a valid admin Bearer token; sets res.locals.adminUser. */
export function requireAdmin(req: Request, res: Response, next: NextFunction) {
  const user = readAdminUser(req);
  if (!user) {
    return res.status(401).json({ success: false, message: 'Phiên đăng nhập quản trị không hợp lệ hoặc đã hết hạn. Vui lòng đăng nhập lại.' });
  }
  res.locals.adminUser = user;
  next();
}

/** Use after requireAdmin. */
export function requireRole(...roles: AdminRole[]) {
  return (req: Request, res: Response, next: NextFunction) => {
    const user = res.locals.adminUser as AdminUser | undefined;
    if (!user || !roles.includes(user.role)) {
      return res.status(403).json({ success: false, message: 'Tài khoản của bạn không có quyền truy cập chức năng này.' });
    }
    next();
  };
}

// Brute-force guard for the login endpoint: per-IP failed attempts in a sliding window.
const LOGIN_WINDOW_MS = 15 * 60 * 1000;
const LOGIN_MAX_FAILURES = 10;
const loginFailures = new Map<string, number[]>();

function recentFailures(ip: string): number[] {
  const now = Date.now();
  const list = (loginFailures.get(ip) || []).filter(t => now - t < LOGIN_WINDOW_MS);
  if (list.length) loginFailures.set(ip, list);
  else loginFailures.delete(ip);
  return list;
}

export function isLoginLocked(ip: string): boolean {
  return recentFailures(ip).length >= LOGIN_MAX_FAILURES;
}

export function recordLoginFailure(ip: string) {
  loginFailures.set(ip, [...recentFailures(ip), Date.now()]);
}

export function clearLoginFailures(ip: string) {
  loginFailures.delete(ip);
}
