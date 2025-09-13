# Utils: Entities handling
# Утилиты для работы с Telegram entities

import json
from typing import List, Dict, Any
from aiogram.types import MessageEntity

def entities_to_dict(entities: List[MessageEntity]) -> List[Dict[str, Any]]:
    """
    Конвертирует список MessageEntity в словари для сохранения в БД
    
    Args:
        entities: Список Telegram entities
        
    Returns:
        Список словарей с данными entities
    """
    if not entities:
        return []
    
    result = []
    for entity in entities:
        entity_dict = {
            'type': entity.type,
            'offset': entity.offset,
            'length': entity.length
        }
        
        # Добавляем дополнительные поля в зависимости от типа
        if hasattr(entity, 'url') and entity.url:
            entity_dict['url'] = entity.url
        if hasattr(entity, 'user') and entity.user:
            entity_dict['user'] = {
                'id': entity.user.id,
                'is_bot': entity.user.is_bot,
                'first_name': entity.user.first_name,
                'last_name': entity.user.last_name,
                'username': entity.user.username
            }
        if hasattr(entity, 'language') and entity.language:
            entity_dict['language'] = entity.language
        
        result.append(entity_dict)
    
    return result

def entities_from_dict(entities_data: List[Dict[str, Any]]) -> List[MessageEntity]:
    """
    Восстанавливает список MessageEntity из словарей из БД
    
    Args:
        entities_data: Список словарей с данными entities
        
    Returns:
        Список MessageEntity объектов
    """
    if not entities_data:
        return []
    
    result = []
    for entity_dict in entities_data:
        try:
            # Создаем MessageEntity с базовыми параметрами
            entity = MessageEntity(
                type=entity_dict['type'],
                offset=entity_dict['offset'],
                length=entity_dict['length']
            )
            
            # Устанавливаем дополнительные атрибуты
            if 'url' in entity_dict:
                entity.url = entity_dict['url']
            if 'user' in entity_dict:
                from aiogram.types import User
                user_data = entity_dict['user']
                entity.user = User(
                    id=user_data['id'],
                    is_bot=user_data.get('is_bot', False),
                    first_name=user_data.get('first_name'),
                    last_name=user_data.get('last_name'),
                    username=user_data.get('username')
                )
            if 'language' in entity_dict:
                entity.language = entity_dict['language']
            
            result.append(entity)
        except Exception as e:
            # Логируем ошибку, но продолжаем обработку
            print(f"Ошибка восстановления entity: {e}")
            continue
    
    return result

def entities_to_json(entities: List[MessageEntity]) -> str:
    """
    Конвертирует entities в JSON строку для сохранения в БД
    
    Args:
        entities: Список MessageEntity
        
    Returns:
        JSON строка
    """
    entities_dict = entities_to_dict(entities)
    return json.dumps(entities_dict, ensure_ascii=False)

def entities_from_json(json_str: str) -> List[MessageEntity]:
    """
    Восстанавливает entities из JSON строки из БД
    
    Args:
        json_str: JSON строка с данными entities
        
    Returns:
        Список MessageEntity объектов
    """
    if not json_str:
        return []
    
    try:
        entities_data = json.loads(json_str)
        return entities_from_dict(entities_data)
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Ошибка парсинга JSON entities: {e}")
        return []

def extract_entities_from_message(message) -> List[MessageEntity]:
    """
    Извлекает entities из сообщения (text или caption)
    
    Args:
        message: Telegram Message объект
        
    Returns:
        Список entities или пустой список
    """
    if message.text and message.entities:
        return message.entities
    elif message.caption and message.caption_entities:
        return message.caption_entities
    else:
        return []

def has_formatting_entities(entities: List[MessageEntity]) -> bool:
    """
    Проверяет, есть ли в entities форматирование (bold, italic, code, etc.)
    
    Args:
        entities: Список MessageEntity
        
    Returns:
        True если есть форматирование
    """
    if not entities:
        return False
    
    formatting_types = {
        'bold', 'italic', 'code', 'pre', 'underline', 
        'strikethrough', 'text_link', 'text_mention'
    }
    
    return any(entity.type in formatting_types for entity in entities)

def get_entities_summary(entities: List[MessageEntity]) -> str:
    """
    Возвращает краткое описание entities для логирования
    
    Args:
        entities: Список MessageEntity
        
    Returns:
        Строка с описанием
    """
    if not entities:
        return "Нет entities"
    
    type_counts = {}
    for entity in entities:
        type_counts[entity.type] = type_counts.get(entity.type, 0) + 1
    
    summary = ", ".join([f"{count} {type}" for type, count in type_counts.items()])
    return f"{len(entities)} entities: {summary}"
