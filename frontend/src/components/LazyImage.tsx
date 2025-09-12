'use client';

import Image from 'next/image';
import { useState, useRef, useEffect } from 'react';
import { optimizeImageUrl, generateBlurDataURL, lazyLoadImage } from '@/lib/asset-optimizer';

interface LazyImageProps {
  src: string;
  alt: string;
  width: number;
  height: number;
  className?: string;
  priority?: boolean;
  placeholder?: 'blur' | 'empty';
  blurDataURL?: string;
  quality?: number;
  sizes?: string;
  format?: 'webp' | 'avif' | 'jpeg' | 'png' | 'auto';
  enableCDN?: boolean;
}

const LazyImage = ({
  src,
  alt,
  width,
  height,
  className = '',
  priority = false,
  placeholder = 'blur',
  blurDataURL,
  quality = 75,
  sizes,
  format = 'auto',
  enableCDN = true,
}: LazyImageProps) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(priority);
  const imgRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (priority) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      {
        threshold: 0.1,
        rootMargin: '50px',
      }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, [priority]);

  const handleLoad = () => {
    setIsLoaded(true);
  };

  // 最適化された画像URLを生成
  const optimizedSrc = enableCDN 
    ? optimizeImageUrl(src, width, height, { quality, format })
    : src;

  // プレースホルダーの生成
  const defaultBlurDataURL = blurDataURL || generateBlurDataURL(width, height);

  return (
    <div
      ref={imgRef}
      className={`relative overflow-hidden ${className}`}
      style={{ width, height }}
    >
      {isInView && (
        <Image
          src={optimizedSrc}
          alt={alt}
          width={width}
          height={height}
          priority={priority}
          placeholder={placeholder}
          blurDataURL={defaultBlurDataURL}
          quality={quality}
          sizes={sizes}
          onLoad={handleLoad}
          className={`transition-opacity duration-300 ${
            isLoaded ? 'opacity-100' : 'opacity-0'
          }`}
        />
      )}
      
      {!isLoaded && isInView && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse flex items-center justify-center">
          <div className="w-8 h-8 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin" />
        </div>
      )}
    </div>
  );
};

export default LazyImage;
