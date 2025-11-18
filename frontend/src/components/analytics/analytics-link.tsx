"use client";

import { useAnalytics } from "@/lib/analytics";
import Link from "next/link";
import { cn } from "@/lib/utils";

interface AnalyticsLinkProps extends React.AnchorHTMLAttributes<HTMLAnchorElement> {
  href: string;
  eventName: string;
  eventParameters?: Record<string, any>;
  children: React.ReactNode;
  className?: string;
}

export function AnalyticsLink({
  href,
  eventName,
  eventParameters,
  children,
  className,
  onClick,
  ...props
}: AnalyticsLinkProps) {
  const { trackEvent } = useAnalytics();

  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    // Track the event
    trackEvent(eventName, eventParameters);

    // Call original onClick if provided
    if (onClick) {
      onClick(e);
    }
  };

  return (
    <Link href={href} className={cn(className)} onClick={handleClick} {...props}>
      {children}
    </Link>
  );
}
