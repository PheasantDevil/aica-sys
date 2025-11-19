"""
Content Quality Service for AICA-SyS
Phase 9-1: Content quality improvement
"""

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ContentQualityService:
    """コンテンツ品質評価サービス"""

    def __init__(self):
        self.min_word_count = 300
        self.max_word_count = 3000
        self.min_quality_score = 65  # 70から65に調整（新しい評価基準を考慮）
        # 評価基準の閾値
        self.min_code_examples = 2  # 最低コード例数
        self.min_links = 2  # 最低リンク数
        self.optimal_sentence_length = 20  # 最適な文の長さ（単語数）
        self.max_sentence_length = 30  # 最大文の長さ

    def evaluate_content(self, content: str, title: str) -> Dict[str, Any]:
        """コンテンツの品質を評価（改善版：新しい評価基準を追加）"""

        # 各評価項目のスコア計算
        readability_score = self._evaluate_readability(content)
        structure_score = self._evaluate_structure(content)
        length_score = self._evaluate_length(content)
        title_score = self._evaluate_title(title)
        technical_accuracy_score = self._evaluate_technical_accuracy(content)
        practicality_score = self._evaluate_practicality(content)
        uniqueness_score = self._evaluate_uniqueness(content)

        # 総合スコア（加重平均 - 新しい評価基準を反映）
        total_score = (
            readability_score * 0.20  # 読みやすさ
            + structure_score * 0.15  # 構造
            + length_score * 0.10  # 長さ
            + title_score * 0.10  # タイトル
            + technical_accuracy_score * 0.20  # 技術的正確性（新規）
            + practicality_score * 0.15  # 実用性（新規）
            + uniqueness_score * 0.10  # 独自性（新規）
        )

        # 品質評価
        quality_level = self._get_quality_level(total_score)

        # 改善提案
        suggestions = self._generate_suggestions(
            readability_score,
            structure_score,
            length_score,
            title_score,
            technical_accuracy_score,
            practicality_score,
            uniqueness_score,
        )

        return {
            "total_score": round(total_score, 2),
            "quality_level": quality_level,
            "scores": {
                "readability": round(readability_score, 2),
                "structure": round(structure_score, 2),
                "length": round(length_score, 2),
                "title": round(title_score, 2),
                "technical_accuracy": round(technical_accuracy_score, 2),
                "practicality": round(practicality_score, 2),
                "uniqueness": round(uniqueness_score, 2),
            },
            "suggestions": suggestions,
            "word_count": len(content.split()),
            "evaluated_at": datetime.utcnow().isoformat(),
        }

    def _evaluate_readability(self, content: str) -> float:
        """読みやすさを評価（0-100）- 改善版"""
        # 文の長さ
        sentences = [s.strip() for s in content.split("。") if s.strip()]
        if not sentences:
            return 0

        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)

        # 段落数
        paragraphs = [p for p in content.split("\n\n") if p.strip()]
        paragraph_count = len(paragraphs)

        # 視覚的区切りの使用（水平線、引用ブロック）
        has_hr = bool(re.search(r"^---|^\*\*\*|^___", content, re.MULTILINE))
        has_quote = bool(re.search(r"^>", content, re.MULTILINE))

        # リストの使用
        list_items = len(re.findall(r"^[\-\*\+]\s+", content, re.MULTILINE))
        has_numbered_list = bool(re.search(r"^\d+\.\s+", content, re.MULTILINE))

        # スコア計算
        score = 100

        # 文の長さ評価（最適範囲を重視）
        if avg_sentence_length > self.max_sentence_length:
            score -= 25
        elif avg_sentence_length < 10:
            score -= 15
        elif abs(avg_sentence_length - self.optimal_sentence_length) > 10:
            score -= 10

        # 段落の適切な分割（3-5文程度の段落が理想）
        if paragraph_count < 3:
            score -= 20
        elif paragraph_count > 15:
            score -= 10

        # 視覚的区切りの使用（加点）
        if has_hr:
            score += 5
        if has_quote:
            score += 5

        # リストの効果的な使用
        if list_items >= 5:
            score += 10
        elif list_items >= 3:
            score += 5
        if has_numbered_list:
            score += 5

        return min(100, max(0, score))

    def _evaluate_structure(self, content: str) -> float:
        """構造を評価（0-100）"""
        score = 100

        # 見出しの存在
        has_headings = bool(re.search(r"#+\s+.+", content))
        if not has_headings:
            score -= 20

        # リストの存在
        has_lists = bool(re.search(r"[\-\*]\s+.+", content))
        if not has_lists:
            score -= 10

        # コードブロックの存在
        has_code = bool(re.search(r"```[\s\S]+?```", content))
        if not has_code:
            score -= 10

        # 段落分け
        paragraphs = [p for p in content.split("\n\n") if p.strip()]
        if len(paragraphs) < 3:
            score -= 15

        return max(0, score)

    def _evaluate_length(self, content: str) -> float:
        """長さを評価（0-100）"""
        word_count = len(content.split())

        if word_count < self.min_word_count:
            # 短すぎる
            return (word_count / self.min_word_count) * 100
        elif word_count > self.max_word_count:
            # 長すぎる
            return max(0, 100 - ((word_count - self.max_word_count) / 100))
        else:
            # 適切な長さ
            return 100

    def _evaluate_title(self, title: str) -> float:
        """タイトルを評価（0-100）"""
        score = 100

        # タイトルの長さ
        title_length = len(title)
        if title_length < 10:
            score -= 30
        elif title_length > 100:
            score -= 20

        # キーワードの存在
        keywords = [
            "TypeScript",
            "Next.js",
            "React",
            "フレームワーク",
            "ライブラリ",
            "開発",
        ]
        has_keyword = any(keyword in title for keyword in keywords)
        if not has_keyword:
            score -= 15

        return max(0, score)

    def _evaluate_technical_accuracy(self, content: str) -> float:
        """技術的正確性を評価（0-100）- 新規評価基準"""
        score = 100

        # バージョン情報の明記（TypeScript 5.x, Next.js 14.x等）
        version_patterns = [
            r"TypeScript\s+[\d.]+",
            r"Next\.js\s+[\d.]+",
            r"React\s+[\d.]+",
            r"Node\.js\s+[\d.]+",
            r"v[\d.]+",
        ]
        has_version = any(
            re.search(pattern, content, re.IGNORECASE) for pattern in version_patterns
        )
        if not has_version:
            score -= 15

        # 公式ドキュメントへの参照
        official_docs = [
            "typescriptlang.org",
            "nextjs.org",
            "react.dev",
            "nodejs.org",
            "developer.mozilla.org",
        ]
        has_official_ref = any(doc in content.lower() for doc in official_docs)
        if not has_official_ref:
            score -= 10

        # 非推奨機能の回避（deprecated, 非推奨などのキーワードがないことを確認）
        deprecated_keywords = ["deprecated", "非推奨", "廃止", "obsolete"]
        has_deprecated = any(
            keyword in content.lower() for keyword in deprecated_keywords
        )
        if has_deprecated:
            # 非推奨機能について言及している場合は、代替案が提示されているか確認
            alternative_keywords = [
                "代わりに",
                "代替",
                "alternative",
                "推奨",
                "recommended",
            ]
            has_alternative = any(
                keyword in content.lower() for keyword in alternative_keywords
            )
            if not has_alternative:
                score -= 20

        # コードブロックの言語指定（typescript, javascript等）
        code_blocks = re.findall(r"```(\w+)?[\s\S]+?```", content)
        has_language_spec = any(block[0] for block in code_blocks if block)
        if code_blocks and not has_language_spec:
            score -= 10

        # 技術用語の正確な使用
        tech_terms = [
            "TypeScript",
            "JavaScript",
            "React",
            "Next.js",
            "API",
            "Type",
            "Interface",
        ]
        term_count = sum(1 for term in tech_terms if term in content)
        if term_count < 3:
            score -= 15

        return max(0, score)

    def _evaluate_practicality(self, content: str) -> float:
        """実用性を評価（0-100）- 新規評価基準"""
        score = 100

        # コード例の数と質
        code_blocks = re.findall(r"```[\s\S]+?```", content)
        code_count = len(code_blocks)
        if code_count < self.min_code_examples:
            score -= 30
        elif code_count < 3:
            score -= 15
        else:
            score += 10  # 3つ以上のコード例がある場合は加点

        # 実装手順の明確さ（番号付きリスト、ステップ形式）
        step_patterns = [
            r"ステップ\s*\d+",
            r"手順\s*\d+",
            r"Step\s*\d+",
            r"^\d+\.\s+.*実装|実装.*\d+\.\s+",
        ]
        has_steps = any(
            re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
            for pattern in step_patterns
        )
        if not has_steps:
            score -= 15

        # エラー解決方法の記載
        error_keywords = [
            "エラー",
            "error",
            "問題",
            "issue",
            "解決",
            "solution",
            "トラブルシューティング",
        ]
        has_error_solution = any(
            keyword in content.lower() for keyword in error_keywords
        )
        if not has_error_solution:
            score -= 10

        # ベストプラクティスの提示
        best_practice_keywords = [
            "ベストプラクティス",
            "best practice",
            "推奨",
            "recommended",
            "最適化",
            "optimization",
        ]
        has_best_practices = any(
            keyword in content.lower() for keyword in best_practice_keywords
        )
        if not has_best_practices:
            score -= 10

        # アクションアイテムの明示（「試してみる」「実装する」等）
        action_keywords = [
            "試す",
            "実装",
            "実行",
            "try",
            "implement",
            "実行してみる",
        ]
        has_actions = any(keyword in content.lower() for keyword in action_keywords)
        if not has_actions:
            score -= 10

        return max(0, score)

    def _evaluate_uniqueness(self, content: str) -> float:
        """独自性を評価（0-100）- 新規評価基準"""
        score = 100

        # 独自の視点やアプローチの提示
        unique_indicators = [
            "独自",
            "オリジナル",
            "カスタム",
            "独自の",
            "original",
            "custom",
            "独自の視点",
            "新しいアプローチ",
        ]
        has_unique_perspective = any(
            indicator in content.lower() for indicator in unique_indicators
        )
        if not has_unique_perspective:
            score -= 15

        # 実体験やケーススタディの記載
        experience_keywords = [
            "実際に",
            "実務で",
            "経験",
            "ケース",
            "case study",
            "実例",
            "実際の",
        ]
        has_experience = any(
            keyword in content.lower() for keyword in experience_keywords
        )
        if not has_experience:
            score -= 10

        # 比較分析（他の方法との比較）
        comparison_keywords = [
            "比較",
            "対比",
            "違い",
            "比較して",
            "compare",
            "versus",
            "vs",
        ]
        has_comparison = any(
            keyword in content.lower() for keyword in comparison_keywords
        )
        if has_comparison:
            score += 10  # 比較がある場合は加点

        # 独自のツールやライブラリの紹介
        tool_keywords = [
            "ツール",
            "ライブラリ",
            "パッケージ",
            "tool",
            "library",
            "package",
        ]
        has_tools = any(keyword in content.lower() for keyword in tool_keywords)
        if has_tools:
            score += 5

        # 一般的すぎる内容の検出（減点）
        generic_phrases = [
            "一般的に",
            "よく知られている",
            "誰でも知っている",
            "基本的な",
        ]
        generic_count = sum(
            1 for phrase in generic_phrases if phrase in content.lower()
        )
        if generic_count > 3:
            score -= 20

        return max(0, score)

    def _get_quality_level(self, score: float) -> str:
        """スコアから品質レベルを取得（改善版：閾値を調整）"""
        if score >= 85:  # 90から85に調整（新しい評価基準を考慮）
            return "excellent"
        elif score >= 75:  # 80から75に調整
            return "good"
        elif score >= 65:  # 70から65に調整
            return "fair"
        else:
            return "needs_improvement"

    def _generate_suggestions(
        self,
        readability: float,
        structure: float,
        length: float,
        title: float,
        technical_accuracy: float,
        practicality: float,
        uniqueness: float,
    ) -> List[str]:
        """改善提案を生成（改善版：新しい評価基準に対応）"""
        suggestions = []

        if readability < 70:
            suggestions.append(
                "文章をもっと短く、読みやすくしましょう（1文20語程度が理想）"
            )
            suggestions.append(
                "段落を適切に分割し、視覚的な区切り（水平線、引用ブロック）を活用しましょう"
            )
            suggestions.append("箇条書きや番号付きリストを効果的に使用しましょう")

        if structure < 70:
            suggestions.append("見出し（H2, H3）を追加して構造を明確にしましょう")
            suggestions.append("リストやコードブロックを活用しましょう")

        if length < 70:
            suggestions.append(
                f"コンテンツの長さを調整しましょう（{self.min_word_count}-{self.max_word_count}語推奨）"
            )

        if title < 70:
            suggestions.append(
                "タイトルをより具体的で魅力的にしましょう（60文字以内、キーワードを含む）"
            )
            suggestions.append("SEO最適化されたキーワードをタイトルに含めましょう")

        if technical_accuracy < 70:
            suggestions.append(
                "バージョン情報（TypeScript 5.x, Next.js 14.x等）を明記しましょう"
            )
            suggestions.append("公式ドキュメントへの参照リンクを追加しましょう")
            suggestions.append(
                "コードブロックに言語指定（typescript, javascript等）を追加しましょう"
            )
            suggestions.append("非推奨機能を使用する場合は、代替案を提示しましょう")

        if practicality < 70:
            suggestions.append(
                f"コード例を最低{self.min_code_examples}個以上追加しましょう"
            )
            suggestions.append("実装手順を段階的に説明しましょう（ステップ形式）")
            suggestions.append("よくあるエラーとその解決方法を記載しましょう")
            suggestions.append(
                "ベストプラクティスやパフォーマンス最適化のヒントを含めましょう"
            )
            suggestions.append("読者が実際に試せるアクションアイテムを明示しましょう")

        if uniqueness < 70:
            suggestions.append("独自の視点やアプローチを提示しましょう")
            suggestions.append("実体験やケーススタディを追加しましょう")
            suggestions.append("他の方法との比較分析を含めましょう")
            suggestions.append("一般的すぎる表現を避け、具体的な内容にしましょう")

        return suggestions


# グローバルインスタンス
content_quality_service = ContentQualityService()


def evaluate_content_quality(content: str, title: str) -> Dict[str, Any]:
    """コンテンツ品質を評価する便利関数"""
    return content_quality_service.evaluate_content(content, title)
