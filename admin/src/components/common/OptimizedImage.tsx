import React, { useState } from 'react';

interface OptimizedImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  src: string;
  alt: string;
  className?: string;
  aspectRatio?: 'square' | 'video' | 'auto';
  priority?: boolean;
  fallbackSrc?: string;
}

export const OptimizedImage: React.FC<OptimizedImageProps> = ({
  src,
  alt,
  className = '',
  aspectRatio = 'square',
  priority = false,
  fallbackSrc = 'https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=600&auto=format&fit=crop&q=80',
  ...props
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);

  // Generate webp path if the src is local and ends in png/jpg/jpeg
  const webpSrc = React.useMemo(() => {
    if (!src) return '';
    if (src.endsWith('.webp')) return src;
    if (src.startsWith('http://') || src.startsWith('https://')) return '';
    return src.replace(/\.(png|jpg|jpeg)$/i, '.webp');
  }, [src]);

  const currentSrc = hasError ? fallbackSrc : src;

  return (
    <div
      className={`relative overflow-hidden flex items-center justify-center ${
        aspectRatio === 'square' ? 'aspect-square w-full' : aspectRatio === 'video' ? 'aspect-video w-full' : ''
      }`}
    >
      {/* Skeleton Shimmer Loading Placeholder */}
      {!isLoaded && (
        <div className="absolute inset-0 bg-slate-150 dark:bg-slate-800/80 animate-pulse rounded-xl flex items-center justify-center pointer-events-none">
          <div className="w-6 h-6 rounded-full border-2 border-slate-300 dark:border-slate-700 border-t-red-600 animate-spin opacity-40" />
        </div>
      )}

      {/* Picture tag for WebP with fallback */}
      <picture className="w-full h-full flex items-center justify-center">
        {webpSrc && !hasError && (
          <source srcSet={webpSrc} type="image/webp" />
        )}
        <img
          src={currentSrc}
          alt={alt}
          loading={priority ? 'eager' : 'lazy'}
          decoding="async"
          fetchPriority={priority ? 'high' : 'auto'}
          onLoad={() => setIsLoaded(true)}
          onError={() => {
            setHasError(true);
            setIsLoaded(true);
          }}
          className={`${className} transition-opacity duration-300 ease-out ${
            isLoaded ? 'opacity-100' : 'opacity-0'
          }`}
          {...props}
        />
      </picture>
    </div>
  );
};
