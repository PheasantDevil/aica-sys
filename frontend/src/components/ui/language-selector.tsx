"use client";

import { getDirection, localeFlags, localeNames, locales } from "@/i18n/config";
import { AccessibilityUtils } from "@/lib/accessibility";
import { cn } from "@/lib/utils";
import { useLocale, useTranslations } from "next-intl";
import { usePathname, useRouter } from "next/navigation";
import React, { useEffect, useRef, useState } from "react";

interface LanguageSelectorProps {
  className?: string;
  variant?: "dropdown" | "buttons";
  showFlags?: boolean;
  showNames?: boolean;
}

export function LanguageSelector({
  className,
  variant = "dropdown",
  showFlags = true,
  showNames = true,
}: LanguageSelectorProps) {
  const t = useTranslations("common");
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const [isOpen, setIsOpen] = useState(false);
  const [focusedIndex, setFocusedIndex] = useState(-1);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const listRef = useRef<HTMLUListElement>(null);

  const currentLocale = locale as keyof typeof localeNames;
  const currentDirection = getDirection(currentLocale);

  const handleLanguageChange = (newLocale: string) => {
    const newPath = pathname.replace(`/${locale}`, `/${newLocale}`);
    router.push(newPath);
    setIsOpen(false);
    setFocusedIndex(-1);

    // Announce change to screen readers
    AccessibilityUtils.announceToScreenReader(
      `Language changed to ${localeNames[newLocale as keyof typeof localeNames]}`,
      "polite",
    );
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    const items = Array.from(listRef.current?.children || []) as HTMLElement[];

    if (event.key === "Escape") {
      setIsOpen(false);
      buttonRef.current?.focus();
      return;
    }

    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      if (!isOpen) {
        setIsOpen(true);
        return;
      }

      if (focusedIndex >= 0 && items[focusedIndex]) {
        const newLocale = items[focusedIndex].getAttribute("data-locale");
        if (newLocale) {
          handleLanguageChange(newLocale);
        }
      }
      return;
    }

    if (isOpen && items.length > 0) {
      const newIndex = AccessibilityUtils.handleArrowKeys(
        event.nativeEvent,
        items,
        focusedIndex,
        "vertical",
      );

      if (newIndex !== focusedIndex) {
        setFocusedIndex(newIndex);
        items[newIndex]?.focus();
      }
    }
  };

  const handleBlur = (event: React.FocusEvent) => {
    // Close dropdown if focus moves outside
    if (!event.currentTarget.contains(event.relatedTarget as Node)) {
      setIsOpen(false);
      setFocusedIndex(-1);
    }
  };

  // Focus management
  useEffect(() => {
    if (isOpen && listRef.current) {
      const items = Array.from(listRef.current.children) as HTMLElement[];
      if (focusedIndex >= 0 && items[focusedIndex]) {
        items[focusedIndex].focus();
      }
    }
  }, [isOpen, focusedIndex]);

  if (variant === "buttons") {
    return (
      <div className={cn("flex gap-2", className)} role="group" aria-label={t("language")}>
        {locales.map((loc) => (
          <button
            key={loc}
            onClick={() => handleLanguageChange(loc)}
            className={cn(
              "flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors",
              "hover:bg-accent hover:text-accent-foreground",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
              locale === loc ? "bg-primary text-primary-foreground" : "text-muted-foreground",
            )}
            aria-pressed={locale === loc}
            aria-current={locale === loc ? "true" : "false"}
          >
            {showFlags && <span aria-hidden="true">{localeFlags[loc]}</span>}
            {showNames && <span>{localeNames[loc]}</span>}
          </button>
        ))}
      </div>
    );
  }

  return (
    <div className={cn("relative", className)} onBlur={handleBlur}>
      <button
        ref={buttonRef}
        onClick={() => setIsOpen(!isOpen)}
        onKeyDown={handleKeyDown}
        className={cn(
          "flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors",
          "hover:bg-accent hover:text-accent-foreground",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
          "aria-expanded={isOpen}",
        )}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-label={t("language")}
      >
        {showFlags && <span aria-hidden="true">{localeFlags[currentLocale]}</span>}
        {showNames && <span>{localeNames[currentLocale]}</span>}
        <svg
          className={cn("w-4 h-4 transition-transform", isOpen && "rotate-180")}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <ul
          ref={listRef}
          role="listbox"
          className={cn(
            "absolute top-full left-0 mt-1 w-full bg-popover border border-border rounded-md shadow-lg z-50",
            "focus-visible:outline-none",
          )}
          aria-label={t("language")}
        >
          {locales.map((loc, index) => (
            <li key={loc} role="none">
              <button
                role="option"
                data-locale={loc}
                onClick={() => handleLanguageChange(loc)}
                onKeyDown={handleKeyDown}
                className={cn(
                  "w-full flex items-center gap-2 px-3 py-2 text-sm text-left transition-colors",
                  "hover:bg-accent hover:text-accent-foreground",
                  "focus-visible:outline-none focus-visible:bg-accent focus-visible:text-accent-foreground",
                  locale === loc && "bg-accent text-accent-foreground",
                  "aria-selected={locale === loc}",
                )}
                aria-selected={locale === loc}
                tabIndex={-1}
              >
                {showFlags && <span aria-hidden="true">{localeFlags[loc]}</span>}
                {showNames && <span>{localeNames[loc]}</span>}
                {locale === loc && (
                  <svg
                    className="w-4 h-4 ml-auto"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                    aria-hidden="true"
                  >
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                )}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
