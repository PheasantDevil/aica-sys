"""
Engagement Service for AICA-SyS
Phase 9-2: User engagement enhancement
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from models.engagement import (BadgeDB, CommentDB, FollowDB, NotificationDB,
                                NotificationType, ReactionDB, ReviewDB,
                                UserBadgeDB, UserPointDB)

logger = logging.getLogger(__name__)


class EngagementService:
    """エンゲージメントサービス"""

    def __init__(self, db: Session):
        self.db = db

    # コメント機能
    async def create_comment(
        self,
        content_id: str,
        user_id: str,
        content: str,
        parent_id: Optional[int] = None
    ) -> CommentDB:
        """コメントを作成"""
        comment = CommentDB(
            content_id=content_id,
            user_id=user_id,
            content=content,
            parent_id=parent_id
        )
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)

        # ポイント付与
        await self._add_points(user_id, 5, "comment")

        # 通知を送信（親コメントへの返信の場合）
        if parent_id:
            parent_comment = self.db.query(CommentDB).filter(
                CommentDB.id == parent_id
            ).first()
            if parent_comment and parent_comment.user_id != user_id:
                await self.create_notification(
                    user_id=parent_comment.user_id,
                    notification_type=NotificationType.REPLY,
                    title="新しい返信",
                    content=f"あなたのコメントに返信がありました",
                    link=f"/content/{content_id}#comment-{comment.id}"
                )

        logger.info(f"Comment created: {comment.id}")
        return comment

    async def get_comments(
        self,
        content_id: str,
        limit: int = 50
    ) -> List[CommentDB]:
        """コメント一覧を取得"""
        comments = self.db.query(CommentDB).filter(
            CommentDB.content_id == content_id
        ).order_by(CommentDB.created_at.desc()).limit(limit).all()
        return comments

    # レビュー機能
    async def create_review(
        self,
        content_id: str,
        user_id: str,
        rating: int,
        title: str,
        content: str
    ) -> ReviewDB:
        """レビューを作成"""
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")

        review = ReviewDB(
            content_id=content_id,
            user_id=user_id,
            rating=rating,
            title=title,
            content=content
        )
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)

        # ポイント付与
        await self._add_points(user_id, 10, "review")

        logger.info(f"Review created: {review.id}")
        return review

    async def get_reviews(
        self,
        content_id: str,
        limit: int = 20
    ) -> List[ReviewDB]:
        """レビュー一覧を取得"""
        reviews = self.db.query(ReviewDB).filter(
            ReviewDB.content_id == content_id
        ).order_by(ReviewDB.created_at.desc()).limit(limit).all()
        return reviews

    async def get_average_rating(self, content_id: str) -> float:
        """平均評価を取得"""
        from sqlalchemy import func
        result = self.db.query(func.avg(ReviewDB.rating)).filter(
            ReviewDB.content_id == content_id
        ).scalar()
        return float(result) if result else 0.0

    # リアクション機能
    async def add_reaction(
        self,
        target_type: str,
        target_id: str,
        user_id: str,
        reaction_type: str
    ) -> ReactionDB:
        """リアクションを追加"""
        # 既存のリアクションを確認
        existing = self.db.query(ReactionDB).filter(
            ReactionDB.target_type == target_type,
            ReactionDB.target_id == target_id,
            ReactionDB.user_id == user_id,
            ReactionDB.reaction_type == reaction_type
        ).first()

        if existing:
            return existing

        reaction = ReactionDB(
            target_type=target_type,
            target_id=target_id,
            user_id=user_id,
            reaction_type=reaction_type
        )
        self.db.add(reaction)
        self.db.commit()
        self.db.refresh(reaction)

        # ポイント付与
        await self._add_points(user_id, 2, "reaction")

        logger.info(f"Reaction added: {reaction.id}")
        return reaction

    async def remove_reaction(
        self,
        target_type: str,
        target_id: str,
        user_id: str,
        reaction_type: str
    ) -> bool:
        """リアクションを削除"""
        reaction = self.db.query(ReactionDB).filter(
            ReactionDB.target_type == target_type,
            ReactionDB.target_id == target_id,
            ReactionDB.user_id == user_id,
            ReactionDB.reaction_type == reaction_type
        ).first()

        if reaction:
            self.db.delete(reaction)
            self.db.commit()
            return True
        return False

    async def get_reaction_counts(
        self,
        target_type: str,
        target_id: str
    ) -> Dict[str, int]:
        """リアクション数を取得"""
        from sqlalchemy import func
        counts = self.db.query(
            ReactionDB.reaction_type,
            func.count(ReactionDB.id)
        ).filter(
            ReactionDB.target_type == target_type,
            ReactionDB.target_id == target_id
        ).group_by(ReactionDB.reaction_type).all()

        return {reaction_type: count for reaction_type, count in counts}

    # フォロー機能
    async def follow_user(
        self,
        follower_id: str,
        following_id: str
    ) -> FollowDB:
        """ユーザーをフォロー"""
        if follower_id == following_id:
            raise ValueError("Cannot follow yourself")

        # 既存のフォローを確認
        existing = self.db.query(FollowDB).filter(
            FollowDB.follower_id == follower_id,
            FollowDB.following_id == following_id
        ).first()

        if existing:
            return existing

        follow = FollowDB(
            follower_id=follower_id,
            following_id=following_id
        )
        self.db.add(follow)
        self.db.commit()
        self.db.refresh(follow)

        # 通知を送信
        await self.create_notification(
            user_id=following_id,
            notification_type=NotificationType.FOLLOW,
            title="新しいフォロワー",
            content=f"あなたをフォローしました",
            link=f"/user/{follower_id}"
        )

        logger.info(f"Follow created: {follower_id} -> {following_id}")
        return follow

    async def unfollow_user(
        self,
        follower_id: str,
        following_id: str
    ) -> bool:
        """ユーザーをアンフォロー"""
        follow = self.db.query(FollowDB).filter(
            FollowDB.follower_id == follower_id,
            FollowDB.following_id == following_id
        ).first()

        if follow:
            self.db.delete(follow)
            self.db.commit()
            return True
        return False

    async def get_followers(
        self,
        user_id: str,
        limit: int = 100
    ) -> List[FollowDB]:
        """フォロワー一覧を取得"""
        followers = self.db.query(FollowDB).filter(
            FollowDB.following_id == user_id
        ).limit(limit).all()
        return followers

    async def get_following(
        self,
        user_id: str,
        limit: int = 100
    ) -> List[FollowDB]:
        """フォロー中一覧を取得"""
        following = self.db.query(FollowDB).filter(
            FollowDB.follower_id == user_id
        ).limit(limit).all()
        return following

    # 通知機能
    async def create_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        content: str,
        link: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> NotificationDB:
        """通知を作成"""
        notification = NotificationDB(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            content=content,
            link=link,
            metadata=metadata
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)

        logger.info(f"Notification created: {notification.id}")
        return notification

    async def get_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[NotificationDB]:
        """通知一覧を取得"""
        query = self.db.query(NotificationDB).filter(
            NotificationDB.user_id == user_id
        )

        if unread_only:
            query = query.filter(NotificationDB.is_read == False)

        notifications = query.order_by(
            NotificationDB.created_at.desc()
        ).limit(limit).all()

        return notifications

    async def mark_notification_read(
        self,
        notification_id: int,
        user_id: str
    ) -> bool:
        """通知を既読にする"""
        notification = self.db.query(NotificationDB).filter(
            NotificationDB.id == notification_id,
            NotificationDB.user_id == user_id
        ).first()

        if notification:
            notification.is_read = True
            self.db.commit()
            return True
        return False

    async def mark_all_read(self, user_id: str) -> int:
        """全通知を既読にする"""
        count = self.db.query(NotificationDB).filter(
            NotificationDB.user_id == user_id,
            NotificationDB.is_read == False
        ).update({"is_read": True})
        self.db.commit()
        return count

    # ポイント・ゲーミフィケーション機能
    async def _add_points(
        self,
        user_id: str,
        points: int,
        reason: str
    ) -> UserPointDB:
        """ポイントを追加"""
        user_point = self.db.query(UserPointDB).filter(
            UserPointDB.user_id == user_id
        ).first()

        if not user_point:
            user_point = UserPointDB(
                user_id=user_id,
                total_points=0,
                level=1
            )
            self.db.add(user_point)

        old_level = user_point.level
        user_point.total_points += points

        # レベルアップ判定（100ポイントごとにレベルアップ）
        new_level = (user_point.total_points // 100) + 1
        if new_level > user_point.level:
            user_point.level = new_level

            # レベルアップ通知
            await self.create_notification(
                user_id=user_id,
                notification_type=NotificationType.LEVEL_UP,
                title="レベルアップ！",
                content=f"レベル{new_level}に到達しました！",
                metadata={"old_level": old_level, "new_level": new_level}
            )

        self.db.commit()
        self.db.refresh(user_point)

        # バッジチェック
        await self._check_badges(user_id, user_point.total_points)

        return user_point

    async def get_user_points(self, user_id: str) -> UserPointDB:
        """ユーザーポイントを取得"""
        user_point = self.db.query(UserPointDB).filter(
            UserPointDB.user_id == user_id
        ).first()

        if not user_point:
            user_point = UserPointDB(
                user_id=user_id,
                total_points=0,
                level=1
            )
            self.db.add(user_point)
            self.db.commit()
            self.db.refresh(user_point)

        return user_point

    async def _check_badges(self, user_id: str, total_points: int):
        """バッジ獲得チェック"""
        # 獲得可能なバッジを取得
        badges = self.db.query(BadgeDB).filter(
            BadgeDB.points_required <= total_points
        ).all()

        # すでに獲得済みのバッジを取得
        earned_badge_ids = [
            ub.badge_id for ub in self.db.query(UserBadgeDB).filter(
                UserBadgeDB.user_id == user_id
            ).all()
        ]

        # 新しいバッジを付与
        for badge in badges:
            if badge.id not in earned_badge_ids:
                user_badge = UserBadgeDB(
                    user_id=user_id,
                    badge_id=badge.id
                )
                self.db.add(user_badge)

                # バッジ獲得通知
                await self.create_notification(
                    user_id=user_id,
                    notification_type=NotificationType.BADGE,
                    title="バッジ獲得！",
                    content=f"「{badge.name}」バッジを獲得しました！",
                    metadata={"badge_id": badge.id, "badge_name": badge.name}
                )

        self.db.commit()

    async def get_user_badges(self, user_id: str) -> List[Dict[str, Any]]:
        """ユーザーのバッジ一覧を取得"""
        user_badges = self.db.query(UserBadgeDB, BadgeDB).join(
            BadgeDB, UserBadgeDB.badge_id == BadgeDB.id
        ).filter(
            UserBadgeDB.user_id == user_id
        ).all()

        return [
            {
                "badge": badge,
                "earned_at": user_badge.earned_at
            }
            for user_badge, badge in user_badges
        ]

    async def get_leaderboard(
        self,
        limit: int = 100
    ) -> List[UserPointDB]:
        """リーダーボードを取得"""
        leaderboard = self.db.query(UserPointDB).order_by(
            UserPointDB.total_points.desc()
        ).limit(limit).all()
        return leaderboard

