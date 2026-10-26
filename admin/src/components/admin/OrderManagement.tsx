import React, { useState, useEffect } from 'react';
import {
  ClipboardList,
  Search,
  CheckCircle2,
  Clock,
  Truck,
  XCircle,
  Eye,
  RefreshCw,
  Phone,
  MapPin
} from 'lucide-react';
import { fetchAdminOrders, updateOrderStatus } from '../../services/api';
import { Order, OrderStatus } from '../../types';

export const OrderManagement: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [statusFilter, setStatusFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);

  const loadOrders = () => {
    setLoading(true);
    fetchAdminOrders(statusFilter)
      .then(data => setOrders(data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadOrders();
  }, [statusFilter]);

  const handleUpdateStatus = async (orderId: string, newStatus: OrderStatus) => {
    try {
      await updateOrderStatus(orderId, newStatus);
      loadOrders();
      if (selectedOrder && selectedOrder.id === orderId) {
        setSelectedOrder({ ...selectedOrder, status: newStatus });
      }
    } catch (err) {
      console.error(err);
    }
  };

  const getStatusBadge = (status: OrderStatus) => {
    switch (status) {
      case 'new':
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 text-blue-700">Mới tạo</span>;
      case 'confirmed':
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-700">Đã xác nhận</span>;
      case 'shipping':
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-100 text-purple-700">Đang giao</span>;
      case 'completed':
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-700">Hoàn tất</span>;
      case 'cancelled':
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-500">Đã hủy</span>;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Status Filter Pills */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h2 className="text-xl font-black text-slate-900 tracking-tight flex items-center space-x-2">
            <ClipboardList className="w-5 h-5 text-blue-600" />
            <span>Quản Lý Đơn Hàng & Vận Chuyển</span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Xử lý quy trình đơn hàng: Mới tạo &rarr; Xác nhận &rarr; Giao hàng &rarr; Hoàn tất
          </p>
        </div>

        <div className="flex items-center space-x-2">
          {['all', 'new', 'confirmed', 'shipping', 'completed'].map(st => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition ${
                statusFilter === st
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'
              }`}
            >
              {st === 'all' ? 'Tất cả' : st === 'new' ? 'Mới' : st === 'confirmed' ? 'Đã duyệt' : st === 'shipping' ? 'Đang giao' : 'Đã xong'}
            </button>
          ))}
          <button
            onClick={loadOrders}
            className="p-2 border border-slate-200 bg-white rounded-lg text-slate-600 hover:bg-slate-50"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Orders List Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
        {loading ? (
          <div className="p-12 text-center text-xs text-slate-400">Đang tải danh sách đơn hàng...</div>
        ) : orders.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-400">Không có đơn hàng nào trong trạng thái này.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700">
              <thead className="bg-slate-50 text-[11px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200">
                <tr>
                  <th className="p-3.5">Mã đơn hàng</th>
                  <th className="p-3.5">Khách hàng</th>
                  <th className="p-3.5">Sản phẩm</th>
                  <th className="p-3.5 text-right">Tổng tiền</th>
                  <th className="p-3.5">Trạng thái</th>
                  <th className="p-3.5">Ngày tạo</th>
                  <th className="p-3.5 text-right">Chuyển trạng thái</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {orders.map(order => (
                  <tr key={order.id} className="hover:bg-slate-50/80 transition">
                    <td className="p-3.5 font-mono font-bold text-blue-600">
                      {order.orderCode}
                    </td>
                    <td className="p-3.5">
                      <div className="font-bold text-slate-900">{order.customerName}</div>
                      <div className="text-[11px] text-slate-500">{order.customerPhone} - {order.customerCity}</div>
                    </td>
                    <td className="p-3.5">
                      <div className="line-clamp-1 font-medium text-slate-800">
                        {order.items.map(it => `${it.productName} (x${it.qty})`).join(', ')}
                      </div>
                    </td>
                    <td className="p-3.5 text-right font-black text-red-600">
                      {new Intl.NumberFormat('vi-VN').format(order.total)}₫
                    </td>
                    <td className="p-3.5">
                      {getStatusBadge(order.status)}
                    </td>
                    <td className="p-3.5 text-slate-500 text-[11px]">
                      {new Date(order.createdAt).toLocaleDateString('vi-VN')}
                    </td>
                    <td className="p-3.5 text-right space-x-1.5">
                      {order.status === 'new' && (
                        <button
                          onClick={() => handleUpdateStatus(order.id, 'confirmed')}
                          className="px-2.5 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded font-semibold text-[11px]"
                        >
                          Duyệt đơn
                        </button>
                      )}
                      {order.status === 'confirmed' && (
                        <button
                          onClick={() => handleUpdateStatus(order.id, 'shipping')}
                          className="px-2.5 py-1 bg-purple-600 hover:bg-purple-700 text-white rounded font-semibold text-[11px]"
                        >
                          Giao hàng
                        </button>
                      )}
                      {order.status === 'shipping' && (
                        <button
                          onClick={() => handleUpdateStatus(order.id, 'completed')}
                          className="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded font-semibold text-[11px]"
                        >
                          Hoàn tất
                        </button>
                      )}
                      {order.status !== 'completed' && order.status !== 'cancelled' && (
                        <button
                          onClick={() => handleUpdateStatus(order.id, 'cancelled')}
                          className="px-2 py-1 border border-slate-200 text-slate-500 hover:text-red-600 rounded text-[11px]"
                        >
                          Hủy
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
