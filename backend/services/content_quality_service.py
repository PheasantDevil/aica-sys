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
        self.min_quality_score = 70

    def evaluate_content(self, content: str, title: str) -> Dict[str, Any]:
        """コンテンツの品質を評価"""

        # 各評価項目のスコア計算
        readability_score = self._evaluate_readability(content)
        structure_score = self._evaluate_structure(content)
        length_score = self._evaluate_length(content)
        title_score = self._evaluate_title(title)
        technical_score = self._evaluate_technical_content(content)

        # 総合スコア（加重平均）
        total_score = (
            readability_score * 0.3
            + structure_score * 0.2
            + length_score * 0.2
            + title_score * 0.1
            + technical_score * 0.2
        )

        # 品質評価
        quality_level = self._get_quality_level(total_score)

        # 改善提案
        suggestions = self._generate_suggestions(
            readability_score,
            structure_score,
            length_score,
            title_score,
            technical_score,
        )

        return {
            "total_score": round(total_score, 2),
            "quality_level": quality_level,
            "scores": {
                "readability": round(readability_score, 2),
                "structure": round(structure_score, 2),
                "length": round(length_score, 2),
                "title": round(title_score, 2),
                "technical": round(technical_score, 2),
            },
            "suggestions": suggestions,
            "word_count": len(content.split()),
            "evaluated_at": datetime.utcnow().isoformat(),
        }

    def _evaluate_readability(self, content: str) -> float:
        """読みやすさを評価（0-100）"""
        # 文の長さ
        sentences = content.split("。")
        avg_sentence_length = (
            sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        )

        # 段落数
        paragraphs = [p for p in content.split("\n\n") if p.strip()]
        paragraph_count = len(paragraphs)

        # スコア計算
        score = 100

        # 文が長すぎる場合は減点
        if avg_sentence_length > 30:
            score -= 20

        # 段落が少なすぎる場合は減点
        if paragraph_count < 3:
            score -= 15

        return max(0, score)

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

    def _evaluate_technical_content(self, content: str) -> float:
        """技術的内容を評価（0-100）"""
        score = 100

        # コードスニペットの存在
        code_blocks = re.findall(r"```[\s\S]+?```", content)
        if len(code_blocks) < 1:
            score -= 20

        # 技術用語の存在
        tech_terms = [
            "API",
            "TypeScript",
            "JavaScript",
            "React",
            "Next.js",
            "フレームワーク",
            "ライブラリ",
        ]
        term_count = sum(1 for term in tech_terms if term in content)
        if term_count < 3:
            score -= 15

        # URLリンクの存在
        links = re.findall(r"https?://[^\s]+", content)
        if len(links) < 2:
            score -= 10

        return max(0, score)

    def _get_quality_level(self, score: float) -> str:
        """スコアから品質レベルを取得"""
        if score >= 90:
            return "excellent"
        elif score >= 80:
            return "good"
        elif score >= 70:
            return "fair"
        else:
            return "needs_improvement"

    def _generate_suggestions(
        self,
        readability: float,
        structure: float,
        length: float,
        title: float,
        technical: float,
    ) -> List[str]:
        """改善提案を生成"""
        suggestions = []

        if readability < 70:
            suggestions.append("文章をもっと短く、読みやすくしましょう")
            suggestions.append("段落を増やして構造化しましょう")

        if structure < 70:
            suggestions.append("見出しを追加して構造を明確にしましょう")
            suggestions.append("リストやコードブロックを活用しましょう")

        if length < 70:
            suggestions.append("コンテンツの長さを調整しましょう（300-3000語推奨）")

        if title < 70:
            suggestions.append("タイトルをより具体的で魅力的にしましょう")
            suggestions.append("キーワードをタイトルに含めましょう")

        if technical < 70:
            suggestions.append("コードスニペットを追加しましょう")
            suggestions.append("技術用語や参考リンクを増やしましょう")

        return suggestions


# グローバルインスタンス
content_quality_service = ContentQualityService()


def evaluate_content_quality(content: str, title: str) -> Dict[str, Any]:
    """コンテンツ品質を評価する便利関数"""
    return content_quality_service.evaluate_content(content, title)
