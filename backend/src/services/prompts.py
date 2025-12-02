"""
============================================
メタ広告審査チェッカー - プロンプトテンプレート
============================================

Meta広告審査基準に基づいたAIプロンプトを構築
"""

from typing import Optional


# --------------------------------------------
# Meta広告審査基準（2025年1月時点）
# --------------------------------------------

META_AD_POLICY = """
# Meta広告審査基準（2025年1月時点）

## 1. 画像内テキスト量（Text Overlay）
- 推奨: 画像内テキストは15%以下が最適
- ガイドライン: 20%以下を強く推奨
- 20%超過: リーチが制限される可能性が高い
- 30%超過: 審査落ちの可能性が非常に高い

## 2. 禁止・制限コンテンツ
以下は特別な許可なく広告不可:
- アルコール（年齢制限あり）
- タバコ、電子タバコ
- 医薬品（処方薬）
- 違法薬物
- 危険なサプリメント
- 武器、弾薬、爆発物
- ギャンブル（年齢制限あり）
- アダルトコンテンツ

## 3. 不適切なコンテンツ（NSFW）
- 過度な肌露出
- 性的示唆が強い表現
- 暴力的な描写
- ショッキングな画像

## 4. ビフォーアフター表現
以下の分野では禁止:
- ダイエット・減量
- 美容整形
- 筋肉増強
- 健康改善

## 5. 誇大広告・誤解を招く表現
- 「100%保証」などの断定表現
- 「業界最安値」「世界一」などの絶対表現（根拠がない場合）
- 「すぐに結果が出る」などの誇張
- 個人の体験談を一般化
- 非現実的な収益保証

## 6. その他のポリシー違反
- 個人情報の不正利用を示唆
- 差別的な表現
- 虚偽または誤解を招く主張
- ターゲティングの悪用を示唆
"""


# --------------------------------------------
# プロンプト構築関数
# --------------------------------------------

def build_meta_ad_review_prompt(
    headline: Optional[str] = None,
    description: Optional[str] = None,
    cta: Optional[str] = None,
    has_image: bool = False,
    page_url: Optional[str] = None,
    page_title: Optional[str] = None,
    page_description: Optional[str] = None,
    page_text: Optional[str] = None,
) -> str:
    """
    Meta広告審査用のプロンプトを構築

    Args:
        headline: 見出し
        description: 説明文
        cta: CTA（Call To Action）
        has_image: 画像が含まれているか
        page_url: ランディングページURL
        page_title: ページタイトル（OGP/title）
        page_description: ページ説明（OGP/meta description）
        page_text: ページ本文テキスト

    Returns:
        str: 構築されたプロンプト
    """
    # 広告テキストの組み立て
    ad_text_parts = []
    if headline:
        ad_text_parts.append(f"【見出し】\n{headline}")
    if description:
        ad_text_parts.append(f"【説明文】\n{description}")
    if cta:
        ad_text_parts.append(f"【CTA】\n{cta}")

    # URL審査の場合、ページ情報を追加
    if page_url:
        ad_text_parts.append(f"【ランディングページURL】\n{page_url}")
        if page_title:
            ad_text_parts.append(f"【ページタイトル】\n{page_title}")
        if page_description:
            ad_text_parts.append(f"【ページ説明】\n{page_description}")
        if page_text:
            # ページテキストは長いので要約部分のみ
            truncated_text = page_text[:1500] + "..." if len(page_text) > 1500 else page_text
            ad_text_parts.append(f"【ページ本文（抜粋）】\n{truncated_text}")

    ad_text = "\n\n".join(ad_text_parts) if ad_text_parts else "（テキストなし）"

    # 画像の有無
    if page_url and has_image:
        image_note = "※ OGP画像（ランディングページのシェア画像）が添付されています。画像内のテキスト量、不適切なコンテンツを重点的にチェックしてください。"
    elif has_image:
        image_note = "※ 画像が添付されています。画像内のテキスト量、不適切なコンテンツを重点的にチェックしてください。"
    else:
        image_note = "※ 画像はありません。"

    # プロンプト構築
    prompt = f"""あなたはMeta（Facebook/Instagram）広告の審査エキスパートです。
以下の広告が、Metaの広告ポリシーに準拠しているかを厳格に審査し、JSON形式で結果を返してください。

{META_AD_POLICY}

---

## 審査対象の広告

{ad_text}

{image_note}

---

## 指示

1. **画像内テキスト量の推定**（画像がある場合のみ）:
   - 画像全体に対するテキストの占有率を0-100%で推定
   - 15%以下: 最適
   - 20%以下: 許容範囲
   - 20-30%: 警告（リーチ制限の可能性）
   - 30%超過: 高リスク（審査落ちの可能性大）

2. **禁止コンテンツのチェック**:
   - テキストおよび画像から、禁止・制限カテゴリに該当する要素を検出
   - 医薬品的効能、アルコール、タバコ、ギャンブル等

3. **NSFW（不適切コンテンツ）の検出**:
   - 過度な肌露出、性的表現、暴力的描写の有無

4. **ビフォーアフター表現のチェック**:
   - ダイエット、美容、筋肉増強分野での使用前後比較の有無

5. **誇大広告・誤解を招く表現のチェック**:
   - 断定表現、絶対表現、非現実的な保証の有無

6. **総合判定**:
   - **overall_score**: 0-100点のスコア（100点が最高）
     * 90-100: 優れた広告（承認の可能性が非常に高い）
     * 70-89: 良好（軽微な改善で承認の可能性が高い）
     * 50-69: 要改善（複数の問題あり、審査落ちの可能性あり）
     * 0-49: 重大な問題（審査落ちの可能性が非常に高い）

   - **status**:
     * "approved": スコア70以上、重大な違反なし
     * "needs_review": スコア50-69、または中程度の違反あり
     * "rejected": スコア49以下、または重大な違反あり（禁止コンテンツ、NSFW等）

   - **confidence**: 0.0-1.0の信頼度
     * 0.9以上: 非常に確信がある
     * 0.7-0.89: 確信がある
     * 0.5-0.69: やや不確実
     * 0.5未満: 不確実（要人間確認）

7. **改善提案**（強化版）:
   - 各違反項目に対して、優先度（must/recommended/optional）を設定
   - 複数の修正候補（suggestions配列）を提示（2-3個）
   - 予想スコア改善値（estimated_score_impact）を算出
   - テキスト改善と画像改善を分けて具体的に提案

8. **画像改善ガイド**（画像がある場合）:
   - テキストオーバーレイの問題箇所を具体的に特定
   - 削除・移動すべき箇所とその方法を提案

---

## 出力形式（必ずこのJSON形式で返してください）

{{
  "overall_score": 45,
  "status": "needs_review",
  "confidence": 0.85,
  "violations": [
    {{
      "category": "misleading",
      "severity": "high",
      "description": "「業界最安値」「100%保証」は根拠なき絶対表現として誇大広告に該当します。",
      "location": "text"
    }},
    {{
      "category": "text_overlay",
      "severity": "medium",
      "description": "画像内のテキスト量が約35%です。Metaは20%以下を推奨しているため、リーチが大幅に制限される可能性があります。",
      "location": "image"
    }}
  ],
  "recommendations": [
    {{
      "target": "text",
      "target_field": "headline",
      "related_violation_category": "misleading",
      "action_type": "replace",
      "priority": "must",
      "estimated_score_impact": 20,
      "title": "見出しの誇大表現を修正",
      "before": "業界最安値で100%保証！今すぐ申し込み",
      "suggestions": [
        "お手頃価格で安心保証付き！今すぐ申し込み",
        "コスパ重視の安心サービス！詳細を見る",
        "納得価格の充実サポート！無料で相談"
      ],
      "reason": "「最安値」「100%」は根拠なき絶対表現としてMetaポリシーに抵触します。具体的な数値や比較データがない限り、誇大広告と判定されます。"
    }},
    {{
      "target": "text",
      "target_field": "description",
      "related_violation_category": "misleading",
      "action_type": "rephrase",
      "priority": "must",
      "estimated_score_impact": 15,
      "title": "説明文の断定表現を緩和",
      "before": "誰でも必ず痩せる！たった3日で-5kg達成",
      "suggestions": [
        "健康的なダイエットをサポート。多くの方に選ばれています",
        "あなたのダイエットを応援。まずは無料カウンセリング"
      ],
      "reason": "「必ず」「たった〇日で」といった断定的な効果保証は、ダイエット分野では特に厳しく審査されます。個人差を考慮した表現に変更してください。"
    }},
    {{
      "target": "image",
      "target_field": null,
      "related_violation_category": "text_overlay",
      "action_type": "reduce",
      "priority": "must",
      "estimated_score_impact": 15,
      "title": "画像内テキストを削減",
      "before": "画像内テキスト量: 35%",
      "suggestions": [
        "テキストを画像から削除し、広告テキスト欄に移動する",
        "ロゴと商品名のみ残し、キャッチコピーは説明文に移動"
      ],
      "reason": "画像内テキストが20%を超えるとリーチが制限されます。15%以下を目標にテキストを削減してください。"
    }}
  ],
  "text_overlay_percentage": 35,
  "nsfw_detected": false,
  "prohibited_content": [],
  "image_improvement": {{
    "text_overlay": {{
      "current_percentage": 35,
      "target_percentage": 15,
      "problematic_areas": [
        "中央の「今だけ50%OFF」バナー（約15%）",
        "下部の長い注意書き（約12%）",
        "左上のキャッチコピー（約8%）"
      ],
      "removal_suggestions": [
        "「50%OFF」は画像から削除し、広告テキスト（説明文）に移動",
        "注意書きはランディングページ内に記載",
        "ロゴと商品名のみ残し、キャッチコピーは説明文に移動",
        "画像は商品/サービスの視覚的魅力に集中させる"
      ]
    }},
    "content_issues": []
  }}
}}

**重要**: 必ずJSON形式のみを返してください。説明文やマークダウンは不要です。
"""

    return prompt
