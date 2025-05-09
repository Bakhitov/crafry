"""
Модуль для работы с базой данных через SQLAlchemy
"""
from typing import Generator, Dict, Any, AsyncGenerator
import os
from contextlib import asynccontextmanager

from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from db.settings import db_settings

# Определяем, использовать ли асинхронное подключение
USE_ASYNC = db_settings.use_async_driver

# Создаем SQLAlchemy Engine для синхронного подключения
db_url: str = db_settings.get_db_url(for_async=False)
engine_kwargs = db_settings.get_engine_kwargs()
db_engine: Engine = create_engine(db_url, **engine_kwargs)

# Создаем класс SessionLocal для синхронного подключения
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

# Если используем асинхронное подключение, также создаем асинхронный движок
if USE_ASYNC:
    async_db_url: str = db_settings.get_db_url(for_async=True)
    async_engine = create_async_engine(async_db_url, **engine_kwargs)
    AsyncSessionLocal = async_sessionmaker(
        async_engine,
        autocommit=False, 
        autoflush=False,
        expire_on_commit=False,
    )


def get_db() -> Generator[Session, None, None]:
    """
    Зависимость для получения синхронной сессии базы данных.
    
    Yields:
        Session: Сессия SQLAlchemy.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Контекстный менеджер для получения асинхронной сессии.
    
    Yields:
        AsyncSession: Асинхронная сессия SQLAlchemy.
    """
    if not USE_ASYNC:
        raise RuntimeError("Асинхронное подключение не настроено. Установите USE_ASYNC_DRIVER=True")
        
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость для получения асинхронной сессии базы данных.
    Используется для внедрения зависимостей в FastAPI.
    
    Yields:
        AsyncSession: Асинхронная сессия SQLAlchemy.
    """
    async with get_async_session() as session:
        yield session


async def init_db() -> None:
    """
    Инициализация базы данных. 
    Вызывается при запуске приложения.
    
    Проверяет соединение с базой данных.
    """
    # Для синхронного соединения проверяем через ping
    with db_engine.connect() as conn:
        conn.execute("SELECT 1")
    
    # Для асинхронного соединения тоже проверяем, если оно настроено
    if USE_ASYNC:
        async with async_engine.connect() as conn:
            await conn.execute("SELECT 1")


async def close_db() -> None:
    """
    Закрытие соединений с базой данных.
    Вызывается при остановке приложения.
    """
    db_engine.dispose()
    
    if USE_ASYNC:
        await async_engine.dispose()


def get_db_stats() -> Dict[str, Any]:
    """
    Получение статистики по базе данных для мониторинга.
    
    Returns:
        Dict[str, Any]: Статистика соединений.
    """
    stats = {
        "sync_mode": "sqlalchemy",
        "async_enabled": USE_ASYNC,
        "engine_stats": db_engine.pool.status(),
    }
    
    if USE_ASYNC:
        stats.update({
            "async_engine_stats": {
                "pool_size": async_engine.pool.size(),
                "checkedin": async_engine.pool.checkedin(),
                "overflow": async_engine.pool.overflow(),
                "checkedout": async_engine.pool.checkedout(),
            }
        })
    
    return stats
