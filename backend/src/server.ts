import 'dotenv/config';
import {
  validateBody,
  CreateOrderSchema,
  CreateReviewSchema,
  CreateQuotationSchema,
  UpdateSettingsSchema
} from './validators/index.js';
import express, { Request, Response } from 'express';
import cors from 'cors';
import { store } from './db/store.js';
import { verifyAdminOTP, getAdminOTPSetupInfo, getAdminOTPQRCode } from './utils/totp.js';
import {
  adminAuthConfigError,
  verifyAdminCredentials,
  issueAdminToken,
  requireAdmin,
  requireRole,
  isLoginLocked,
  recordLoginFailure,
  clearLoginFailures
} from './utils/adminAuth.js';

import path from 'path';
import fs from 'fs';

const app = express();
// Behind a reverse proxy (Render), set TRUST_PROXY=1 so req.ip is the client IP for the login rate limit.
if (process.env.TRUST_PROXY) app.set('trust proxy', Number(process.env.TRUST_PROXY) || process.env.TRUST_PROXY);
const PORT = process.env.PORT || 5000;
const AI_SERVICE_URL = (process.env.AI_SERVICE_URL || '').trim();
// A local LLM on CPU can take tens of seconds; past this the rule engine answers instead.
const AI_TIMEOUT_MS = Number(process.env.AI_TIMEOUT_MS) || 90000;
// Shared secret checked by the AI service (X-Internal-Key); its admin channel is locked without it.
const AI_HEADERS: Record<string, string> = { 'Content-Type': 'application/json' };
if (process.env.AI_INTERNAL_KEY) AI_HEADERS['X-Internal-Key'] = process.env.AI_INTERNAL_KEY;

if (AI_SERVICE_URL) {
  console.log(`[AI Bridge] Active: Forwarding chatbot requests to Docker AI Service at ${AI_SERVICE_URL}`);
} else {
  console.log(`[AI Bridge] Standalone: Using built-in TechStore Knowledge Engine (AI_SERVICE_URL not set).`);
}

// CORS: storefront, admin portal, onrender.com domains and local development.
const toOrigin = (value: string) => {
  const v = value.trim().replace(/\/+$/, '');
  return /^https?:\/\//.test(v) ? v : `https://${v}`;
};
const configuredOrigins = [process.env.FRONTEND_ORIGIN, process.env.ADMIN_ORIGIN, process.env.CORS_ORIGINS]
  .flatMap(v => (v || '').split(','))
  .filter(v => v.trim())
  .map(toOrigin);
const ALLOWED_ORIGINS = new Set(configuredOrigins);
console.log(`[CORS] Explicit allowed origins: ${[...ALLOWED_ORIGINS].join(', ') || '(none - dynamic matching enabled)'}`);

app.use(cors({
  origin: (origin, callback) => {
    // 1. Requests without Origin (curl, server-to-server, health check) -> always allow
    if (!origin) return callback(null, true);

    // 2. If no specific origins were configured in env, allow all origins
    if (ALLOWED_ORIGINS.size === 0) return callback(null, true);

    // 3. Match against explicitly allowed origins
    if (ALLOWED_ORIGINS.has(origin)) return callback(null, true);

    // 4. Always allow any onrender.com subdomains and local development
    try {
      const parsed = new URL(origin);
      if (
        parsed.hostname.endsWith('.onrender.com') ||
        parsed.hostname === 'localhost' ||
        parsed.hostname === '127.0.0.1'
      ) {
        return callback(null, true);
      }
    } catch {
      // ignore malformed origin
    }

    return callback(null, false);
  },
  credentials: true
}));
app.use(express.json());

// Diagnostic endpoint to check AI Microservice status
app.get('/api/ai/status', async (req: Request, res: Response) => {
  if (!AI_SERVICE_URL) {
    return res.json({
      configured: false,
      online: false,
      url: null,
      message: 'AI_SERVICE_URL chưa được cấu hình. Đang chạy chế độ Dự phòng (Built-in Knowledge Engine).'
    });
  }

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 3000);
    const start = Date.now();
    const response = await fetch(`${AI_SERVICE_URL}/health`, { signal: controller.signal });
    clearTimeout(timeout);
    const latencyMs = Date.now() - start;

    return res.json({
      configured: true,
      online: response.ok,
      url: AI_SERVICE_URL,
      latencyMs,
      message: response.ok
        ? 'Đã kết nối thành công tới Docker Model AI Container'
        : `Docker Model AI phản hồi mã lỗi: ${response.status}`
    });
  } catch (err: any) {
    return res.json({
      configured: true,
      online: false,
      url: AI_SERVICE_URL,
      error: err.message,
      message: 'Không thể kết nối tới Docker Model AI Container (Đang khởi động hoặc sai cổng kết nối)'
    });
  }
});

// Serve local product images
const staticOpts = { maxAge: '7d', immutable: true, etag: true };
const publicImages = path.join(process.cwd(), 'public', 'images');
const fallbackImages = path.resolve(process.cwd(), '..', 'AI', 'data', 'product_images', 'images');
if (fs.existsSync(publicImages)) {
  app.use('/images', express.static(publicImages, staticOpts));
} else if (fs.existsSync(fallbackImages)) {
  app.use('/images', express.static(fallbackImages, staticOpts));
}


// --- PUBLIC STOREFRONT APIS ---
app.get('/api/categories', (req: Request, res: Response) => {
  res.json({ success: true, data: store.getCategories() });
});

app.get('/api/brands', (req: Request, res: Response) => {
  res.json({ success: true, data: store.getBrands() });
});

app.get('/api/products', (req: Request, res: Response) => {
  try {
    const {
      category,
      brand,
      q,
      minPrice,
      maxPrice,
      demand,
      panel,
      ram_gb,
      inStockOnly,
      hasInstallment0,
      sort,
      page,
      limit
    } = req.query;

    const result = store.getProducts({
      category: category as string,
      brand: brand as string,
      q: q as string,
      minPrice: minPrice ? parseInt(minPrice as string, 10) : undefined,
      maxPrice: maxPrice ? parseInt(maxPrice as string, 10) : undefined,
      demand: demand as string,
      panel: panel as string,
      ram_gb: ram_gb ? parseInt(ram_gb as string, 10) : undefined,
      inStockOnly: inStockOnly === 'true',
      hasInstallment0: hasInstallment0 === 'true',
      sort: sort as any,
      page: page ? parseInt(page as string, 10) : 1,
      limit: limit ? parseInt(limit as string, 10) : 12
    });

    res.json({ success: true, ...result });
  } catch (err: any) {
    res.status(500).json({ success: false, message: err.message });
  }
});

app.get('/api/products/:slug', (req: Request, res: Response) => {
  const product = store.getProductBySlug(req.params.slug as string);
  if (!product) {
    return res.status(404).json({ success: false, message: 'Không tìm thấy sản phẩm' });
  }
  res.json({ success: true, data: product });
});

app.get('/api/products/:slug/stock', (req: Request, res: Response) => {
  const stockInfo = store.getProductStockStatus(req.params.slug as string);
  res.json({ success: true, data: stockInfo });
});

app.get('/api/settings', (req: Request, res: Response) => {
  res.json({ success: true, data: store.getStoreSettings() });
});

app.get('/api/promotions', (req: Request, res: Response) => {
  res.json({ success: true, data: store.getAllPromotions() });
});

app.post('/api/promotions/validate', (req: Request, res: Response) => {
  const { code, orderTotal } = req.body;
  const result = store.validatePromotion(code, Number(orderTotal) || 0);
  res.json({ success: result.valid, ...result });
});

// Customer Reviews API
app.get('/api/products/:slug/reviews', (req: Request, res: Response) => {
  const reviews = store.getProductApprovedReviews(req.params.slug as string);
  res.json({ success: true, data: reviews });
});

app.post('/api/products/:slug/reviews', validateBody(CreateReviewSchema), (req: Request, res: Response) => {
  const { author, customerName, rating, comment, productName } = req.body;
  if (!comment) {
    return res.status(400).json({ success: false, message: 'Nội dung nhận xét là bắt buộc' });
  }
  const review = store.createReview({
    productSlug: req.params.slug as string,
    customerName: author || customerName || 'Khách hàng TechStore',
    productName: productName || 'Sản phẩm TechStore',
    rating: Number(rating) || 5,
    comment
  });
  res.json({ success: true, data: review });
});

// Customer PC Builder Quotation API
app.post('/api/quotations', validateBody(CreateQuotationSchema), (req: Request, res: Response) => {
  const { customerName, phone, title, totalPrice, totalWatts, recommendedPsu, compatibilityScore, parts, note } = req.body;
  if (!customerName || !phone) {
    return res.status(400).json({ success: false, message: 'Vui lòng cung cấp họ tên và số điện thoại liên hệ' });
  }
  const quotation = store.createCustomerQuotation({
    customerName,
    phone,
    title,
    totalPrice,
    totalWatts,
    recommendedPsu,
    compatibilityScore,
    parts,
    note
  });
  res.json({ success: true, data: quotation });
});

app.post('/api/cart/validate', (req: Request, res: Response) => {
  const { items } = req.body;
  if (!items || !Array.isArray(items)) {
    return res.status(400).json({ success: false, message: 'Dữ liệu giỏ hàng không hợp lệ' });
  }
  const result = store.validateCart(items);
  res.json({ success: true, data: result });
});

app.post('/api/orders', validateBody(CreateOrderSchema), (req: Request, res: Response) => {
  const { customerName, customerPhone, customerAddress, customerCity, notes, items, paymentMethod } = req.body;
  if (!customerName || !customerPhone || !customerAddress || !items || items.length === 0) {
    return res.status(400).json({ success: false, message: 'Vui lòng điền đầy đủ thông tin đặt hàng' });
  }

  const result = store.createOrder({
    customerName,
    customerPhone,
    customerAddress,
    customerCity: customerCity || 'Hà Nội',
    notes,
    items,
    paymentMethod: paymentMethod || 'cod'
  });

  if (!result.success) {
    return res.status(400).json(result);
  }
  res.json(result);
});

app.get('/api/orders/lookup', (req: Request, res: Response) => {
  const { phone, code } = req.query;
  if (!phone || !code) {
    return res.status(400).json({ success: false, message: 'Vui lòng cung cấp số điện thoại và mã đơn hàng' });
  }
  const order = store.lookupOrder(phone as string, code as string);
  if (!order) {
    return res.status(404).json({ success: false, message: 'Không tìm thấy đơn hàng phù hợp với thông tin đã nhập' });
  }
  res.json({ success: true, data: order });
});

// PC Builder Compatibility Validator (BP-R1..BP-R10)
app.post('/api/pc-builder/validate', (req: Request, res: Response) => {
  const { parts } = req.body; // { cpu, mainboard, ram, vga, psu, case, cooler }
  const result = store.validatePCBuild(parts || {});
  res.json({ success: true, data: result });
});

// Customer Shopping Chatbot (CU-01..CU-11) with Docker AI Model Bridge
app.post('/api/chat/customer', async (req: Request, res: Response) => {
  const { message, pageContext, sessionId } = req.body;
  if (!message) {
    return res.status(400).json({ success: false, message: 'Tin nhắn không được để trống' });
  }

  // 1. If AI_SERVICE_URL is set, forward to Docker Model AI Service
  if (AI_SERVICE_URL) {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), AI_TIMEOUT_MS);

      const aiRes = await fetch(`${AI_SERVICE_URL}/api/chat/customer`, {
        method: 'POST',
        headers: AI_HEADERS,
        body: JSON.stringify({
          message,
          sessionId,
          pageContext
        }),
        signal: controller.signal
      });
      clearTimeout(timeout);

      if (aiRes.ok) {
        const aiData: any = await aiRes.json();
        const replyText = aiData.replyText || aiData.answer || aiData.response || aiData.data?.replyText || '';
        if (replyText) {
          return res.json({
            success: true,
            data: {
              replyText,
              products: aiData.products || aiData.data?.products || [],
              suggestedPills: aiData.suggestedPills || aiData.data?.suggestedPills || [
                'Tư vấn laptop sinh viên',
                'Build PC đồ họa 25 triệu',
                'Chính sách trả góp 0%'
              ],
              action: aiData.action || 'ai_inference'
            }
          });
        }
      }
    } catch (err: any) {
      console.warn(`[AI Bridge Warning] Docker AI request failed (${AI_SERVICE_URL}): ${err.message}. Seamlessly falling back to local store engine.`);
    }
  }

  // 2. Fallback: Internal high-performance TechStore rule-based engine
  const result = store.processCustomerChat(message, pageContext);
  res.json({ success: true, data: result });
});

// --- ADMIN APIS ---
// Every /admin/* route needs a valid admin JWT, except login (and the OTP dev helper when explicitly enabled locally).
const OTP_DEV_HELPER = process.env.ADMIN_OTP_DEV_HELPER === 'true' && process.env.NODE_ENV !== 'production';
const ADMIN_PUBLIC_PATHS = new Set(['/auth/login', '/auth/setup-qr', ...(OTP_DEV_HELPER ? ['/auth/otp-setup'] : [])]);
const authConfigError = adminAuthConfigError();
if (authConfigError) {
  console.warn(`[Admin Auth] Admin login disabled: ${authConfigError}`);
}

app.use('/admin', (req: Request, res: Response, next) => {
  if (ADMIN_PUBLIC_PATHS.has(req.path)) return next();
  return requireAdmin(req, res, next);
});

// Reveals the TOTP secret, so it is owner-only; the public dev helper (with the current code) exists only when
// ADMIN_OTP_DEV_HELPER=true outside production.
app.get('/admin/auth/otp-setup', OTP_DEV_HELPER ? (req, res, next) => next() : requireRole('owner'), (req: Request, res: Response) => {
  const info = getAdminOTPSetupInfo(OTP_DEV_HELPER);
  res.json({ success: true, data: info });
});


app.post('/admin/auth/setup-qr', async (req: Request, res: Response) => {
  if (authConfigError) {
    return res.status(503).json({ success: false, message: 'Đăng nhập quản trị chưa được cấu hình trên máy chủ.' });
  }

  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ success: false, message: 'Vui lòng nhập tên đăng nhập và mật khẩu để tạo mã QR thiết lập.' });
  }

  const user = verifyAdminCredentials(String(username).trim(), String(password));
  if (!user) {
    return res.status(401).json({ success: false, message: 'Tên đăng nhập hoặc mật khẩu không chính xác' });
  }

  try {
    const qrInfo = await getAdminOTPQRCode(user.email || `${user.id}@techstore.vn`, 'TechStore Admin');
    res.json({ success: true, data: qrInfo });
  } catch (err: any) {
    res.status(500).json({ success: false, message: 'Không thể tạo mã QR: ' + err.message });
  }
});

app.post('/admin/auth/login', (req: Request, res: Response) => {
  if (authConfigError) {
    return res.status(503).json({ success: false, message: 'Đăng nhập quản trị chưa được cấu hình trên máy chủ.' });
  }

  const ip = req.ip || req.socket.remoteAddress || 'unknown';
  if (isLoginLocked(ip)) {
    return res.status(429).json({ success: false, message: 'Bạn đã thử đăng nhập sai quá nhiều lần. Vui lòng thử lại sau 15 phút.' });
  }

  const { username, password, otp } = req.body;
  if (!username || !password) {
    return res.status(400).json({ success: false, message: 'Vui lòng cung cấp đầy đủ tên đăng nhập và mật khẩu.' });
  }

  // 1. Verify user credentials
  const user = verifyAdminCredentials(String(username).trim(), String(password));
  if (!user) {
    recordLoginFailure(ip);
    return res.status(401).json({ success: false, message: 'Tên đăng nhập hoặc mật khẩu không chính xác' });
  }

  // 2. Verify 2FA OTP (Google Authenticator TOTP or Master OTP)
  if (!otp || String(otp).trim().length !== 6) {
    return res.status(400).json({
      success: false,
      requireOtp: true,
      message: 'Vui lòng nhập mã OTP bảo mật 6 số từ ứng dụng Google Authenticator hoặc Master OTP.'
    });
  }

  const cleanOtp = String(otp).trim();
  const isValidOtp = verifyAdminOTP(cleanOtp);
  if (!isValidOtp) {
    recordLoginFailure(ip);
    return res.status(401).json({
      success: false,
      requireOtp: true,
      message: 'Mã xác thực OTP không chính xác hoặc đã hết hiệu lực. Vui lòng thử lại!'
    });
  }

  // 3. Issue Token
  clearLoginFailures(ip);
  return res.json({
    success: true,
    token: issueAdminToken(user),
    user
  });
});

app.get('/admin/dashboard/kpis', (req: Request, res: Response) => {
  const kpis = store.getDashboardKPIs();
  res.json({ success: true, data: kpis });
});

app.get('/admin/dashboard/charts', (req: Request, res: Response) => {
  const charts = store.getDashboardCharts();
  res.json({ success: true, data: charts });
});

app.get('/admin/dashboard/widgets', (req: Request, res: Response) => {
  const pinned = store.getPinnedWidgets();
  res.json({ success: true, data: pinned });
});

app.post('/admin/dashboard/widgets/pin', (req: Request, res: Response) => {
  const { widget } = req.body;
  if (!widget) return res.status(400).json({ success: false, message: 'Thiếu dữ liệu widget' });
  const pinned = store.pinWidget(widget);
  res.json({ success: true, data: pinned });
});

app.get('/admin/inventory', (req: Request, res: Response) => {
  const list = store.getInventoryList();
  res.json({ success: true, data: list });
});

app.post('/admin/inventory/receipt', (req: Request, res: Response) => {
  const { variantId, qty, note } = req.body;
  if (!variantId || !qty || qty <= 0) {
    return res.status(400).json({ success: false, message: 'Thông tin nhập kho không hợp lệ' });
  }
  const result = store.createStockReceipt(variantId, qty, note || 'Nhập hàng bổ sung');
  res.json(result);
});

app.get('/admin/orders', (req: Request, res: Response) => {
  const { status } = req.query;
  const orders = store.getOrders(status as string);
  res.json({ success: true, data: orders });
});

app.patch('/admin/orders/:id/status', (req: Request, res: Response) => {
  const { status, note } = req.body;
  if (!status) return res.status(400).json({ success: false, message: 'Thiếu trạng thái mới' });
  const result = store.updateOrderStatus(req.params.id as string, status, note);
  res.json(result);
});

app.get('/admin/documents', (req: Request, res: Response) => {
  const docs = store.getDocuments();
  res.json({ success: true, data: docs });
});

app.post('/admin/documents', (req: Request, res: Response) => {
  const { title, docType, period, effectiveFrom, effectiveTo, version, content } = req.body;
  if (!title || !content) {
    return res.status(400).json({ success: false, message: 'Tiêu đề và nội dung tài liệu là bắt buộc' });
  }
  const newDoc = store.addDocument({
    title,
    docType: docType || 'policy',
    period: period || '2026',
    effectiveFrom: effectiveFrom || '2026-01-01',
    effectiveTo: effectiveTo || '2026-12-31',
    version: version || '1.0',
    content
  });
  res.json({ success: true, data: newDoc });
});

// Admin Data Science & Analytics Chatbot with Docker AI Bridge
// Forwarded to the AI service's admin channel (business data), so owner only.
app.post('/admin/chat', requireRole('owner'), async (req: Request, res: Response) => {
  const { query, sessionId } = req.body;
  if (!query) {
    return res.status(400).json({ success: false, message: 'Câu hỏi không được để trống' });
  }

  if (AI_SERVICE_URL) {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), AI_TIMEOUT_MS);

      const aiRes = await fetch(`${AI_SERVICE_URL}/api/chat/admin`, {
        method: 'POST',
        headers: AI_HEADERS,
        body: JSON.stringify({
          query,
          sessionId
        }),
        signal: controller.signal
      });
      clearTimeout(timeout);

      if (aiRes.ok) {
        const aiData: any = await aiRes.json();
        const data = aiData.data || aiData;
        if (data.thoughtSummary || data.insight || data.answer) {
          return res.json({
            success: true,
            data: {
              thoughtSummary: data.thoughtSummary || 'Phân tích tổng hợp từ Docker AI RAG Engine',
              insight: data.insight || data.answer || '',
              chartSpec: data.chartSpec,
              proposal: data.proposal
            }
          });
        }
      }
    } catch (err: any) {
      console.warn(`[AI Bridge Warning] Docker AI Admin request failed: ${err.message}.`);
    }
  }

  const result = store.processAdminChat(query);
  res.json({ success: true, data: result });
});

app.post('/admin/recommendations/:id/decision', (req: Request, res: Response) => {
  const { optionId, decision } = req.body; // decision: 'approved' | 'rejected'
  const result = store.decideProposal(req.params.id as string, optionId, decision);
  res.json(result);
});

// --- ADMIN EXTENDED ENTERPRISE ENDPOINTS ---

// 1. Products Management
app.get('/admin/products', (req: Request, res: Response) => {
  const list = store.getAllAdminProducts();
  res.json({ success: true, data: list });
});

app.post('/admin/products', (req: Request, res: Response) => {
  const product = store.createProduct(req.body);
  res.json({ success: true, data: product });
});

app.put('/admin/products/:id', (req: Request, res: Response) => {
  const updated = store.updateProduct(req.params.id as string, req.body);
  if (!updated) return res.status(404).json({ success: false, message: 'Không tìm thấy sản phẩm' });
  res.json({ success: true, data: updated });
});

app.delete('/admin/products/:id', (req: Request, res: Response) => {
  const ok = store.deleteProduct(req.params.id as string);
  res.json({ success: ok });
});

// 2. Promotions Management
app.get('/admin/promotions', (req: Request, res: Response) => {
  const list = store.getAllPromotions();
  res.json({ success: true, data: list });
});

app.post('/admin/promotions', (req: Request, res: Response) => {
  const promo = store.createPromotion(req.body);
  res.json({ success: true, data: promo });
});

app.patch('/admin/promotions/:id/toggle', (req: Request, res: Response) => {
  const promo = store.togglePromotion(req.params.id as string);
  res.json({ success: !!promo, data: promo });
});

app.delete('/admin/promotions/:id', (req: Request, res: Response) => {
  const ok = store.deletePromotion(req.params.id as string);
  res.json({ success: ok });
});

// 3. Customers CRM
app.get('/admin/customers', (req: Request, res: Response) => {
  const customers = store.getCustomersCRM();
  res.json({ success: true, data: customers });
});

// 4. PC Builder Quotations
app.get('/admin/quotations', (req: Request, res: Response) => {
  const quotes = store.getCustomerQuotations();
  res.json({ success: true, data: quotes });
});

app.patch('/admin/quotations/:id/status', (req: Request, res: Response) => {
  const { status } = req.body;
  const quote = store.updateQuotationStatus(req.params.id as string, status);
  if (!quote) return res.status(404).json({ success: false, message: 'Không tìm thấy báo giá' });
  res.json({ success: true, data: quote });
});

// 5. Customer Reviews
app.get('/admin/reviews', (req: Request, res: Response) => {
  const reviews = store.getCustomerReviews();
  res.json({ success: true, data: reviews });
});

app.patch('/admin/reviews/:id/status', (req: Request, res: Response) => {
  const { status } = req.body;
  const rev = store.toggleReviewStatus(req.params.id as string, status);
  if (!rev) return res.status(404).json({ success: false, message: 'Không tìm thấy đánh giá' });
  res.json({ success: true, data: rev });
});

app.post('/admin/reviews/:id/reply', (req: Request, res: Response) => {
  const { reply } = req.body;
  const rev = store.replyToReview(req.params.id as string, reply || '');
  if (!rev) return res.status(404).json({ success: false, message: 'Không tìm thấy đánh giá' });
  res.json({ success: true, data: rev });
});

// 6. Store Settings
app.get('/admin/settings', (req: Request, res: Response) => {
  const settings = store.getStoreSettings();
  res.json({ success: true, data: settings });
});

app.put('/admin/settings', validateBody(UpdateSettingsSchema), (req: Request, res: Response) => {
  const updated = store.updateStoreSettings(req.body);
  res.json({ success: true, data: updated });
});

if (process.env.NODE_ENV !== 'test') {
  app.listen(Number(PORT), '0.0.0.0', () => {
    console.log('[TechStore Backend Server] Running cleanly on port ' + PORT);
  });
}

export { app };

