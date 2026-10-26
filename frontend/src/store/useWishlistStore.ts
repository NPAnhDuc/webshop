import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { sound } from '../utils/sound';

interface WishlistState {
  wishlistIds: string[];
  toggleWishlist: (productId: string) => boolean;
  isWishlisted: (productId: string) => boolean;
  clearWishlist: () => void;
  count: number;
}

export const useWishlistStore = create<WishlistState>()(
  persist(
    (set, get) => ({
      wishlistIds: [],
      count: 0,

      toggleWishlist: (productId: string) => {
        const current = get().wishlistIds;
        const exists = current.includes(productId);

        if (exists) {
          const updated = current.filter(id => id !== productId);
          sound.playClick();
          set({ wishlistIds: updated, count: updated.length });
          return false;
        } else {
          const updated = [...current, productId];
          sound.playPop();
          set({ wishlistIds: updated, count: updated.length });
          return true;
        }
      },

      isWishlisted: (productId: string) => {
        return get().wishlistIds.includes(productId);
      },

      clearWishlist: () => {
        sound.playClick();
        set({ wishlistIds: [], count: 0 });
      }
    }),
    {
      name: 'techstore_wishlist_zustand',
      storage: createJSONStorage(() => localStorage),
      onRehydrateStorage: () => (state) => {
        if (state) {
          state.count = state.wishlistIds.length;
        }
      }
    }
  )
);
