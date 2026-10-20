import React, { createContext, useContext, useState, useEffect } from 'react';
import { sound } from '../utils/sound';

interface WishlistContextType {
  wishlistIds: string[];
  toggleWishlist: (productId: string) => boolean;
  isWishlisted: (productId: string) => boolean;
  clearWishlist: () => void;
  count: number;
}

const WishlistContext = createContext<WishlistContextType | undefined>(undefined);

export const WishlistProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [wishlistIds, setWishlistIds] = useState<string[]>(() => {
    try {
      const saved = localStorage.getItem('techstore_wishlist');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem('techstore_wishlist', JSON.stringify(wishlistIds));
    } catch (e) {
      console.error('Failed to save wishlist', e);
    }
  }, [wishlistIds]);

  const toggleWishlist = (productId: string): boolean => {
    const exists = wishlistIds.includes(productId);
    if (exists) {
      setWishlistIds(prev => prev.filter(id => id !== productId));
      sound.playClick();
      return false;
    } else {
      setWishlistIds(prev => [...prev, productId]);
      sound.playPop();
      return true;
    }
  };

  const isWishlisted = (productId: string) => wishlistIds.includes(productId);

  const clearWishlist = () => {
    setWishlistIds([]);
    sound.playClick();
  };

  return (
    <WishlistContext.Provider
      value={{
        wishlistIds,
        toggleWishlist,
        isWishlisted,
        clearWishlist,
        count: wishlistIds.length
      }}
    >
      {children}
    </WishlistContext.Provider>
  );
};

export const useWishlist = () => {
  const context = useContext(WishlistContext);
  if (!context) {
    throw new Error('useWishlist must be used within a WishlistProvider');
  }
  return context;
};
