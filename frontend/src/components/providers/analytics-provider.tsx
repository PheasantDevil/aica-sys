"use client";

import { useEffect } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import { Analytics, trackWebVitals } from "@/lib/analytics";

interface AnalyticsProviderProps {
  children: React.ReactNode;
}

export function AnalyticsProvider({ children }: AnalyticsProviderProps) {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    // Initialize analytics
    Analytics.init();

    // Track page view on route change
    const url = pathname + (searchParams?.toString() ? `?${searchParams.toString()}` : "");
    Analytics.trackPageView(url);

    // Track web vitals
    trackWebVitals();
  }, [pathname, searchParams]);

  useEffect(() => {
    // Track user engagement
    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        Analytics.trackUserEngagement("page_visible");
      } else {
        Analytics.trackUserEngagement("page_hidden");
      }
    };

    const handleBeforeUnload = () => {
      Analytics.trackUserEngagement("page_unload");
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    window.addEventListener("beforeunload", handleBeforeUnload);

    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      window.removeEventListener("beforeunload", handleBeforeUnload);
    };
  }, []);

  return <>{children}</>;
}
