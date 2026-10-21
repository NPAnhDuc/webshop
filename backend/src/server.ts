import express, { Request, Response } from 'express';
import cors from 'cors';
import { store } from './db/store.js';

import path from 'path';
import fs from 'fs';

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// Serve local product images
const publicImages = path.join(process.cwd(), 'public', 'images');
const fallbackImages = path.resolve(process.cwd(), '..', 'AI', 'data', 'product_images', 'images');
if (fs.existsSync(publicImages)) {
  app.use('/images', express.static(publicImages));
} else if (fs.existsSync(fallbackImages)) {
  app.use('/images', express.static(fallbackImages));
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

app.post('/api/products/:slug/reviews', (req: Request, res: Response) => {
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
app.post('/api/quotations', (req: Request, res: Response) => {
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

app.post('/api/orders', (req: Request, res: Response) => {
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

// Customer Shopping Chatbot (CU-01..CU-11)
app.post('/api/chat/customer', (req: Request, res: Response) => {
  const { message, pageContext } = req.body;
  if (!message) {
    return res.status(400).json({ success: false, message: 'Tin nhắn không được để trống' });
  }
  const result = store.processCustomerChat(message, pageContext);
  res.json({ success: true, data: result });
});

// --- ADMIN APIS ---
app.post('/admin/auth/login', (req: Request, res: Response) => {
  const { username, password } = req.body;
  // Demo mock authentication with role support
  if (username === 'admin' && (password === 'admin123' || password === 'admin')) {
    return res.json({
      success: true,
      token: 'jwt-token-mock-super-admin',
      user: { id: 'usr-1', name: 'Chị Lan (Chủ Shop)', role: 'owner', email: 'lan.techstore@gmail.com' }
    });
  }
  if (username === 'kho' && password === 'kho123') {
    return res.json({
      success: true,
      token: 'jwt-token-mock-warehouse',
      user: { id: 'usr-2', name: 'Anh Tuấn (Nhân Viên Kho)', role: 'warehouse', email: 'tuan.kho@techstore.vn' }
    });
  }
  res.status(401).json({ success: false, message: 'Tên đăng nhập hoặc mật khẩu không chính xác' });
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

// Admin Data Science & Analytics Chatbot
app.post('/admin/chat', (req: Request, res: Response) => {
  const { query } = req.body;
  if (!query) {
    return res.status(400).json({ success: false, message: 'Câu hỏi không được để trống' });
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

app.put('/admin/settings', (req: Request, res: Response) => {
  const updated = store.updateStoreSettings(req.body);
  res.json({ success: true, data: updated });
});

app.listen(Number(PORT), '0.0.0.0', () => {
  console.log(`[TechStore Backend Server] Running cleanly on http://localhost:${PORT}`);
});
