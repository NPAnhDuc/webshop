import React, { createContext, useContext } from 'react';
import { useCartStore } from '../store/useCartStore';

const CartContext = createContext<ReturnType<typeof useCartStore> | undefined>(undefined);

export const CartProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <>{children}</>;
};

export const useCart = () => {
  return useCartStore();
};
