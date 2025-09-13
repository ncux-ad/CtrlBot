"""
@file: services/ai.py
@description: Сервис для работы с YandexGPT API
@dependencies: config.py, aiohttp
@created: 2025-09-13
"""

import aiohttp
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from config import config
from utils.logging import get_logger

logger = get_logger(__name__)

class AIService:
    """Сервис для работы с YandexGPT API"""
    
    def __init__(self):
        self.api_key = config.YANDEX_API_KEY
        self.folder_id = config.YANDEX_FOLDER_ID
        self.base_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self.headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def _make_request(self, prompt: str, max_tokens: int = 1000) -> Optional[Dict[str, Any]]:
        """Выполнение запроса к YandexGPT API"""
        if not self.api_key or not self.folder_id:
            logger.warning("YandexGPT API not configured")
            return None
        
        try:
            payload = {
                "modelUri": f"gpt://{self.folder_id}/yandexgpt-lite",
                "completionOptions": {
                    "stream": False,
                    "temperature": 0.6,
                    "maxTokens": max_tokens
                },
                "messages": [
                    {
                        "role": "user",
                        "text": prompt
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result
                    else:
                        error_text = await response.text()
                        logger.error("YandexGPT API error %s: %s", response.status, error_text)
                        return None
                        
        except Exception as e:
            logger.error("Failed to make YandexGPT request: %s", e)
            return None
    
    async def suggest_tags(self, post_text: str, existing_tags: List[str] = None) -> List[str]:
        """Предложение тегов на основе текста поста"""
        try:
            existing_tags_text = ""
            if existing_tags:
                existing_tags_text = f"\n\nСуществующие теги: {', '.join(existing_tags)}"
            
            prompt = f"""
Проанализируй текст поста и предложи 3-5 релевантных тегов на русском языке.

Текст поста:
{post_text[:500]}{existing_tags_text}

Требования:
- Теги должны быть короткими (1-3 слова)
- Используй только русский язык
- Избегай повторения существующих тегов
- Теги должны отражать основную тему поста
- Формат ответа: только теги через запятую, без дополнительного текста

Пример: новости, технологии, анонс, важное, обновление
"""
            
            result = await self._make_request(prompt, max_tokens=200)
            if not result:
                return []
            
            # Извлекаем текст ответа
            response_text = result.get("result", {}).get("alternatives", [{}])[0].get("message", {}).get("text", "")
            
            if not response_text:
                return []
            
            # Парсим теги
            tags = [tag.strip().lower() for tag in response_text.split(",") if tag.strip()]
            return tags[:5]  # Максимум 5 тегов
            
        except Exception as e:
            logger.error("Failed to suggest tags: %s", e)
            return []
    
    async def shorten_text(self, text: str, max_length: int = 200) -> str:
        """Сокращение текста до указанной длины"""
        try:
            if len(text) <= max_length:
                return text
            
            prompt = f"""
Сократи следующий текст до {max_length} символов, сохранив основную суть и важную информацию.

Исходный текст:
{text}

Требования:
- Сохрани основную мысль
- Убери лишние слова, но оставь читаемость
- Длина не должна превышать {max_length} символов
- Начни с самого важного
- Сохрани структуру, если есть списки или абзацы
"""
            
            result = await self._make_request(prompt, max_tokens=500)
            if not result:
                return text[:max_length] + "..."
            
            response_text = result.get("result", {}).get("alternatives", [{}])[0].get("message", {}).get("text", "")
            
            if not response_text:
                return text[:max_length] + "..."
            
            return response_text.strip()
            
        except Exception as e:
            logger.error("Failed to shorten text: %s", e)
            return text[:max_length] + "..."
    
    async def change_style(self, text: str, style: str = "formal") -> str:
        """Изменение стиля текста"""
        try:
            style_prompts = {
                "formal": "Перепиши текст в официальном, деловом стиле",
                "casual": "Перепиши текст в неформальном, дружелюбном стиле",
                "news": "Перепиши текст в стиле новостной статьи",
                "marketing": "Перепиши текст в маркетинговом, продающем стиле",
                "technical": "Перепиши текст в техническом, профессиональном стиле"
            }
            
            if style not in style_prompts:
                return text
            
            prompt = f"""
{style_prompts[style]}.

Исходный текст:
{text}

Требования:
- Сохрани основную информацию
- Измени тон и стиль изложения
- Сохрани длину примерно такой же
- Сделай текст более подходящим для выбранного стиля
"""
            
            result = await self._make_request(prompt, max_tokens=1000)
            if not result:
                return text
            
            response_text = result.get("result", {}).get("alternatives", [{}])[0].get("message", {}).get("text", "")
            
            if not response_text:
                return text
            
            return response_text.strip()
            
        except Exception as e:
            logger.error("Failed to change text style: %s", e)
            return text
    
    async def generate_annotation(self, text: str) -> str:
        """Генерация аннотации для поста"""
        try:
            prompt = f"""
Создай краткую аннотацию (2-3 предложения) для следующего поста.

Текст поста:
{text}

Требования:
- Аннотация должна быть информативной и привлекательной
- Длина: 2-3 предложения
- Выдели главную мысль поста
- Сделай аннотацию интересной для чтения
- Используй русский язык
"""
            
            result = await self._make_request(prompt, max_tokens=300)
            if not result:
                return "Аннотация недоступна"
            
            response_text = result.get("result", {}).get("alternatives", [{}])[0].get("message", {}).get("text", "")
            
            if not response_text:
                return "Аннотация недоступна"
            
            return response_text.strip()
            
        except Exception as e:
            logger.error("Failed to generate annotation: %s", e)
            return "Аннотация недоступна"
    
    async def improve_text(self, text: str) -> str:
        """Улучшение текста (грамматика, стиль, читаемость)"""
        try:
            prompt = f"""
Улучши следующий текст: исправь грамматические ошибки, улучши стиль и читаемость.

Исходный текст:
{text}

Требования:
- Исправь грамматические и орфографические ошибки
- Улучши структуру предложений
- Сделай текст более читаемым
- Сохрани оригинальный смысл
- Сохрани длину примерно такой же
- Используй русский язык
"""
            
            result = await self._make_request(prompt, max_tokens=1000)
            if not result:
                return text
            
            response_text = result.get("result", {}).get("alternatives", [{}])[0].get("message", {}).get("text", "")
            
            if not response_text:
                return text
            
            return response_text.strip()
            
        except Exception as e:
            logger.error("Failed to improve text: %s", e)
            return text
    
    async def check_api_status(self) -> Dict[str, Any]:
        """Проверка статуса API"""
        try:
            if not self.api_key or not self.folder_id:
                return {
                    "status": "not_configured",
                    "message": "API ключ или папка не настроены"
                }
            
            # Простой тестовый запрос
            result = await self._make_request("Привет", max_tokens=10)
            
            if result:
                return {
                    "status": "working",
                    "message": "API работает корректно"
                }
            else:
                return {
                    "status": "error",
                    "message": "Ошибка подключения к API"
                }
                
        except Exception as e:
            logger.error("Failed to check API status: %s", e)
            return {
                "status": "error",
                "message": f"Ошибка: {str(e)}"
            }

# Глобальный экземпляр сервиса
ai_service = AIService()