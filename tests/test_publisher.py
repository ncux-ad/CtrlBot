# Tests: PostPublisher
# Тесты для централизованного сервиса публикации постов

import pytest
from unittest.mock import Mock, AsyncMock
from aiogram.types import Message, MessageEntity
from aiogram.enums import MessageEntityType

from services.publisher import PostPublisher

@pytest.fixture
def mock_bot():
    """Создает мок бота для тестов"""
    bot = Mock()
    bot.send_message = AsyncMock()
    bot.send_photo = AsyncMock()
    bot.send_video = AsyncMock()
    bot.send_document = AsyncMock()
    bot.copy_message = AsyncMock()
    return bot

@pytest.fixture
def publisher(mock_bot):
    """Создает экземпляр PostPublisher с мок ботом"""
    return PostPublisher(mock_bot)

@pytest.fixture
def sample_entities():
    """Создает пример entities для тестов"""
    return [
        MessageEntity(
            type=MessageEntityType.BOLD,
            offset=0,
            length=5
        ),
        MessageEntity(
            type=MessageEntityType.ITALIC,
            offset=6,
            length=7
        )
    ]

class TestPostPublisher:
    """Тесты для PostPublisher"""
    
    async def test_publish_text_with_entities(self, publisher, sample_entities):
        """Тест публикации текста с entities"""
        # Arrange
        chat_id = -1001234567890
        text = "Hello *world*"
        mock_message = Mock()
        mock_message.message_id = 123
        publisher.bot.send_message.return_value = mock_message
        
        # Act
        result = await publisher.publish_text(
            chat_id=chat_id,
            text=text,
            entities=sample_entities
        )
        
        # Assert
        assert result == mock_message
        publisher.bot.send_message.assert_called_once_with(
            chat_id=chat_id,
            text=text,
            entities=sample_entities,
            reply_markup=None
        )
    
    async def test_publish_text_with_parse_mode(self, publisher):
        """Тест публикации текста с parse_mode"""
        # Arrange
        chat_id = -1001234567890
        text = "*Hello* world"
        mock_message = Mock()
        mock_message.message_id = 123
        publisher.bot.send_message.return_value = mock_message
        
        # Act
        result = await publisher.publish_text(
            chat_id=chat_id,
            text=text,
            parse_mode="MarkdownV2"
        )
        
        # Assert
        assert result == mock_message
        publisher.bot.send_message.assert_called_once_with(
            chat_id=chat_id,
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=None
        )
    
    async def test_publish_text_auto_formatting(self, publisher):
        """Тест автоматического определения форматирования"""
        # Arrange
        chat_id = -1001234567890
        text = "*Hello* world"
        mock_message = Mock()
        mock_message.message_id = 123
        publisher.bot.send_message.return_value = mock_message
        
        # Act
        result = await publisher.publish_text(
            chat_id=chat_id,
            text=text
        )
        
        # Assert
        assert result == mock_message
        publisher.bot.send_message.assert_called_once_with(
            chat_id=chat_id,
            text=text,
            parse_mode="MarkdownV2",
            reply_markup=None
        )
    
    async def test_publish_text_fallback_on_parse_error(self, publisher):
        """Тест fallback при ошибке парсинга Markdown"""
        # Arrange
        chat_id = -1001234567890
        text = "*Invalid markdown"
        mock_message = Mock()
        mock_message.message_id = 123
        
        # Первый вызов с MarkdownV2 вызывает ошибку
        publisher.bot.send_message.side_effect = [
            Exception("can't parse entities"),
            mock_message
        ]
        
        # Act
        result = await publisher.publish_text(
            chat_id=chat_id,
            text=text
        )
        
        # Assert
        assert result == mock_message
        assert publisher.bot.send_message.call_count == 2
        
        # Первый вызов с MarkdownV2
        first_call = publisher.bot.send_message.call_args_list[0]
        assert first_call[1]['parse_mode'] == "MarkdownV2"
        
        # Второй вызов без parse_mode
        second_call = publisher.bot.send_message.call_args_list[1]
        assert 'parse_mode' not in second_call[1]
    
    async def test_publish_copy(self, publisher):
        """Тест копирования сообщения"""
        # Arrange
        chat_id = -1001234567890
        from_chat_id = -1009876543210
        message_id = 456
        mock_message = Mock()
        mock_message.message_id = 789
        publisher.bot.copy_message.return_value = mock_message
        
        # Act
        result = await publisher.publish_copy(
            chat_id=chat_id,
            from_chat_id=from_chat_id,
            message_id=message_id
        )
        
        # Assert
        assert result == mock_message
        publisher.bot.copy_message.assert_called_once_with(
            chat_id=chat_id,
            from_chat_id=from_chat_id,
            message_id=message_id,
            reply_markup=None
        )
    
    def test_has_markdown_formatting(self, publisher):
        """Тест определения Markdown форматирования"""
        # Arrange & Act & Assert
        assert publisher._has_markdown_formatting("*bold*") == True
        assert publisher._has_markdown_formatting("_italic_") == True
        assert publisher._has_markdown_formatting("`code`") == True
        assert publisher._has_markdown_formatting("[link](url)") == True
        assert publisher._has_markdown_formatting("plain text") == False
        assert publisher._has_markdown_formatting("") == False

class TestEntitiesUtils:
    """Тесты для утилит работы с entities"""
    
    def test_entities_to_dict(self, sample_entities):
        """Тест конвертации entities в словари"""
        from utils.entities import entities_to_dict
        
        # Act
        result = entities_to_dict(sample_entities)
        
        # Assert
        assert len(result) == 2
        assert result[0]['type'] == 'bold'
        assert result[0]['offset'] == 0
        assert result[0]['length'] == 5
        assert result[1]['type'] == 'italic'
        assert result[1]['offset'] == 6
        assert result[1]['length'] == 7
    
    def test_entities_from_dict(self):
        """Тест восстановления entities из словарей"""
        from utils.entities import entities_from_dict
        
        # Arrange
        entities_data = [
            {'type': 'bold', 'offset': 0, 'length': 5},
            {'type': 'italic', 'offset': 6, 'length': 7}
        ]
        
        # Act
        result = entities_from_dict(entities_data)
        
        # Assert
        assert len(result) == 2
        assert result[0].type == 'bold'
        assert result[0].offset == 0
        assert result[0].length == 5
        assert result[1].type == 'italic'
        assert result[1].offset == 6
        assert result[1].length == 7
    
    def test_entities_to_json_roundtrip(self, sample_entities):
        """Тест полного цикла: entities -> JSON -> entities"""
        from utils.entities import entities_to_json, entities_from_json
        
        # Act
        json_str = entities_to_json(sample_entities)
        restored_entities = entities_from_json(json_str)
        
        # Assert
        assert len(restored_entities) == 2
        assert restored_entities[0].type == 'bold'
        assert restored_entities[0].offset == 0
        assert restored_entities[0].length == 5
        assert restored_entities[1].type == 'italic'
        assert restored_entities[1].offset == 6
        assert restored_entities[1].length == 7
