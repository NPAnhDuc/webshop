import React from 'react';
import {
  ShieldCheck,
  Truck,
  RotateCcw,
  CreditCard,
  PhoneCall,
  Mail,
  MapPin,
  CheckCircle,
  Award,
  Sparkles
} from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

export const Footer: React.FC = () => {
  const { lang, t } = useLanguage();

  return (
    <footer className="bg-white dark:bg-[#0b0f19] text-slate-600 dark:text-slate-400 text-xs border-t border-gray-200 dark:border-slate-800 mt-12 select-none transition-colors">
      {/* 4 TechStore Value Props */}
      <div className="border-b border-gray-200 dark:border-slate-800 py-6 bg-gray-50/70 dark:bg-[#151c2c]/40">
        <div className="max-w-[1440px] xl:max-w-[1536px] mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6">
          <div className="flex items-center space-x-3 bg-white dark:bg-[#151c2c] p-3 rounded-xl border border-gray-150 dark:border-slate-800 shadow-2xs">
            <div className="w-10 h-10 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 text-[#059669] flex items-center justify-center flex-shrink-0">
              <Truck className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-bold text-slate-900 dark:text-slate-100 text-xs">
                {lang === 'vi' ? 'Giao Nhanh 2 Giờ' : 'Fast 2H Delivery'}
              </h4>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">
                {lang === 'vi' ? 'Miễn phí cho đơn từ 300.000₫' : 'Free shipping from 300k'}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3 bg-white dark:bg-[#151c2c] p-3 rounded-xl border border-gray-150 dark:border-slate-800 shadow-2xs">
            <div className="w-10 h-10 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 text-[#059669] flex items-center justify-center flex-shrink-0">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-bold text-slate-900 dark:text-slate-100 text-xs">
                {lang === 'vi' ? '100% Chính Hãng' : '100% Genuine'}
              </h4>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">
                {lang === 'vi' ? 'Đầy đủ hóa đơn VAT điện tử' : 'Full e-VAT Invoices'}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3 bg-white dark:bg-[#151c2c] p-3 rounded-xl border border-gray-150 dark:border-slate-800 shadow-2xs">
            <div className="w-10 h-10 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 text-[#059669] flex items-center justify-center flex-shrink-0">
              <RotateCcw className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-bold text-slate-900 dark:text-slate-100 text-xs">
                {lang === 'vi' ? '1 Đổi 1 Trong 30 Ngày' : '30-Day 1-to-1 Swap'}
              </h4>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">
                {lang === 'vi' ? 'Lỗi phần cứng là đổi mới ngay' : 'Instant hardware replacement'}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3 bg-white dark:bg-[#151c2c] p-3 rounded-xl border border-gray-150 dark:border-slate-800 shadow-2xs">
            <div className="w-10 h-10 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 text-[#059669] flex items-center justify-center flex-shrink-0">
              <CreditCard className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-bold text-slate-900 dark:text-slate-100 text-xs">
                {lang === 'vi' ? 'Trả Góp 0% Lãi Suất' : '0% Installment'}
              </h4>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">
                {lang === 'vi' ? 'Qua thẻ tín dụng duyệt 15p' : 'Via Credit Card & ID (15 mins)'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main 4 Footer Columns */}
      <div className="max-w-[1440px] xl:max-w-[1536px] mx-auto px-4 py-10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
        
        {/* Col 1: Hotlines & Payments */}
        <div className="space-y-3">
          <h3 className="font-black text-slate-900 dark:text-slate-100 text-xs uppercase tracking-wider text-[#059669] dark:text-emerald-400">
            {lang === 'vi' ? 'Tổng Đài Hỗ Trợ Miễn Phí' : 'Toll-Free Support Lines'}
          </h3>
          <ul className="space-y-1.5 text-[11px]">
            <li>{lang === 'vi' ? 'Gọi mua hàng:' : 'Sales hotline:'} <strong className="text-slate-900 dark:text-slate-100 font-bold">1800.6868</strong> (8h00 - 21h30)</li>
            <li>{lang === 'vi' ? 'Khiếu nại, góp ý:' : 'Feedback:'} <strong className="text-slate-900 dark:text-slate-100 font-bold">1800.6888</strong> (8h00 - 21h30)</li>
            <li>{lang === 'vi' ? 'Bảo hành & kỹ thuật:' : 'Warranty & Lab:'} <strong className="text-slate-900 dark:text-slate-100 font-bold">1800.6899</strong> (8h00 - 21h00)</li>
          </ul>

          <div className="pt-2">
            <h4 className="font-bold text-slate-900 dark:text-slate-100 text-xs mb-2">
              {lang === 'vi' ? 'Phương thức thanh toán' : 'Payment Methods'}
            </h4>
            <div className="flex flex-wrap gap-1.5">
              <span className="px-2 py-1 bg-gray-100 dark:bg-slate-800 rounded border border-gray-200 dark:border-slate-700 font-bold text-[10px] text-slate-700 dark:text-slate-300">VISA / MASTER</span>
              <span className="px-2 py-1 bg-emerald-50 dark:bg-emerald-950/60 rounded border border-emerald-200 dark:border-emerald-800 font-bold text-[10px] text-[#059669] dark:text-emerald-400">VNPAY QR</span>
              <span className="px-2 py-1 bg-pink-50 dark:bg-pink-950/60 rounded border border-pink-200 dark:border-pink-900/60 font-bold text-[10px] text-pink-700 dark:text-pink-300">MOMO</span>
              <span className="px-2 py-1 bg-blue-50 dark:bg-blue-950/60 rounded border border-blue-200 dark:border-blue-900/60 font-bold text-[10px] text-blue-700 dark:text-blue-300">ZALOPAY</span>
              <span className="px-2 py-1 bg-yellow-50 dark:bg-yellow-950/60 rounded border border-yellow-200 dark:border-yellow-800/60 font-bold text-[10px] text-yellow-800 dark:text-yellow-300">TRẢ GÓP 0%</span>
            </div>
          </div>
        </div>

        {/* Col 2: Policies */}
        <div className="space-y-2.5">
          <h3 className="font-black text-slate-900 dark:text-slate-100 text-xs uppercase tracking-wider">
            {lang === 'vi' ? 'Thông Tin & Chính Sách' : 'Information & Policies'}
          </h3>
          <ul className="space-y-2 text-[11px] text-slate-600 dark:text-slate-400">
            <li><a href="#" className="hover:text-[#059669] dark:hover:text-emerald-400 transition">{lang === 'vi' ? 'Mua hàng và thanh toán Online' : 'Online Purchase & Checkout'}</a></li>
            <li><a href="#" className="hover:text-[#059669] dark:hover:text-emerald-400 transition">{lang === 'vi' ? 'Chính sách mua hàng trả góp 0%' : '0% Installment Policy'}</a></li>
            <li><a href="#" className="hover:text-[#059669] dark:hover:text-emerald-400 transition">{lang === 'vi' ? 'Chính sách giao hàng hỏa tốc 2 giờ' : '2-Hour Delivery Policy'}</a></li>
            <li><a href="#" className="hover:text-[#059669] dark:hover:text-emerald-400 transition">{lang === 'vi' ? 'Chính sách bảo hành & 1 đổi 1 trong 30 ngày' : '30-Day Hardware Replacement'}</a></li>
            <li><a href="#" className="hover:text-[#059669] dark:hover:text-emerald-400 transition">{lang === 'vi' ? 'Tra cứu hóa đơn điện tử VAT' : 'E-VAT Invoice Lookup'}</a></li>
            <li><a href="#" className="hover:text-[#059669] dark:hover:text-emerald-400 transition">{lang === 'vi' ? 'Chính sách bảo mật thông tin khách hàng' : 'Customer Privacy Policy'}</a></li>
          </ul>
        </div>

        {/* Col 3: Services & T-Member */}
        <div className="space-y-2.5">
          <h3 className="font-black text-slate-900 dark:text-slate-100 text-xs uppercase tracking-wider">
            {lang === 'vi' ? 'Dịch Vụ & T-Member' : 'Services & T-Member'}
          </h3>
          <ul className="space-y-2 text-[11px] text-slate-600 dark:text-slate-400">
            <li><a href="#" className="hover:text-[#059669] dark:hover:text-emerald-400 transition">{lang === 'vi' ? 'Khách hàng doanh nghiệp (B2B) chiết khấu cao' : 'Corporate B2B Discount Program'}</a></li>
            <li><a href="#" className="hover:text-[#059669] dark:hover:text-emerald-400 transition">{lang === 'vi' ? 'Đặc quyền hội viên T-Member & T-VIP' : 'T-Member & T-VIP Perks'}</a></li>
            <li><a href="#" className="hover:text-[#059669] dark:hover:text-emerald-400 transition">{lang === 'vi' ? 'Thu cũ đổi mới - Lên đời trợ giá 4 triệu' : 'Trade-in & Upgrade Subsidy up to 4M'}</a></li>
            <li><a href="#" className="hover:text-[#059669] dark:hover:text-emerald-400 transition">{lang === 'vi' ? 'Dịch vụ kỹ thuật bảo dưỡng phòng Lab' : 'Lab Maintenance & Stress-Testing'}</a></li>
            <li><a href="#" className="hover:text-[#059669] dark:hover:text-emerald-400 transition">{lang === 'vi' ? 'Tin công nghệ TechStore News mới nhất' : 'TechStore News & Updates'}</a></li>
          </ul>
        </div>

        {/* Col 4: Certification & AI Assistant */}
        <div className="space-y-3">
          <h3 className="font-black text-slate-900 dark:text-slate-100 text-xs uppercase tracking-wider">
            {lang === 'vi' ? 'Chứng Nhận & Công Nghệ' : 'Certifications & AI'}
          </h3>
          <div className="p-3 bg-emerald-50/60 dark:bg-emerald-950/40 rounded-xl border border-emerald-200/80 dark:border-emerald-800 text-[11px] space-y-1.5">
            <div className="flex items-center space-x-1.5 text-[#059669] dark:text-emerald-400 font-bold">
              <Sparkles className="w-4 h-4" />
              <span>{lang === 'vi' ? 'Trợ Lý AI TechStore' : 'TechStore AI Assistant'}</span>
            </div>
            <p className="text-slate-600 dark:text-slate-300 leading-snug">
              {lang === 'vi'
                ? 'Tư vấn chọn cấu hình laptop, ráp PC Gaming theo ngân sách và kiểm tra tương thích chân cắm 24/7.'
                : '24/7 AI-driven PC configuration, laptop advisory, and hardware socket compatibility validation.'}
            </p>
          </div>

          <div className="pt-1 flex items-center space-x-2">
            <div className="px-3 py-1.5 bg-blue-50 dark:bg-blue-950/60 border border-blue-200 dark:border-blue-900/60 rounded-lg text-blue-700 dark:text-blue-300 font-extrabold text-[10px] flex items-center space-x-1">
              <CheckCircle className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
              <span>{lang === 'vi' ? 'ĐÃ THÔNG BÁO BỘ CÔNG THƯƠNG' : 'MINISTRY OF INDUSTRY & TRADE VERIFIED'}</span>
            </div>
          </div>
        </div>

      </div>

      {/* Showroom Network Bar */}
      <div className="border-t border-gray-200 dark:border-slate-800 py-6 bg-gray-50 dark:bg-[#111726]/60">
        <div className="max-w-[1440px] xl:max-w-[1536px] mx-auto px-4 space-y-3">
          <div className="flex items-center space-x-2 text-slate-900 dark:text-slate-100 font-bold text-xs">
            <MapPin className="w-4 h-4 text-[#059669] dark:text-emerald-400" />
            <span className="uppercase tracking-wide">{lang === 'vi' ? 'Hệ thống Showroom TechStore PC trên toàn quốc:' : 'TechStore PC Flagship Showroom Network:'}</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-[11px] text-slate-600 dark:text-slate-400">
            <div>
              <strong className="text-slate-800 dark:text-slate-200">Showroom 1 (Thái Hà):</strong> 377-379 Thái Hà, Q. Đống Đa, Hà Nội • <span className="text-[#059669] dark:text-emerald-400 font-mono">097.111.3323</span>
            </div>
            <div>
              <strong className="text-slate-800 dark:text-slate-200">Showroom 2 (Lê Thanh Nghị):</strong> 131 Lê Thanh Nghị, Q. Hai Bà Trưng, Hà Nội • <span className="text-[#059669] dark:text-emerald-400 font-mono">098.333.6623</span>
            </div>
            <div>
              <strong className="text-slate-800 dark:text-slate-200">Showroom 3 (TP.HCM):</strong> 249 Lý Thường Kiệt, P.15, Q.10, TP.HCM • <span className="text-[#059669] dark:text-emerald-400 font-mono">090.888.6623</span>
            </div>
            <div>
              <strong className="text-slate-800 dark:text-slate-200">Showroom 4 (Đà Nẵng):</strong> 83-85 Nguyễn Văn Linh, Q. Hải Châu, Đà Nẵng • <span className="text-[#059669] dark:text-emerald-400 font-mono">091.777.9923</span>
            </div>
          </div>
        </div>
      </div>

      <div className="border-t border-gray-200 dark:border-slate-800 py-4 bg-gray-50 dark:bg-[#0b0f19] text-center text-[11px] text-slate-500 dark:text-slate-500">
        © 2026 {lang === 'vi' ? 'Hệ thống Showroom Máy Tính & Linh Kiện TechStore PC. Tiêu chuẩn bán lẻ phần cứng chuyên nghiệp.' : 'TechStore PC Hardware & Computer Showroom Network. Professional PC retail standards.'}
      </div>
    </footer>
  );
};

