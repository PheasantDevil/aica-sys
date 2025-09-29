"""
データベース接続設定 - パフォーマンス最適化版
"""

import logging
import os

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool, StaticPool

logger = logging.getLogger(__name__)

# データベースURL（環境変数から取得、デフォルトはSQLite）
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aica_sys.db")

# データベースタイプの判定
is_sqlite = "sqlite" in DATABASE_URL
is_postgresql = "postgresql" in DATABASE_URL

# 接続プール設定
if is_sqlite:
    # SQLite用の設定
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        pool_pre_ping=True,
        echo=False,
    )
elif is_postgresql:
    # PostgreSQL用の設定（本番環境）
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=20,  # 接続プールサイズ
        max_overflow=30,  # 最大オーバーフロー接続数
        pool_pre_ping=True,  # 接続の生存確認
        pool_recycle=3600,  # 接続のリサイクル時間（1時間）
        echo=False,
    )
else:
    # その他のデータベース
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        echo=False,
    )

# セッションファクトリ
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,  # パフォーマンス向上
)

# ベースクラス
Base = declarative_base()

# 接続プールの監視
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """SQLite用の最適化設定"""
    if is_sqlite:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")  # WALモードでパフォーマンス向上
        cursor.execute("PRAGMA synchronous=NORMAL")  # 同期モードの最適化
        cursor.execute("PRAGMA cache_size=10000")  # キャッシュサイズの増加
        cursor.execute("PRAGMA temp_store=MEMORY")  # 一時テーブルをメモリに
        cursor.execute("PRAGMA mmap_size=268435456")  # メモリマップサイズ
        cursor.close()

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """接続チェックアウト時のログ"""
    logger.debug("Connection checked out from pool")

@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """接続チェックイン時のログ"""
    logger.debug("Connection checked in to pool")

def get_db():
    """データベースセッションを取得（最適化版）"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def get_db_session():
    """直接セッションを取得（バッチ処理用）"""
    return SessionLocal()

def close_db_session(session):
    """セッションを明示的に閉じる"""
    if session:
        session.close()

def init_db():
    """データベースを初期化（テーブル作成）"""
    try:
        # すべてのモデルをインポートしてテーブルを作成
        from models.audit import AuditEventDB
        from models.content import Article, Newsletter, Trend
        from models.subscription import Subscription
        from models.user import User

        # テーブルを作成
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        return False

def drop_db():
    """データベースを削除（全テーブル削除）"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
        return True
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        return False