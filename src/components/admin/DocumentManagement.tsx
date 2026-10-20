import React, { useState, useEffect } from 'react';
import {
  FileText,
  Upload,
  CheckCircle2,
  Clock,
  BookOpen,
  Plus,
  Search,
  Tag
} from 'lucide-react';
import { fetchAdminDocuments, uploadStrategicDoc } from '../../services/api';
import { StrategicDocument } from '../../types';

export const DocumentManagement: React.FC = () => {
  const [docs, setDocs] = useState<StrategicDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [title, setTitle] = useState('');
  const [docType, setDocType] = useState<'sales_plan' | 'marketing' | 'policy' | 'management_report'>('sales_plan');
  const [period, setPeriod] = useState('2026-Q4');
  const [version, setVersion] = useState('1.0');
  const [content, setContent] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const loadDocs = () => {
    setLoading(true);
    fetchAdminDocuments()
      .then(data => setDocs(data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadDocs();
  }, []);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !content) return;
    setSubmitting(true);
    try {
      await uploadStrategicDoc({
        title,
        docType,
        period,
        version,
        content
      });
      setShowUploadModal(false);
      setTitle('');
      setContent('');
      loadDocs();
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h2 className="text-xl font-black text-slate-900 tracking-tight flex items-center space-x-2">
            <FileText className="w-5 h-5 text-blue-600" />
            <span>Quản Lý Tài Liệu Chiến Lược (RAG Knowledge Base)</span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Các tài liệu định hướng kinh doanh, chính sách giá và ngân sách được lập chỉ mục cho AI Chatbot trích dẫn
          </p>
        </div>

        <button
          onClick={() => setShowUploadModal(true)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold flex items-center space-x-1.5 shadow-sm transition"
        >
          <Upload className="w-4 h-4" />
          <span>Tải lên tài liệu mới</span>
        </button>
      </div>

      {/* Documents List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-full py-12 text-center text-xs text-slate-400">Đang tải kho tri thức RAG...</div>
        ) : (
          docs.map(doc => (
            <div key={doc.id} className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between space-y-4 hover:border-blue-400 transition">
              <div>
                <div className="flex justify-between items-start">
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-50 text-blue-700 uppercase">
                    {doc.docType.replace('_', ' ')}
                  </span>
                  <span className="flex items-center space-x-1 text-[11px] font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">
                    <CheckCircle2 className="w-3 h-3" />
                    <span>Đã lập chỉ mục</span>
                  </span>
                </div>

                <h3 className="font-bold text-slate-900 text-sm mt-2.5 line-clamp-1">{doc.title}</h3>
                <div className="flex items-center space-x-3 text-xs text-slate-500 mt-1">
                  <span>Kỳ: <strong>{doc.period}</strong></span>
                  <span>•</span>
                  <span>Phiên bản: <strong>{doc.version}</strong></span>
                </div>

                {/* Chunks summary */}
                <div className="mt-4 pt-3 border-t border-slate-100 space-y-2">
                  <span className="text-[11px] font-bold text-slate-700 flex items-center space-x-1">
                    <BookOpen className="w-3 h-3 text-blue-600" />
                    <span>Các đoạn trích mục tiêu ({doc.chunks?.length || 0}):</span>
                  </span>
                  <div className="space-y-1.5">
                    {doc.chunks?.slice(0, 2).map((ch, idx) => (
                      <div key={idx} className="p-2 bg-slate-50 rounded border border-slate-100 text-[11px] text-slate-600">
                        <strong className="text-slate-800 block text-[10px] truncate">{ch.headingPath}</strong>
                        <p className="line-clamp-2 mt-0.5">{ch.text}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="pt-2 text-[10px] text-slate-400 border-t border-slate-100 flex items-center justify-between">
                <span>Hiệu lực: {doc.effectiveFrom} &rarr; {doc.effectiveTo}</span>
                <span className="text-blue-600 font-semibold cursor-pointer hover:underline">Xem toàn văn</span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Upload Document Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
                <Upload className="w-4 h-4 text-blue-600" />
                <span>Nạp Tài Liệu Chiến Lược Mới Vào RAG</span>
              </h3>
              <button onClick={() => setShowUploadModal(false)} className="text-slate-400 hover:text-slate-600">&times;</button>
            </div>

            <form onSubmit={handleUpload} className="space-y-3 text-xs">
              <div>
                <label className="block font-medium text-slate-700 mb-1">Tiêu đề tài liệu:</label>
                <input
                  type="text"
                  value={title}
                  onChange={e => setTitle(e.target.value)}
                  placeholder="Ví dụ: Kế hoạch bán hàng và Marketing tháng 11/2026"
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs"
                  required
                />
              </div>

              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="block font-medium text-slate-700 mb-1">Loại:</label>
                  <select
                    value={docType}
                    onChange={e => setDocType(e.target.value as any)}
                    className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg text-xs bg-white"
                  >
                    <option value="sales_plan">Kế hoạch bán</option>
                    <option value="marketing">Marketing</option>
                    <option value="policy">Chính sách giá</option>
                    <option value="management_report">Báo cáo quản trị</option>
                  </select>
                </div>
                <div>
                  <label className="block font-medium text-slate-700 mb-1">Kỳ áp dụng:</label>
                  <input
                    type="text"
                    value={period}
                    onChange={e => setPeriod(e.target.value)}
                    className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg text-xs"
                  />
                </div>
                <div>
                  <label className="block font-medium text-slate-700 mb-1">Phiên bản:</label>
                  <input
                    type="text"
                    value={version}
                    onChange={e => setVersion(e.target.value)}
                    className="w-full px-2.5 py-1.5 border border-slate-200 rounded-lg text-xs"
                  />
                </div>
              </div>

              <div>
                <label className="block font-medium text-slate-700 mb-1">Nội dung văn bản (Markdown hoặc văn bản thuần):</label>
                <textarea
                  rows={8}
                  value={content}
                  onChange={e => setContent(e.target.value)}
                  placeholder="Dán nội dung kế hoạch doanh thu, ngân sách, chỉ tiêu từng nhóm hàng tại đây..."
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs font-mono"
                  required
                />
              </div>

              <div className="pt-2 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-4 py-2 border border-slate-200 text-slate-700 rounded-lg font-semibold hover:bg-slate-50"
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold"
                >
                  {submitting ? 'Đang lập chỉ mục RAG...' : 'Tải lên & Lập chỉ mục'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
