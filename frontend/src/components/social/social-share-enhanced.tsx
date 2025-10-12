"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAnalytics } from "@/lib/analytics";
import {
  Check,
  Copy,
  ExternalLink,
  Facebook,
  Github,
  Linkedin,
  Link as LinkIcon,
  Share2,
  Twitter,
} from "lucide-react";
import { useState } from "react";

interface SocialShareProps {
  url?: string;
  title: string;
  description?: string;
  image?: string;
  hashtags?: string[];
  via?: string;
  className?: string;
  showCounts?: boolean;
  showAllPlatforms?: boolean;
}

interface ShareData {
  url: string;
  title: string;
  description: string;
  image: string;
  hashtags: string[];
  via: string;
}

interface ShareCounts {
  twitter?: number;
  facebook?: number;
  linkedin?: number;
  total?: number;
}

export function SocialShareEnhanced({
  url,
  title,
  description = "",
  image = "",
  hashtags = [],
  via = "aica_sys",
  className = "",
  showCounts = false,
  showAllPlatforms = false,
}: SocialShareProps) {
  const [shareCounts, setShareCounts] = useState<ShareCounts>({});
  const [copied, setCopied] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const analytics = useAnalytics();

  const currentUrl = url || (typeof window !== "undefined" ? window.location.href : "");
  const currentTitle = title || (typeof window !== "undefined" ? document.title : "");
  const currentImage =
    image || (typeof window !== "undefined" ? `${window.location.origin}/og-default.png` : "");

  const shareData: ShareData = {
    url: currentUrl,
    title: currentTitle,
    description,
    image: currentImage,
    hashtags,
    via,
  };

  const handleShare = async (platform: string, shareUrl: string) => {
    setIsLoading(true);

    try {
      // アナリティクスに記録
      analytics.trackEvent("Social Share", {
        platform,
        url: currentUrl,
        title: currentTitle,
      });

      // シェアを実行
      if (platform === "native" && navigator.share) {
        await navigator.share({
          title: currentTitle,
          text: description,
          url: currentUrl,
        });
      } else {
        window.open(shareUrl, "_blank", "width=600,height=400");
      }

      // シェア数を更新
      if (showCounts) {
        await updateShareCounts();
      }
    } catch (error) {
      console.error(`Error sharing to ${platform}:`, error);
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(currentUrl);
      setCopied(true);

      analytics.trackEvent("Copy Link", {
        url: currentUrl,
        title: currentTitle,
      });

      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error("Error copying to clipboard:", error);
    }
  };

  const updateShareCounts = async () => {
    try {
      // 実際の実装では、各プラットフォームのAPIを使用してシェア数を取得
      // ここでは仮のデータを使用
      const counts: ShareCounts = {
        twitter: Math.floor(Math.random() * 100),
        facebook: Math.floor(Math.random() * 50),
        linkedin: Math.floor(Math.random() * 30),
      };

      counts.total = (counts.twitter || 0) + (counts.facebook || 0) + (counts.linkedin || 0);
      setShareCounts(counts);
    } catch (error) {
      console.error("Error updating share counts:", error);
    }
  };

  const getShareUrls = () => {
    const encodedUrl = encodeURIComponent(currentUrl);
    const encodedTitle = encodeURIComponent(currentTitle);
    const encodedDescription = encodeURIComponent(description);
    const encodedHashtags = hashtags.map((tag) => `%23${tag}`).join("");

    return {
      twitter: `https://twitter.com/intent/tweet?url=${encodedUrl}&text=${encodedTitle}&via=${via}&hashtags=${encodedHashtags}`,
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`,
      linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`,
      github: `https://github.com/intent/tweet?url=${encodedUrl}&text=${encodedTitle}`,
    };
  };

  const shareUrls = getShareUrls();

  const platforms = [
    {
      id: "twitter",
      name: "Twitter",
      icon: Twitter,
      url: shareUrls.twitter,
      color: "bg-blue-400 hover:bg-blue-500",
      count: shareCounts.twitter,
    },
    {
      id: "facebook",
      name: "Facebook",
      icon: Facebook,
      url: shareUrls.facebook,
      color: "bg-blue-600 hover:bg-blue-700",
      count: shareCounts.facebook,
    },
    {
      id: "linkedin",
      name: "LinkedIn",
      icon: Linkedin,
      url: shareUrls.linkedin,
      color: "bg-blue-700 hover:bg-blue-800",
      count: shareCounts.linkedin,
    },
    {
      id: "github",
      name: "GitHub",
      icon: Github,
      url: shareUrls.github,
      color: "bg-gray-800 hover:bg-gray-900",
      count: undefined,
    },
  ];

  const visiblePlatforms = showAllPlatforms ? platforms : platforms.slice(0, 3);

  return (
    <Card className={`w-full ${className}`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Share2 className="h-5 w-5" />
          シェア
        </CardTitle>
        <CardDescription>このコンテンツをソーシャルメディアでシェア</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* プラットフォームボタン */}
        <div className="flex flex-wrap gap-2">
          {visiblePlatforms.map((platform) => (
            <Button
              key={platform.id}
              variant="outline"
              size="sm"
              className={`${platform.color} text-white border-0`}
              onClick={() => handleShare(platform.id, platform.url)}
              disabled={isLoading}
            >
              <platform.icon className="h-4 w-4 mr-2" />
              {platform.name}
              {showCounts && platform.count !== undefined && (
                <Badge variant="secondary" className="ml-2 text-xs">
                  {platform.count}
                </Badge>
              )}
            </Button>
          ))}

          {/* ネイティブシェア（モバイル） */}
          {typeof window !== "undefined" && "share" in navigator && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleShare("native", "")}
              disabled={isLoading}
            >
              <Share2 className="h-4 w-4 mr-2" />
              シェア
            </Button>
          )}
        </div>

        {/* リンクコピー */}
        <div className="flex items-center gap-2">
          <div className="flex-1 p-2 bg-gray-100 rounded text-sm text-gray-600 truncate">
            {currentUrl}
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={copyToClipboard}
            className="flex items-center gap-2"
          >
            {copied ? (
              <>
                <Check className="h-4 w-4" />
                コピー済み
              </>
            ) : (
              <>
                <Copy className="h-4 w-4" />
                コピー
              </>
            )}
          </Button>
        </div>

        {/* シェア統計 */}
        {showCounts && shareCounts.total && (
          <div className="flex items-center justify-between text-sm text-gray-600">
            <span>総シェア数</span>
            <Badge variant="outline">{shareCounts.total}</Badge>
          </div>
        )}

        {/* プレビュー */}
        <div className="border rounded-lg p-3 bg-gray-50">
          <div className="text-sm font-medium text-gray-900 mb-1">{currentTitle}</div>
          <div className="text-sm text-gray-600 mb-2">{description || "説明がありません"}</div>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <LinkIcon className="h-3 w-3" />
            <span className="truncate">{currentUrl}</span>
            <ExternalLink className="h-3 w-3" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * インラインシェアボタン（軽量版）
 */
export function InlineSocialShare({
  url,
  title,
  description = "",
  hashtags = [],
  via = "aica_sys",
  className = "",
}: Omit<SocialShareProps, "showCounts" | "showAllPlatforms">) {
  const analytics = useAnalytics();

  const currentUrl = url || (typeof window !== "undefined" ? window.location.href : "");
  const currentTitle = title || (typeof window !== "undefined" ? document.title : "");

  const handleShare = (platform: string, shareUrl: string) => {
    analytics.trackEvent("Social Share", {
      platform,
      url: currentUrl,
      title: currentTitle,
    });

    window.open(shareUrl, "_blank", "width=600,height=400");
  };

  const getShareUrls = () => {
    const encodedUrl = encodeURIComponent(currentUrl);
    const encodedTitle = encodeURIComponent(currentTitle);
    const encodedHashtags = hashtags.map((tag) => `%23${tag}`).join("");

    return {
      twitter: `https://twitter.com/intent/tweet?url=${encodedUrl}&text=${encodedTitle}&via=${via}&hashtags=${encodedHashtags}`,
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`,
      linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`,
    };
  };

  const shareUrls = getShareUrls();

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <span className="text-sm text-gray-600">シェア:</span>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => handleShare("twitter", shareUrls.twitter)}
        className="p-1 h-8 w-8"
      >
        <Twitter className="h-4 w-4 text-blue-400" />
      </Button>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => handleShare("facebook", shareUrls.facebook)}
        className="p-1 h-8 w-8"
      >
        <Facebook className="h-4 w-4 text-blue-600" />
      </Button>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => handleShare("linkedin", shareUrls.linkedin)}
        className="p-1 h-8 w-8"
      >
        <Linkedin className="h-4 w-4 text-blue-700" />
      </Button>
    </div>
  );
}
