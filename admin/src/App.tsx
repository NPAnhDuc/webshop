import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './context/AuthContext';
import { AdminLoginGate } from './components/auth/AdminLoginGate';
import { AdminLayout, AdminTabType } from './components/admin/AdminLayout';
import { ToastContainer, ToastMessage } from './components/common/Toast';

// Lazy-loaded Admin Panels
const DashboardView = React.lazy(() => import('./components/admin/DashboardView').then(m => ({ default: m.DashboardView })));
const ProductManagement = React.lazy(() => import('./components/admin/ProductManagement').then(m => ({ default: m.ProductManagement })));
const InventoryManagement = React.lazy(() => import('./components/admin/InventoryManagement').then(m => ({ default: m.InventoryManagement })));
const OrderManagement = React.lazy(() => import('./components/admin/OrderManagement').then(m => ({ default: m.OrderManagement })));
const PromotionManagement = React.lazy(() => import('./components/admin/PromotionManagement').then(m => ({ default: m.PromotionManagement })));
const QuotationManagement = React.lazy(() => import('./components/admin/QuotationManagement').then(m => ({ default: m.QuotationManagement })));
const CustomerManagement = React.lazy(() => import('./components/admin/CustomerManagement').then(m => ({ default: m.CustomerManagement })));
const ReviewManagement = React.lazy(() => import('./components/admin/ReviewManagement').then(m => ({ default: m.ReviewManagement })));
const DocumentManagement = React.lazy(() => import('./components/admin/DocumentManagement').then(m => ({ default: m.DocumentManagement })));
const AdminChatbotView = React.lazy(() => import('./components/admin/AdminChatbotView').then(m => ({ default: m.AdminChatbotView })));
const StoreSettingsManagement = React.lazy(() => import('./components/admin/StoreSettingsManagement').then(m => ({ default: m.StoreSettingsManagement })));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 2,
      refetchOnWindowFocus: false
    }
  }
});

const AdminMainApp: React.FC = () => {
  const { isAuthenticated, logout, user } = useAuth();
  const [currentTab, setCurrentTab] = useState<AdminTabType>('dashboard');
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const addToast = (title: string, message?: string, type: 'success' | 'warning' | 'info' = 'success') => {
    const id = `toast-${Date.now()}-${Math.random()}`;
    setToasts(prev => [...prev, { id, title, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 4000);
  };

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  const handleOpenStorefront = () => {
    // Open the customer-facing storefront in a new tab
    const storefrontUrl = window.location.port === '5174'
      ? `${window.location.protocol}//${window.location.hostname}:5173`
      : '/';
    window.open(storefrontUrl, '_blank');
  };

  if (!isAuthenticated) {
    return (
      <>
        <AdminLoginGate
          onSuccess={() => {
            addToast('Đăng nhập thành công', `Chào mừng ${user?.name || 'Quản trị viên'}`, 'success');
          }}
        />
        <ToastContainer toasts={toasts} onDismiss={removeToast} />
      </>
    );
  }

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col">
      <AdminLayout
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        onBackToStorefront={handleOpenStorefront}
      >
        {currentTab === 'dashboard' && <DashboardView onNavigateToChatbot={() => setCurrentTab('chatbot')} />}
        {currentTab === 'products' && <ProductManagement />}
        {currentTab === 'inventory' && <InventoryManagement />}
        {currentTab === 'orders' && <OrderManagement />}
        {currentTab === 'promotions' && <PromotionManagement />}
        {currentTab === 'quotations' && <QuotationManagement />}
        {currentTab === 'customers' && <CustomerManagement />}
        {currentTab === 'reviews' && <ReviewManagement />}
        {currentTab === 'documents' && <DocumentManagement />}
        {currentTab === 'chatbot' && <AdminChatbotView />}
        {currentTab === 'settings' && <StoreSettingsManagement />}
      </AdminLayout>
      <ToastContainer toasts={toasts} onDismiss={removeToast} />
    </div>
  );
};

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <AdminMainApp />
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
