import React, { useState, useRef, useEffect } from 'react';
import {
  MessageSquare,
  X,
  Send,
  Sparkles,
  User,
  ShoppingBag,
  ArrowRight,
  Headphones,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { sendCustomerChatMessage } from '../../services/api';
import { Product } from '../../types';
import { useCart } from '../../context/CartContext';
import { CuteRobotAvatar } from '../common/CuteRobotAvatar';

interface Message {
  id: string;
  sender: 'user' | 'bot';
  text: string;
  products?: Product[];
  suggestedPills?: string[];
  action?: string;
  timestamp: string;
}

interface CustomerChatWidgetProps {
  currentProduct?: Product | null;
  onSelectProduct: (product: Product) => void;
}

export const CustomerChatWidget: React.FC<CustomerChatWidgetProps> = ({
  currentProduct,
  onSelectProduct
}) => {
  const { addToCart } = useCart();
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'msg-welcome',
      sender: 'bot',
      text: 'Chào bạn! Tớ là Trợ lý AI của TechStore 🤖✨\n\nBạn đang cần tìm laptop học tập/văn phòng, máy gaming hay cần lên cấu hình ráp PC theo tầm tiền nào ạ?',
      suggestedPills: [
        'Laptop tầm 20 triệu màn OLED',
        'Tư vấn PC Gaming 25 triệu',
        'Chính sách đổi trả & bảo hành',
        'Trả góp 0% như thế nào?'
      ],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSend = async (textToSend?: string) => {
    const text = textToSend || input;
    if (!text.trim() || loading) return;

    const userMsg: Message = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    if (!textToSend) setInput('');
    setLoading(true);

    try {
      const pageContext = currentProduct ? { currentProductSlug: currentProduct.slug } : undefined;
      const res = await sendCustomerChatMessage(text, pageContext);

      const botMsg: Message = {
        id: `bot-${Date.now()}`,
        sender: 'bot',
        text: res.replyText,
        products: res.products,
        suggestedPills: res.suggestedPills,
        action: res.action,
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
          text: 'Xin lỗi bạn, đường truyền kết nối đến máy chủ đang bận. Bạn vui lòng thử lại hoặc gọi tổng đài miễn phí 1800.2097 để được hỗ trợ ngay nhé!',
          suggestedPills: ['Gọi tổng đài 1800.2097', 'Thử lại'],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-5 right-5 z-50 select-none">
      {/* Floating Cute Robot Assistant Trigger */}
      {!isOpen && (
        <div className="relative flex flex-col items-end group cursor-pointer" onClick={() => setIsOpen(true)}>
          <CuteRobotAvatar
            mode="customer"
            size="md"
            showSpeechBubble={true}
            speechText="Chào bạn! Cần tớ tư vấn máy tính không? 👋"
            isWaving={true}
            onClick={() => setIsOpen(true)}
            className="hover:scale-110 transition-transform duration-300 drop-shadow-2xl"
          />
          <button
            onClick={() => setIsOpen(true)}
            className="mt-1 flex items-center space-x-1.5 bg-[#059669] hover:bg-[#047857] text-white px-3.5 py-1.5 rounded-full shadow-lg text-[11px] font-bold tracking-wide transition-all duration-300 hover:shadow-xl active:scale-95 cursor-pointer"
            aria-label="Mở trợ lý AI"
          >
            <Sparkles className="w-3.5 h-3.5 text-yellow-300 animate-spin-slow" />
            <span>Hỏi Trợ Lý AI</span>
          </button>
        </div>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="bg-white dark:bg-[#151c2c] rounded-2xl shadow-2xl border border-gray-200 dark:border-slate-800 w-[92vw] sm:w-[420px] h-[580px] max-h-[85vh] flex flex-col overflow-hidden animate-in zoom-in-95 duration-200 transition-colors">
          {/* Header with Cute Robot */}
          <div className="bg-[#059669] text-white px-4 py-3 flex items-center justify-between border-b border-emerald-700">
            <div className="flex items-center space-x-3">
              <CuteRobotAvatar mode="customer" size="sm" isWaving={false} />
              <div>
                <div className="flex items-center space-x-1.5">
                  <h3 className="text-sm font-bold">Trợ Lý AI TechStore</h3>
                  <span className="w-2 h-2 rounded-full bg-emerald-300 animate-pulse" />
                </div>
                <p className="text-[10px] text-emerald-100">Tư vấn thông số & hỗ trợ mua sắm 24/7</p>
              </div>
            </div>
            <div className="flex items-center space-x-1">
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-lg text-white/80 hover:text-white hover:bg-black/20 transition cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Current product context notification */}
          {currentProduct && (
            <div className="bg-emerald-50 dark:bg-emerald-950/40 border-b border-emerald-100 dark:border-emerald-900 px-3 py-1.5 text-[11px] text-slate-700 dark:text-slate-300 flex items-center justify-between">
              <span className="truncate">Đang xem: <strong>{currentProduct.name}</strong></span>
              <button
                onClick={() => handleSend(`Con ${currentProduct.name} này còn hàng không?`)}
                className="text-[#059669] dark:text-emerald-400 font-bold hover:underline ml-2 flex-shrink-0 cursor-pointer"
              >
                Hỏi về máy này
              </button>
            </div>
          )}

          {/* Messages Body */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs bg-gray-50/60 dark:bg-[#0b0f19]/80">
            {messages.map(msg => (
              <div
                key={msg.id}
                className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
              >
                <div className={`flex items-start space-x-2 ${msg.sender === 'user' ? 'justify-end max-w-[88%]' : 'max-w-[88%]'}`}>
                  {msg.sender === 'bot' && (
                    <div className="flex-shrink-0 mt-0.5">
                      <CuteRobotAvatar mode="customer" size="sm" isWaving={false} />
                    </div>
                  )}
                  <div
                    className={`rounded-2xl px-3.5 py-2.5 leading-relaxed shadow-xs whitespace-pre-wrap ${
                      msg.sender === 'user'
                        ? 'bg-[#059669] text-white rounded-br-none'
                        : 'bg-white dark:bg-[#151c2c] text-slate-800 dark:text-slate-100 border border-gray-200 dark:border-slate-800 rounded-bl-none'
                    }`}
                  >
                    {msg.text}
                  </div>
                </div>

                {/* Embedded Product Cards in Bot Message */}
                {msg.products && msg.products.length > 0 && (
                  <div className="mt-2.5 space-y-2 w-full max-w-[95%]">
                    {msg.products.map(p => (
                      <div
                        key={p.id}
                        className="bg-white dark:bg-[#151c2c] rounded-xl border border-gray-200 dark:border-slate-800 p-2.5 flex items-center space-x-3 shadow-xs hover:border-[#059669] dark:hover:border-emerald-500 transition"
                      >
                        <img
                          src={p.imageUrl}
                          alt={p.name}
                          className="w-14 h-14 object-contain rounded-lg bg-white dark:bg-slate-800 border border-gray-150 dark:border-slate-700 p-1 flex-shrink-0"
                        />
                        <div className="flex-1 min-w-0">
                          <h5
                            onClick={() => onSelectProduct(p)}
                            className="font-bold text-slate-900 dark:text-slate-100 text-xs line-clamp-1 hover:text-[#059669] dark:hover:text-emerald-400 cursor-pointer"
                          >
                            {p.name}
                          </h5>
                          <div className="flex items-center space-x-1.5 mt-0.5">
                            <span className="font-bold text-[#059669] dark:text-emerald-400 font-mono">
                              {new Intl.NumberFormat('vi-VN').format(p.price)}₫
                            </span>
                            {p.specs.panel && (
                              <span className="text-[10px] px-1 bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800 rounded">
                                {p.specs.panel}
                              </span>
                            )}
                          </div>
                          <div className="flex items-center space-x-2 mt-1">
                            <button
                              onClick={() => onSelectProduct(p)}
                              className="text-[11px] text-[#059669] dark:text-emerald-400 font-semibold hover:underline cursor-pointer"
                            >
                              Xem chi tiết &rarr;
                            </button>
                            <span className="text-slate-300 dark:text-slate-700">•</span>
                            <button
                              onClick={() => addToCart(p)}
                              className="text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold hover:underline cursor-pointer"
                            >
                              + Thêm giỏ
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Quick Pills */}
                {msg.suggestedPills && msg.suggestedPills.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1.5 max-w-[95%]">
                    {msg.suggestedPills.map((pill, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSend(pill)}
                        className="text-[11px] px-2.5 py-1 bg-white dark:bg-slate-800 hover:bg-emerald-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 hover:text-[#059669] dark:hover:text-emerald-400 border border-gray-200 dark:border-slate-700 rounded-full transition shadow-2xs text-left cursor-pointer"
                      >
                        {pill}
                      </button>
                    ))}
                  </div>
                )}

                <span className="text-[10px] text-slate-400 dark:text-slate-500 mt-1 px-1">
                  {msg.timestamp}
                </span>
              </div>
            ))}

            {loading && (
              <div className="flex items-center space-x-2 text-slate-400 dark:text-slate-500 text-xs py-1">
                <div className="w-2 h-2 bg-[#059669] rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-[#059669] rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-[#059669] rounded-full animate-bounce delay-200" />
                <span className="text-[11px] text-slate-500 dark:text-slate-400 italic ml-1">Trợ lý AI đang đối chiếu dữ liệu kho...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Footer */}
          <div className="p-3 bg-white dark:bg-[#151c2c] border-t border-gray-200 dark:border-slate-800">
            <form
              onSubmit={e => {
                e.preventDefault();
                handleSend();
              }}
              className="flex items-center space-x-2"
            >
              <input
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                placeholder="Nhập câu hỏi... (VD: laptop 20tr màn OLED)"
                className="flex-1 px-3.5 py-2 border border-gray-200 dark:border-slate-700 rounded-xl text-xs focus:outline-none focus:border-[#059669] focus:ring-1 focus:ring-[#059669] bg-gray-50 dark:bg-slate-900 text-slate-800 dark:text-slate-100"
              />
              <button
                type="submit"
                disabled={!input.trim() || loading}
                className="p-2 bg-[#059669] hover:bg-[#047857] disabled:bg-gray-300 dark:disabled:bg-slate-800 text-white rounded-xl transition cursor-pointer"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
