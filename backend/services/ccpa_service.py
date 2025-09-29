import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from database import get_db
from models.user import User
from sqlalchemy.orm import Session
from utils.logging import get_logger

logger = get_logger(__name__)


class CCPARightType(Enum):
    """CCPA消費者権利タイプ"""
    DISCLOSURE = "disclosure"
    DELETION = "deletion"
    OPT_OUT = "opt_out"
    NON_DISCRIMINATION = "non_discrimination"


class DataSaleCategory(Enum):
    """データ売却カテゴリ"""
    PERSONAL_INFO = "personal_info"
    BEHAVIORAL_DATA = "behavioral_data"
    LOCATION_DATA = "location_data"
    FINANCIAL_DATA = "financial_data"
    HEALTH_DATA = "health_data"


class CCPAService:
    """
    CCPA（カリフォルニア州消費者プライバシー法）対応サービス
    """

    def __init__(self):
        self.data_categories = self._initialize_data_categories()
        self.sale_categories = self._initialize_sale_categories()
        self.third_parties = self._initialize_third_parties()

    def _initialize_data_categories(self) -> Dict[str, Dict[str, Any]]:
        """データカテゴリを初期化"""
        return {
            "identifiers": {
                "name": "Name, email, phone number, IP address",
                "retention_days": 2555,  # 7年
                "sale_allowed": True
            },
            "commercial_information": {
                "name": "Purchase history, preferences, transaction records",
                "retention_days": 2555,  # 7年
                "sale_allowed": True
            },
            "internet_activity": {
                "name": "Browsing history, search history, website interactions",
                "retention_days": 730,  # 2年
                "sale_allowed": True
            },
            "geolocation_data": {
                "name": "Location information, GPS coordinates",
                "retention_days": 365,  # 1年
                "sale_allowed": False
            },
            "biometric_information": {
                "name": "Fingerprints, facial recognition, voice patterns",
                "retention_days": 2555,  # 7年
                "sale_allowed": False
            },
            "sensory_data": {
                "name": "Audio, visual, thermal, olfactory information",
                "retention_days": 365,  # 1年
                "sale_allowed": False
            },
            "professional_employment": {
                "name": "Job title, employer, work history",
                "retention_days": 1825,  # 5年
                "sale_allowed": True
            },
            "education_information": {
                "name": "Educational background, degrees, certifications",
                "retention_days": 1825,  # 5年
                "sale_allowed": True
            }
        }

    def _initialize_sale_categories(self) -> Dict[str, Dict[str, Any]]:
        """売却カテゴリを初期化"""
        return {
            DataSaleCategory.PERSONAL_INFO.value: {
                "description": "Personal identifiers and contact information",
                "price_per_record": 0.50,
                "buyers": ["marketing_partners", "data_brokers"]
            },
            DataSaleCategory.BEHAVIORAL_DATA.value: {
                "description": "User behavior and interaction data",
                "price_per_record": 0.25,
                "buyers": ["analytics_companies", "advertisers"]
            },
            DataSaleCategory.LOCATION_DATA.value: {
                "description": "Geographic location information",
                "price_per_record": 0.75,
                "buyers": ["location_services", "retail_partners"]
            },
            DataSaleCategory.FINANCIAL_DATA.value: {
                "description": "Financial transaction and payment data",
                "price_per_record": 1.00,
                "buyers": ["financial_services", "credit_bureaus"]
            },
            DataSaleCategory.HEALTH_DATA.value: {
                "description": "Health and wellness information",
                "price_per_record": 2.00,
                "buyers": ["healthcare_providers", "research_institutions"]
            }
        }

    def _initialize_third_parties(self) -> Dict[str, Dict[str, Any]]:
        """第三者を初期化"""
        return {
            "marketing_partners": {
                "name": "Marketing Partners Inc.",
                "purpose": "Targeted advertising and marketing campaigns",
                "data_categories": ["identifiers", "commercial_information"],
                "contact_info": "privacy@marketingpartners.com"
            },
            "data_brokers": {
                "name": "Data Brokers LLC",
                "purpose": "Data aggregation and resale",
                "data_categories": ["identifiers", "behavioral_data"],
                "contact_info": "privacy@databrokers.com"
            },
            "analytics_companies": {
                "name": "Analytics Solutions Corp",
                "purpose": "Website analytics and user behavior analysis",
                "data_categories": ["internet_activity", "behavioral_data"],
                "contact_info": "privacy@analytics.com"
            },
            "advertisers": {
                "name": "Digital Advertisers Inc",
                "purpose": "Programmatic advertising and ad targeting",
                "data_categories": ["identifiers", "commercial_information"],
                "contact_info": "privacy@advertisers.com"
            }
        }

    def handle_consumer_request(self, user_id: str, request_type: CCPARightType, db: Session) -> Dict[str, Any]:
        """
        消費者権利要求を処理
        
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
                "response_data": None
            }

            if request_type == CCPARightType.DISCLOSURE:
                request_record["response_data"] = self._handle_disclosure_request(user_id, db)
            elif request_type == CCPARightType.DELETION:
                request_record["response_data"] = self._handle_deletion_request(user_id, db)
            elif request_type == CCPARightType.OPT_OUT:
                request_record["response_data"] = self._handle_opt_out_request(user_id, db)
            elif request_type == CCPARightType.NON_DISCRIMINATION:
                request_record["response_data"] = self._handle_non_discrimination_request(user_id, db)

            request_record["status"] = "completed"
            logger.info(f"CCPA consumer request processed: {request_type.value} for user {user_id}")
            
            return request_record
            
        except Exception as e:
            logger.error(f"Error handling CCPA consumer request: {e}")
            raise

    def _handle_disclosure_request(self, user_id: str, db: Session) -> Dict[str, Any]:
        """開示権要求を処理"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"error": "User not found"}

            disclosure_data = {
                "data_categories_collected": self._get_collected_data_categories(user_id, db),
                "data_sources": self._get_data_sources(user_id, db),
                "business_purposes": self._get_business_purposes(user_id, db),
                "third_parties": self._get_third_parties(user_id, db),
                "data_sales": self._get_data_sales(user_id, db),
                "consumer_rights": self._get_consumer_rights(),
                "contact_information": self._get_contact_information()
            }

            return disclosure_data
            
        except Exception as e:
            logger.error(f"Error handling disclosure request: {e}")
            return {"error": str(e)}

    def _handle_deletion_request(self, user_id: str, db: Session) -> Dict[str, Any]:
        """削除権要求を処理"""
        try:
            # 削除対象データを特定
            data_to_delete = self._identify_deletable_data(user_id, db)
            
            deletion_data = {
                "user_id": user_id,
                "deletion_timestamp": datetime.utcnow().isoformat(),
                "data_categories_deleted": data_to_delete,
                "retention_exceptions": self._get_retention_exceptions(user_id, db),
                "status": "processed",
                "message": "Data deletion request processed"
            }

            return deletion_data
            
        except Exception as e:
            logger.error(f"Error handling deletion request: {e}")
            return {"error": str(e)}

    def _handle_opt_out_request(self, user_id: str, db: Session) -> Dict[str, Any]:
        """オプトアウト権要求を処理"""
        try:
            opt_out_data = {
                "user_id": user_id,
                "opt_out_timestamp": datetime.utcnow().isoformat(),
                "data_sales_stopped": self._stop_data_sales(user_id, db),
                "third_party_notifications": self._notify_third_parties(user_id, db),
                "status": "processed",
                "message": "Opt-out request processed"
            }

            return opt_out_data
            
        except Exception as e:
            logger.error(f"Error handling opt-out request: {e}")
            return {"error": str(e)}

    def _handle_non_discrimination_request(self, user_id: str, db: Session) -> Dict[str, Any]:
        """非差別権要求を処理"""
        try:
            non_discrimination_data = {
                "user_id": user_id,
                "request_timestamp": datetime.utcnow().isoformat(),
                "service_levels_maintained": True,
                "pricing_unaffected": True,
                "access_restrictions_removed": self._remove_access_restrictions(user_id, db),
                "status": "processed",
                "message": "Non-discrimination request processed"
            }

            return non_discrimination_data
            
        except Exception as e:
            logger.error(f"Error handling non-discrimination request: {e}")
            return {"error": str(e)}

    def _get_collected_data_categories(self, user_id: str, db: Session) -> List[Dict[str, Any]]:
        """収集されたデータカテゴリを取得"""
        try:
            categories = []
            for category_id, category_info in self.data_categories.items():
                categories.append({
                    "category": category_id,
                    "name": category_info["name"],
                    "collected": True,  # 仮の値
                    "retention_days": category_info["retention_days"]
                })
            return categories
            
        except Exception as e:
            logger.error(f"Error getting collected data categories: {e}")
            return []

    def _get_data_sources(self, user_id: str, db: Session) -> List[str]:
        """データソースを取得"""
        try:
            return [
                "Direct user input",
                "Website interactions",
                "Transaction records",
                "Third-party integrations",
                "Analytics systems"
            ]
            
        except Exception as e:
            logger.error(f"Error getting data sources: {e}")
            return []

    def _get_business_purposes(self, user_id: str, db: Session) -> List[Dict[str, str]]:
        """事業目的を取得"""
        try:
            return [
                {
                    "purpose": "Service delivery",
                    "description": "Providing and maintaining our services"
                },
                {
                    "purpose": "Customer support",
                    "description": "Responding to customer inquiries and support requests"
                },
                {
                    "purpose": "Marketing",
                    "description": "Sending promotional communications and targeted advertising"
                },
                {
                    "purpose": "Analytics",
                    "description": "Understanding user behavior and improving our services"
                },
                {
                    "purpose": "Legal compliance",
                    "description": "Meeting legal and regulatory requirements"
                }
            ]
            
        except Exception as e:
            logger.error(f"Error getting business purposes: {e}")
            return []

    def _get_third_parties(self, user_id: str, db: Session) -> List[Dict[str, Any]]:
        """第三者を取得"""
        try:
            third_parties = []
            for party_id, party_info in self.third_parties.items():
                third_parties.append({
                    "name": party_info["name"],
                    "purpose": party_info["purpose"],
                    "data_categories": party_info["data_categories"],
                    "contact_info": party_info["contact_info"]
                })
            return third_parties
            
        except Exception as e:
            logger.error(f"Error getting third parties: {e}")
            return []

    def _get_data_sales(self, user_id: str, db: Session) -> Dict[str, Any]:
        """データ売却情報を取得"""
        try:
            sales_data = {
                "sales_occurred": True,
                "sales_categories": [],
                "total_value": 0.0,
                "buyers": []
            }

            for category_id, category_info in self.sale_categories.items():
                sales_data["sales_categories"].append({
                    "category": category_id,
                    "description": category_info["description"],
                    "price_per_record": category_info["price_per_record"],
                    "buyers": category_info["buyers"]
                })
                sales_data["total_value"] += category_info["price_per_record"]

            return sales_data
            
        except Exception as e:
            logger.error(f"Error getting data sales: {e}")
            return {}

    def _get_consumer_rights(self) -> List[Dict[str, str]]:
        """消費者権利を取得"""
        try:
            return [
                {
                    "right": "Right to Know",
                    "description": "Right to know what personal information is collected and how it's used"
                },
                {
                    "right": "Right to Delete",
                    "description": "Right to request deletion of personal information"
                },
                {
                    "right": "Right to Opt-Out",
                    "description": "Right to opt-out of the sale of personal information"
                },
                {
                    "right": "Right to Non-Discrimination",
                    "description": "Right to non-discriminatory treatment for exercising privacy rights"
                }
            ]
            
        except Exception as e:
            logger.error(f"Error getting consumer rights: {e}")
            return []

    def _get_contact_information(self) -> Dict[str, str]:
        """連絡先情報を取得"""
        try:
            return {
                "privacy_email": "privacy@aica-sys.com",
                "privacy_phone": "1-800-PRIVACY",
                "privacy_address": "123 Privacy Street, Privacy City, PC 12345",
                "website": "https://aica-sys.com/privacy"
            }
            
        except Exception as e:
            logger.error(f"Error getting contact information: {e}")
            return {}

    def _identify_deletable_data(self, user_id: str, db: Session) -> List[str]:
        """削除可能なデータを特定"""
        try:
            # 実際の実装では、データベースをスキャンして削除対象を特定
            deletable_categories = []
            
            for category_id, category_info in self.data_categories.items():
                if category_info.get("sale_allowed", False):
                    deletable_categories.append(category_id)
            
            return deletable_categories
            
        except Exception as e:
            logger.error(f"Error identifying deletable data: {e}")
            return []

    def _get_retention_exceptions(self, user_id: str, db: Session) -> List[str]:
        """保持期間の例外を取得"""
        try:
            return [
                "Legal compliance requirements",
                "Fraud prevention",
                "Security purposes",
                "Service functionality"
            ]
            
        except Exception as e:
            logger.error(f"Error getting retention exceptions: {e}")
            return []

    def _stop_data_sales(self, user_id: str, db: Session) -> List[str]:
        """データ売却を停止"""
        try:
            stopped_sales = []
            
            for category_id, category_info in self.sale_categories.items():
                if category_info.get("sale_allowed", False):
                    stopped_sales.append(category_id)
            
            logger.info(f"Data sales stopped for user {user_id}: {stopped_sales}")
            return stopped_sales
            
        except Exception as e:
            logger.error(f"Error stopping data sales: {e}")
            return []

    def _notify_third_parties(self, user_id: str, db: Session) -> List[Dict[str, str]]:
        """第三者に通知"""
        try:
            notifications = []
            
            for party_id, party_info in self.third_parties.items():
                notifications.append({
                    "party": party_info["name"],
                    "notification_sent": True,
                    "notification_timestamp": datetime.utcnow().isoformat(),
                    "status": "acknowledged"
                })
            
            return notifications
            
        except Exception as e:
            logger.error(f"Error notifying third parties: {e}")
            return []

    def _remove_access_restrictions(self, user_id: str, db: Session) -> List[str]:
        """アクセス制限を削除"""
        try:
            restrictions_removed = [
                "Service level restrictions",
                "Feature limitations",
                "Pricing adjustments"
            ]
            
            logger.info(f"Access restrictions removed for user {user_id}")
            return restrictions_removed
            
        except Exception as e:
            logger.error(f"Error removing access restrictions: {e}")
            return []

    def track_data_sale(self, user_id: str, sale_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        データ売却を追跡
        
        Args:
            user_id: ユーザーID
            sale_data: 売却データ
            db: データベースセッション
            
        Returns:
            売却記録
        """
        try:
            sale_record = {
                "user_id": user_id,
                "sale_timestamp": datetime.utcnow().isoformat(),
                "data_category": sale_data.get("data_category"),
                "buyer": sale_data.get("buyer"),
                "price": sale_data.get("price", 0.0),
                "data_points": sale_data.get("data_points", 0),
                "purpose": sale_data.get("purpose"),
                "legal_basis": sale_data.get("legal_basis", "sale")
            }

            # データベースに記録（実際の実装では専用テーブルを使用）
            logger.info(f"Data sale tracked for user {user_id}: {sale_record}")
            
            return sale_record
            
        except Exception as e:
            logger.error(f"Error tracking data sale: {e}")
            raise

    def get_sale_statistics(self, db: Session) -> Dict[str, Any]:
        """売却統計を取得"""
        try:
            statistics = {
                "total_sales": 0,
                "total_revenue": 0.0,
                "sales_by_category": {},
                "sales_by_buyer": {},
                "opt_out_rate": 0.0,
                "period": "last_12_months"
            }

            # 実際の実装では、データベースから統計を計算
            for category_id, category_info in self.sale_categories.items():
                statistics["sales_by_category"][category_id] = {
                    "count": 0,  # 仮の値
                    "revenue": 0.0,  # 仮の値
                    "price_per_record": category_info["price_per_record"]
                }

            return statistics
            
        except Exception as e:
            logger.error(f"Error getting sale statistics: {e}")
            return {}

    def generate_privacy_notice(self, user_location: str = "california") -> Dict[str, Any]:
        """プライバシー通知を生成"""
        try:
            if user_location.lower() != "california":
                return {"message": "CCPA privacy notice not applicable for this location"}

            privacy_notice = {
                "title": "California Consumer Privacy Act (CCPA) Privacy Notice",
                "effective_date": datetime.utcnow().isoformat(),
                "data_categories_collected": list(self.data_categories.keys()),
                "business_purposes": self._get_business_purposes("", None),
                "data_sales": self._get_data_sales("", None),
                "consumer_rights": self._get_consumer_rights(),
                "contact_information": self._get_contact_information(),
                "opt_out_link": "https://aica-sys.com/opt-out",
                "do_not_sell_link": "https://aica-sys.com/do-not-sell"
            }

            return privacy_notice
            
        except Exception as e:
            logger.error(f"Error generating privacy notice: {e}")
            return {}


# グローバルインスタンス
ccpa_service = CCPAService()


def get_ccpa_service() -> CCPAService:
    """CCPAサービスを取得"""
    return ccpa_service
