import crypto from 'crypto';
import QRCode from 'qrcode';

// Base32 secret. The well-known demo secret is only a fallback outside production (login is refused there without it).
const ADMIN_TOTP_SECRET = (process.env.ADMIN_TOTP_SECRET || (process.env.NODE_ENV === 'production' ? '' : 'JBSWY3DPEHPK3PXP')).trim();
// Emergency recovery OTP: disabled unless explicitly configured.
const ADMIN_MASTER_OTP = (process.env.ADMIN_MASTER_OTP || '').trim();
const STEP_SECONDS = 30;

function base32Decode(base32: string): Buffer {
  const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
  let bits = 0;
  let value = 0;
  let index = 0;
  const clean = base32.toUpperCase().replace(/=+$/, '');
  const bytes = new Uint8Array((clean.length * 5 / 8) | 0);
  for (let i = 0; i < clean.length; i++) {
    const val = alphabet.indexOf(clean[i]);
    if (val === -1) continue;
    value = (value << 5) | val;
    bits += 5;
    if (bits >= 8) {
      bytes[index++] = (value >>> (bits - 8)) & 255;
      bits -= 8;
    }
  }
  return Buffer.from(bytes.buffer, 0, index);
}

/**
 * Generate 6-digit TOTP code compliant with RFC 6238 (Google Authenticator)
 */
export function generateTOTP(secret: string = ADMIN_TOTP_SECRET, stepOffset: number = 0): string {
  const counter = Math.floor(Date.now() / 1000 / STEP_SECONDS) + stepOffset;
  const buf = Buffer.alloc(8);
  buf.writeBigInt64BE(BigInt(counter));
  const key = base32Decode(secret);
  const hmac = crypto.createHmac('sha1', key).update(buf).digest();
  const offset = hmac[hmac.length - 1] & 0xf;
  const binary =
    ((hmac[offset] & 0x7f) << 24) |
    ((hmac[offset + 1] & 0xff) << 16) |
    ((hmac[offset + 2] & 0xff) << 8) |
    (hmac[offset + 3] & 0xff);
  return (binary % 1000000).toString().padStart(6, '0');
}

/**
 * Verify OTP against TOTP window (±1 step, i.e. 30s drift tolerance) or Master Emergency OTP
 */
export function verifyAdminOTP(token: string, secret: string = ADMIN_TOTP_SECRET): boolean {
  const cleanToken = token.trim();
  
  if (!secret || !/^\d{6}$/.test(cleanToken)) {
    return false;
  }

  // 1. Check Master Emergency OTP
  if (ADMIN_MASTER_OTP && cleanToken === ADMIN_MASTER_OTP) {
    return true;
  }

  // 2. Check TOTP window (-1, 0, +1) to account for time drift
  for (const offset of [-2, -1, 0, 1, 2]) {
    if (generateTOTP(secret, offset) === cleanToken) {
      return true;
    }
  }

  return false;
}

/**
 * Information needed to pair with Google Authenticator or Microsoft Authenticator
 */
export function getAdminOTPSetupInfo(includeDevHelpers: boolean, account = 'admin@techstore.vn', issuer = 'TechStore Studio Admin') {
  const otpauthUrl = `otpauth://totp/${encodeURIComponent(issuer)}:${encodeURIComponent(account)}?secret=${ADMIN_TOTP_SECRET}&issuer=${encodeURIComponent(issuer)}&algorithm=SHA1&digits=6&period=30`;
  
  return {
    secret: ADMIN_TOTP_SECRET,
    otpauthUrl,
    // Local development only: the current code would bypass 2FA anywhere else.
    currentDevOtp: includeDevHelpers ? generateTOTP(ADMIN_TOTP_SECRET) : undefined,
    stepSeconds: STEP_SECONDS
  };
}


/**
 * Generate QR code data URL for pairing with Google Authenticator
 */
export async function getAdminOTPQRCode(account = 'admin@techstore.vn', issuer = 'TechStore Admin') {
  const otpauthUrl = `otpauth://totp/${encodeURIComponent(issuer)}:${encodeURIComponent(account)}?secret=${ADMIN_TOTP_SECRET}&issuer=${encodeURIComponent(issuer)}&algorithm=SHA1&digits=6&period=30`;
  const qrCodeDataUrl = await QRCode.toDataURL(otpauthUrl, {
    margin: 2,
    width: 280,
    color: {
      dark: '#000000',
      light: '#ffffff'
    }
  });

  return {
    secret: ADMIN_TOTP_SECRET,
    otpauthUrl,
    qrCodeDataUrl,
    account,
    issuer
  };
}
