'use client';

import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { X } from 'lucide-react';

interface Filters {
  timeframe: string;
  category: string;
  sortBy: string;
}

interface TrendFiltersProps {
  filters: Filters;
  onFiltersChange: (filters: Filters) => void;
}

const timeframes = [
  { value: 'day', label: '今日' },
  { value: 'week', label: '今週' },
  { value: 'month', label: '今月' },
  { value: 'quarter', label: '今四半期' },
  { value: 'year', label: '今年' },
];

const categories = [
  { value: 'all', label: 'すべて' },
  { value: 'libraries', label: 'ライブラリ' },
  { value: 'frameworks', label: 'フレームワーク' },
  { value: 'tools', label: 'ツール' },
  { value: 'patterns', label: 'パターン' },
  { value: 'ecosystem', label: 'エコシステム' },
];

const sortOptions = [
  { value: 'trending', label: 'トレンド順' },
  { value: 'newest', label: '新しい順' },
  { value: 'engagement', label: 'エンゲージメント順' },
  { value: 'score', label: 'スコア順' },
];

export function TrendFilters({ filters, onFiltersChange }: TrendFiltersProps) {
  const handleTimeframeChange = (timeframe: string) => {
    onFiltersChange({ ...filters, timeframe });
  };

  const handleCategoryChange = (category: string) => {
    onFiltersChange({ ...filters, category });
  };

  const handleSortChange = (sortBy: string) => {
    onFiltersChange({ ...filters, sortBy });
  };

  const clearFilters = () => {
    onFiltersChange({
      timeframe: 'week',
      category: 'all',
      sortBy: 'trending',
    });
  };

  const hasActiveFilters = 
    filters.timeframe !== 'week' || 
    filters.category !== 'all' || 
    filters.sortBy !== 'trending';

  return (
    <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
      <div className="flex flex-col sm:flex-row gap-4 flex-1">
        <Select value={filters.timeframe} onValueChange={handleTimeframeChange}>
          <SelectTrigger className="w-full sm:w-40">
            <SelectValue placeholder="期間" />
          </SelectTrigger>
          <SelectContent>
            {timeframes.map((timeframe) => (
              <SelectItem key={timeframe.value} value={timeframe.value}>
                {timeframe.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        
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
