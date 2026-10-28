import {
  Product,
  Order,
  ChartSpec,
  StrategicDocument,
  StrategyProposal
} from '../types';

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
const BASE_URL = getApiBaseUrl();

export const DEFAULT_PRODUCT_FALLBACK_IMAGE = 'https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=600&auto=format&fit=crop&q=80';

export function formatProductImageUrl(url?: string): string {
  if (!url || typeof url !== 'string' || !url.trim()) {
    return DEFAULT_PRODUCT_FALLBACK_IMAGE;
  }
  const trimmed = url.trim();
  if (trimmed.startsWith('http://') || trimmed.startsWith('https://') || trimmed.startsWith('data:')) {
    return trimmed;
  }
  const cleanPath = trimmed.replace(/^\/+/, '');
  if (BASE_URL) {
    return `${BASE_URL}/${cleanPath}`;
  }
  return `/${cleanPath}`;
}

export const ADMIN_TOKEN_KEY = 'techstore_admin_token';
// Fired when the backend rejects the admin token (expired/invalid); AuthContext logs out on it.
export const ADMIN_UNAUTHORIZED_EVENT = 'techstore-admin-unauthorized';

function authHeaders(extra?: HeadersInit): Headers {
  const headers = new Headers(extra);
  const token = localStorage.getItem(ADMIN_TOKEN_KEY);
  if (token) headers.set('Authorization', `Bearer ${token}`);
  return headers;
}

async function adminFetch(url: string, init: RequestInit = {}): Promise<Response> {
  const res = await fetch(url, { ...init, headers: authHeaders(init.headers) });
  if (res.status === 401) {
    window.dispatchEvent(new Event(ADMIN_UNAUTHORIZED_EVENT));
  }
  return res;
}

// 2FA OTP & AUTH APIS
// Owner-only on the server (public only with the local dev helper); null when not available.
export async function fetchOtpSetup(): Promise<{
  secret: string;
  otpauthUrl: string;
  currentDevOtp?: string;
  stepSeconds: number;
} | null> {
  const res = await fetch(`${BASE_URL}/admin/auth/otp-setup`, { headers: authHeaders() });
  if (!res.ok) return null;
  const json = await res.json();
  return json.data;
}


// Whether the server currently serves the pairing QR (ADMIN_TOTP_ENROLLMENT=true).
export async function fetchSetupQrStatus(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE_URL}/admin/auth/setup-qr`);
    const json = await res.json();
    return Boolean(json?.data?.enrollmentOpen);
  } catch {
    return false;
  }
}

export async function fetchAdminSetupQr(credentials: {
  username: string;
  password: string;
}): Promise<{
  success: boolean;
  data?: {
    secret: string;
    otpauthUrl: string;
    qrCodeDataUrl: string;
    account: string;
    issuer: string;
  };
  message?: string;
}> {
  const res = await fetch(`${BASE_URL}/admin/auth/setup-qr`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials)
  });
  return await res.json();
}

export async function adminLogin(credentials: {
  username: string;
  password: string;
  otp: string;
}): Promise<{
  success: boolean;
  token?: string;
  user?: any;
  message?: string;
  requireOtp?: boolean;
}> {
  const res = await fetch(`${BASE_URL}/admin/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials)
  });
  return await res.json();
}

// DASHBOARD & ANALYTICS
export async function fetchAdminKPIs(): Promise<any> {
  const res = await adminFetch(`${BASE_URL}/admin/dashboard/kpis`);
  const json = await res.json();
  return json.data;
}

export async function fetchAdminCharts(): Promise<ChartSpec[]> {
  const res = await adminFetch(`${BASE_URL}/admin/dashboard/charts`);
  const json = await res.json();
  return json.data;
}

export async function fetchPinnedWidgets(): Promise<ChartSpec[]> {
  const res = await adminFetch(`${BASE_URL}/admin/dashboard/widgets`);
  const json = await res.json();
  return json.data;
}

export async function pinChartWidget(widget: ChartSpec): Promise<any> {
  const res = await adminFetch(`${BASE_URL}/admin/dashboard/widgets/pin`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ widget })
  });
  return await res.json();
}

// INVENTORY
export async function fetchAdminInventory(): Promise<any[]> {
  const res = await adminFetch(`${BASE_URL}/admin/inventory`);
  const json = await res.json();
  return json.data;
}

export async function createStockReceipt(receiptData: { variantId: string; qty: number; note: string }): Promise<any> {
  const res = await adminFetch(`${BASE_URL}/admin/inventory/receipt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(receiptData)
  });
  return await res.json();
}

// ORDERS
export async function fetchAdminOrders(status?: string): Promise<Order[]> {
  const url = status ? `${BASE_URL}/admin/orders?status=${status}` : `${BASE_URL}/admin/orders`;
  const res = await adminFetch(url);
  const json = await res.json();
  return json.data;
}

export async function updateOrderStatus(orderId: string, status: string, note?: string): Promise<any> {
  const res = await adminFetch(`${BASE_URL}/admin/orders/${orderId}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status, note })
  });
  return await res.json();
}

// DOCUMENTS
export async function fetchAdminDocuments(): Promise<StrategicDocument[]> {
  const res = await adminFetch(`${BASE_URL}/admin/documents`);
  const json = await res.json();
  return json.data;
}

export async function uploadStrategicDoc(doc: any): Promise<any> {
  const res = await adminFetch(`${BASE_URL}/admin/documents`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(doc)
  });
  return await res.json();
}

// STRATEGY CHATBOT
export async function sendAdminChatMessage(query: string): Promise<{
  thoughtSummary: string;
  insight: string;
  chartSpec?: ChartSpec;
  tableData?: any[];
  citations: string[];
  proposal?: StrategyProposal;
}> {
  const res = await adminFetch(`${BASE_URL}/admin/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
  });
  const json = await res.json();
  if (!res.ok || json.success === false) {
    throw new Error(json.message || `HTTP ${res.status}`);
  }
  return json.data;
}

export async function decideProposal(proposalId: string, optionId: string, decision: 'approved' | 'rejected'): Promise<any> {
  const res = await adminFetch(`${BASE_URL}/admin/recommendations/${proposalId}/decision`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ optionId, decision })
  });
  return await res.json();
}

// PRODUCTS
export async function fetchAdminProducts(): Promise<any[]> {
  const res = await adminFetch(`${BASE_URL}/admin/products`);
  const json = await res.json();
  return json.data || [];
}

export async function createAdminProduct(productData: any): Promise<any> {
  const res = await adminFetch(`${BASE_URL}/admin/products`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(productData)
  });
  return await res.json();
}

export async function updateAdminProduct(id: string, productData: any): Promise<any> {
  const res = await adminFetch(`${BASE_URL}/admin/products/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(productData)
  });
  return await res.json();
}

export async function deleteAdminProduct(id: string): Promise<any> {
  const res = await adminFetch(`${BASE_URL}/admin/products/${id}`, {
    method: 'DELETE'
  });
  return await res.json();
}

// PROMOTIONS
export async function fetchAdminPromotions(): Promise<any[]> {
  const res = await adminFetch(`${BASE_URL}/admin/promotions`);
  const json = await res.json();
  return json.data || [];
}

export async function createAdminPromotion(promoData: any): Promise<any> {
  const res = await adminFetch(`${BASE_URL}/admin/promotions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(promoData)
  });
  return await res.json();
}

export async function toggleAdminPromotion(id: string): Promise<any> {
  const res = await adminFetch(`${BASE_URL}/admin/promotions/${id}/toggle`, {
    method: 'PATCH'
  });
  return await res.json();
}

export async function deleteAdminPromotion(id: string): Promise<any> {
  const res = await adminFetch(`${BASE_URL}/admin/promotions/${id}`, {
    method: 'DELETE'
  });
  return await res.json();
}

// CUSTOMERS
export async function fetchAdminCustomers(): Promise<any[]> {
  const res = await adminFetch(`${BASE_URL}/admin/customers`);
  const json = await res.json();
  return json.data || [];
}

// QUOTATIONS
export async function fetchAdminQuotations(): Promise<any[]> {
  const res = await adminFetch(`${BASE_URL}/admin/quotations`);
  const json = await res.json();
  return json.data || [];
}

export async function updateAdminQuotationStatus(id: string, status: string): Promise<any> {
  const res = await adminFetch(`${BASE_URL}/admin/quotations/${id}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status })
  });
  return await res.json();
}

// REVIEWS
export async function fetchAdminReviews(): Promise<any[]> {
  const res = await adminFetch(`${BASE_URL}/admin/reviews`);
  const json = await res.json();
  return json.data || [];
}

export async function toggleAdminReviewStatus(id: string, status?: string): Promise<any> {
  const res = await adminFetch(`${BASE_URL}/admin/reviews/${id}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status })
  });
  return await res.json();
}

export async function replyAdminReview(id: string, reply: string): Promise<any> {
  const res = await adminFetch(`${BASE_URL}/admin/reviews/${id}/reply`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reply })
  });
  return await res.json();
}

// SETTINGS
export async function fetchAdminSettings(): Promise<any> {
  const res = await adminFetch(`${BASE_URL}/admin/settings`);
  const json = await res.json();
  return json.data;
}

export async function updateAdminSettings(settings: any): Promise<any> {
  const res = await adminFetch(`${BASE_URL}/admin/settings`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings)
  });
  return await res.json();
}
