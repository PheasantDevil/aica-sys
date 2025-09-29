import Fuse, { FuseResult, FuseResultMatch, FuseSortFunction } from 'fuse.js';

export interface SearchableItem {
  id: string;
  title: string;
  content: string;
  tags: string[];
  category: string;
  author: string;
  publishedAt: string;
  type: 'article' | 'newsletter' | 'trend';
  slug: string;
  excerpt?: string;
  metadata?: Record<string, any>;
}

export interface SearchOptions {
  keys: Array<{ name: string; weight: number }>;
  threshold: number;
  includeScore: boolean;
  includeMatches: boolean;
  minMatchCharLength: number;
  shouldSort: boolean;
  sortFn?: FuseSortFunction;
}

export interface SearchResult {
  item: SearchableItem;
  score?: number;
  matches?: readonly FuseResultMatch[];
  refIndex: number;
}

export interface SearchFilters {
  category?: string;
  type?: string;
  author?: string;
  dateRange?: {
    start: Date;
    end: Date;
  };
  tags?: string[];
}

export class SearchEngine {
  private fuse: Fuse<SearchableItem>;
  private items: SearchableItem[] = [];
  private options: SearchOptions;

  constructor(items: SearchableItem[] = [], options: Partial<SearchOptions> = {}) {
    this.items = items;
    
    this.options = {
      keys: [
        { name: 'title', weight: 0.3 },
        { name: 'content', weight: 0.2 },
        { name: 'excerpt', weight: 0.2 },
        { name: 'tags', weight: 0.15 },
        { name: 'category', weight: 0.1 },
        { name: 'author', weight: 0.05 },
      ],
      threshold: 0.3,
      includeScore: true,
      includeMatches: true,
      minMatchCharLength: 2,
      shouldSort: true,
      ...options,
    };

    this.fuse = new Fuse(this.items, this.options);
  }

  // Add items to search index
  addItems(items: SearchableItem[]): void {
    this.items = [...this.items, ...items];
    this.fuse = new Fuse(this.items, this.options);
  }

  // Remove items from search index
  removeItems(ids: string[]): void {
    this.items = this.items.filter(item => !ids.includes(item.id));
    this.fuse = new Fuse(this.items, this.options);
  }

  // Update an item in the search index
  updateItem(item: SearchableItem): void {
    const index = this.items.findIndex(i => i.id === item.id);
    if (index !== -1) {
      this.items[index] = item;
      this.fuse = new Fuse(this.items, this.options);
    }
  }

  // Search with query and filters
  search(
    query: string,
    filters: SearchFilters = {},
    limit: number = 20
  ): SearchResult[] {
    if (!query.trim()) {
      return this.getFilteredItems(filters, limit);
    }

    const results = this.fuse.search(query);
    let filteredResults = results.map(result => result);

    // Apply filters
    if (filters.category) {
      filteredResults = filteredResults.filter(
        result => result.item.category === filters.category
      );
    }

    if (filters.type) {
      filteredResults = filteredResults.filter(
        result => result.item.type === filters.type
      );
    }

    if (filters.author) {
      filteredResults = filteredResults.filter(
        result => result.item.author === filters.author
      );
    }

    if (filters.dateRange) {
      const { start, end } = filters.dateRange;
      filteredResults = filteredResults.filter(result => {
        const itemDate = new Date(result.item.publishedAt);
        return itemDate >= start && itemDate <= end;
      });
    }

    if (filters.tags && filters.tags.length > 0) {
      filteredResults = filteredResults.filter(result =>
        filters.tags!.some(tag => result.item.tags.includes(tag))
      );
    }

    return filteredResults.slice(0, limit);
  }

  // Get filtered items without search query
  private getFilteredItems(filters: SearchFilters, limit: number): SearchResult[] {
    let filteredItems = this.items;

    if (filters.category) {
      filteredItems = filteredItems.filter(item => item.category === filters.category);
    }

    if (filters.type) {
      filteredItems = filteredItems.filter(item => item.type === filters.type);
    }

    if (filters.author) {
      filteredItems = filteredItems.filter(item => item.author === filters.author);
    }

    if (filters.dateRange) {
      const { start, end } = filters.dateRange;
      filteredItems = filteredItems.filter(item => {
        const itemDate = new Date(item.publishedAt);
        return itemDate >= start && itemDate <= end;
      });
    }

    if (filters.tags && filters.tags.length > 0) {
      filteredItems = filteredItems.filter(item =>
        filters.tags!.some(tag => item.tags.includes(tag))
      );
    }

    return filteredItems.slice(0, limit).map((item, index) => ({
      item,
      refIndex: index,
    }));
  }

  // Get search suggestions
  getSuggestions(query: string, limit: number = 5): string[] {
    if (!query.trim()) return [];

    const results = this.fuse.search(query);
    const suggestions = new Set<string>();

    results.forEach(result => {
      if (result.matches) {
        result.matches.forEach(match => {
          if (match.value) {
            suggestions.add(match.value);
          }
        });
      }
    });

    return Array.from(suggestions).slice(0, limit);
  }

  // Get popular search terms
  getPopularTerms(limit: number = 10): string[] {
    // This would typically come from analytics data
    // For now, return common terms from the content
    const termCounts = new Map<string, number>();
    
    this.items.forEach(item => {
      const words = [
        ...item.title.toLowerCase().split(/\s+/),
        ...item.content.toLowerCase().split(/\s+/),
        ...item.tags.map(tag => tag.toLowerCase()),
      ];

      words.forEach(word => {
        if (word.length > 2) {
          termCounts.set(word, (termCounts.get(word) || 0) + 1);
        }
      });
    });

    return Array.from(termCounts.entries())
      .sort(([, a], [, b]) => b - a)
      .slice(0, limit)
      .map(([term]) => term);
  }

  // Get search analytics
  getSearchAnalytics(): {
    totalItems: number;
    categories: Record<string, number>;
    types: Record<string, number>;
    authors: Record<string, number>;
  } {
    const categories: Record<string, number> = {};
    const types: Record<string, number> = {};
    const authors: Record<string, number> = {};

    this.items.forEach(item => {
      categories[item.category] = (categories[item.category] || 0) + 1;
      types[item.type] = (types[item.type] || 0) + 1;
      authors[item.author] = (authors[item.author] || 0) + 1;
    });

    return {
      totalItems: this.items.length,
      categories,
      types,
      authors,
    };
  }
}

// Search history management
export class SearchHistory {
  private static readonly STORAGE_KEY = 'search_history';
  private static readonly MAX_HISTORY = 20;

  static addSearch(query: string): void {
    if (!query.trim()) return;

    const history = this.getHistory();
    const filteredHistory = history.filter(item => item !== query);
    const newHistory = [query, ...filteredHistory].slice(0, this.MAX_HISTORY);
    
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(newHistory));
  }

  static getHistory(): string[] {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  }

  static clearHistory(): void {
    localStorage.removeItem(this.STORAGE_KEY);
  }

  static removeSearch(query: string): void {
    const history = this.getHistory();
    const filteredHistory = history.filter(item => item !== query);
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(filteredHistory));
  }
}

// Search filters utilities
export class SearchFilters {
  static createFromURL(searchParams: URLSearchParams): SearchFilters {
    const filters: SearchFilters = {};

    const category = searchParams.get('category');
    if (category) filters.category = category;

    const type = searchParams.get('type');
    if (type) filters.type = type;

    const author = searchParams.get('author');
    if (author) filters.author = author;

    const tags = searchParams.get('tags');
    if (tags) filters.tags = tags.split(',');

    const startDate = searchParams.get('startDate');
    const endDate = searchParams.get('endDate');
    if (startDate && endDate) {
      filters.dateRange = {
        start: new Date(startDate),
        end: new Date(endDate),
      };
    }

    return filters;
  }

  static toURL(filters: SearchFilters): URLSearchParams {
    const params = new URLSearchParams();

    if (filters.category) params.set('category', filters.category);
    if (filters.type) params.set('type', filters.type);
    if (filters.author) params.set('author', filters.author);
    if (filters.tags) params.set('tags', filters.tags.join(','));
    if (filters.dateRange) {
      params.set('startDate', filters.dateRange.start.toISOString());
      params.set('endDate', filters.dateRange.end.toISOString());
    }

    return params;
  }

  static isEmpty(filters: SearchFilters): boolean {
    return !(
      filters.category ||
      filters.type ||
      filters.author ||
      filters.tags?.length ||
      filters.dateRange
    );
  }
}

// Search result ranking
export class SearchRanking {
  static rankResults(
    results: SearchResult[],
    userPreferences: {
      preferredCategories?: string[];
      preferredAuthors?: string[];
      recentSearches?: string[];
    } = {}
  ): SearchResult[] {
    return results.map(result => {
      let boost = 0;

      // Category preference boost
      if (userPreferences.preferredCategories?.includes(result.item.category)) {
        boost += 0.1;
      }

      // Author preference boost
      if (userPreferences.preferredAuthors?.includes(result.item.author)) {
        boost += 0.05;
      }

      // Recent search boost
      if (userPreferences.recentSearches?.some(search => 
        result.item.title.toLowerCase().includes(search.toLowerCase()) ||
        result.item.content.toLowerCase().includes(search.toLowerCase())
      )) {
        boost += 0.05;
      }

      // Recency boost (newer content gets slight boost)
      const daysSincePublished = (Date.now() - new Date(result.item.publishedAt).getTime()) / (1000 * 60 * 60 * 24);
      if (daysSincePublished < 7) boost += 0.02;
      else if (daysSincePublished < 30) boost += 0.01;

      return {
        ...result,
        score: (result.score || 0) + boost,
      };
    }).sort((a, b) => (b.score || 0) - (a.score || 0));
  }
}
