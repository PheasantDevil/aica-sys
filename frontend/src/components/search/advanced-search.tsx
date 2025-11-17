"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { cn } from "@/lib/utils";
import { AccessibilityUtils } from "@/lib/accessibility";
import { SearchEngine, SearchFilters, SearchHistory, SearchResult } from "@/lib/search";
import { useTranslations } from "next-intl";

interface AdvancedSearchProps {
  searchEngine: SearchEngine;
  onResultsChange?: (results: SearchResult[]) => void;
  className?: string;
  placeholder?: string;
  showFilters?: boolean;
  showHistory?: boolean;
  showSuggestions?: boolean;
  maxSuggestions?: number;
  autoFocus?: boolean;
}

export function AdvancedSearch({
  searchEngine,
  onResultsChange,
  className,
  placeholder,
  showFilters = true,
  showHistory = true,
  showSuggestions = true,
  maxSuggestions = 5,
  autoFocus = false,
}: AdvancedSearchProps) {
  const t = useTranslations("common");
  const router = useRouter();
  const searchParams = useSearchParams();

  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [history, setHistory] = useState<string[]>([]);
  const [filters, setFilters] = useState<SearchFilters>({});
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [focusedIndex, setFocusedIndex] = useState(-1);

  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLUListElement>(null);
  const searchRef = useRef<HTMLDivElement>(null);

  // Load initial state from URL
  useEffect(() => {
    const urlQuery = searchParams.get("q") || "";
    const urlFilters = SearchFilters.createFromURL(searchParams);

    setQuery(urlQuery);
    setFilters(urlFilters);

    if (urlQuery) {
      performSearch(urlQuery, urlFilters);
    }
  }, [searchParams]);

  // Load search history
  useEffect(() => {
    if (showHistory) {
      setHistory(SearchHistory.getHistory());
    }
  }, [showHistory]);

  // Auto-focus
  useEffect(() => {
    if (autoFocus && inputRef.current) {
      inputRef.current.focus();
    }
  }, [autoFocus]);

  // Perform search
  const performSearch = useCallback(
    async (searchQuery: string, searchFilters: SearchFilters = filters) => {
      if (!searchQuery.trim()) {
        setResults([]);
        onResultsChange?.([]);
        return;
      }

      setIsLoading(true);

      try {
        const searchResults = searchEngine.search(searchQuery, searchFilters);
        setResults(searchResults);
        onResultsChange?.(searchResults);

        // Add to search history
        SearchHistory.addSearch(searchQuery);
        setHistory(SearchHistory.getHistory());

        // Update URL
        const newParams = new URLSearchParams(searchParams);
        newParams.set("q", searchQuery);

        const filterParams = SearchFilters.toURL(searchFilters);
        filterParams.forEach((value, key) => {
          newParams.set(key, value);
        });

        router.push(`/search?${newParams.toString()}`, { scroll: false });
      } finally {
        setIsLoading(false);
      }
    },
    [searchEngine, filters, onResultsChange, router, searchParams],
  );

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    setFocusedIndex(-1);

    if (value.trim()) {
      if (showSuggestions) {
        const newSuggestions = searchEngine.getSuggestions(value, maxSuggestions);
        setSuggestions(newSuggestions);
      }
      setIsOpen(true);
    } else {
      setSuggestions([]);
      setIsOpen(false);
    }
  };

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    performSearch(query, filters);
    setIsOpen(false);
  };

  // Handle suggestion selection
  const handleSuggestionSelect = (suggestion: string) => {
    setQuery(suggestion);
    performSearch(suggestion, filters);
    setIsOpen(false);
    inputRef.current?.focus();
  };

  // Handle history selection
  const handleHistorySelect = (historyItem: string) => {
    setQuery(historyItem);
    performSearch(historyItem, filters);
    setIsOpen(false);
    inputRef.current?.focus();
  };

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    const allItems = [...suggestions, ...history];

    if (e.key === "Escape") {
      setIsOpen(false);
      setFocusedIndex(-1);
      return;
    }

    if (e.key === "Enter") {
      e.preventDefault();
      if (focusedIndex >= 0 && allItems[focusedIndex]) {
        const selectedItem = allItems[focusedIndex];
        if (suggestions.includes(selectedItem)) {
          handleSuggestionSelect(selectedItem);
        } else {
          handleHistorySelect(selectedItem);
        }
      } else {
        handleSubmit(e);
      }
      return;
    }

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setFocusedIndex((prev) => (prev < allItems.length - 1 ? prev + 1 : 0));
      return;
    }

    if (e.key === "ArrowUp") {
      e.preventDefault();
      setFocusedIndex((prev) => (prev > 0 ? prev - 1 : allItems.length - 1));
      return;
    }
  };

  // Handle filter change
  const handleFilterChange = (newFilters: SearchFilters) => {
    setFilters(newFilters);
    if (query.trim()) {
      performSearch(query, newFilters);
    }
  };

  // Clear search
  const clearSearch = () => {
    setQuery("");
    setResults([]);
    setSuggestions([]);
    setIsOpen(false);
    onResultsChange?.([]);
    inputRef.current?.focus();

    // Clear URL
    router.push("/search", { scroll: false });
  };

  // Clear history
  const clearHistory = () => {
    SearchHistory.clearHistory();
    setHistory([]);
  };

  return (
    <div ref={searchRef} className={cn("relative", className)}>
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            onFocus={() => setIsOpen(true)}
            placeholder={placeholder || t("search")}
            className={cn(
              "w-full px-4 py-3 pr-12 rounded-lg border border-input bg-background",
              "focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent",
              "text-sm placeholder:text-muted-foreground",
            )}
            aria-expanded={isOpen}
            aria-haspopup="listbox"
            aria-autocomplete="list"
            aria-activedescendant={focusedIndex >= 0 ? `suggestion-${focusedIndex}` : undefined}
          />

          <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
            {isLoading && (
              <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            )}

            {query && (
              <button
                type="button"
                onClick={clearSearch}
                className="p-1 hover:bg-accent rounded-md transition-colors"
                aria-label={t("clear")}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            )}

            <button
              type="submit"
              className="p-1 hover:bg-accent rounded-md transition-colors"
              aria-label={t("search")}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </button>
          </div>
        </div>

        {/* Suggestions and History Dropdown */}
        {isOpen && (suggestions.length > 0 || history.length > 0) && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-popover border border-border rounded-lg shadow-lg z-50 max-h-80 overflow-y-auto">
            <ul ref={suggestionsRef} role="listbox" className="py-2">
              {/* Suggestions */}
              {suggestions.length > 0 && (
                <>
                  <li className="px-4 py-2 text-xs font-medium text-muted-foreground uppercase tracking-wide">
                    {t("suggestions")}
                  </li>
                  {suggestions.map((suggestion, index) => (
                    <li key={`suggestion-${index}`} role="none">
                      <button
                        id={`suggestion-${index}`}
                        role="option"
                        onClick={() => handleSuggestionSelect(suggestion)}
                        className={cn(
                          "w-full px-4 py-2 text-left text-sm hover:bg-accent transition-colors",
                          focusedIndex === index && "bg-accent",
                        )}
                        aria-selected={focusedIndex === index}
                      >
                        {suggestion}
                      </button>
                    </li>
                  ))}
                </>
              )}

              {/* Search History */}
              {history.length > 0 && (
                <>
                  <li className="px-4 py-2 text-xs font-medium text-muted-foreground uppercase tracking-wide border-t border-border mt-2 pt-2">
                    {t("recentSearches")}
                  </li>
                  {history.slice(0, 5).map((historyItem, index) => (
                    <li key={`history-${index}`} role="none">
                      <button
                        id={`history-${index}`}
                        role="option"
                        onClick={() => handleHistorySelect(historyItem)}
                        className={cn(
                          "w-full px-4 py-2 text-left text-sm hover:bg-accent transition-colors flex items-center justify-between",
                          focusedIndex === suggestions.length + index && "bg-accent",
                        )}
                        aria-selected={focusedIndex === suggestions.length + index}
                      >
                        <span>{historyItem}</span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            SearchHistory.removeSearch(historyItem);
                            setHistory(SearchHistory.getHistory());
                          }}
                          className="p-1 hover:bg-accent-foreground/20 rounded transition-colors"
                          aria-label={t("remove")}
                        >
                          <svg
                            className="w-3 h-3"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M6 18L18 6M6 6l12 12"
                            />
                          </svg>
                        </button>
                      </button>
                    </li>
                  ))}

                  <li className="px-4 py-2 border-t border-border">
                    <button
                      onClick={clearHistory}
                      className="w-full text-left text-xs text-muted-foreground hover:text-foreground transition-colors"
                    >
                      {t("clearHistory")}
                    </button>
                  </li>
                </>
              )}
            </ul>
          </div>
        )}
      </form>

      {/* Search Filters */}
      {showFilters && (
        <SearchFiltersComponent
          filters={filters}
          onFiltersChange={handleFilterChange}
          searchEngine={searchEngine}
        />
      )}
    </div>
  );
}

// Search Filters Component
interface SearchFiltersComponentProps {
  filters: SearchFilters;
  onFiltersChange: (filters: SearchFilters) => void;
  searchEngine: SearchEngine;
}

function SearchFiltersComponent({
  filters,
  onFiltersChange,
  searchEngine,
}: SearchFiltersComponentProps) {
  const t = useTranslations("common");
  const analytics = searchEngine.getSearchAnalytics();

  const handleCategoryChange = (category: string) => {
    onFiltersChange({
      ...filters,
      category: category || undefined,
    });
  };

  const handleTypeChange = (type: string) => {
    onFiltersChange({
      ...filters,
      type: type || undefined,
    });
  };

  const handleAuthorChange = (author: string) => {
    onFiltersChange({
      ...filters,
      author: author || undefined,
    });
  };

  const clearFilters = () => {
    onFiltersChange({});
  };

  return (
    <div className="mt-4 p-4 bg-muted/50 rounded-lg">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium">{t("filters")}</h3>
        {!SearchFilters.isEmpty(filters) && (
          <button
            onClick={clearFilters}
            className="text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            {t("clearFilters")}
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Category Filter */}
        <div>
          <label className="block text-xs font-medium text-muted-foreground mb-2">
            {t("category")}
          </label>
          <select
            value={filters.category || ""}
            onChange={(e) => handleCategoryChange(e.target.value)}
            className="w-full px-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
          >
            <option value="">{t("allCategories")}</option>
            {Object.entries(analytics.categories).map(([category, count]) => (
              <option key={category} value={category}>
                {category} ({count})
              </option>
            ))}
          </select>
        </div>

        {/* Type Filter */}
        <div>
          <label className="block text-xs font-medium text-muted-foreground mb-2">
            {t("type")}
          </label>
          <select
            value={filters.type || ""}
            onChange={(e) => handleTypeChange(e.target.value)}
            className="w-full px-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
          >
            <option value="">{t("allTypes")}</option>
            {Object.entries(analytics.types).map(([type, count]) => (
              <option key={type} value={type}>
                {type} ({count})
              </option>
            ))}
          </select>
        </div>

        {/* Author Filter */}
        <div>
          <label className="block text-xs font-medium text-muted-foreground mb-2">
            {t("author")}
          </label>
          <select
            value={filters.author || ""}
            onChange={(e) => handleAuthorChange(e.target.value)}
            className="w-full px-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
          >
            <option value="">{t("allAuthors")}</option>
            {Object.entries(analytics.authors).map(([author, count]) => (
              <option key={author} value={author}>
                {author} ({count})
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}
