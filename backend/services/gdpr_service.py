import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from database import get_db
from models.user import User
from sqlalchemy.orm import Session
from utils.logging import get_logger

logger = get_logger(__name__)


class GDPRRightType(Enum):
    """GDPRデータ主体の権利タイプ"""

    ACCESS = "access"
    RECTIFICATION = "rectification"
    ERASURE = "erasure"
    RESTRICTION = "restriction"
    PORTABILITY = "portability"
    OBJECTION = "objection"


class ConsentType(Enum):
    """同意タイプ"""

    MARKETING = "marketing"
    ANALYTICS = "analytics"
    FUNCTIONAL = "functional"
    NECESSARY = "necessary"


class GDPRService:
    """
    GDPR対応サービス
    """

    def __init__(self):
        self.consent_categories = self._initialize_consent_categories()
        self.data_retention_periods = self._initialize_retention_periods()

    def _initialize_consent_categories(self) -> Dict[str, Dict[str, Any]]:
        """同意カテゴリを初期化"""
        return {
            ConsentType.MARKETING.value: {
                "name": "Marketing Communications",
                "description": "Receive marketing emails and promotional content",
                "required": False,
                "retention_days": 365,
                "legal_basis": "consent",
            },
            ConsentType.ANALYTICS.value: {
                "name": "Analytics and Tracking",
                "description": "Allow analytics and performance tracking",
                "required": False,
                "retention_days": 730,
                "legal_basis": "consent",
            },
            ConsentType.FUNCTIONAL.value: {
                "name": "Functional Cookies",
                "description": "Enable enhanced functionality and personalization",
                "required": False,
                "retention_days": 365,
                "legal_basis": "consent",
            },
            ConsentType.NECESSARY.value: {
                "name": "Necessary Cookies",
                "description": "Essential for website functionality",
                "required": True,
                "retention_days": 30,
                "legal_basis": "legitimate_interest",
            },
        }

    def _initialize_retention_periods(self) -> Dict[str, int]:
        """データ保持期間を初期化（日数）"""
        return {
            "user_profile": 2555,  # 7年
            "transaction_history": 2555,  # 7年
            "communication_logs": 1095,  # 3年
            "analytics_data": 730,  # 2年
            "marketing_data": 365,  # 1年
            "session_data": 30,  # 30日
            "audit_logs": 2555,  # 7年
        }

    def record_consent(
        self, user_id: str, consent_data: Dict[str, Any], db: Session
    ) -> Dict[str, Any]:
        """
        同意を記録

        Args:
            user_id: ユーザーID
            consent_data: 同意データ
            db: データベースセッション

        Returns:
            記録された同意情報
        """
        try:
            consent_record = {
                "user_id": user_id,
                "consent_type": consent_data.get("consent_type"),
                "consent_given": consent_data.get("consent_given", False),
                "consent_timestamp": datetime.utcnow().isoformat(),
                "consent_method": consent_data.get("consent_method", "web_form"),
                "ip_address": consent_data.get("ip_address"),
                "user_agent": consent_data.get("user_agent"),
                "consent_version": consent_data.get("consent_version", "1.0"),
                "withdrawal_timestamp": None,
                "legal_basis": self.consent_categories.get(
                    consent_data.get("consent_type"), {}
                ).get("legal_basis", "consent"),
            }

            # データベースに保存（実際の実装では専用テーブルを使用）
            logger.info(f"Consent recorded for user {user_id}: {consent_record}")

            return consent_record

        except Exception as e:
            logger.error(f"Error recording consent: {e}")
            raise

    def withdraw_consent(
        self, user_id: str, consent_type: str, db: Session
    ) -> Dict[str, Any]:
        """
        同意を撤回

        Args:
            user_id: ユーザーID
            consent_type: 同意タイプ
            db: データベースセッション

        Returns:
            撤回された同意情報
        """
        try:
            withdrawal_record = {
                "user_id": user_id,
                "consent_type": consent_type,
                "withdrawal_timestamp": datetime.utcnow().isoformat(),
                "status": "withdrawn",
            }

            # データベースで同意を撤回（実際の実装では専用テーブルを更新）
            logger.info(f"Consent withdrawn for user {user_id}, type: {consent_type}")

            return withdrawal_record

        except Exception as e:
            logger.error(f"Error withdrawing consent: {e}")
            raise

    def get_user_consents(self, user_id: str, db: Session) -> List[Dict[str, Any]]:
        """
        ユーザーの同意履歴を取得

        Args:
            user_id: ユーザーID
            db: データベースセッション

        Returns:
            同意履歴のリスト
        """
        try:
            # 実際の実装では専用テーブルから取得
            consents = []

            for consent_type, config in self.consent_categories.items():
                consent_record = {
                    "consent_type": consent_type,
                    "name": config["name"],
                    "description": config["description"],
                    "required": config["required"],
                    "legal_basis": config["legal_basis"],
                    "consent_given": True,  # 仮の値
                    "consent_timestamp": datetime.utcnow().isoformat(),
                    "withdrawal_timestamp": None,
                }
                consents.append(consent_record)

            return consents

        except Exception as e:
            logger.error(f"Error getting user consents: {e}")
            raise

    def handle_data_subject_request(
        self, user_id: str, request_type: GDPRRightType, db: Session
    ) -> Dict[str, Any]:
        """
        データ主体の権利要求を処理

        Args:
            user_id: ユーザーID
            request_type: 要求タイプ
            db: データベースセッション

        Returns:
            処理結果
        """
        try:
            request_record = {
                "user_id": user_id,
                "request_type": request_type.value,
                "request_timestamp": datetime.utcnow().isoformat(),
                "status": "processing",
                "response_data": None,
            }

            if request_type == GDPRRightType.ACCESS:
                request_record["response_data"] = self._handle_access_request(
                    user_id, db
                )
            elif request_type == GDPRRightType.RECTIFICATION:
                request_record["response_data"] = self._handle_rectification_request(
                    user_id, db
                )
            elif request_type == GDPRRightType.ERASURE:
                request_record["response_data"] = self._handle_erasure_request(
                    user_id, db
                )
            elif request_type == GDPRRightType.RESTRICTION:
                request_record["response_data"] = self._handle_restriction_request(
                    user_id, db
                )
            elif request_type == GDPRRightType.PORTABILITY:
                request_record["response_data"] = self._handle_portability_request(
                    user_id, db
                )
            elif request_type == GDPRRightType.OBJECTION:
                request_record["response_data"] = self._handle_objection_request(
                    user_id, db
                )

            request_record["status"] = "completed"
            logger.info(
                f"Data subject request processed: {request_type.value} for user {user_id}"
            )

            return request_record

        except Exception as e:
            logger.error(f"Error handling data subject request: {e}")
            raise

    def _handle_access_request(self, user_id: str, db: Session) -> Dict[str, Any]:
        """アクセス権要求を処理"""
        try:
            # ユーザーデータを取得
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"error": "User not found"}

            # 関連データを収集
            access_data = {
                "personal_data": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "created_at": (
                        user.created_at.isoformat() if user.created_at else None
                    ),
                    "last_login": (
                        user.last_login.isoformat() if user.last_login else None
                    ),
                },
                "consent_data": self.get_user_consents(user_id, db),
                "data_categories": self._get_user_data_categories(user_id, db),
                "data_sources": self._get_user_data_sources(user_id, db),
                "retention_periods": self.data_retention_periods,
                "legal_basis": self._get_legal_basis(user_id, db),
            }

            return access_data

        except Exception as e:
            logger.error(f"Error handling access request: {e}")
            return {"error": str(e)}

    def _handle_rectification_request(
        self, user_id: str, db: Session
    ) -> Dict[str, Any]:
        """訂正権要求を処理"""
        try:
            # 実際の実装では、ユーザーが提供した訂正データで更新
            rectification_data = {
                "user_id": user_id,
                "rectification_timestamp": datetime.utcnow().isoformat(),
                "status": "processed",
                "message": "Data rectification request processed",
            }

            return rectification_data

        except Exception as e:
            logger.error(f"Error handling rectification request: {e}")
            return {"error": str(e)}

    def _handle_erasure_request(self, user_id: str, db: Session) -> Dict[str, Any]:
        """削除権（忘れられる権利）要求を処理"""
        try:
            # 削除対象データを特定
            data_to_delete = self._identify_data_for_erasure(user_id, db)

            # データを削除（実際の実装では論理削除）
            erasure_data = {
                "user_id": user_id,
                "erasure_timestamp": datetime.utcnow().isoformat(),
                "data_categories_deleted": data_to_delete,
                "status": "processed",
                "message": "Data erasure request processed",
            }

            return erasure_data

        except Exception as e:
            logger.error(f"Error handling erasure request: {e}")
            return {"error": str(e)}

    def _handle_restriction_request(self, user_id: str, db: Session) -> Dict[str, Any]:
        """処理制限権要求を処理"""
        try:
            restriction_data = {
                "user_id": user_id,
                "restriction_timestamp": datetime.utcnow().isoformat(),
                "status": "processed",
                "message": "Data processing restriction applied",
            }

            return restriction_data

        except Exception as e:
            logger.error(f"Error handling restriction request: {e}")
            return {"error": str(e)}

    def _handle_portability_request(self, user_id: str, db: Session) -> Dict[str, Any]:
        """データポータビリティ要求を処理"""
        try:
            # 機械可読形式でデータをエクスポート
            portable_data = self._export_user_data(user_id, db)

            portability_data = {
                "user_id": user_id,
                "portability_timestamp": datetime.utcnow().isoformat(),
                "data_format": "JSON",
                "data_size": len(json.dumps(portable_data)),
                "download_url": f"/api/gdpr/export/{user_id}",  # 仮のURL
                "status": "ready_for_download",
            }

            return portability_data

        except Exception as e:
            logger.error(f"Error handling portability request: {e}")
            return {"error": str(e)}

    def _handle_objection_request(self, user_id: str, db: Session) -> Dict[str, Any]:
        """異議申し立て権要求を処理"""
        try:
            objection_data = {
                "user_id": user_id,
                "objection_timestamp": datetime.utcnow().isoformat(),
                "status": "processed",
                "message": "Objection to data processing recorded",
            }

            return objection_data

        except Exception as e:
            logger.error(f"Error handling objection request: {e}")
            return {"error": str(e)}

    def _get_user_data_categories(self, user_id: str, db: Session) -> List[str]:
        """ユーザーのデータカテゴリを取得"""
        try:
            # 実際の実装では、データベースから取得
            return [
                "personal_info",
                "transaction_history",
                "communication_logs",
                "analytics_data",
            ]

        except Exception as e:
            logger.error(f"Error getting user data categories: {e}")
            return []

    def _get_user_data_sources(self, user_id: str, db: Session) -> List[str]:
        """ユーザーのデータソースを取得"""
        try:
            # 実際の実装では、データベースから取得
            return [
                "user_registration",
                "transaction_system",
                "analytics_system",
                "communication_system",
            ]

        except Exception as e:
            logger.error(f"Error getting user data sources: {e}")
            return []

    def _get_legal_basis(self, user_id: str, db: Session) -> Dict[str, str]:
        """法的根拠を取得"""
        try:
            return {
                "personal_data": "contract",
                "marketing_data": "consent",
                "analytics_data": "legitimate_interest",
                "transaction_data": "contract",
            }

        except Exception as e:
            logger.error(f"Error getting legal basis: {e}")
            return {}

    def _identify_data_for_erasure(self, user_id: str, db: Session) -> List[str]:
        """削除対象データを特定"""
        try:
            # 実際の実装では、データベースをスキャンして削除対象を特定
            return ["personal_info", "transaction_history", "communication_logs"]

        except Exception as e:
            logger.error(f"Error identifying data for erasure: {e}")
            return []

    def _export_user_data(self, user_id: str, db: Session) -> Dict[str, Any]:
        """ユーザーデータをエクスポート"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {}

            export_data = {
                "user_profile": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "created_at": (
                        user.created_at.isoformat() if user.created_at else None
                    ),
                },
                "consent_history": self.get_user_consents(user_id, db),
                "data_categories": self._get_user_data_categories(user_id, db),
                "export_timestamp": datetime.utcnow().isoformat(),
                "export_version": "1.0",
            }

            return export_data

        except Exception as e:
            logger.error(f"Error exporting user data: {e}")
            return {}

    def conduct_dpia(self, processing_activity: Dict[str, Any]) -> Dict[str, Any]:
        """
        データ保護影響評価（DPIA）を実施

        Args:
            processing_activity: 処理活動の詳細

        Returns:
            DPIA結果
        """
        try:
            dpia_result = {
                "processing_activity": processing_activity,
                "assessment_date": datetime.utcnow().isoformat(),
                "risk_level": self._assess_risk_level(processing_activity),
                "risks_identified": self._identify_risks(processing_activity),
                "mitigation_measures": self._suggest_mitigation_measures(
                    processing_activity
                ),
                "recommendation": self._generate_recommendation(processing_activity),
                "requires_consultation": self._requires_consultation(
                    processing_activity
                ),
            }

            logger.info(
                f"DPIA conducted for activity: {processing_activity.get('name', 'Unknown')}"
            )
            return dpia_result

        except Exception as e:
            logger.error(f"Error conducting DPIA: {e}")
            raise

    def _assess_risk_level(self, processing_activity: Dict[str, Any]) -> str:
        """リスクレベルを評価"""
        try:
            risk_score = 0

            # データの種類によるリスク
            data_types = processing_activity.get("data_types", [])
            if "sensitive_personal_data" in data_types:
                risk_score += 3
            elif "personal_data" in data_types:
                risk_score += 2

            # 処理の規模によるリスク
            scale = processing_activity.get("scale", "small")
            if scale == "large":
                risk_score += 2
            elif scale == "medium":
                risk_score += 1

            # 自動化の程度によるリスク
            automation = processing_activity.get("automation_level", "low")
            if automation == "high":
                risk_score += 2
            elif automation == "medium":
                risk_score += 1

            # リスクレベルを決定
            if risk_score >= 5:
                return "high"
            elif risk_score >= 3:
                return "medium"
            else:
                return "low"

        except Exception as e:
            logger.error(f"Error assessing risk level: {e}")
            return "unknown"

    def _identify_risks(
        self, processing_activity: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """リスクを特定"""
        try:
            risks = []

            # 一般的なリスク
            risks.append(
                {
                    "risk": "Unauthorized access to personal data",
                    "impact": "Privacy breach, reputational damage",
                    "likelihood": "medium",
                }
            )

            risks.append(
                {
                    "risk": "Data loss or corruption",
                    "impact": "Loss of personal data, service disruption",
                    "likelihood": "low",
                }
            )

            # 処理活動に応じたリスク
            if processing_activity.get("automation_level") == "high":
                risks.append(
                    {
                        "risk": "Automated decision-making bias",
                        "impact": "Discrimination, unfair treatment",
                        "likelihood": "medium",
                    }
                )

            return risks

        except Exception as e:
            logger.error(f"Error identifying risks: {e}")
            return []

    def _suggest_mitigation_measures(
        self, processing_activity: Dict[str, Any]
    ) -> List[str]:
        """軽減策を提案"""
        try:
            measures = [
                "Implement strong access controls and authentication",
                "Encrypt personal data at rest and in transit",
                "Regular security assessments and penetration testing",
                "Staff training on data protection principles",
                "Incident response plan for data breaches",
            ]

            # 処理活動に応じた追加の軽減策
            if processing_activity.get("automation_level") == "high":
                measures.append(
                    "Regular review of automated decision-making algorithms"
                )
                measures.append("Human oversight for high-risk automated decisions")

            return measures

        except Exception as e:
            logger.error(f"Error suggesting mitigation measures: {e}")
            return []

    def _generate_recommendation(self, processing_activity: Dict[str, Any]) -> str:
        """推奨事項を生成"""
        try:
            risk_level = self._assess_risk_level(processing_activity)

            if risk_level == "high":
                return "High risk processing activity. Requires detailed DPIA and supervisory authority consultation."
            elif risk_level == "medium":
                return "Medium risk processing activity. Implement recommended mitigation measures and monitor regularly."
            else:
                return "Low risk processing activity. Standard data protection measures should be sufficient."

        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            return "Unable to generate recommendation"

    def _requires_consultation(self, processing_activity: Dict[str, Any]) -> bool:
        """監督機関への相談が必要かどうかを判定"""
        try:
            risk_level = self._assess_risk_level(processing_activity)
            return risk_level == "high"

        except Exception as e:
            logger.error(f"Error checking consultation requirement: {e}")
            return False


# グローバルインスタンス
gdpr_service = GDPRService()


def get_gdpr_service() -> GDPRService:
    """GDPRサービスを取得"""
    return gdpr_service
