export interface Asset {
  id: number;
  symbol: string;
  name: string;
  user_id: number;
  created_at: string;
}

export interface Quote {
  symbol: string;
  shortName: string | null;
  regularMarketPrice: number | null;
  regularMarketChangePercent: number | null;
  regularMarketVolume: number | null;
  regularMarketPreviousClose: number | null;
  logourl: string | null;
}

export interface PriceHistoryPoint {
  price: number;
  change_percent: number | null;
  fetched_at: string;
}

export interface Highlight {
  asset_id: number;
  symbol: string;
  name: string;
  change_percent: number;
  price: number;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  email: string;
}
