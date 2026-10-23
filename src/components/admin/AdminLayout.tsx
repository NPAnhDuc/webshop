import React, { useState } from 'react';
import {
  LayoutDashboard,
  Package,
  Boxes,
  ClipboardList,
  Tag,
  SlidersHorizontal,
  Users,
  Star,
  FileText,
  Bot,
  Settings,
  LogOut,
  Store,
  User,
  Shield,
  ChevronRight,
  Sparkles
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { CuteRobotAvatar } from '../common/CuteRobotAvatar';

export type AdminTabType =
  | 'dashboard'
  | 'products'
  | 'inventory'
  | 'orders'
  | 'promotions'
  | 'quotations'
  | 'customers'
  | 'reviews'
  | 'documents'
  | 'chatbot'
  | 'settings';

interface AdminLayoutProps {
  currentTab: AdminTabType;
  onSelectTab: (tab: AdminTabType) => void;
  onBackToStorefront: () => void;
  children: React.ReactNode;
}

export const AdminLayout: React.FC<AdminLayoutProps> = ({
  currentTab,
  onSelectTab,
  onBackToStorefront,
  children
}) => {
  const { user, logout } = useAuth();

  const navItems: { key: AdminTabType; label: string; icon: any; isSpecial?: boolean; badge?: string }[] = [
    { key: 'dashboard', label: 'Tổng quan & Doanh thu', icon: LayoutDashboard },
    { key: 'products', label: 'Quản lý Sản phẩm', icon: Package, badge: '67 SP' },
    { key: 'inventory', label: 'Quản lý Kho & Tồn', icon: Boxes },
    { key: 'orders', label: 'Quản lý Đơn hàng', icon: ClipboardList },
    { key: 'promotions', label: 'Mã Giảm & Flash Sale', icon: Tag },
    { key: 'quotations', label: 'Báo Giá Ráp PC (Rigs)', icon: SlidersHorizontal },
    { key: 'customers', label: 'Khách Hàng & T-Member', icon: Users },
    { key: 'reviews', label: 'Kiểm Duyệt Đánh Giá', icon: Star },
    { key: 'documents', label: 'Tài liệu Chiến lược (RAG)', icon: FileText },
    { key: 'chatbot', label: 'Bộ phận Dữ liệu AI (Bot)', icon: Bot, isSpecial: true },
    { key: 'settings', label: 'Cấu hình Cửa Hàng', icon: Settings }
  ];

  return (
    <div className="min-h-screen bg-slate-100 dark:bg-[#0b0f19] flex flex-col md:flex-row select-none transition-colors">
      {/* Sidebar */}
      <aside className="w-full md:w-64 bg-slate-900 dark:bg-[#070c14] text-slate-300 flex flex-col justify-between border-r border-slate-800 flex-shrink-0">
        <div>
          {/* Brand */}
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center text-white font-black text-sm shadow-md">
                TS
              </div>
              <div>
                <span className="text-sm font-black text-white tracking-wide block">TechStore Admin</span>
                <span className="text-[10px] text-emerald-400 font-semibold block">Hệ điều hành bán lẻ & AI</span>
              </div>
            </div>
          </div>

          {/* User badge */}
          <div className="p-3 mx-3 my-3 bg-slate-800/80 dark:bg-slate-850/60 rounded-xl border border-slate-700/60 flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xs flex-shrink-0">
              <User className="w-4 h-4" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-bold text-white truncate">{user?.name || 'Chị Lan (Chủ Shop)'}</p>
              <p className="text-[10px] text-emerald-400 flex items-center space-x-1">
                <Shield className="w-2.5 h-2.5" />
                <span>Toàn quyền quản trị</span>
              </p>
            </div>
          </div>

          {/* Navigation Items */}
          <nav className="px-3 space-y-0.5 mt-2 max-h-[calc(100vh-250px)] overflow-y-auto scrollbar-none">
            {navItems.map(item => {
              const Icon = item.icon;
              const isActive = currentTab === item.key;
              return (
                <button
                  key={item.key}
                  onClick={() => onSelectTab(item.key)}
                  className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-semibold transition cursor-pointer ${
                    isActive
                      ? 'bg-[#059669] text-white shadow-xs'
                      : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'
                  }`}
                >
                  <div className="flex items-center space-x-2.5 min-w-0">
                    {item.key === 'chatbot' ? (
                      <div className="w-5 h-5 flex items-center justify-center flex-shrink-0">
                        <CuteRobotAvatar mode="admin" size="sm" isWaving={true} className="scale-75" />
                      </div>
                    ) : (
                      <Icon className={`w-4 h-4 flex-shrink-0 ${isActive ? 'text-white' : item.isSpecial ? 'text-amber-400' : 'text-slate-400'}`} />
                    )}
                    <span className="truncate">{item.label}</span>
                  </div>

                  {item.badge && (
                    <span className="text-[9px] bg-slate-800 text-slate-300 font-bold px-1.5 py-0.2 rounded border border-slate-700">
                      {item.badge}
                    </span>
                  )}

                  {item.isSpecial && (
                    <span className="text-[9px] bg-amber-400/20 text-amber-300 font-bold px-1.5 py-0.2 rounded animate-pulse">
                      DE/DA/DS
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Sidebar Footer */}
        <div className="p-3 border-t border-slate-800 space-y-1">
          <button
            onClick={onBackToStorefront}
            className="w-full flex items-center space-x-2 px-3 py-2 rounded-xl text-xs font-semibold text-slate-300 hover:bg-slate-800 hover:text-white transition cursor-pointer"
          >
            <Store className="w-4 h-4 text-emerald-400" />
            <span>Về trang bán lẻ Storefront</span>
          </button>
          <button
            onClick={() => {
              logout();
              onBackToStorefront();
            }}
            className="w-full flex items-center space-x-2 px-3 py-2 rounded-xl text-xs font-semibold text-red-400 hover:bg-red-500/10 transition cursor-pointer"
          >
            <LogOut className="w-4 h-4" />
            <span>Đăng xuất hệ thống</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        {/* Top Header bar */}
        <header className="bg-white dark:bg-[#151c2c] border-b border-slate-200 dark:border-slate-800 px-6 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-2 text-xs text-slate-500 dark:text-slate-400">
            <span>Admin</span>
            <ChevronRight className="w-3.5 h-3.5" />
            <span className="font-bold text-slate-800 dark:text-slate-100">
              {navItems.find(i => i.key === currentTab)?.label}
            </span>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={onBackToStorefront}
              className="text-xs font-bold px-3.5 py-1.5 border border-slate-200 dark:border-slate-700 hover:border-emerald-500 rounded-xl text-slate-700 dark:text-slate-200 bg-white dark:bg-slate-800 hover:bg-slate-50 flex items-center space-x-1.5 transition cursor-pointer shadow-2xs"
            >
              <Store className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
              <span>Xem Web Bán Hàng</span>
            </button>
          </div>
        </header>

        {/* Content Body */}
        <div className="p-6 flex-1 bg-slate-50/70 dark:bg-[#0b0f19]">
          {children}
        </div>
      </main>
    </div>
  );
};
