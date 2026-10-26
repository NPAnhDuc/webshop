import React, { createContext, useContext } from 'react';
import { useWishlistStore } from '../store/useWishlistStore';

const WishlistContext = createContext<ReturnType<typeof useWishlistStore> | undefined>(undefined);

export const WishlistProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <>{children}</>;
};

export const useWishlist = () => {
  return useWishlistStore();
};
