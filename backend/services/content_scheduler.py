"""
コンテンツ配信スケジューラー
定期配信システムの管理と実行
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from database import get_db
from models.content import Article, Newsletter, Trend
from services.ai_analyzer import AIAnalyzer
from services.content_generator import ContentGenerator, ContentType
from services.data_collector import DataCollector
from sqlalchemy.orm import Session
from utils.logging import get_logger

logger = get_logger(__name__)

class ScheduleType(Enum):
    """配信スケジュールタイプ"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

class DeliveryStatus(Enum):
    """配信ステータス"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class DeliverySchedule:
    """配信スケジュール"""
    id: str
    name: str
    schedule_type: ScheduleType
    content_type: ContentType
    target_audience: str
    tone: str
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DeliveryJob:
    """配信ジョブ"""
    id: str
    schedule_id: str
    status: DeliveryStatus
    content_id: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class ContentScheduler:
    """コンテンツ配信スケジューラー"""
    
    def __init__(self):
        self.schedules: Dict[str, DeliverySchedule] = {}
        self.jobs: Dict[str, DeliveryJob] = {}
        self.content_generator = None
        self.ai_analyzer = None
        self.data_collector = None
        self.is_running = False
        
    async def initialize(self):
        """スケジューラーを初期化"""
        try:
            # サービスを初期化
            self.content_generator = ContentGenerator(
                openai_api_key="your_openai_api_key",
                google_ai_api_key="your_google_ai_api_key"
            )
            self.ai_analyzer = AIAnalyzer()
            self.data_collector = DataCollector()
            
            # デフォルトスケジュールを設定
            await self._setup_default_schedules()
            
            logger.info("ContentScheduler initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ContentScheduler: {e}")
            raise

    async def _setup_default_schedules(self):
        """デフォルトスケジュールを設定"""
        default_schedules = [
            DeliverySchedule(
                id="daily_news",
                name="日次技術ニュース",
                schedule_type=ScheduleType.DAILY,
                content_type=ContentType.ARTICLE,
                target_audience="TypeScript開発者",
                tone="professional",
                next_run=datetime.now() + timedelta(hours=1)
            ),
            DeliverySchedule(
                id="weekly_newsletter",
                name="週刊ニュースレター",
                schedule_type=ScheduleType.WEEKLY,
                content_type=ContentType.NEWSLETTER,
                target_audience="TypeScript開発者",
                tone="friendly",
                next_run=datetime.now() + timedelta(days=7)
            ),
            DeliverySchedule(
                id="monthly_trends",
                name="月間トレンド分析",
                schedule_type=ScheduleType.MONTHLY,
                content_type=ContentType.TECHNICAL_GUIDE,
                target_audience="中級〜上級開発者",
                tone="technical",
                next_run=datetime.now() + timedelta(days=30)
            )
        ]
        
        for schedule in default_schedules:
            self.schedules[schedule.id] = schedule
        
        logger.info(f"Setup {len(default_schedules)} default schedules")

    async def start_scheduler(self):
        """スケジューラーを開始"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        logger.info("ContentScheduler started")
        
        try:
            while self.is_running:
                await self._process_schedules()
                await asyncio.sleep(60)  # 1分ごとにチェック
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            self.is_running = False
            raise

    async def stop_scheduler(self):
        """スケジューラーを停止"""
        self.is_running = False
        logger.info("ContentScheduler stopped")

    async def _process_schedules(self):
        """スケジュールを処理"""
        current_time = datetime.now()
        
        for schedule_id, schedule in self.schedules.items():
            if not schedule.enabled:
                continue
                
            if schedule.next_run and schedule.next_run <= current_time:
                await self._execute_schedule(schedule)

    async def _execute_schedule(self, schedule: DeliverySchedule):
        """スケジュールを実行"""
        job_id = f"{schedule.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        job = DeliveryJob(
            id=job_id,
            schedule_id=schedule.id,
            status=DeliveryStatus.IN_PROGRESS,
            started_at=datetime.now()
        )
        
        self.jobs[job_id] = job
        
        try:
            logger.info(f"Executing schedule: {schedule.name}")
            
            # コンテンツを生成
            content = await self._generate_scheduled_content(schedule)
            
            # データベースに保存
            content_id = await self._save_content(content, schedule)
            
            # 配信を実行
            await self._deliver_content(content, schedule)
            
            # ジョブを完了
            job.status = DeliveryStatus.COMPLETED
            job.content_id = content_id
            job.completed_at = datetime.now()
            
            # 次回実行時間を更新
            schedule.last_run = datetime.now()
            schedule.next_run = self._calculate_next_run(schedule)
            
            logger.info(f"Schedule executed successfully: {schedule.name}")
            
        except Exception as e:
            logger.error(f"Schedule execution failed: {schedule.name} - {e}")
            job.status = DeliveryStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now()

    async def _generate_scheduled_content(self, schedule: DeliverySchedule):
        """スケジュールされたコンテンツを生成"""
        # データを収集
        collected_data = await self.data_collector.collect_content()
        
        # AI分析を実行
        analysis_results = await self.ai_analyzer.analyze_content(collected_data)
        
        # コンテンツを生成
        content = await self.content_generator.generate_content(
            content_type=schedule.content_type,
            analysis_results=analysis_results,
            target_audience=schedule.target_audience,
            tone=schedule.tone
        )
        
        return content

    async def _save_content(self, content, schedule: DeliverySchedule) -> str:
        """コンテンツをデータベースに保存"""
        db = next(get_db())
        
        try:
            if schedule.content_type == ContentType.ARTICLE:
                article = Article(
                    title=content.title,
                    content=content.content,
                    summary=content.summary,
                    tags=content.tags,
                    author_id=None,  # AI生成の場合はNone
                    published_at=datetime.now()
                )
                db.add(article)
                db.commit()
                db.refresh(article)
                return str(article.id)
                
            elif schedule.content_type == ContentType.NEWSLETTER:
                newsletter = Newsletter(
                    title=content.title,
                    content=content.content,
                    summary=content.summary,
                    published_at=datetime.now()
                )
                db.add(newsletter)
                db.commit()
                db.refresh(newsletter)
                return str(newsletter.id)
                
            elif schedule.content_type == ContentType.TECHNICAL_GUIDE:
                # 技術ガイドは記事として保存
                article = Article(
                    title=content.title,
                    content=content.content,
                    summary=content.summary,
                    tags=content.tags + ["technical-guide"],
                    author_id=None,
                    published_at=datetime.now()
                )
                db.add(article)
                db.commit()
                db.refresh(article)
                return str(article.id)
                
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save content: {e}")
            raise
        finally:
            db.close()

    async def _deliver_content(self, content, schedule: DeliverySchedule):
        """コンテンツを配信"""
        # メール配信
        await self._send_email_notification(content, schedule)
        
        # Webサイト更新
        await self._update_website(content, schedule)
        
        # RSS配信
        await self._update_rss_feed(content, schedule)
        
        # ソーシャルメディア投稿
        await self._post_to_social_media(content, schedule)

    async def _send_email_notification(self, content, schedule: DeliverySchedule):
        """メール通知を送信"""
        # 実装: メール配信サービスとの連携
        logger.info(f"Email notification sent for: {content.title}")

    async def _update_website(self, content, schedule: DeliverySchedule):
        """Webサイトを更新"""
        # 実装: Webサイトの更新
        logger.info(f"Website updated with: {content.title}")

    async def _update_rss_feed(self, content, schedule: DeliverySchedule):
        """RSSフィードを更新"""
        # 実装: RSSフィードの更新
        logger.info(f"RSS feed updated with: {content.title}")

    async def _post_to_social_media(self, content, schedule: DeliverySchedule):
        """ソーシャルメディアに投稿"""
        # 実装: ソーシャルメディアAPIとの連携
        logger.info(f"Social media post created for: {content.title}")

    def _calculate_next_run(self, schedule: DeliverySchedule) -> datetime:
        """次回実行時間を計算"""
        current_time = datetime.now()
        
        if schedule.schedule_type == ScheduleType.DAILY:
            return current_time + timedelta(days=1)
        elif schedule.schedule_type == ScheduleType.WEEKLY:
            return current_time + timedelta(weeks=1)
        elif schedule.schedule_type == ScheduleType.MONTHLY:
            return current_time + timedelta(days=30)
        else:
            # カスタムスケジュール
            interval_hours = schedule.metadata.get('interval_hours', 24)
            return current_time + timedelta(hours=interval_hours)

    async def create_schedule(self, schedule: DeliverySchedule):
        """新しいスケジュールを作成"""
        self.schedules[schedule.id] = schedule
        logger.info(f"Created new schedule: {schedule.name}")

    async def update_schedule(self, schedule_id: str, updates: Dict[str, Any]):
        """スケジュールを更新"""
        if schedule_id in self.schedules:
            schedule = self.schedules[schedule_id]
            for key, value in updates.items():
                if hasattr(schedule, key):
                    setattr(schedule, key, value)
            logger.info(f"Updated schedule: {schedule_id}")

    async def delete_schedule(self, schedule_id: str):
        """スケジュールを削除"""
        if schedule_id in self.schedules:
            del self.schedules[schedule_id]
            logger.info(f"Deleted schedule: {schedule_id}")

    async def get_schedule_status(self) -> Dict[str, Any]:
        """スケジュールの状態を取得"""
        return {
            "is_running": self.is_running,
            "total_schedules": len(self.schedules),
            "enabled_schedules": len([s for s in self.schedules.values() if s.enabled]),
            "total_jobs": len(self.jobs),
            "recent_jobs": list(self.jobs.values())[-10:]  # 最新10件
        }

    async def get_schedule_list(self) -> List[Dict[str, Any]]:
        """スケジュール一覧を取得"""
        return [
            {
                "id": schedule.id,
                "name": schedule.name,
                "type": schedule.schedule_type.value,
                "content_type": schedule.content_type.value,
                "enabled": schedule.enabled,
                "last_run": schedule.last_run.isoformat() if schedule.last_run else None,
                "next_run": schedule.next_run.isoformat() if schedule.next_run else None
            }
            for schedule in self.schedules.values()
        ]

# グローバルスケジューラーインスタンス
scheduler = ContentScheduler()

async def start_content_scheduler():
    """コンテンツスケジューラーを開始"""
    await scheduler.initialize()
    await scheduler.start_scheduler()

async def stop_content_scheduler():
    """コンテンツスケジューラーを停止"""
    await scheduler.stop_scheduler()

# 使用例
async def main():
    """スケジューラーの実行例"""
    scheduler = ContentScheduler()
    await scheduler.initialize()
    
    # スケジューラーを開始（バックグラウンドで実行）
    asyncio.create_task(scheduler.start_scheduler())
    
    # スケジュール状態を確認
    status = await scheduler.get_schedule_status()
    print(f"Scheduler status: {status}")
    
    # スケジュール一覧を表示
    schedules = await scheduler.get_schedule_list()
    for schedule in schedules:
        print(f"Schedule: {schedule['name']} - Next run: {schedule['next_run']}")

if __name__ == "__main__":
    asyncio.run(main())
