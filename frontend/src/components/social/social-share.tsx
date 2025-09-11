'use client';

import React, { useState, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { AccessibilityUtils } from '@/lib/accessibility';
import { useTranslations } from 'next-intl';

interface SocialShareProps {
  url: string;
  title: string;
  description?: string;
  hashtags?: string[];
  className?: string;
  variant?: 'buttons' | 'dropdown' | 'floating';
  showCounts?: boolean;
  platforms?: SocialPlatform[];
}

interface SocialPlatform {
  name: string;
  icon: React.ReactNode;
  color: string;
  shareUrl: string;
  count?: number;
}

const defaultPlatforms: SocialPlatform[] = [
  {
    name: 'Twitter',
    icon: (
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
        <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
      </svg>
    ),
    color: 'bg-blue-500 hover:bg-blue-600',
    shareUrl: 'https://twitter.com/intent/tweet',
  },
  {
    name: 'Facebook',
    icon: (
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
        <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
      </svg>
    ),
    color: 'bg-blue-600 hover:bg-blue-700',
    shareUrl: 'https://www.facebook.com/sharer/sharer.php',
  },
  {
    name: 'LinkedIn',
    icon: (
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
        <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
      </svg>
    ),
    color: 'bg-blue-700 hover:bg-blue-800',
    shareUrl: 'https://www.linkedin.com/sharing/share-offsite/',
  },
  {
    name: 'Reddit',
    icon: (
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.587.545a1.25 1.25 0 0 1 1.249-1.25zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.07 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z"/>
      </svg>
    ),
    color: 'bg-orange-500 hover:bg-orange-600',
    shareUrl: 'https://reddit.com/submit',
  },
  {
    name: 'WhatsApp',
    icon: (
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
        <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893A11.821 11.821 0 0020.885 3.488"/>
      </svg>
    ),
    color: 'bg-green-500 hover:bg-green-600',
    shareUrl: 'https://wa.me/',
  },
  {
    name: 'Telegram',
    icon: (
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
        <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
      </svg>
    ),
    color: 'bg-blue-400 hover:bg-blue-500',
    shareUrl: 'https://t.me/share/url',
  },
];

export function SocialShare({
  url,
  title,
  description,
  hashtags = [],
  className,
  variant = 'buttons',
  showCounts = false,
  platforms = defaultPlatforms,
}: SocialShareProps) {
  const t = useTranslations('common');
  const [isOpen, setIsOpen] = useState(false);
  const [shareCounts, setShareCounts] = useState<Record<string, number>>({});
  const [isLoading, setIsLoading] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Load share counts
  useEffect(() => {
    if (showCounts) {
      loadShareCounts();
    }
  }, [url, showCounts]);

  const loadShareCounts = async () => {
    setIsLoading(true);
    try {
      // This would typically call an API to get share counts
      // For now, we'll simulate with random numbers
      const counts: Record<string, number> = {};
      platforms.forEach(platform => {
        counts[platform.name] = Math.floor(Math.random() * 1000);
      });
      setShareCounts(counts);
    } finally {
      setIsLoading(false);
    }
  };

  const getShareUrl = (platform: SocialPlatform): string => {
    const encodedUrl = encodeURIComponent(url);
    const encodedTitle = encodeURIComponent(title);
    const encodedDescription = encodeURIComponent(description || '');
    const encodedHashtags = encodeURIComponent(hashtags.join(','));

    switch (platform.name) {
      case 'Twitter':
        return `${platform.shareUrl}?url=${encodedUrl}&text=${encodedTitle}&hashtags=${encodedHashtags}`;
      case 'Facebook':
        return `${platform.shareUrl}?u=${encodedUrl}&quote=${encodedTitle}`;
      case 'LinkedIn':
        return `${platform.shareUrl}?url=${encodedUrl}&title=${encodedTitle}&summary=${encodedDescription}`;
      case 'Reddit':
        return `${platform.shareUrl}?url=${encodedUrl}&title=${encodedTitle}`;
      case 'WhatsApp':
        return `${platform.shareUrl}?text=${encodedTitle}%20${encodedUrl}`;
      case 'Telegram':
        return `${platform.shareUrl}?url=${encodedUrl}&text=${encodedTitle}`;
      default:
        return `${platform.shareUrl}?url=${encodedUrl}&title=${encodedTitle}`;
    }
  };

  const handleShare = (platform: SocialPlatform) => {
    const shareUrl = getShareUrl(platform);
    window.open(shareUrl, '_blank', 'width=600,height=400');
    
    // Track share event
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'share', {
        method: platform.name,
        content_type: 'article',
        item_id: url,
      });
    }

    // Announce to screen readers
    AccessibilityUtils.announceToScreenReader(
      `Shared to ${platform.name}`,
      'polite'
    );
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(url);
      AccessibilityUtils.announceToScreenReader('URL copied to clipboard', 'polite');
    } catch (err) {
      console.error('Failed to copy URL:', err);
    }
  };

  if (variant === 'floating') {
    return (
      <div className={cn('fixed bottom-6 right-6 z-50', className)}>
        <div className="relative">
          <button
            ref={buttonRef}
            onClick={() => setIsOpen(!isOpen)}
            className={cn(
              'w-14 h-14 rounded-full bg-primary text-primary-foreground shadow-lg',
              'hover:bg-primary/90 transition-colors',
              'focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2'
            )}
            aria-label={t('share')}
            aria-expanded={isOpen}
          >
            <svg className="w-6 h-6 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
            </svg>
          </button>

          {isOpen && (
            <div
              ref={dropdownRef}
              className="absolute bottom-16 right-0 bg-popover border border-border rounded-lg shadow-lg p-2 min-w-[200px]"
            >
              <div className="space-y-1">
                {platforms.map((platform) => (
                  <button
                    key={platform.name}
                    onClick={() => handleShare(platform)}
                    className={cn(
                      'w-full flex items-center gap-3 px-3 py-2 text-sm rounded-md',
                      'hover:bg-accent transition-colors',
                      'focus:outline-none focus:bg-accent'
                    )}
                  >
                    <span className={cn('p-1 rounded text-white', platform.color)}>
                      {platform.icon}
                    </span>
                    <span className="flex-1 text-left">{platform.name}</span>
                    {showCounts && shareCounts[platform.name] && (
                      <span className="text-xs text-muted-foreground">
                        {shareCounts[platform.name]}
                      </span>
                    )}
                  </button>
                ))}
                
                <div className="border-t border-border pt-1">
                  <button
                    onClick={copyToClipboard}
                    className="w-full flex items-center gap-3 px-3 py-2 text-sm rounded-md hover:bg-accent transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    <span className="flex-1 text-left">{t('copyLink')}</span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  if (variant === 'dropdown') {
    return (
      <div ref={dropdownRef} className={cn('relative', className)}>
        <button
          ref={buttonRef}
          onClick={() => setIsOpen(!isOpen)}
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-md border border-input bg-background',
            'hover:bg-accent hover:text-accent-foreground transition-colors',
            'focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2'
          )}
          aria-expanded={isOpen}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
          </svg>
          {t('share')}
        </button>

        {isOpen && (
          <div className="absolute top-full left-0 mt-1 bg-popover border border-border rounded-lg shadow-lg p-2 min-w-[200px] z-50">
            <div className="space-y-1">
              {platforms.map((platform) => (
                <button
                  key={platform.name}
                  onClick={() => handleShare(platform)}
                  className={cn(
                    'w-full flex items-center gap-3 px-3 py-2 text-sm rounded-md',
                    'hover:bg-accent transition-colors',
                    'focus:outline-none focus:bg-accent'
                  )}
                >
                  <span className={cn('p-1 rounded text-white', platform.color)}>
                    {platform.icon}
                  </span>
                  <span className="flex-1 text-left">{platform.name}</span>
                  {showCounts && shareCounts[platform.name] && (
                    <span className="text-xs text-muted-foreground">
                      {shareCounts[platform.name]}
                    </span>
                  )}
                </button>
              ))}
              
              <div className="border-t border-border pt-1">
                <button
                  onClick={copyToClipboard}
                  className="w-full flex items-center gap-3 px-3 py-2 text-sm rounded-md hover:bg-accent transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  <span className="flex-1 text-left">{t('copyLink')}</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Default buttons variant
  return (
    <div className={cn('flex flex-wrap gap-2', className)}>
      {platforms.map((platform) => (
        <button
          key={platform.name}
          onClick={() => handleShare(platform)}
          className={cn(
            'flex items-center gap-2 px-3 py-2 rounded-md text-white text-sm font-medium',
            'transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
            platform.color
          )}
          aria-label={`Share on ${platform.name}`}
        >
          {platform.icon}
          <span>{platform.name}</span>
          {showCounts && shareCounts[platform.name] && (
            <span className="text-xs opacity-75">
              ({shareCounts[platform.name]})
            </span>
          )}
        </button>
      ))}
      
      <button
        onClick={copyToClipboard}
        className="flex items-center gap-2 px-3 py-2 rounded-md border border-input bg-background text-foreground text-sm font-medium hover:bg-accent transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        aria-label="Copy link"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
        {t('copyLink')}
      </button>
    </div>
  );
}
