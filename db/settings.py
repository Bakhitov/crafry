from os import getenv
from typing import Optional, Dict, Any

from pydantic_settings import BaseSettings


class DbSettings(BaseSettings):
    """Database settings that can be set using environment variables.

    Reference: https://docs.pydantic.dev/latest/usage/pydantic_settings/
    """

    # Database configuration
    db_host: Optional[str] = None
    db_port: Optional[int] = None
    db_user: Optional[str] = None
    db_pass: Optional[str] = None
    db_database: Optional[str] = None
    db_driver: str = "postgresql+psycopg"
    # Create/Upgrade database on startup using alembic
    migrate_db: bool = False
    
    # Neon DB configuration
    database_url: Optional[str] = None
    database_url_async: Optional[str] = None
    database_url_unpooled: Optional[str] = None
    
    # Pool settings
    pool_size: int = 5
    max_overflow: int = 10
    
    # Использовать ли асинхронные драйверы для подключения
    use_async_driver: bool = False

    def get_db_url(self, for_async: bool = False) -> str:
        """
        Получает URL для подключения к базе данных.
        
        Приоритет:
        1. Neon DB через DATABASE_URL или DATABASE_URL_ASYNC, если доступны
        2. Стандартную строку подключения SQLAlchemy через параметры
        3. Локальную базу данных, если в dev-режиме
        
        Args:
            for_async: использовать ли асинхронный URL
            
        Returns:
            str: URL подключения к базе данных
        """
        # Проверяем прямые URL подключения для Neon DB
        if for_async and self.database_url_async:
            return self.database_url_async
        
        if not for_async and self.database_url:
            return self.database_url
            
        # Если нет прямых URL, но есть DATABASE_URL из Neon, адаптируем его
        if self.database_url:
            # Преобразуем postgres:// в postgresql:// для SQLAlchemy
            base_url = self.database_url.replace("postgres://", "postgresql://")
            
            if for_async:
                # Для асинхронного подключения используем asyncpg
                return base_url.replace("postgresql://", "postgresql+asyncpg://")
            return base_url
        
        # В противном случае строим URL из отдельных параметров
        driver = "postgresql+asyncpg" if for_async else self.db_driver
        
        db_url = "{}://{}{}@{}:{}/{}".format(
            driver,
            self.db_user,
            f":{self.db_pass}" if self.db_pass else "",
            self.db_host,
            self.db_port,
            self.db_database,
        )
        
        # Используем локальную базу данных, если RUNTIME_ENV не установлен
        if "None" in db_url and getenv("RUNTIME_ENV") is None:
            from workspace.dev_resources import dev_db

            # logger.debug("Using local connection")
            local_db_url = dev_db.get_db_connection_local()
            if local_db_url:
                if for_async:
                    # Если нужно асинхронное подключение, заменяем драйвер
                    return local_db_url.replace("postgresql://", "postgresql+asyncpg://")
                return local_db_url

        # Проверяем валидность URL
        if "None" in db_url or db_url is None:
            raise ValueError("Could not build database connection")
        return db_url
    
    def get_engine_kwargs(self) -> Dict[str, Any]:
        """
        Возвращает аргументы для создания SQLAlchemy Engine
        
        Returns:
            Dict[str, Any]: аргументы для engine
        """
        kwargs = {
            "pool_pre_ping": True,
            "pool_size": self.pool_size,
            "max_overflow": self.max_overflow,
        }
        
        # Добавляем SSL настройки для Neon DB
        if self.database_url and "neon.tech" in self.database_url:
            kwargs.update({
                "connect_args": {
                    "sslmode": "require"
                }
            })
            
        return kwargs


db_settings = DbSettings(
    # Загружаем из переменных окружения
    db_host=getenv("DB_HOST"),
    db_port=getenv("DB_PORT"),
    db_user=getenv("DB_USER"),
    db_pass=getenv("DB_PASS"),
    db_database=getenv("DB_DATABASE"),
    migrate_db=getenv("MIGRATE_DB", "False").lower() in ("true", "1", "yes"),
    
    # Neon DB настройки
    database_url=getenv("DATABASE_URL"),
    database_url_async=getenv("DATABASE_URL_ASYNC"),
    database_url_unpooled=getenv("DATABASE_URL_UNPOOLED"),
    
    # Использовать асинхронный драйвер по умолчанию
    use_async_driver=getenv("USE_ASYNC_DRIVER", "False").lower() in ("true", "1", "yes"),
)
