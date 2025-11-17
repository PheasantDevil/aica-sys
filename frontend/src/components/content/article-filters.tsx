"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Search, X } from "lucide-react";
import { useEffect, useState } from "react";

interface Filters {
  category: string;
  sortBy: string;
  search: string;
}

interface ArticleFiltersProps {
  filters: Filters;
  onFiltersChange: (filters: Filters) => void;
}

const categories = [
  { value: "all", label: "すべて" },
  { value: "tutorial", label: "チュートリアル" },
  { value: "tips", label: "Tips & Tricks" },
  { value: "news", label: "ニュース" },
  { value: "advanced", label: "上級者向け" },
  { value: "tools", label: "ツール" },
];

const sortOptions = [
  { value: "newest", label: "新しい順" },
  { value: "oldest", label: "古い順" },
  { value: "popular", label: "人気順" },
  { value: "trending", label: "トレンド順" },
];

export function ArticleFilters({ filters, onFiltersChange }: ArticleFiltersProps) {
  const [searchValue, setSearchValue] = useState(filters.search);

  useEffect(() => {
    const timer = setTimeout(() => {
      onFiltersChange({ ...filters, search: searchValue });
    }, 500);

    return () => clearTimeout(timer);
  }, [searchValue, filters, onFiltersChange]);

  const handleCategoryChange = (category: string) => {
    onFiltersChange({ ...filters, category });
  };

  const handleSortChange = (sortBy: string) => {
    onFiltersChange({ ...filters, sortBy });
  };

  const clearFilters = () => {
    setSearchValue("");
    onFiltersChange({
      category: "all",
      sortBy: "newest",
      search: "",
    });
  };

  const hasActiveFilters =
    filters.category !== "all" || filters.sortBy !== "newest" || filters.search;

  return (
    <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
      <div className="flex flex-col sm:flex-row gap-4 flex-1">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="記事を検索..."
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            className="pl-10"
          />
        </div>

        <Select value={filters.category} onValueChange={handleCategoryChange}>
          <SelectTrigger className="w-full sm:w-40">
            <SelectValue placeholder="カテゴリ" />
          </SelectTrigger>
          <SelectContent>
            {categories.map((category) => (
              <SelectItem key={category.value} value={category.value}>
                {category.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={filters.sortBy} onValueChange={handleSortChange}>
          <SelectTrigger className="w-full sm:w-40">
            <SelectValue placeholder="並び順" />
          </SelectTrigger>
          <SelectContent>
            {sortOptions.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {hasActiveFilters && (
        <Button variant="outline" size="sm" onClick={clearFilters}>
          <X className="h-4 w-4 mr-2" />
          フィルターをクリア
        </Button>
      )}
    </div>
  );
}
