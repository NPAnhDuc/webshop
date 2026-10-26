import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  fetchProducts,
  fetchProductDetail,
  fetchCategories,
  fetchBrands,
  fetchStoreSettings,
  fetchProductReviews,
  submitProductReview,
  createOrder
} from '../services/api';
import { Product } from '../types';

/**
 * Cache key factories for structured cache invalidation
 */
export const queryKeys = {
  products: (filters?: Record<string, any>) => ['products', filters || {}] as const,
  productDetail: (slug: string) => ['product', slug] as const,
  categories: ['categories'] as const,
  brands: ['brands'] as const,
  settings: ['settings'] as const,
  reviews: (slug: string) => ['reviews', slug] as const
};

/**
 * Hook to fetch and cache products list by active filters
 */
export function useProductsQuery(filters: Record<string, any>, enabled = true) {
  return useQuery({
    queryKey: queryKeys.products(filters),
    queryFn: () => fetchProducts(filters),
    enabled,
    staleTime: 1000 * 60 * 3 // 3 mins fresh
  });
}

/**
 * Hook to fetch and cache product detail by slug or ID
 */
export function useProductDetailQuery(slugOrId: string, enabled = true) {
  return useQuery({
    queryKey: queryKeys.productDetail(slugOrId),
    queryFn: () => fetchProductDetail(slugOrId),
    enabled: Boolean(slugOrId) && enabled,
    staleTime: 1000 * 60 * 10 // 10 mins cache for product details
  });
}

/**
 * Hook to fetch and cache categories
 */
export function useCategoriesQuery() {
  return useQuery({
    queryKey: queryKeys.categories,
    queryFn: fetchCategories,
    staleTime: 1000 * 60 * 30 // 30 mins
  });
}

/**
 * Hook to fetch and cache brands
 */
export function useBrandsQuery() {
  return useQuery({
    queryKey: queryKeys.brands,
    queryFn: fetchBrands,
    staleTime: 1000 * 60 * 30 // 30 mins
  });
}

/**
 * Hook to fetch and cache store settings
 */
export function useStoreSettingsQuery() {
  return useQuery({
    queryKey: queryKeys.settings,
    queryFn: fetchStoreSettings,
    staleTime: 1000 * 60 * 10
  });
}

/**
 * Hook to fetch and cache product reviews
 */
export function useProductReviewsQuery(slug: string, enabled = true) {
  return useQuery({
    queryKey: queryKeys.reviews(slug),
    queryFn: () => fetchProductReviews(slug),
    enabled: Boolean(slug) && enabled,
    staleTime: 1000 * 60 * 5
  });
}

/**
 * Mutation for submitting customer reviews with auto cache invalidation
 */
export function useSubmitReviewMutation(slug: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { author: string; rating: number; comment: string; productName?: string }) =>
      submitProductReview(slug, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.reviews(slug) });
    }
  });
}
