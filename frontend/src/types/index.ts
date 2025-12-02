// ============================================
// メタ広告審査チェッカー - 型定義
// バックエンドと完全同期を保つ単一真実源
// ============================================

// --------------------------------------------
// API Request Types
// --------------------------------------------

export interface AdCheckRequest {
  headline?: string;
  description?: string;
  cta?: string;
  image?: File | string; // File (フロント) or base64 string (バックエンド)
  image_url?: string; // 画像URL
  page_url?: string; // LP URL（OGP自動抽出用）
}

// --------------------------------------------
// API Response Types
// --------------------------------------------

export type AdStatus = 'approved' | 'needs_review' | 'rejected';

export type ViolationSeverity = 'high' | 'medium' | 'low';

export type ViolationCategory =
  | 'text_overlay'
  | 'prohibited_content'
  | 'nsfw'
  | 'before_after'
  | 'misleading';

export interface Violation {
  category: ViolationCategory;
  severity: ViolationSeverity;
  description: string;
  location: 'text' | 'image' | 'both';
}

export interface Recommendation {
  before: string;
  after: string;
  reason: string;
}

export interface AdCheckResponse {
  // 基本情報
  overall_score: number; // 0-100
  status: AdStatus;
  confidence: number; // 0.0-1.0

  // 問題箇所
  violations: Violation[];

  // 改善提案
  recommendations: Recommendation[];

  // 詳細情報
  text_overlay_percentage?: number; // 0-100 (画像がある場合)
  nsfw_detected: boolean;
  prohibited_content: string[];

  // メタ情報
  checked_at: string; // ISO 8601 format
  api_used: string;
}

// --------------------------------------------
// Error Response Types
// --------------------------------------------

export interface ApiError {
  error: string;
  message: string;
  details?: Record<string, unknown>;
}

// --------------------------------------------
// Health Check Types
// --------------------------------------------

export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy';
  timestamp: string;
}

// --------------------------------------------
// Guide Content Types (P-002)
// --------------------------------------------

export interface StepItem {
  number: number;
  title: string;
  description: string;
}

export interface FaqItem {
  question: string;
  answer: string;
}

export interface GuideSection {
  section_title: string;
  content: string;
  items?: string[]; // For list items (ul/li)
}

export interface GuideContent {
  title: string;
  subtitle: string;
  sections: GuideSection[];
  steps: StepItem[];
  faqs: FaqItem[];
  external_links: {
    meta_policy_url: string;
    meta_help_center_url: string;
  };
}

// --------------------------------------------
// UI State Types (Component-specific)
// --------------------------------------------

export interface AdFormData {
  headline: string;
  description: string;
  cta: string;
  imageFile: File | null;
  pageUrl: string; // LP/広告URL審査用
}

export interface CheckState {
  isLoading: boolean;
  hasResult: boolean;
  error: string | null;
}

export interface ImagePreview {
  file: File;
  previewUrl: string;
}
