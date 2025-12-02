"""
============================================
メタ広告審査チェッカー - 型定義
バックエンドとフロントエンドの完全同期を保つ単一真実源
============================================

注意: この型定義は frontend/src/types/index.ts と完全に同期する必要があります。
変更時は必ず両方を同時に更新してください。
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator
from enum import Enum


# --------------------------------------------
# Enum Types
# --------------------------------------------

class AdStatus(str, Enum):
    """広告ステータス"""
    APPROVED = "approved"
    NEEDS_REVIEW = "needs_review"
    REJECTED = "rejected"


class ViolationSeverity(str, Enum):
    """違反の重要度"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ViolationCategory(str, Enum):
    """違反カテゴリ"""
    TEXT_OVERLAY = "text_overlay"
    PROHIBITED_CONTENT = "prohibited_content"
    NSFW = "nsfw"
    BEFORE_AFTER = "before_after"
    MISLEADING = "misleading"


class ViolationLocation(str, Enum):
    """問題箇所"""
    TEXT = "text"
    IMAGE = "image"
    BOTH = "both"


# --------------------------------------------
# API Request Types
# --------------------------------------------

class AdCheckRequest(BaseModel):
    """広告審査リクエスト"""
    headline: Optional[str] = Field(None, max_length=255, description="見出し（最大255文字）")
    description: Optional[str] = Field(None, max_length=2000, description="説明文（最大2000文字）")
    cta: Optional[str] = Field(None, max_length=30, description="CTA（最大30文字）")
    image: Optional[str] = Field(None, description="画像（Base64エンコード文字列）")
    image_url: Optional[str] = Field(None, description="画像URL（オプション）")
    page_url: Optional[str] = Field(None, description="ランディングページURL（オプション）")

    @field_validator('headline', 'description', 'cta')
    @classmethod
    def validate_text_fields(cls, v: Optional[str]) -> Optional[str]:
        """テキストフィールドのバリデーション"""
        if v is not None and v.strip() == "":
            return None
        return v

    def has_content(self) -> bool:
        """コンテンツが存在するかチェック"""
        return any([
            self.headline and self.headline.strip(),
            self.description and self.description.strip(),
            self.cta and self.cta.strip(),
            self.image,
            self.image_url,
            self.page_url,
        ])


# --------------------------------------------
# API Response Types
# --------------------------------------------

class Violation(BaseModel):
    """違反項目"""
    category: ViolationCategory
    severity: ViolationSeverity
    description: str = Field(..., description="具体的な問題点")
    location: ViolationLocation


class RecommendationPriority(str, Enum):
    """改善提案の優先度"""
    MUST = "must"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"


class RecommendationActionType(str, Enum):
    """改善アクションの種類"""
    REPLACE = "replace"
    REMOVE = "remove"
    REDUCE = "reduce"
    REPHRASE = "rephrase"
    RELOCATE = "relocate"


class RecommendationTarget(str, Enum):
    """改善対象"""
    TEXT = "text"
    IMAGE = "image"


class Recommendation(BaseModel):
    """改善提案（強化版）"""
    # 対象情報
    target: RecommendationTarget = Field(..., description="修正対象（text/image）")
    target_field: Optional[str] = Field(None, description="具体的フィールド（headline/description/cta）")
    related_violation_category: Optional[str] = Field(None, description="関連する違反カテゴリ")

    # アクションと優先度
    action_type: RecommendationActionType = Field(..., description="アクションタイプ")
    priority: RecommendationPriority = Field(..., description="優先度（must/recommended/optional）")
    estimated_score_impact: int = Field(..., ge=0, le=100, description="予想スコア改善（0-100）")

    # 改善内容
    title: str = Field(..., description="改善タイトル")
    before: str = Field(..., description="修正前")
    suggestions: list[str] = Field(default_factory=list, description="修正候補（複数）")
    reason: str = Field(..., description="理由")

    # 後方互換性のためafterプロパティを追加
    @property
    def after(self) -> str:
        """後方互換性: suggestionsの最初の要素を返す"""
        return self.suggestions[0] if self.suggestions else ""


class ImageImprovementTextOverlay(BaseModel):
    """画像内テキスト改善情報"""
    current_percentage: float = Field(..., ge=0, le=100, description="現在のテキスト量（%）")
    target_percentage: float = Field(default=15.0, ge=0, le=100, description="目標テキスト量（%）")
    problematic_areas: list[str] = Field(default_factory=list, description="問題箇所リスト")
    removal_suggestions: list[str] = Field(default_factory=list, description="削除・移動の提案")


class ImageImprovementContentIssue(BaseModel):
    """画像コンテンツ問題"""
    issue: str = Field(..., description="問題の概要")
    location: str = Field(..., description="問題箇所")
    alternatives: list[str] = Field(default_factory=list, description="代替案")


class ImageImprovement(BaseModel):
    """画像改善ガイド"""
    text_overlay: Optional[ImageImprovementTextOverlay] = Field(None, description="テキストオーバーレイ改善")
    content_issues: list[ImageImprovementContentIssue] = Field(default_factory=list, description="コンテンツ問題リスト")


class AdCheckResponse(BaseModel):
    """広告審査レスポンス"""
    # 基本情報
    overall_score: int = Field(..., ge=0, le=100, description="総合スコア（0-100）")
    status: AdStatus
    confidence: float = Field(..., ge=0.0, le=1.0, description="信頼度（0.0-1.0）")

    # 問題箇所
    violations: list[Violation] = Field(default_factory=list)

    # 改善提案
    recommendations: list[Recommendation] = Field(default_factory=list)

    # 詳細情報
    text_overlay_percentage: Optional[float] = Field(None, ge=0, le=100, description="画像内テキスト量（0-100）")
    nsfw_detected: bool = Field(default=False)
    prohibited_content: list[str] = Field(default_factory=list)

    # 画像改善ガイド（新規追加）
    image_improvement: Optional[ImageImprovement] = Field(None, description="画像改善ガイド")

    # メタ情報
    checked_at: str = Field(..., description="チェック日時（ISO 8601形式）")
    api_used: str = Field(..., description="使用したAI API")

    @classmethod
    def create_with_timestamp(
        cls,
        overall_score: int,
        status: AdStatus,
        confidence: float,
        violations: list[Violation],
        recommendations: list[Recommendation],
        text_overlay_percentage: Optional[float],
        nsfw_detected: bool,
        prohibited_content: list[str],
        api_used: str,
        image_improvement: Optional[ImageImprovement] = None,
    ) -> "AdCheckResponse":
        """タイムスタンプ付きでレスポンスを作成"""
        return cls(
            overall_score=overall_score,
            status=status,
            confidence=confidence,
            violations=violations,
            recommendations=recommendations,
            text_overlay_percentage=text_overlay_percentage,
            nsfw_detected=nsfw_detected,
            prohibited_content=prohibited_content,
            image_improvement=image_improvement,
            checked_at=datetime.utcnow().isoformat() + "Z",
            api_used=api_used,
        )


# --------------------------------------------
# Error Response Types
# --------------------------------------------

class ApiError(BaseModel):
    """APIエラーレスポンス"""
    error: str = Field(..., description="エラータイプ")
    message: str = Field(..., description="エラーメッセージ")
    details: Optional[dict] = Field(None, description="詳細情報")


# --------------------------------------------
# Health Check Types
# --------------------------------------------

class HealthStatus(str, Enum):
    """ヘルスステータス"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"


class HealthCheckResponse(BaseModel):
    """ヘルスチェックレスポンス"""
    status: HealthStatus
    timestamp: str = Field(..., description="タイムスタンプ（ISO 8601形式）")

    @classmethod
    def create_healthy(cls) -> "HealthCheckResponse":
        """正常なヘルスチェックレスポンスを作成"""
        return cls(
            status=HealthStatus.HEALTHY,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )

    @classmethod
    def create_unhealthy(cls) -> "HealthCheckResponse":
        """異常なヘルスチェックレスポンスを作成"""
        return cls(
            status=HealthStatus.UNHEALTHY,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
