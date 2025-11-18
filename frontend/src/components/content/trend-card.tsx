"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { TrendingUp, Calendar, BarChart3, ExternalLink, ArrowUp, ArrowDown } from "lucide-react";
import Link from "next/link";
import { formatDistanceToNow } from "date-fns";
import { ja } from "date-fns/locale";

interface Trend {
  id: string;
  title: string;
  description: string;
  category: string;
  tags: string[];
  publishedAt: string;
  trendScore: number;
  changeRate: number;
  engagement: number;
  isPremium: boolean;
  imageUrl?: string;
  metrics: {
    mentions: number;
    growth: number;
    sentiment: "positive" | "neutral" | "negative";
  };
}

interface TrendCardProps {
  trend: Trend;
}

export function TrendCard({ trend }: TrendCardProps) {
  const timeAgo = formatDistanceToNow(new Date(trend.publishedAt), {
    addSuffix: true,
    locale: ja,
  });

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case "positive":
        return "text-green-600 bg-green-50 border-green-200";
      case "negative":
        return "text-red-600 bg-red-50 border-red-200";
      default:
        return "text-gray-600 bg-gray-50 border-gray-200";
    }
  };

  const getSentimentLabel = (sentiment: string) => {
    switch (sentiment) {
      case "positive":
        return "ポジティブ";
      case "negative":
        return "ネガティブ";
      default:
        return "ニュートラル";
    }
  };

  return (
    <Card className="group hover:shadow-lg transition-shadow duration-200">
      {trend.imageUrl && (
        <div className="aspect-video overflow-hidden rounded-t-lg">
          <img
            src={trend.imageUrl}
            alt={trend.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
          />
        </div>
      )}

      <CardHeader>
        <div className="flex items-center justify-between mb-2">
          <Badge variant="secondary">{trend.category}</Badge>
          {trend.isPremium && <Badge className="bg-yellow-500 text-white">Premium</Badge>}
        </div>

        <CardTitle className="line-clamp-2 group-hover:text-primary transition-colors">
          <Link href={`/trends/${trend.id}`}>{trend.title}</Link>
        </CardTitle>

        <CardDescription className="line-clamp-2">{trend.description}</CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="flex flex-wrap gap-1">
          {trend.tags.slice(0, 3).map((tag) => (
            <Badge key={tag} variant="outline" className="text-xs">
              #{tag}
            </Badge>
          ))}
          {trend.tags.length > 3 && (
            <Badge variant="outline" className="text-xs">
              +{trend.tags.length - 3}
            </Badge>
          )}
        </div>

        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <Calendar className="h-3 w-3" />
            <span>{timeAgo}</span>
          </div>

          <div className="flex items-center gap-1">
            <TrendingUp className="h-3 w-3" />
            <span>スコア: {trend.trendScore}</span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="flex items-center gap-2">
            <BarChart3 className="h-3 w-3 text-muted-foreground" />
            <span className="text-muted-foreground">言及数:</span>
            <span className="font-medium">{trend.metrics.mentions.toLocaleString()}</span>
          </div>
          <div className="flex items-center gap-2">
            {trend.changeRate >= 0 ? (
              <ArrowUp className="h-3 w-3 text-green-600" />
            ) : (
              <ArrowDown className="h-3 w-3 text-red-600" />
            )}
            <span className="text-muted-foreground">変化率:</span>
            <span
              className={`font-medium ${trend.changeRate >= 0 ? "text-green-600" : "text-red-600"}`}
            >
              {Math.abs(trend.changeRate)}%
            </span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <Badge
            variant="outline"
            className={`text-xs ${getSentimentColor(trend.metrics.sentiment)}`}
          >
            {getSentimentLabel(trend.metrics.sentiment)}
          </Badge>

          <span className="text-sm text-muted-foreground">
            エンゲージメント: {trend.engagement}%
          </span>
        </div>

        <div className="pt-2">
          <Button variant="outline" size="sm" className="w-full" asChild>
            <Link href={`/trends/${trend.id}`}>
              <ExternalLink className="h-4 w-4 mr-2" />
              詳細を見る
            </Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
