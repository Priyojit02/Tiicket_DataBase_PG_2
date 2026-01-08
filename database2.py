# ============================================
# CORE - Database Connection & Session Management
# ============================================

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine
from typing import AsyncGenerator
from app.core.config import settings


# Async Engine for FastAPI
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# Sync Engine for Alembic migrations
sync_engine = create_engine(
    settings.database_sync_url,
    echo=settings.debug,
    pool_pre_ping=True
)

# Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


# Base class for all models
class Base(DeclarativeBase):
    """Base class for SQLAlchemy models"""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injection for database sessions.
    Use in FastAPI endpoints: db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database - create all tables and run migrations"""
    async with async_engine.begin() as conn:
        # Create tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)

        # Run automatic migrations for development
        await conn.run_sync(run_auto_migrations)


def run_auto_migrations(connection):
    """Run automatic database migrations for development"""
    # Only run in development/debug mode
    if not settings.debug:
        return

    try:
        # Check and add has_attachments column to email_sources table
        result = connection.execute("PRAGMA table_info(email_sources)")
        columns = [row[1] for row in result.fetchall()]

        if "has_attachments" not in columns:
            print("🔄 Auto-migrating: Adding has_attachments column to email_sources...")
            connection.execute("ALTER TABLE email_sources ADD COLUMN has_attachments BOOLEAN DEFAULT FALSE")
            connection.commit()
            print("✅ Auto-migration completed: has_attachments column added")
        else:
            print("✅ has_attachments column already exists")

    except Exception as e:
        print(f"⚠️  Auto-migration failed (this is normal for fresh databases): {e}")


async def close_db():
    """Close database connections"""
    await async_engine.dispose()
