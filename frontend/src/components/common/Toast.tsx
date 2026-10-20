import React from 'react';
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react';

export interface ToastMessage {
  id: string;
  type: 'success' | 'warning' | 'info';
  title: string;
  message?: string;
}

interface ToastContainerProps {
  toasts: ToastMessage[];
  onDismiss: (id: string) => void;
}

export const ToastContainer: React.FC<ToastContainerProps> = ({ toasts, onDismiss }) => {
  if (toasts.length === 0) return null;

  return (
    <div className="fixed top-5 right-5 z-50 flex flex-col space-y-2.5 max-w-sm w-full pointer-events-none">
      {toasts.map(t => (
        <div
          key={t.id}
          className="pointer-events-auto bg-white rounded-xl shadow-xl border border-slate-200 p-3.5 flex items-start space-x-3 animate-in slide-in-from-top-3 fade-in duration-200"
        >
          <div className="flex-shrink-0 mt-0.5">
            {t.type === 'success' && <CheckCircle2 className="w-5 h-5 text-emerald-600" />}
            {t.type === 'warning' && <AlertCircle className="w-5 h-5 text-amber-500" />}
            {t.type === 'info' && <Info className="w-5 h-5 text-blue-600" />}
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="text-xs font-bold text-slate-900">{t.title}</h4>
            {t.message && <p className="text-[11px] text-slate-500 mt-0.5 leading-snug">{t.message}</p>}
          </div>
          <button
            onClick={() => onDismiss(t.id)}
            className="text-slate-400 hover:text-slate-600 p-1 -mr-1"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      ))}
    </div>
  );
};
