"use client";

import { useAnalytics } from "@/lib/analytics";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface AnalyticsButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  eventName: string;
  eventParameters?: Record<string, any>;
  children: React.ReactNode;
  variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link";
  size?: "default" | "sm" | "lg" | "icon";
  className?: string;
}

export function AnalyticsButton({
  eventName,
  eventParameters,
  children,
  variant = "default",
  size = "default",
  className,
  onClick,
  ...props
}: AnalyticsButtonProps) {
  const { trackEvent } = useAnalytics();

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    // Track the event
    trackEvent(eventName, eventParameters);

    // Call original onClick if provided
    if (onClick) {
      onClick(e);
    }
  };

  return (
    <Button
      variant={variant}
      size={size}
      className={cn(className)}
      onClick={handleClick}
      {...props}
    >
      {children}
    </Button>
  );
}
