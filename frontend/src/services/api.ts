import { Product, Category, Brand, Order, ChartSpec, StrategyProposal, StrategicDocument } from '../types';

const getApiBaseUrl = () => {
  let url = (import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || '').trim();
  if (!url && typeof window !== 'undefined') {
    if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
      url = 'https://webshop-cwnn.onrender.com';
    }
  }
  if (url && !url.startsWith('http://') && !url.startsWith('https://')) {
    url = `https://${url}`;
  }
  return url.replace(/\/+$/, '');
};
export const API_BASE_URL = getApiBaseUrl();
const BASE_URL = API_BASE_URL;

export function formatImageUrl(url?: string): string {
  if (!url) return 'https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=600&auto=format&fit=crop&q=80';
  if (url.startsWith('http://') || url.startsWith('https://')) return url;
  if (!API_BASE_URL) return url;
  return `${API_BASE_URL}/${url.replace(/^\/+/, '')}`;
}

export async function fetchCategories(): Promise<Category[]> {
  const res = await fetch(`${BASE_URL}/api/categories`);
  const json = await res.json();
  return json.data || [];
}

export async function fetchBrands(): Promise<Brand[]> {
  const res = await fetch(`${BASE_URL}/api/brands`);
  const json = await res.json();
  return json.data || [];
}

export async function fetchProducts(params: Record<string, any> = {}): Promise<{
  products: Product[];
  total: number;
  page: number;
  totalPages: number;
  facets: any;
}> {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') {
      query.set(k, String(v));
    }
  });

  const res = await fetch(`${BASE_URL}/api/products?${query.toString()}`);
  const json = await res.json();
  return json;
}

export async function fetchProductDetail(slug: string): Promise<any> {
  const res = await fetch(`${BASE_URL}/api/products/${slug}`);
  const json = await res.json();
  return json.data;
}

export async function validateCart(items: { variantId: string; qty: number }[]): Promise<any> {
  const res = await fetch(`${BASE_URL}/api/cart/validate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ items })
  });
  const json = await res.json();
  return json.data;
}

export async function createOrder(orderData: any): Promise<any> {
  const res = await fetch(`${BASE_URL}/api/orders`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(orderData)
  });
  return await res.json();
}

export async function lookupOrder(phone: string, code: string): Promise<any> {
  const res = await fetch(`${BASE_URL}/api/orders/lookup?phone=${encodeURIComponent(phone)}&code=${encodeURIComponent(code)}`);
  return await res.json();
}

export async function validatePCBuild(parts: Record<string, string>): Promise<any> {
  const res = await fetch(`${BASE_URL}/api/pc-builder/validate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ parts })
  });
  const json = await res.json();
  return json.data;
}

export async function sendCustomerChatMessage(message: string, pageContext?: any): Promise<any> {
  const res = await fetch(`${BASE_URL}/api/chat/customer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, pageContext })
  });
  const json = await res.json();
  return json.data;
}

// ADMIN APIS
export async function adminLogin(credentials: { username: string; password: string }): Promise<any> {
  const res = await fetch(`${BASE_URL}/admin/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials)
  });
  return await res.json();
}

export async function fetchAdminKPIs(): Promise<any> {
  const res = await fetch(`${BASE_URL}/admin/dashboard/kpis`);
  const json = await res.json();
  return json.data;
}

export async function fetchAdminCharts(): Promise<ChartSpec[]> {
  const res = await fetch(`${BASE_URL}/admin/dashboard/charts`);
  const json = await res.json();
  return json.data;
}

export async function fetchPinnedWidgets(): Promise<ChartSpec[]> {
  const res = await fetch(`${BASE_URL}/admin/dashboard/widgets`);
  const json = await res.json();
  return json.data;
}

export async function pinChartWidget(widget: ChartSpec): Promise<any> {
  const res = await fetch(`${BASE_URL}/admin/dashboard/widgets/pin`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ widget })
  });
  return await res.json();
}

export async function fetchAdminInventory(): Promise<any[]> {
  const res = await fetch(`${BASE_URL}/admin/inventory`);
  const json = await res.json();
  return json.data;
}

export async function createStockReceipt(receiptData: { variantId: string; qty: number; note: string }): Promise<any> {
  const res = await fetch(`${BASE_URL}/admin/inventory/receipt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(receiptData)
  });
  return await res.json();
}

export async function fetchAdminOrders(status?: string): Promise<Order[]> {
  const url = status ? `${BASE_URL}/admin/orders?status=${status}` : `${BASE_URL}/admin/orders`;
  const res = await fetch(url);
  const json = await res.json();
  return json.data;
}

export async function updateOrderStatus(orderId: string, status: string, note?: string): Promise<any> {
  const res = await fetch(`${BASE_URL}/admin/orders/${orderId}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status, note })
  });
  return await res.json();
}

export async function fetchAdminDocuments(): Promise<StrategicDocument[]> {
  const res = await fetch(`${BASE_URL}/admin/documents`);
  const json = await res.json();
  return json.data;
}

export async function uploadStrategicDoc(doc: any): Promise<any> {
  const res = await fetch(`${BASE_URL}/admin/documents`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(doc)
  });
  return await res.json();
}

export async function sendAdminChatMessage(query: string): Promise<{
  thoughtSummary: string;
  insight: string;
  chartSpec?: ChartSpec;
  tableData?: any[];
  citations: string[];
  proposal?: StrategyProposal;
}> {
  const res = await fetch(`${BASE_URL}/admin/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
  });
  const json = await res.json();
  return json.data;
}

export async function decideProposal(proposalId: string, optionId: string, decision: 'approved' | 'rejected'): Promise<any> {
  const res = await fetch(`${BASE_URL}/admin/recommendations/${proposalId}/decision`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ optionId, decision })
  });
  return await res.json();
}

// EXTENDED ENTERPRISE ADMIN APIS

// 1. Products
export async function fetchAdminProducts(): Promise<any[]> {
  const res = await fetch(`${BASE_URL}/admin/products`);
  const json = await res.json();
  return json.data || [];
}

export async function createAdminProduct(productData: any): Promise<any> {
  const res = await fetch(`${BASE_URL}/admin/products`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(productData)
  });
  return await res.json();
}

export async function updateAdminProduct(id: string, productData: any): Promise<any> {
  const res = await fetch(`${BASE_URL}/admin/products/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(productData)
  });
  return await res.json();
}

export async function deleteAdminProduct(id: string): Promise<any> {
  const res = await fetch(`${BASE_URL}/admin/products/${id}`, {
    method: 'DELETE'
  });
  return await res.json();
}

// 2. Promotions
export async function fetchAdminPromotions(): Promise<any[]> {
  const res = await fetch(`${BASE_URL}/admin/promotions`);
  const json = await res.json();
  return json.data || [];
}

export async function createAdminPromotion(promoData: any): Promise<any> {
  const res = await fetch(`${BASE_URL}/admin/promotions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(promoData)
  });
  return await res.json();
}

export async function toggleAdminPromotion(id: string): Promise<any> {
  const res = await fetch(`${BASE_URL}/admin/promotions/${id}/toggle`, {
    method: 'PATCH'
  });
  return await res.json();
}

export async function deleteAdminPromotion(id: string): Promise<any> {
  const res = await fetch(`${BASE_URL}/admin/promotions/${id}`, {
    method: 'DELETE'
  });
  return await res.json();
}

// 3. Customers CRM
export async function fetchAdminCustomers(): Promise<any[]> {
  const res = await fetch(`${BASE_URL}/admin/customers`);
  const json = await res.json();
  return json.data || [];
}

// 4. PC Builder Quotations
export async function fetchAdminQuotations(): Promise<any[]> {
  const res = await fetch(`${BASE_URL}/admin/quotations`);
  const json = await res.json();
  return json.data || [];
}

export async function updateAdminQuotationStatus(id: string, status: string): Promise<any> {
  const res = await fetch(`${BASE_URL}/admin/quotations/${id}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status })
  });
  return await res.json();
}

export async function submitPCQuotation(quotationData: any): Promise<any> {
  const res = await fetch(`${BASE_URL}/api/quotations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(quotationData)
  });
  return await res.json();
}

// 5. Customer Reviews
export async function fetchAdminReviews(): Promise<any[]> {
  const res = await fetch(`${BASE_URL}/admin/reviews`);
  const json = await res.json();
  return json.data || [];
}

export async function toggleAdminReviewStatus(id: string, status?: string): Promise<any> {
  const res = await fetch(`${BASE_URL}/admin/reviews/${id}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status })
  });
  return await res.json();
}

export async function replyAdminReview(id: string, reply: string): Promise<any> {
  const res = await fetch(`${BASE_URL}/admin/reviews/${id}/reply`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reply })
  });
  return await res.json();
}

export async function fetchProductReviews(slug: string): Promise<any[]> {
  const res = await fetch(`${BASE_URL}/api/products/${slug}/reviews`);
  const json = await res.json();
  return json.data || [];
}

export async function submitProductReview(slug: string, reviewData: any): Promise<any> {
  const res = await fetch(`${BASE_URL}/api/products/${slug}/reviews`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(reviewData)
  });
  return await res.json();
}

// 6. Store Settings
export async function fetchStoreSettings(): Promise<any> {
  const res = await fetch(`${BASE_URL}/api/settings`);
  const json = await res.json();
  return json.data;
}

export async function fetchAdminSettings(): Promise<any> {
  const res = await fetch(`${BASE_URL}/admin/settings`);
  const json = await res.json();
  return json.data;
}

export async function updateAdminSettings(settings: any): Promise<any> {
  const res = await fetch(`${BASE_URL}/admin/settings`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings)
  });
  return await res.json();
}

// 7. Dynamic Coupon Validation
export async function validateCoupon(code: string, orderTotal: number = 0): Promise<any> {
  const res = await fetch(`${BASE_URL}/api/promotions/validate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code, orderTotal })
  });
  return await res.json();
}
