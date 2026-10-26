import { z } from 'zod';
import { Request, Response, NextFunction } from 'express';

export const CreateOrderSchema = z.object({
  customerName: z.string().min(2, 'Họ tên phải có ít nhất 2 ký tự').max(100, 'Họ tên không được vượt quá 100 ký tự'),
  customerPhone: z.string().min(9, 'Số điện thoại phải từ 9 đến 12 ký tự').regex(/^[0-9+\s().-]{9,15}$/, 'Số điện thoại không hợp lệ (Ví dụ: 0981234567)'),
  customerAddress: z.string().min(3, 'Địa chỉ phải có ít nhất 3 ký tự'),
  customerCity: z.string().optional().default('Hà Nội'),
  notes: z.string().optional(),
  paymentMethod: z.enum(['cod', 'bank_transfer', 'installment']).optional().default('cod'),
  items: z.array(
    z.object({
      variantId: z.string().min(1, 'Mã biến thể sản phẩm là bắt buộc'),
      qty: z.number().int().positive('Số lượng sản phẩm phải lớn hơn 0')
    })
  ).min(1, 'Giỏ hàng không được để trống'),
  promotionCode: z.string().optional()
});

export const CreateReviewSchema = z.object({
  customerName: z.string().optional(),
  author: z.string().optional(),
  rating: z.union([z.number(), z.string().transform(v => Number(v))])
    .pipe(z.number().min(1, 'Đánh giá tối thiểu 1 sao').max(5, 'Đánh giá tối đa 5 sao')),
  comment: z.string().min(2, 'Nội dung nhận xét phải có ít nhất 2 ký tự').max(1000, 'Nội dung không được vượt quá 1000 ký tự'),
  productName: z.string().optional()
});

export const CreateQuotationSchema = z.object({
  customerName: z.string().min(2, 'Tên khách hàng phải từ 2 ký tự'),
  phone: z.string().min(9, 'Số điện thoại liên hệ không hợp lệ'),
  title: z.string().optional(),
  totalPrice: z.number().nonnegative(),
  totalWatts: z.number().optional(),
  recommendedPsu: z.string().optional(),
  compatibilityScore: z.number().optional(),
  parts: z.array(z.any()).min(1, 'Cấu hình phải có ít nhất 1 linh kiện'),
  note: z.string().optional()
});

export const UpdateSettingsSchema = z.object({
  storeName: z.string().min(1, 'Tên cửa hàng không được để trống').optional(),
  slogan: z.string().optional(),
  hotlineSales: z.string().optional(),
  hotlineWarranty: z.string().optional(),
  marqueeText: z.string().optional(),
  freeShippingThreshold: z.number().nonnegative().optional(),
  vatPercent: z.number().min(0).max(100).optional(),
  showrooms: z.array(z.any()).optional()
});

/**
 * Express middleware helper for Zod schema validation
 */
export function validateBody(schema: z.ZodTypeAny) {
  return (req: Request, res: Response, next: NextFunction) => {
    const result = schema.safeParse(req.body);
    if (!result.success) {
      const issues = (result.error as any).issues || (result.error as any).errors || [];
      const fieldErrors = issues.map((err: any) => ({
        field: Array.isArray(err.path) ? err.path.join('.') : String(err.path || ''),
        message: err.message || 'Dữ liệu không hợp lệ'
      }));

      return res.status(400).json({
        success: false,
        message: fieldErrors[0]?.message || 'Dữ liệu không hợp lệ',
        errors: fieldErrors
      });
    }

    req.body = result.data;
    next();
  };
}
