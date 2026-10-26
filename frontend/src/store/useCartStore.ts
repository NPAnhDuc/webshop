import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { CartItem, Product, ProductVariant } from '../types';
import { sound } from '../utils/sound';

interface CartState {
  cart: CartItem[];
  isOpen: boolean;
  openCart: () => void;
  closeCart: () => void;
  addToCart: (product: Product, variant?: ProductVariant, qty?: number) => void;
  removeFromCart: (variantId: string) => void;
  updateQty: (variantId: string, qty: number) => void;
  clearCart: () => void;
  totalItems: number;
  totalAmount: number;
}

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      cart: [],
      isOpen: false,

      openCart: () => set({ isOpen: true }),
      closeCart: () => set({ isOpen: false }),

      addToCart: (product: Product, variant?: ProductVariant, qty = 1) => {
        const selectedVariant = variant || product.variants[0];
        if (!selectedVariant) return;

        const currentCart = get().cart;
        const existingIndex = currentCart.findIndex(item => item.variantId === selectedVariant.id);

        let newCart: CartItem[];
        if (existingIndex > -1) {
          newCart = currentCart.map((item, idx) =>
            idx === existingIndex ? { ...item, qty: item.qty + qty } : item
          );
        } else {
          newCart = [
            ...currentCart,
            {
              variantId: selectedVariant.id,
              productId: product.id,
              productName: product.name,
              variantName: selectedVariant.name,
              sku: selectedVariant.sku,
              price: selectedVariant.price,
              imageUrl: product.imageUrl,
              availableQty: product.stockStatus?.availableQty || 15,
              qty
            }
          ];
        }

        const totalItems = newCart.reduce((sum, item) => sum + item.qty, 0);
        const totalAmount = newCart.reduce((sum, item) => sum + item.price * item.qty, 0);

        sound.playPop();
        set({ cart: newCart, totalItems, totalAmount, isOpen: true });
      },

      removeFromCart: (variantId: string) => {
        const newCart = get().cart.filter(item => item.variantId !== variantId);
        const totalItems = newCart.reduce((sum, item) => sum + item.qty, 0);
        const totalAmount = newCart.reduce((sum, item) => sum + item.price * item.qty, 0);

        sound.playClick();
        set({ cart: newCart, totalItems, totalAmount });
      },

      updateQty: (variantId: string, qty: number) => {
        if (qty <= 0) {
          get().removeFromCart(variantId);
          return;
        }

        const newCart = get().cart.map(item =>
          item.variantId === variantId ? { ...item, qty } : item
        );
        const totalItems = newCart.reduce((sum, item) => sum + item.qty, 0);
        const totalAmount = newCart.reduce((sum, item) => sum + item.price * item.qty, 0);

        set({ cart: newCart, totalItems, totalAmount });
      },

      clearCart: () => {
        sound.playClick();
        set({ cart: [], totalItems: 0, totalAmount: 0 });
      },

      totalItems: 0,
      totalAmount: 0
    }),
    {
      name: 'techstore_cart_zustand',
      storage: createJSONStorage(() => localStorage),
      onRehydrateStorage: () => (state) => {
        if (state) {
          state.totalItems = state.cart.reduce((sum, item) => sum + item.qty, 0);
          state.totalAmount = state.cart.reduce((sum, item) => sum + item.price * item.qty, 0);
        }
      }
    }
  )
);
