export interface Link {
  short_code: string;
  short_url: string;
  original_url: string;
  is_custom_alias: boolean;
  created_at: string;
  expires_at: string | null;
  is_active: boolean;
  is_expired: boolean;
  click_count: number;
  last_clicked_at: string | null;
}

export interface LinkListResponse {
  items: Link[];
  total: number;
  page: number;
  page_size: number;
}

export interface ClickBucket {
  day: string;
  clicks: number;
}

export interface LinkAnalytics {
  short_code: string;
  total_clicks: number;
  clicks_by_day: ClickBucket[];
}

export interface CreateLinkInput {
  original_url: string;
  custom_alias?: string;
  expires_at?: string;
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    details: Record<string, unknown>;
    request_id: string;
  };
}
