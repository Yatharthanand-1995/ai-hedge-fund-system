export interface FilterOptions {
  sector: string[];
  scoreRange: string;
  riskLevel: string[];
  consensus: string[];
  priceRange: string;
  searchQuery: string;
}

export type SortOption = 'score-desc' | 'score-asc' | 'price-desc' | 'price-asc' | 'momentum-desc' | 'alpha-asc' | 'alpha-desc';
