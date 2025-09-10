'use client';

import { analyticsEvents, trackEvent } from '@/lib/analytics';
import { Check, Copy, Facebook, Linkedin, Share2, Twitter } from 'lucide-react';
import { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';

interface SocialShareProps {
  url: string;
  title: string;
  description?: string;
  hashtags?: string[];
  className?: string;
}

export function SocialShare({
  url,
  title,
  description,
  hashtags = [],
  className,
}: SocialShareProps) {
  const [copied, setCopied] = useState(false);

  const shareData = {
    url,
    title,
    description: description || title,
    hashtags: hashtags.join(','),
  };

  const handleShare = (platform: string) => {
    let shareUrl = '';

    switch (platform) {
      case 'twitter':
        shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(
          title
        )}&url=${encodeURIComponent(url)}&hashtags=${hashtags.join(',')}`;
        break;
      case 'facebook':
        shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(
          url
        )}`;
        break;
      case 'linkedin':
        shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(
          url
        )}`;
        break;
      case 'copy':
        navigator.clipboard.writeText(url);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
        trackEvent('copy_link', 'engagement', 'social_share');
        return;
    }

    if (shareUrl) {
      window.open(shareUrl, '_blank', 'width=600,height=400');
      trackEvent('social_share', 'engagement', platform);
    }
  };

  const handleNativeShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share(shareData);
        trackEvent(
          'native_share',
          'engagement',
          'web_share_api'
        );
      } catch (error) {
        console.log('Error sharing:', error);
      }
    }
  };

  return (
    <Card className={className}>
      <CardContent className='p-4'>
        <div className='flex items-center justify-between mb-4'>
          <h3 className='text-sm font-medium'>シェア</h3>
          {typeof navigator !== 'undefined' && 'share' in navigator && (
            <Button
              variant='outline'
              size='sm'
              onClick={handleNativeShare}
              className='text-xs'
            >
              <Share2 className='h-3 w-3 mr-1' />
              共有
            </Button>
          )}
        </div>

        <div className='flex gap-2'>
          <Button
            variant='outline'
            size='sm'
            onClick={() => handleShare('twitter')}
            className='flex-1'
          >
            <Twitter className='h-4 w-4 mr-1' />
            Twitter
          </Button>

          <Button
            variant='outline'
            size='sm'
            onClick={() => handleShare('facebook')}
            className='flex-1'
          >
            <Facebook className='h-4 w-4 mr-1' />
            Facebook
          </Button>

          <Button
            variant='outline'
            size='sm'
            onClick={() => handleShare('linkedin')}
            className='flex-1'
          >
            <Linkedin className='h-4 w-4 mr-1' />
            LinkedIn
          </Button>

          <Button
            variant='outline'
            size='sm'
            onClick={() => handleShare('copy')}
            className='flex-1'
          >
            {copied ? (
              <Check className='h-4 w-4 mr-1' />
            ) : (
              <Copy className='h-4 w-4 mr-1' />
            )}
            {copied ? 'コピー済み' : 'コピー'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

// 記事用ソーシャルシェア
export function ArticleSocialShare({
  articleId,
  title,
  description,
  tags,
}: {
  articleId: string;
  title: string;
  description: string;
  tags: string[];
}) {
  const url = `${window.location.origin}/articles/${articleId}`;
  const hashtags = ['TypeScript', 'プログラミング', ...tags.slice(0, 3)];

  return (
    <SocialShare
      url={url}
      title={title}
      description={description}
      hashtags={hashtags}
    />
  );
}

// ニュースレター用ソーシャルシェア
export function NewsletterSocialShare({
  newsletterId,
  title,
  description,
}: {
  newsletterId: string;
  title: string;
  description: string;
}) {
  const url = `${window.location.origin}/newsletters/${newsletterId}`;
  const hashtags = ['TypeScript', 'ニュースレター', '技術情報'];

  return (
    <SocialShare
      url={url}
      title={title}
      description={description}
      hashtags={hashtags}
    />
  );
}
