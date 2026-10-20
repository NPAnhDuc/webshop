import React, { useState, useRef, useEffect } from 'react';
import {
  Bot,
  Send,
  Pin,
  CheckCircle2,
  AlertTriangle,
  FileText,
  TrendingUp,
  Sparkles,
  Layers,
  ThumbsUp,
  ThumbsDown,
  BookOpen
} from 'lucide-react';
import { sendAdminChatMessage, pinChartWidget, decideProposal } from '../../services/api';
import { ChartSpec, StrategyProposal } from '../../types';
import { CuteRobotAvatar } from '../common/CuteRobotAvatar';

interface AdminMessage {
  id: string;
  sender: 'user' | 'bot';
  text?: string;
  thoughtSummary?: string;
  insight?: string;
  chartSpec?: ChartSpec;
  tableData?: any[];
  citations?: string[];
  proposal?: StrategyProposal;
  timestamp: string;
}

export const AdminChatbotView: React.FC = () => {
  const [messages, setMessages] = useState<AdminMessage[]>([
    {
      id: 'init-msg',
      sender: 'bot',
      thoughtSummary: 'Sẵn sàng tiếp nhận câu hỏi điều hành kinh doanh từ chủ shop.',
      insight: `Chào chị Lan! Em là **Trợ lý Phân tích Dữ liệu AI** của TechStore (đóng vai trò DE/DA/DS thu nhỏ).\n\nEm đã kết nối trực tiếp với **Cơ sở dữ liệu bán hàng thời gian thực** và kho **Tài liệu chiến lược (RAG)** của shop. Chị có thể hỏi em các câu hỏi mẫu sau hoặc gõ câu hỏi tự nhiên:`,
      citations: ['Kho dữ liệu bán hàng và tài liệu chiến lược TechStore Q3-Q4/2026'],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [pinnedSuccess, setPinnedSuccess] = useState<string | null>(null);
  const [proposalStatus, setProposalStatus] = useState<Record<string, string>>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const sampleQuestions = [
    'Quý 3 này đạt bao nhiêu % kế hoạch, vì sao bị lệch?',
    'Mã nào đang tồn lâu nhất, tháng sau nên làm gì?',
    'Mục tiêu doanh thu quý 4 của nhóm gaming là bao nhiêu?',
    'Tổng quan sức khỏe kinh doanh hiện tại'
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (textToSend?: string) => {
    const text = textToSend || input;
    if (!text.trim() || loading) return;

    const userMsg: AdminMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    if (!textToSend) setInput('');
    setLoading(true);

    try {
      const res = await sendAdminChatMessage(text);
      const botMsg: AdminMessage = {
        id: `bot-${Date.now()}`,
        sender: 'bot',
        thoughtSummary: res.thoughtSummary,
        insight: res.insight,
        chartSpec: res.chartSpec,
        tableData: res.tableData,
        citations: res.citations,
        proposal: res.proposal,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [
        ...prev,
        {
          id: `bot-err-${Date.now()}`,
          sender: 'bot',
          insight: 'Đã xảy ra lỗi khi phân tích dữ liệu, vui lòng kiểm tra kết nối máy chủ.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handlePin = async (chartSpec: ChartSpec) => {
    try {
      await pinChartWidget(chartSpec);
      setPinnedSuccess(chartSpec.chart_id);
      setTimeout(() => setPinnedSuccess(null), 3000);
    } catch (err) {
      console.error(err);
    }
  };

  const handleProposalDecision = async (proposalId: string, optionId: string, decision: 'approved' | 'rejected') => {
    try {
      await decideProposal(proposalId, optionId, decision);
      setProposalStatus(prev => ({
        ...prev,
        [proposalId]: decision === 'approved' ? `Đã phê duyệt phương án ${optionId.toUpperCase()}` : 'Đã từ chối phương án'
      }));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col h-[78vh] overflow-hidden">
      {/* Top Header with Cute Admin Robot */}
      <div className="bg-slate-900 text-white px-6 py-4 flex items-center justify-between border-b border-slate-800">
        <div className="flex items-center space-x-3.5">
          <CuteRobotAvatar
            mode="admin"
            size="md"
            isWaving={true}
            showSpeechBubble={false}
          />
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="font-bold text-sm">Trợ Lý Dữ Liệu AI (Robo-Analyst DE/DA/DS)</h3>
              <span className="text-[10px] bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded-full font-semibold animate-pulse">
                RAG Active & Connected
              </span>
            </div>
            <p className="text-xs text-slate-400">Trợ lý robot thông minh đối chiếu dữ liệu bán hàng với tài liệu kế hoạch & sinh phương án</p>
          </div>
        </div>

        {/* Status pill */}
        <div className="hidden sm:flex items-center space-x-2 text-xs text-slate-400">
          <span>Human-in-the-loop: <strong>Bật</strong></span>
        </div>
      </div>

      {/* Quick Prompts Bar */}
      <div className="bg-slate-50 border-b border-slate-200 px-6 py-2.5 flex items-center space-x-2 overflow-x-auto scrollbar-none text-xs">
        <span className="font-bold text-slate-500 flex-shrink-0 flex items-center space-x-1">
          <Sparkles className="w-3.5 h-3.5 text-blue-600" />
          <span>Câu hỏi gợi ý:</span>
        </span>
        {sampleQuestions.map((q, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(q)}
            className="flex-shrink-0 px-3 py-1 bg-white hover:bg-blue-50 text-slate-700 hover:text-blue-700 border border-slate-200 rounded-full font-medium transition shadow-2xs"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 text-xs bg-slate-50/40">
        {messages.map(msg => (
          <div
            key={msg.id}
            className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
          >
            {msg.sender === 'user' ? (
              <div className="max-w-[75%] bg-blue-600 text-white rounded-2xl rounded-br-none px-4 py-3 leading-relaxed shadow-sm font-medium">
                {msg.text}
              </div>
            ) : (
              <div className="flex items-start space-x-3 max-w-[92%]">
                <div className="flex-shrink-0 mt-1">
                  <CuteRobotAvatar mode="admin" size="sm" isWaving={false} />
                </div>
                <div className="flex-1 bg-white border border-slate-200 rounded-2xl rounded-tl-none p-5 shadow-sm space-y-4">
                  {/* 1. Thought Summary (Collapsible/Subtle tag) */}
                  {msg.thoughtSummary && (
                    <div className="bg-slate-50 border border-slate-100 rounded-lg p-2.5 text-[11px] text-slate-600 flex items-start space-x-2">
                      <Sparkles className="w-3.5 h-3.5 text-blue-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <span className="font-bold text-slate-800">Quy trình phân tích của AI: </span>
                        <span>{msg.thoughtSummary}</span>
                      </div>
                    </div>
                  )}

                {/* 2. Main Insight */}
                {msg.insight && (
                  <div className="text-slate-800 leading-relaxed whitespace-pre-wrap text-xs sm:text-sm">
                    {msg.insight}
                  </div>
                )}

                {/* 3. Interactive Chart Spec Embed with "Ghim lên Dashboard" button */}
                {msg.chartSpec && (
                  <div className="mt-4 p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
                    <div className="flex justify-between items-center">
                      <div className="flex items-center space-x-2">
                        <TrendingUp className="w-4 h-4 text-blue-600" />
                        <h4 className="font-bold text-slate-900 text-xs">{msg.chartSpec.title}</h4>
                      </div>
                      <button
                        onClick={() => handlePin(msg.chartSpec!)}
                        className="px-3 py-1 bg-white hover:bg-slate-100 border border-slate-200 rounded text-[11px] font-bold text-blue-600 flex items-center space-x-1 transition shadow-2xs"
                      >
                        <Pin className="w-3 h-3" />
                        <span>{pinnedSuccess === msg.chartSpec.chart_id ? 'Đã ghim thành công!' : 'Ghim lên Dashboard'}</span>
                      </button>
                    </div>

                    {/* Chart Data Preview (Bar / Line representation) */}
                    <div className="h-44 flex items-end justify-between gap-3 pt-6 pb-2 px-3 bg-white rounded-lg border border-slate-100">
                      {msg.chartSpec.data?.map((d: any, idx: number) => {
                        const val = d.actual || d.daysInStock || d.share || 10;
                        const max = 100;
                        const heightPct = Math.min(100, Math.max(15, (val / max) * 100));

                        return (
                          <div key={idx} className="flex-1 flex flex-col items-center h-full justify-end">
                            <span className="text-[10px] font-bold text-slate-800 mb-1">{val}</span>
                            <div
                              className="w-full max-w-[28px] bg-blue-600 rounded-t transition-all hover:bg-blue-700"
                              style={{ height: `${heightPct}%` }}
                            />
                            <span className="text-[10px] text-slate-500 mt-2 truncate w-full text-center">
                              {d.week || d.name?.split(' ')[0] || d.period}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* 4. Strategy Proposals (Section 6.5.4: Human-in-the-loop decision card) */}
                {msg.proposal && (
                  <div className="mt-4 p-5 bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-200 rounded-xl space-y-4">
                    <div className="flex items-center space-x-2 text-amber-900 font-bold text-xs uppercase tracking-wide">
                      <Layers className="w-4 h-4 text-amber-600" />
                      <span>Đề Xuất Chiến Lược Chờ Duyệt (Human-in-the-loop)</span>
                    </div>

                    {proposalStatus[msg.proposal.id] ? (
                      <div className="p-3 bg-emerald-100 border border-emerald-300 rounded-lg text-emerald-800 font-bold flex items-center space-x-2">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                        <span>{proposalStatus[msg.proposal.id]}</span>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {msg.proposal.options.map(opt => (
                          <div key={opt.id} className="bg-white p-4 rounded-lg border border-amber-200 shadow-2xs space-y-2">
                            <div className="flex justify-between items-start">
                              <h5 className="font-bold text-slate-900 text-xs">{opt.title}</h5>
                              {opt.isRecommended && (
                                <span className="bg-amber-100 text-amber-800 text-[10px] font-bold px-2 py-0.5 rounded">
                                  AI Khuyến Nghị
                                </span>
                              )}
                            </div>
                            <p className="text-slate-600 text-[11px] leading-relaxed">{opt.description}</p>

                            <div className="grid grid-cols-3 gap-2 pt-2 text-[10px] bg-slate-50 p-2 rounded border border-slate-100">
                              <div>
                                <span className="text-slate-400 block">Dự kiến tăng bán:</span>
                                <strong className="text-slate-900">{opt.impactMetrics.expectedSalesIncrease}</strong>
                              </div>
                              <div>
                                <span className="text-slate-400 block">Ngân sách chi:</span>
                                <strong className="text-slate-900">{opt.impactMetrics.budgetRequired}</strong>
                              </div>
                              <div>
                                <span className="text-slate-400 block">Biên sau CT:</span>
                                <strong className="text-emerald-700">{opt.impactMetrics.projectedMargin}</strong>
                              </div>
                            </div>

                            <div className="pt-2 flex justify-end space-x-2">
                              <button
                                onClick={() => handleProposalDecision(msg.proposal!.id, opt.id, 'rejected')}
                                className="px-3 py-1 border border-slate-200 hover:bg-slate-50 text-slate-600 rounded text-[11px] font-semibold"
                              >
                                Từ chối
                              </button>
                              <button
                                onClick={() => handleProposalDecision(msg.proposal!.id, opt.id, 'approved')}
                                className="px-3.5 py-1 bg-amber-600 hover:bg-amber-700 text-white rounded text-[11px] font-bold shadow-xs"
                              >
                                Duyệt phương án này
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* 5. Citations from RAG Knowledge Base */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="pt-3 border-t border-slate-100 text-[11px] text-slate-500 flex items-start space-x-1.5">
                    <BookOpen className="w-3.5 h-3.5 text-blue-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold text-slate-700">Nguồn dữ liệu trích dẫn: </span>
                      <span>{msg.citations.join('; ')}</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
          <span className="text-[10px] text-slate-400 mt-1 px-1">
              {msg.timestamp}
            </span>
          </div>
        ))}

        {loading && (
          <div className="flex items-center space-x-2 text-slate-500 text-xs py-2 bg-white p-3 rounded-xl border border-slate-200 w-fit">
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" />
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce delay-100" />
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce delay-200" />
            <span className="text-xs font-medium ml-1">Đang phân tích số liệu SQL & trích xuất RAG...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <div className="p-4 bg-white border-t border-slate-200">
        <form
          onSubmit={e => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center space-x-3"
        >
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Đặt câu hỏi phân tích dữ liệu, doanh thu, hàng tồn, hoặc chiến lược kinh doanh..."
            className="flex-1 px-4 py-2.5 border border-slate-200 rounded-xl text-xs focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600 bg-slate-50/50"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white rounded-xl text-xs font-bold transition flex items-center space-x-1.5 shadow-sm"
          >
            <span>Phân tích</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>
    </div>
  );
};
