"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDistanceToNow } from "date-fns";
import { ja } from "date-fns/locale";
import { Calendar, ExternalLink, Mail, Users } from "lucide-react";
import Link from "next/link";

interface Newsletter {
  id: string;
  title: string;
  description: string;
  content: string;
  publishedAt: string;
  subscribers: number;
  openRate: number;
  clickRate: number;
  isPremium: boolean;
  imageUrl?: string;
  tags: string[];
}

interface NewsletterCardProps {
  newsletter: Newsletter;
}

export function NewsletterCard({ newsletter }: NewsletterCardProps) {
  const timeAgo = formatDistanceToNow(new Date(newsletter.publishedAt), {
    addSuffix: true,
    locale: ja,
  });

  return (
    <Card className="group hover:shadow-lg transition-shadow duration-200">
      {newsletter.imageUrl && (
        <div className="aspect-video overflow-hidden rounded-t-lg">
          <img
            src={newsletter.imageUrl}
            alt={newsletter.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
          />
        </div>
      )}

      <CardHeader>
        <div className="flex items-center justify-between mb-2">
          <Badge variant="secondary">ニュースレター</Badge>
          {newsletter.isPremium && <Badge className="bg-yellow-500 text-white">Premium</Badge>}
        </div>

        <CardTitle className="line-clamp-2 group-hover:text-primary transition-colors">
          <Link href={`/newsletters/${newsletter.id}`}>{newsletter.title}</Link>
        </CardTitle>

        <CardDescription className="line-clamp-2">{newsletter.description}</CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="flex flex-wrap gap-1">
          {newsletter.tags.slice(0, 3).map((tag) => (
            <Badge key={tag} variant="outline" className="text-xs">
              #{tag}
            </Badge>
          ))}
          {newsletter.tags.length > 3 && (
            <Badge variant="outline" className="text-xs">
              +{newsletter.tags.length - 3}
            </Badge>
          )}
        </div>

        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <Calendar className="h-3 w-3" />
            <span>{timeAgo}</span>
          </div>

          <div className="flex items-center gap-1">
            <Users className="h-3 w-3" />
            <span>{newsletter.subscribers.toLocaleString()}</span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="flex items-center gap-2">
            <Mail className="h-3 w-3 text-muted-foreground" />
            <span className="text-muted-foreground">開封率:</span>
            <span className="font-medium">{newsletter.openRate}%</span>
          </div>
          <div className="flex items-center gap-2">
            <ExternalLink className="h-3 w-3 text-muted-foreground" />
            <span className="text-muted-foreground">クリック率:</span>
            <span className="font-medium">{newsletter.clickRate}%</span>
          </div>
        </div>

        <div className="pt-2">
          <Button variant="outline" size="sm" className="w-full" asChild>
            <Link href={`/newsletters/${newsletter.id}`}>詳細を見る</Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
