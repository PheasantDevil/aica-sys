import asyncio
import json
import logging
import os
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp

from utils.logging import get_logger

logger = get_logger(__name__)


class NotificationChannel(Enum):
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"


class AlertTemplate:
    """アラートテンプレート"""

    @staticmethod
    def get_critical_alert_template(alert_data: Dict[str, Any]) -> str:
        """Critical アラートのテンプレート"""
        return f"""
🚨 CRITICAL ALERT 🚨

Service: {alert_data.get('service', 'Unknown')}
Title: {alert_data.get('title', 'Unknown')}
Message: {alert_data.get('message', 'No message')}
Time: {alert_data.get('timestamp', 'Unknown')}

Please investigate immediately!

---
AICA-SyS Monitoring System
        """.strip()

    @staticmethod
    def get_warning_alert_template(alert_data: Dict[str, Any]) -> str:
        """Warning アラートのテンプレート"""
        return f"""
⚠️ WARNING ALERT ⚠️

Service: {alert_data.get('service', 'Unknown')}
Title: {alert_data.get('title', 'Unknown')}
Message: {alert_data.get('message', 'No message')}
Time: {alert_data.get('timestamp', 'Unknown')}

Please review and take action if necessary.

---
AICA-SyS Monitoring System
        """.strip()

    @staticmethod
    def get_info_alert_template(alert_data: Dict[str, Any]) -> str:
        """Info アラートのテンプレート"""
        return f"""
ℹ️ INFO ALERT ℹ️

Service: {alert_data.get('service', 'Unknown')}
Title: {alert_data.get('title', 'Unknown')}
Message: {alert_data.get('message', 'No message')}
Time: {alert_data.get('timestamp', 'Unknown')}

For your information.

---
AICA-SyS Monitoring System
        """.strip()


class EmailNotifier:
    """Email通知サービス"""

    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_username)
        self.to_emails = os.getenv("ALERT_EMAILS", "").split(",")

    async def send_alert(self, alert_data: Dict[str, Any]) -> bool:
        """アラートをEmailで送信"""
        if not self.smtp_username or not self.smtp_password or not self.to_emails:
            logger.warning(
                "Email configuration not complete, skipping email notification"
            )
            return False

        try:
            # アラートレベルに応じてテンプレートを選択
            level = alert_data.get("level", "info")
            if level == "critical":
                template = AlertTemplate.get_critical_alert_template(alert_data)
                subject = f"🚨 CRITICAL: {alert_data.get('title', 'Alert')}"
            elif level == "warning":
                template = AlertTemplate.get_warning_alert_template(alert_data)
                subject = f"⚠️ WARNING: {alert_data.get('title', 'Alert')}"
            else:
                template = AlertTemplate.get_info_alert_template(alert_data)
                subject = f"ℹ️ INFO: {alert_data.get('title', 'Alert')}"

            # Email送信
            await self._send_email(subject, template, self.to_emails)
            logger.info(f"Email alert sent successfully: {alert_data.get('title')}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False

    async def _send_email(self, subject: str, body: str, to_emails: List[str]):
        """Email送信の実装"""

        def _send():
            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = ", ".join(to_emails)
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)

            text = msg.as_string()
            server.sendmail(self.from_email, to_emails, text)
            server.quit()

        # 非同期でEmail送信を実行
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _send)


class SlackNotifier:
    """Slack通知サービス"""

    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        self.channel = os.getenv("SLACK_CHANNEL", "#alerts")

    async def send_alert(self, alert_data: Dict[str, Any]) -> bool:
        """アラートをSlackで送信"""
        if not self.webhook_url:
            logger.warning(
                "Slack webhook URL not configured, skipping Slack notification"
            )
            return False

        try:
            # Slackメッセージを構築
            level = alert_data.get("level", "info")
            color = self._get_color_for_level(level)
            emoji = self._get_emoji_for_level(level)

            payload = {
                "channel": self.channel,
                "username": "AICA-SyS Monitor",
                "icon_emoji": ":robot_face:",
                "attachments": [
                    {
                        "color": color,
                        "title": f"{emoji} {alert_data.get('title', 'Alert')}",
                        "text": alert_data.get("message", "No message"),
                        "fields": [
                            {
                                "title": "Service",
                                "value": alert_data.get("service", "Unknown"),
                                "short": True,
                            },
                            {"title": "Level", "value": level.upper(), "short": True},
                            {
                                "title": "Time",
                                "value": alert_data.get("timestamp", "Unknown"),
                                "short": False,
                            },
                        ],
                        "footer": "AICA-SyS Monitoring System",
                        "ts": int(datetime.now().timestamp()),
                    }
                ],
            }

            # Slackに送信
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status == 200:
                        logger.info(
                            f"Slack alert sent successfully: {alert_data.get('title')}"
                        )
                        return True
                    else:
                        logger.error(f"Slack notification failed: {response.status}")
                        return False

        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return False

    def _get_color_for_level(self, level: str) -> str:
        """アラートレベルに応じた色を取得"""
        colors = {"critical": "danger", "warning": "warning", "info": "good"}
        return colors.get(level, "good")

    def _get_emoji_for_level(self, level: str) -> str:
        """アラートレベルに応じた絵文字を取得"""
        emojis = {"critical": "🚨", "warning": "⚠️", "info": "ℹ️"}
        return emojis.get(level, "ℹ️")


class WebhookNotifier:
    """Webhook通知サービス"""

    def __init__(self):
        self.webhook_urls = os.getenv("ALERT_WEBHOOK_URLS", "").split(",")
        self.webhook_urls = [url.strip() for url in self.webhook_urls if url.strip()]

    async def send_alert(self, alert_data: Dict[str, Any]) -> bool:
        """アラートをWebhookで送信"""
        if not self.webhook_urls:
            logger.warning("No webhook URLs configured, skipping webhook notification")
            return False

        success_count = 0
        for webhook_url in self.webhook_urls:
            try:
                # Webhookペイロードを構築
                payload = {
                    "alert_id": alert_data.get("id"),
                    "level": alert_data.get("level"),
                    "title": alert_data.get("title"),
                    "message": alert_data.get("message"),
                    "service": alert_data.get("service"),
                    "timestamp": alert_data.get("timestamp"),
                    "source": "aica-sys-monitoring",
                }

                # Webhookに送信
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        webhook_url,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as response:
                        if response.status in [200, 201, 202]:
                            success_count += 1
                            logger.info(
                                f"Webhook alert sent successfully to {webhook_url}"
                            )
                        else:
                            logger.error(
                                f"Webhook notification failed to {webhook_url}: {response.status}"
                            )

            except Exception as e:
                logger.error(f"Failed to send webhook alert to {webhook_url}: {e}")

        return success_count > 0


class AlertService:
    """アラート・通知サービス"""

    def __init__(self):
        self.email_notifier = EmailNotifier()
        self.slack_notifier = SlackNotifier()
        self.webhook_notifier = WebhookNotifier()

        # 通知設定
        self.notification_config = {
            "critical": [
                NotificationChannel.EMAIL,
                NotificationChannel.SLACK,
                NotificationChannel.WEBHOOK,
            ],
            "warning": [NotificationChannel.EMAIL, NotificationChannel.SLACK],
            "info": [NotificationChannel.SLACK],
        }

        # レート制限設定
        self.rate_limits = {
            "critical": {"max_per_hour": 10, "cooldown_minutes": 5},
            "warning": {"max_per_hour": 20, "cooldown_minutes": 15},
            "info": {"max_per_hour": 50, "cooldown_minutes": 30},
        }

        # 送信履歴
        self.sent_alerts: Dict[str, List[datetime]] = {}

    async def send_alert(self, alert_data: Dict[str, Any]) -> Dict[str, bool]:
        """アラートを送信"""
        level = alert_data.get("level", "info")
        service = alert_data.get("service", "unknown")
        alert_key = f"{service}_{level}"

        # レート制限チェック
        if not self._check_rate_limit(alert_key, level):
            logger.warning(f"Rate limit exceeded for alert: {alert_key}")
            return {"rate_limited": True}

        # 通知チャネルを取得
        channels = self.notification_config.get(level, [NotificationChannel.SLACK])

        # 各チャネルで通知を送信
        results = {}
        for channel in channels:
            try:
                if channel == NotificationChannel.EMAIL:
                    results["email"] = await self.email_notifier.send_alert(alert_data)
                elif channel == NotificationChannel.SLACK:
                    results["slack"] = await self.slack_notifier.send_alert(alert_data)
                elif channel == NotificationChannel.WEBHOOK:
                    results["webhook"] = await self.webhook_notifier.send_alert(
                        alert_data
                    )
            except Exception as e:
                logger.error(f"Failed to send alert via {channel.value}: {e}")
                results[channel.value] = False

        # 送信履歴を記録
        self._record_sent_alert(alert_key)

        return results

    def _check_rate_limit(self, alert_key: str, level: str) -> bool:
        """レート制限をチェック"""
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)

        # 送信履歴を取得
        sent_times = self.sent_alerts.get(alert_key, [])

        # 1時間以内の送信回数をカウント
        recent_sends = [t for t in sent_times if t > hour_ago]

        # レート制限をチェック
        rate_limit = self.rate_limits.get(
            level, {"max_per_hour": 50, "cooldown_minutes": 30}
        )

        if len(recent_sends) >= rate_limit["max_per_hour"]:
            return False

        # クールダウンをチェック
        if recent_sends:
            last_send = max(recent_sends)
            cooldown_minutes = rate_limit["cooldown_minutes"]
            if now - last_send < timedelta(minutes=cooldown_minutes):
                return False

        return True

    def _record_sent_alert(self, alert_key: str):
        """送信履歴を記録"""
        now = datetime.utcnow()

        if alert_key not in self.sent_alerts:
            self.sent_alerts[alert_key] = []

        self.sent_alerts[alert_key].append(now)

        # 古い履歴を削除（24時間以上前）
        day_ago = now - timedelta(days=1)
        self.sent_alerts[alert_key] = [
            t for t in self.sent_alerts[alert_key] if t > day_ago
        ]

    async def send_test_alert(self, level: str = "info") -> Dict[str, bool]:
        """テストアラートを送信"""
        test_alert_data = {
            "id": f"test_{int(datetime.now().timestamp())}",
            "level": level,
            "title": "Test Alert",
            "message": "This is a test alert from AICA-SyS monitoring system.",
            "service": "monitoring_system",
            "timestamp": datetime.utcnow().isoformat(),
        }

        return await self.send_alert(test_alert_data)

    def get_notification_stats(self) -> Dict[str, Any]:
        """通知統計を取得"""
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)

        stats = {
            "total_alerts_sent": 0,
            "alerts_last_hour": 0,
            "alerts_last_day": 0,
            "by_level": {},
            "by_service": {},
        }

        for alert_key, sent_times in self.sent_alerts.items():
            service, level = alert_key.rsplit("_", 1)

            # レベル別統計
            if level not in stats["by_level"]:
                stats["by_level"][level] = 0
            stats["by_level"][level] += len(sent_times)

            # サービス別統計
            if service not in stats["by_service"]:
                stats["by_service"][service] = 0
            stats["by_service"][service] += len(sent_times)

            # 時間別統計
            stats["total_alerts_sent"] += len(sent_times)
            stats["alerts_last_hour"] += len([t for t in sent_times if t > hour_ago])
            stats["alerts_last_day"] += len([t for t in sent_times if t > day_ago])

        return stats


# グローバルなアラートサービスインスタンス
_alert_service_instance: Optional[AlertService] = None


def get_alert_service() -> AlertService:
    """アラートサービスインスタンスを取得"""
    global _alert_service_instance
    if _alert_service_instance is None:
        _alert_service_instance = AlertService()
    return _alert_service_instance
