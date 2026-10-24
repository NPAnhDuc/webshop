import React, { useState, useEffect } from 'react';
import { PhoneCall, ArrowUp, FileText } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

interface SideWingsProps {
  onNavigatePCBuilder?: () => void;
  onOpenLookup?: () => void;
  onOpenChatbot?: () => void;
}

export const SideWings: React.FC<SideWingsProps> = ({
  onOpenLookup
}) => {
  const { lang } = useLanguage();
  const [showScrollTop, setShowScrollTop] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setShowScrollTop(window.scrollY > 300);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="fixed bottom-6 left-6 z-40 flex flex-col items-center space-y-2 select-none">
      {/* Hotline Quick Call */}
      <a
        href="tel:18006868"
        title="Hotline miễn phí 1800.6868"
        className="w-10 h-10 rounded-full bg-slate-900 hover:bg-red-600 dark:bg-slate-800 dark:hover:bg-red-600 text-white shadow-md flex items-center justify-center transition-all duration-200 hover:scale-105 active:scale-95"
      >
        <PhoneCall className="w-4 h-4" />
      </a>

      {/* Track Order Quick Icon */}
      {onOpenLookup && (
        <button
          onClick={onOpenLookup}
          title={lang === 'vi' ? 'Tra cứu tiến độ đơn hàng' : 'Track Order'}
          className="w-10 h-10 rounded-full bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 shadow-md flex items-center justify-center transition-all duration-200 hover:scale-105 active:scale-95 cursor-pointer hover:border-red-500 hover:text-red-600"
        >
          <FileText className="w-4 h-4" />
        </button>
      )}

      {/* Back to Top Button */}
      {showScrollTop && (
        <button
          onClick={scrollToTop}
          title={lang === 'vi' ? 'Lên đầu trang' : 'Back to top'}
          className="w-10 h-10 rounded-full bg-slate-900/90 dark:bg-slate-700/90 backdrop-blur-md text-white shadow-md flex items-center justify-center transition-all duration-200 hover:scale-105 active:scale-95 cursor-pointer animate-in fade-in"
        >
          <ArrowUp className="w-4 h-4" />
        </button>
      )}
    </div>
  );
};
