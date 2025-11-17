"use client";

import React, { forwardRef, useRef, useEffect } from "react";
import { cn } from "@/lib/utils";
import { AccessibilityUtils } from "@/lib/accessibility";

interface AccessibleButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link";
  size?: "default" | "sm" | "lg" | "icon";
  loading?: boolean;
  loadingText?: string;
  children: React.ReactNode;
  className?: string;
  ariaDescribedBy?: string;
  ariaExpanded?: boolean;
  ariaControls?: string;
  ariaPressed?: boolean;
  ariaCurrent?: boolean | "page" | "step" | "location" | "date" | "time";
  ariaHaspopup?: boolean | "menu" | "listbox" | "tree" | "grid" | "dialog";
  ariaLabel?: string;
  ariaLabelledBy?: string;
}

const AccessibleButton = forwardRef<HTMLButtonElement, AccessibleButtonProps>(
  (
    {
      variant = "default",
      size = "default",
      loading = false,
      loadingText = "Loading...",
      children,
      className,
      ariaDescribedBy,
      ariaExpanded,
      ariaControls,
      ariaPressed,
      ariaCurrent,
      ariaHaspopup,
      ariaLabel,
      ariaLabelledBy,
      disabled,
      onClick,
      ...props
    },
    ref,
  ) => {
    const buttonRef = useRef<HTMLButtonElement>(null);
    const [isFocused, setIsFocused] = React.useState(false);

    // Combine refs
    React.useImperativeHandle(ref, () => buttonRef.current!);

    // Focus management
    useEffect(() => {
      const button = buttonRef.current;
      if (!button) return;

      const handleFocus = () => setIsFocused(true);
      const handleBlur = () => setIsFocused(false);

      button.addEventListener("focus", handleFocus);
      button.addEventListener("blur", handleBlur);

      return () => {
        button.removeEventListener("focus", handleFocus);
        button.removeEventListener("blur", handleBlur);
      };
    }, []);

    // Keyboard event handling
    const handleKeyDown = (event: React.KeyboardEvent<HTMLButtonElement>) => {
      // Handle space and enter keys for button activation
      if (event.key === " " || event.key === "Enter") {
        event.preventDefault();
        if (!disabled && !loading && onClick) {
          onClick(event as any);
        }
      }
    };

    // Generate unique ID for accessibility
    const buttonId = React.useId();

    const baseClasses =
      "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50";

    const variantClasses = {
      default: "bg-primary text-primary-foreground hover:bg-primary/90",
      destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
      outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
      secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
      ghost: "hover:bg-accent hover:text-accent-foreground",
      link: "text-primary underline-offset-4 hover:underline",
    };

    const sizeClasses = {
      default: "h-10 px-4 py-2",
      sm: "h-9 rounded-md px-3",
      lg: "h-11 rounded-md px-8",
      icon: "h-10 w-10",
    };

    const isDisabled = disabled || loading;

    return (
      <button
        ref={buttonRef}
        type="button"
        className={cn(
          baseClasses,
          variantClasses[variant],
          sizeClasses[size],
          isFocused && "ring-2 ring-ring ring-offset-2",
          className,
        )}
        disabled={isDisabled}
        onClick={onClick}
        onKeyDown={handleKeyDown}
        aria-label={ariaLabel}
        aria-labelledby={ariaLabelledBy}
        aria-describedby={ariaDescribedBy}
        aria-expanded={ariaExpanded}
        aria-controls={ariaControls}
        aria-pressed={ariaPressed}
        aria-current={ariaCurrent}
        aria-haspopup={ariaHaspopup}
        aria-busy={loading}
        {...props}
      >
        {loading && (
          <>
            <svg
              className="mr-2 h-4 w-4 animate-spin"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            <span className="sr-only">{loadingText}</span>
          </>
        )}
        <span className={loading ? "sr-only" : ""}>{children}</span>
        {loading && (
          <span className="sr-only" aria-live="polite">
            {loadingText}
          </span>
        )}
      </button>
    );
  },
);

AccessibleButton.displayName = "AccessibleButton";

export { AccessibleButton };
