"""
Пример маршрута для работы с SQLAlchemy и Neon DB
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from sqlalchemy.orm import Session

from db.session import get_db, get_async_db, get_db_stats

router = APIRouter(prefix="/db", tags=["database"])


@router.get("/status")
async def get_db_status() -> Dict[str, Any]:
    """
    Получение статуса базы данных.
    
    Returns:
        Dict[str, Any]: Статус базы данных
    """
    return {
        "status": "online",
        "stats": get_db_stats(),
    }


@router.get("/examples")
def get_examples(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Получение списка примеров из базы данных через синхронный SQLAlchemy.
    
    Args:
        db (Session): Сессия SQLAlchemy
        
    Returns:
        List[Dict[str, Any]]: Список примеров
    """
    try:
        # В реальном приложении здесь будет запрос к таблице examples
        # result = db.execute(select(ExampleModel)).scalars().all()
        
        # Пока просто выполняем тестовый запрос к БД
        result = db.execute(text("SELECT 1 as id, 'Пример 1' as name"))
        rows = result.fetchall()
        
        # Преобразуем результаты в список словарей
        examples = [
            {"id": str(row.id), "name": row.name} 
            for row in rows
        ]
        
        # Добавляем тестовые данные
        examples.extend([
            {"id": "2", "name": "Пример 2"},
            {"id": "3", "name": "Пример 3"}
        ])
        
        return examples
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")


@router.get("/async-examples")
async def get_async_examples(db: AsyncSession = Depends(get_async_db)) -> List[Dict[str, Any]]:
    """
    Получение списка примеров из базы данных через асинхронный SQLAlchemy.
    
    Args:
        db (AsyncSession): Асинхронная сессия SQLAlchemy
        
    Returns:
        List[Dict[str, Any]]: Список примеров
    """
    try:
        # В реальном приложении здесь будет асинхронный запрос к таблице examples
        # result = await db.execute(select(ExampleModel))
        # rows = result.scalars().all()
        
        # Пока просто выполняем тестовый запрос к БД
        result = await db.execute(text("SELECT 1 as id, 'Асинхронный пример' as name"))
        rows = result.fetchall()
        
        # Преобразуем результаты в список словарей
        examples = [
            {"id": str(row.id), "name": row.name} 
            for row in rows
        ]
        
        # Добавляем тестовые данные
        examples.extend([
            {"id": "2", "name": "Асинхронный пример 2"},
            {"id": "3", "name": "Асинхронный пример 3"}
        ])
        
        return examples
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")


@router.post("/examples")
def create_example(data: Dict[str, Any], db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Создание нового примера через SQLAlchemy.
    
    Args:
        data (Dict[str, Any]): Данные для создания примера
        db (Session): Сессия SQLAlchemy
        
    Returns:
        Dict[str, Any]: Созданный пример
    """
    try:
        # В реальном приложении здесь будет создание записи в таблице examples
        # example = ExampleModel(name=data["name"])
        # db.add(example)
        # db.commit()
        # db.refresh(example)
        
        # Пока возвращаем тестовые данные
        return {
            "id": "100",
            "name": data.get("name", "Новый пример")
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")


@router.post("/async-examples")
async def create_async_example(data: Dict[str, Any], db: AsyncSession = Depends(get_async_db)) -> Dict[str, Any]:
    """
    Создание нового примера через асинхронный SQLAlchemy.
    
    Args:
        data (Dict[str, Any]): Данные для создания примера
        db (AsyncSession): Асинхронная сессия SQLAlchemy
        
    Returns:
        Dict[str, Any]: Созданный пример
    """
    try:
        # В реальном приложении здесь будет асинхронное создание записи
        # example = ExampleModel(name=data["name"])
        # db.add(example)
        # await db.commit()
        # await db.refresh(example)
        
        # Пока возвращаем тестовые данные
        return {
            "id": "200",
            "name": data.get("name", "Новый асинхронный пример")
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}") 