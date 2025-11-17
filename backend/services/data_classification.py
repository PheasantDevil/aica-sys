import re
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from utils.logging import get_logger

logger = get_logger(__name__)


class DataSensitivity(Enum):
    """データ機密度レベル"""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    TOP_SECRET = "top_secret"


class DataCategory(Enum):
    """データカテゴリ"""

    PERSONAL_INFO = "personal_info"
    FINANCIAL_INFO = "financial_info"
    TECHNICAL_INFO = "technical_info"
    BUSINESS_INFO = "business_info"
    HEALTH_INFO = "health_info"
    LEGAL_INFO = "legal_info"


class DataClassificationService:
    """
    データ分類・ラベリングサービス
    """

    def __init__(self):
        self.classification_rules = self._initialize_classification_rules()
        self.retention_policies = self._initialize_retention_policies()
        self.masking_rules = self._initialize_masking_rules()

    def _initialize_classification_rules(self) -> Dict[str, Dict]:
        """分類ルールを初期化"""
        return {
            # 個人情報のパターン
            "email": {
                "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                "category": DataCategory.PERSONAL_INFO,
                "sensitivity": DataSensitivity.CONFIDENTIAL,
                "description": "Email address",
            },
            "phone": {
                "pattern": r"(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})",
                "category": DataCategory.PERSONAL_INFO,
                "sensitivity": DataSensitivity.CONFIDENTIAL,
                "description": "Phone number",
            },
            "ssn": {
                "pattern": r"\b\d{3}-?\d{2}-?\d{4}\b",
                "category": DataCategory.PERSONAL_INFO,
                "sensitivity": DataSensitivity.TOP_SECRET,
                "description": "Social Security Number",
            },
            "credit_card": {
                "pattern": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
                "category": DataCategory.FINANCIAL_INFO,
                "sensitivity": DataSensitivity.TOP_SECRET,
                "description": "Credit card number",
            },
            "bank_account": {
                "pattern": r"\b\d{8,17}\b",
                "category": DataCategory.FINANCIAL_INFO,
                "sensitivity": DataSensitivity.TOP_SECRET,
                "description": "Bank account number",
            },
            "api_key": {
                "pattern": r'(?i)(api[_-]?key|secret[_-]?key|access[_-]?token)[\s:=]+["\']?([a-zA-Z0-9_-]{20,})["\']?',
                "category": DataCategory.TECHNICAL_INFO,
                "sensitivity": DataSensitivity.TOP_SECRET,
                "description": "API key or secret",
            },
            "password": {
                "pattern": r'(?i)(password|passwd|pwd)[\s:=]+["\']?([^"\'\s]{6,})["\']?',
                "category": DataCategory.TECHNICAL_INFO,
                "sensitivity": DataSensitivity.TOP_SECRET,
                "description": "Password",
            },
            "ip_address": {
                "pattern": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
                "category": DataCategory.TECHNICAL_INFO,
                "sensitivity": DataSensitivity.INTERNAL,
                "description": "IP address",
            },
            "url": {
                "pattern": r'https?://[^\s<>"{}|\\^`\[\]]+',
                "category": DataCategory.TECHNICAL_INFO,
                "sensitivity": DataSensitivity.PUBLIC,
                "description": "URL",
            },
            "name": {
                "pattern": r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",
                "category": DataCategory.PERSONAL_INFO,
                "sensitivity": DataSensitivity.CONFIDENTIAL,
                "description": "Full name",
            },
        }

    def _initialize_retention_policies(self) -> Dict[str, int]:
        """保持期間ポリシーを初期化（日数）"""
        return {
            DataCategory.PERSONAL_INFO.value: 2555,  # 7年
            DataCategory.FINANCIAL_INFO.value: 2555,  # 7年
            DataCategory.TECHNICAL_INFO.value: 1095,  # 3年
            DataCategory.BUSINESS_INFO.value: 1825,  # 5年
            DataCategory.HEALTH_INFO.value: 2555,  # 7年
            DataCategory.LEGAL_INFO.value: 3650,  # 10年
        }

    def _initialize_masking_rules(self) -> Dict[str, str]:
        """マスキングルールを初期化"""
        return {
            DataCategory.PERSONAL_INFO.value: "partial",
            DataCategory.FINANCIAL_INFO.value: "full",
            DataCategory.TECHNICAL_INFO.value: "partial",
            DataCategory.BUSINESS_INFO.value: "none",
            DataCategory.HEALTH_INFO.value: "full",
            DataCategory.LEGAL_INFO.value: "partial",
        }

    def classify_data(self, data: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        データを分類・ラベリング

        Args:
            data: 分類するデータ
            context: データの文脈（オプション）

        Returns:
            分類結果
        """
        try:
            classification_result = {
                "data": data,
                "context": context,
                "classifications": [],
                "highest_sensitivity": DataSensitivity.PUBLIC.value,
                "categories": set(),
                "retention_days": 0,
                "masking_required": False,
                "classified_at": datetime.utcnow().isoformat(),
            }

            # 各パターンでデータをスキャン
            for rule_name, rule in self.classification_rules.items():
                pattern = rule["pattern"]
                matches = re.finditer(pattern, data, re.IGNORECASE)

                for match in matches:
                    classification = {
                        "rule": rule_name,
                        "category": rule["category"].value,
                        "sensitivity": rule["sensitivity"].value,
                        "description": rule["description"],
                        "match": match.group(),
                        "position": match.span(),
                        "confidence": self._calculate_confidence(
                            match.group(), rule_name
                        ),
                    }

                    classification_result["classifications"].append(classification)
                    classification_result["categories"].add(rule["category"].value)

                    # 最高機密度を更新
                    if self._is_higher_sensitivity(
                        rule["sensitivity"].value,
                        classification_result["highest_sensitivity"],
                    ):
                        classification_result["highest_sensitivity"] = rule[
                            "sensitivity"
                        ].value

            # 保持期間を計算
            classification_result["retention_days"] = self._calculate_retention_period(
                classification_result["categories"]
            )

            # マスキング要件を判定
            classification_result["masking_required"] = self._requires_masking(
                classification_result["categories"]
            )

            # セットをリストに変換
            classification_result["categories"] = list(
                classification_result["categories"]
            )

            logger.info(
                f"Data classified: {len(classification_result['classifications'])} matches found"
            )
            return classification_result

        except Exception as e:
            logger.error(f"Error classifying data: {e}")
            raise

    def _calculate_confidence(self, match: str, rule_name: str) -> float:
        """マッチの信頼度を計算"""
        confidence_scores = {
            "email": 0.95,
            "phone": 0.90,
            "ssn": 0.98,
            "credit_card": 0.85,
            "bank_account": 0.70,
            "api_key": 0.80,
            "password": 0.75,
            "ip_address": 0.95,
            "url": 0.90,
            "name": 0.60,
        }
        return confidence_scores.get(rule_name, 0.50)

    def _is_higher_sensitivity(self, sensitivity1: str, sensitivity2: str) -> bool:
        """機密度レベルを比較"""
        sensitivity_levels = {
            DataSensitivity.PUBLIC.value: 1,
            DataSensitivity.INTERNAL.value: 2,
            DataSensitivity.CONFIDENTIAL.value: 3,
            DataSensitivity.TOP_SECRET.value: 4,
        }
        return sensitivity_levels.get(sensitivity1, 0) > sensitivity_levels.get(
            sensitivity2, 0
        )

    def _calculate_retention_period(self, categories: List[str]) -> int:
        """保持期間を計算"""
        if not categories:
            return 365  # デフォルト1年

        max_retention = 0
        for category in categories:
            retention = self.retention_policies.get(category, 365)
            max_retention = max(max_retention, retention)

        return max_retention

    def _requires_masking(self, categories: List[str]) -> bool:
        """マスキング要件を判定"""
        for category in categories:
            masking_rule = self.masking_rules.get(category, "none")
            if masking_rule in ["partial", "full"]:
                return True
        return False

    def mask_data(self, data: str, masking_type: str = "partial") -> str:
        """
        データをマスキング

        Args:
            data: マスキングするデータ
            masking_type: マスキングタイプ（partial, full, none）

        Returns:
            マスキングされたデータ
        """
        try:
            if masking_type == "none":
                return data

            classification_result = self.classify_data(data)
            masked_data = data

            # 各マッチをマスキング
            for classification in reversed(
                classification_result["classifications"]
            ):  # 逆順で処理
                start, end = classification["position"]
                match_text = classification["match"]

                if masking_type == "full":
                    masked_text = "*" * len(match_text)
                elif masking_type == "partial":
                    if len(match_text) <= 4:
                        masked_text = "*" * len(match_text)
                    else:
                        masked_text = (
                            match_text[:2]
                            + "*" * (len(match_text) - 4)
                            + match_text[-2:]
                        )
                else:
                    masked_text = match_text

                masked_data = masked_data[:start] + masked_text + masked_data[end:]

            logger.info(f"Data masked: {masking_type} masking applied")
            return masked_data

        except Exception as e:
            logger.error(f"Error masking data: {e}")
            raise

    def get_data_label(self, classification_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        データラベルを生成

        Args:
            classification_result: 分類結果

        Returns:
            データラベル
        """
        try:
            label = {
                "sensitivity_level": classification_result["highest_sensitivity"],
                "categories": classification_result["categories"],
                "retention_until": (
                    datetime.utcnow()
                    + timedelta(days=classification_result["retention_days"])
                ).isoformat(),
                "masking_required": classification_result["masking_required"],
                "classification_count": len(classification_result["classifications"]),
                "created_at": classification_result["classified_at"],
                "label_version": "1.0",
            }

            return label

        except Exception as e:
            logger.error(f"Error generating data label: {e}")
            raise

    def should_retain_data(
        self, classification_result: Dict[str, Any], created_at: datetime
    ) -> bool:
        """
        データを保持すべきかどうかを判定

        Args:
            classification_result: 分類結果
            created_at: データ作成日時

        Returns:
            保持すべきかどうか
        """
        try:
            retention_days = classification_result["retention_days"]
            retention_until = created_at + timedelta(days=retention_days)

            return datetime.utcnow() < retention_until

        except Exception as e:
            logger.error(f"Error checking data retention: {e}")
            return True  # エラーの場合は保持

    def get_expired_data_candidates(
        self, data_records: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        保持期間が過ぎたデータの候補を取得

        Args:
            data_records: データレコードのリスト

        Returns:
            削除候補のデータレコード
        """
        try:
            expired_candidates = []

            for record in data_records:
                if "classification_result" in record and "created_at" in record:
                    classification_result = record["classification_result"]
                    created_at = datetime.fromisoformat(record["created_at"])

                    if not self.should_retain_data(classification_result, created_at):
                        expired_candidates.append(record)

            logger.info(f"Found {len(expired_candidates)} expired data candidates")
            return expired_candidates

        except Exception as e:
            logger.error(f"Error finding expired data candidates: {e}")
            return []

    def update_classification_rules(self, new_rules: Dict[str, Dict]) -> None:
        """
        分類ルールを更新

        Args:
            new_rules: 新しい分類ルール
        """
        try:
            self.classification_rules.update(new_rules)
            logger.info(
                f"Updated classification rules: {len(new_rules)} rules added/modified"
            )

        except Exception as e:
            logger.error(f"Error updating classification rules: {e}")
            raise

    def get_classification_summary(
        self, data_records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        データ分類のサマリーを取得

        Args:
            data_records: データレコードのリスト

        Returns:
            分類サマリー
        """
        try:
            summary = {
                "total_records": len(data_records),
                "sensitivity_distribution": {},
                "category_distribution": {},
                "retention_summary": {},
                "masking_required_count": 0,
                "expired_count": 0,
            }

            for record in data_records:
                if "classification_result" in record:
                    classification_result = record["classification_result"]

                    # 機密度分布
                    sensitivity = classification_result["highest_sensitivity"]
                    summary["sensitivity_distribution"][sensitivity] = (
                        summary["sensitivity_distribution"].get(sensitivity, 0) + 1
                    )

                    # カテゴリ分布
                    for category in classification_result["categories"]:
                        summary["category_distribution"][category] = (
                            summary["category_distribution"].get(category, 0) + 1
                        )

                    # マスキング要件
                    if classification_result["masking_required"]:
                        summary["masking_required_count"] += 1

                    # 保持期間サマリー
                    retention_days = classification_result["retention_days"]
                    retention_range = f"{retention_days} days"
                    summary["retention_summary"][retention_range] = (
                        summary["retention_summary"].get(retention_range, 0) + 1
                    )

                    # 期限切れチェック
                    if "created_at" in record:
                        created_at = datetime.fromisoformat(record["created_at"])
                        if not self.should_retain_data(
                            classification_result, created_at
                        ):
                            summary["expired_count"] += 1

            logger.info("Classification summary generated")
            return summary

        except Exception as e:
            logger.error(f"Error generating classification summary: {e}")
            raise


# グローバルインスタンス
data_classification_service = DataClassificationService()


def get_data_classification_service() -> DataClassificationService:
    """データ分類サービスを取得"""
    return data_classification_service
