from typing import List, Any, TypeVar, Generic
from pydantic import BaseModel
from .base import connection
from .models import Group
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete, func


@connection()
async def add_many(session, data: List[BaseModel]):
    values_list = [item.model_dump(exclude_unset=True) for item in data]
    logger.info(f"Добавление нескольких записей. Количество: {len(values_list)}")
    new_instances = [Group(**values) for values in values_list]
    session.add_all(new_instances)
    try:
        await session.commit()
        logger.info(f"Успешно добавлено {len(new_instances)} записей.")
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Ошибка при добавлении нескольких записей: {e}")
        raise e
    return new_instances


@connection()
async def delete_group(session, name_group: str):
    query = sqlalchemy_delete(Group).filter(Group.group_name == name_group)
    try:
        result = await session.execute(query)
        await session.commit()
        logger.info(f"Удалено {result.rowcount} записей.")
        return result.rowcount
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Ошибка при удалении записей: {e}")
        raise e


@connection()
async def delete_chanel(session, name_chanel: str):
    query = sqlalchemy_delete(Group).filter(Group.chat_name == name_chanel)
    try:
        result = await session.execute(query)
        await session.commit()
        logger.info(f"Удалено {result.rowcount} записей.")
        return result.rowcount
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Ошибка при удалении записей: {e}")
        raise e


@connection()
async def get_group_counts(session):
    query = (
        select(Group.group_name, func.count(Group.id).label("count"))
        .group_by(Group.group_name)
        .order_by(Group.group_name)  # Можно использовать для сортировки
    )
    try:
        result = await session.execute(query)
        groups = result.fetchall()
        logger.info(f"Получено {len(groups)} групп с количеством записей.")
        return [{"group_name": row.group_name, "count": row.count} for row in groups]
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении данных: {e}")
        raise e


@connection()
async def find_all(session, group_name: str):
    query = select(Group.chat_name).filter(Group.group_name == group_name)
    try:
        result = await session.execute(query)
        chanels = result.fetchall()
        logger.info(f"Получено {len(chanels)} каналов для группы {group_name}.")
        return [row.chat_name for row in chanels]
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении данных: {e}")
        raise e
