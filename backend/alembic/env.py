import os
import sys
from logging.config import fileConfig
from pathlib import Path

# Load environment variables from .env.local
from dotenv import load_dotenv

# backend/.env.localを読み込む（backend/alembic/env.pyから見て../）
env_path = Path(__file__).parent.parent / '.env.local'
load_dotenv(env_path)

from alembic import context
from sqlalchemy import create_engine, engine_from_config, pool

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your models
from models.base import Base
from models.collection import AnalysisResult, CollectionJob
from models.content import Article, Newsletter, Trend
from models.subscription import Subscription
from models.user import User
from models.automated_content import (AutomatedContentDB, TrendDataDB,
                                      SourceDataDB, ContentGenerationLogDB)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Use environment variable for database URL
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL environment variable is required")
    
    # Convert postgres:// to postgresql+psycopg2:// for SQLAlchemy
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    
    # Remove invalid connection options
    if "supa=base-pooler.x" in url:
        url = url.replace("&supa=base-pooler.x", "")
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Use environment variable for database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required")
    
    # Convert postgres:// to postgresql+psycopg2:// for SQLAlchemy
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
    
    # Remove invalid connection options
    if "supa=base-pooler.x" in database_url:
        database_url = database_url.replace("&supa=base-pooler.x", "")
    
    connectable = create_engine(
        database_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
