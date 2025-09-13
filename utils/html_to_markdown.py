# Utils: HTML to Markdown converter

import re
from typing import Optional

def detect_and_convert_formatting(text: str) -> str:
    """
    Детектирует HTML или Markdown форматирование и конвертирует в Markdown
    """
    if not text:
        return text
    
    # Проверяем, есть ли HTML теги
    if '<' in text and '>' in text:
        return html_to_markdown(text)
    
    # Если это уже Markdown, возвращаем как есть
    if any(marker in text for marker in ['*', '_', '`', '[', ']']):
        return text
    
    # Применяем базовое форматирование к структурированному тексту
    return apply_basic_formatting(text)

def html_to_markdown(html_text: str) -> str:
    """
    Конвертирует HTML форматирование в Markdown
    """
    text = html_text
    
    # Убираем лишние пробелы и переносы строк
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Конвертируем HTML теги в Markdown
    # Жирный текст
    text = re.sub(r'<b>(.*?)</b>', r'*\1*', text, flags=re.DOTALL)
    text = re.sub(r'<strong>(.*?)</strong>', r'*\1*', text, flags=re.DOTALL)
    
    # Курсив
    text = re.sub(r'<i>(.*?)</i>', r'_\1_', text, flags=re.DOTALL)
    text = re.sub(r'<em>(.*?)</em>', r'_\1_', text, flags=re.DOTALL)
    
    # Моноширинный код
    text = re.sub(r'<code>(.*?)</code>', r'`\1`', text, flags=re.DOTALL)
    
    # Блок кода
    text = re.sub(r'<pre>(.*?)</pre>', r'```\n\1\n```', text, flags=re.DOTALL)
    
    # Ссылки
    text = re.sub(r'<a href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', text, flags=re.DOTALL)
    
    # Подчеркивание (если есть)
    text = re.sub(r'<u>(.*?)</u>', r'_\1_', text, flags=re.DOTALL)
    
    # Зачеркивание (если есть)
    text = re.sub(r'<s>(.*?)</s>', r'~~\1~~', text, flags=re.DOTALL)
    text = re.sub(r'<strike>(.*?)</strike>', r'~~\1~~', text, flags=re.DOTALL)
    text = re.sub(r'<del>(.*?)</del>', r'~~\1~~', text, flags=re.DOTALL)
    
    # Убираем оставшиеся HTML теги
    text = re.sub(r'<[^>]+>', '', text)
    
    # Декодируем HTML entities
    text = html_entities_decode(text)
    
    # Очищаем лишние пробелы
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text

def html_entities_decode(text: str) -> str:
    """
    Декодирует HTML entities
    """
    entities = {
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'",
        '&apos;': "'",
        '&nbsp;': ' ',
        '&copy;': '©',
        '&reg;': '®',
        '&trade;': '™',
        '&hellip;': '…',
        '&mdash;': '—',
        '&ndash;': '–',
        '&lsquo;': ''',
        '&rsquo;': ''',
        '&ldquo;': '"',
        '&rdquo;': '"',
    }
    
    for entity, char in entities.items():
        text = text.replace(entity, char)
    
    return text

def is_html_formatting(text: str) -> bool:
    """
    Проверяет, содержит ли текст HTML форматирование
    """
    if not text:
        return False
    
    # Простая проверка на наличие HTML тегов
    html_pattern = r'<[^>]+>'
    return bool(re.search(html_pattern, text))

def format_detection_info(text: str) -> str:
    """
    Возвращает информацию о детектированном форматировании
    """
    if is_html_formatting(text):
        return "🔍 <b>Обнаружено HTML форматирование</b> - конвертировано в Markdown"
    elif any(marker in text for marker in ['*', '_', '`', '[', ']']):
        return "📝 <b>Обнаружено Markdown форматирование</b> - используется как есть"
    elif has_rich_formatting(text):
        return "✨ <b>Обнаружено форматирование</b> - применено базовое форматирование"
    else:
        return "📄 <b>Обычный текст</b> - без форматирования"

def has_rich_formatting(text: str) -> bool:
    """
    Проверяет, есть ли в тексте признаки форматирования (кавычки, тире, эмодзи и т.д.)
    """
    # Проверяем на различные признаки форматирования
    formatting_indicators = [
        '"',  # Кавычки
        '«', '»',  # Русские кавычки
        '—', '–',  # Длинные тире
        '•', '◦', '▪', '▫',  # Маркеры списков
        '1.', '2.', '3.',  # Нумерация
        'P.S.', 'P.S',  # Постскриптум
        'Вопрос:', 'Ответ:',  # Структурированный текст
        ':',  # Двоеточие (часто используется для выделения)
    ]
    
    # Проверяем наличие эмодзи
    emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]'
    has_emoji = bool(re.search(emoji_pattern, text))
    
    # Проверяем наличие форматирующих символов
    has_formatting = any(indicator in text for indicator in formatting_indicators)
    
    # Проверяем на структурированный текст (заголовки, списки)
    lines = text.split('\n')
    has_structure = any(
        line.strip().endswith(':') or  # Заголовки
        line.strip().startswith(('•', '◦', '▪', '▫', '-', '*')) or  # Списки
        line.strip().startswith(tuple(f'{i}.' for i in range(1, 10)))  # Нумерация
        for line in lines
    )
    
    return has_emoji or has_formatting or has_structure

def apply_basic_formatting(text: str) -> str:
    """
    Применяет базовое Markdown форматирование к структурированному тексту
    """
    if not text:
        return text
    
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            formatted_lines.append('')
            continue
        
        # Заголовки (строки, заканчивающиеся на двоеточие)
        if line.endswith(':') and not line.startswith(('http', 'www')):
            formatted_lines.append(f"*{line}*")
            continue
        
        # Списки с маркерами
        if line.startswith(('•', '◦', '▪', '▫', '-', '*')):
            # Убираем маркер и добавляем Markdown маркер
            content = line[1:].strip()
            if content:
                formatted_lines.append(f"• {content}")
            else:
                formatted_lines.append(line)
            continue
        
        # Нумерованные списки
        if re.match(r'^\d+\.', line):
            formatted_lines.append(line)
            continue
        
        # Цитаты (строки, начинающиеся с кавычек)
        if line.startswith(('"', '«', '"')):
            formatted_lines.append(f"> {line}")
            continue
        
        # P.S. и подобные
        if line.startswith(('P.S.', 'P.S', 'P.S:')):
            formatted_lines.append(f"*{line}*")
            continue
        
        # Обычные строки
        formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def restore_formatting_from_entities(text: str, entities) -> str:
    """
    Восстанавливает форматирование из Telegram entities
    """
    if not entities:
        return text
    
    # Сортируем entities по позиции (от начала к концу)
    sorted_entities = sorted(entities, key=lambda e: e.offset)
    
    # Создаем список символов для работы
    chars = list(text)
    offset = 0  # Смещение из-за вставленных символов
    
    for entity in sorted_entities:
        start = entity.offset + offset
        end = start + entity.length
        
        if start >= len(chars) or end > len(chars):
            continue
            
        original_text = ''.join(chars[start:end])
        
        # Применяем форматирование в зависимости от типа entity
        if entity.type == "bold":
            formatted_text = f"*{original_text}*"
        elif entity.type == "italic":
            formatted_text = f"_{original_text}_"
        elif entity.type == "code":
            formatted_text = f"`{original_text}`"
        elif entity.type == "pre":
            formatted_text = f"```\n{original_text}\n```"
        elif entity.type == "text_link" and entity.url:
            formatted_text = f"[{original_text}]({entity.url})"
        elif entity.type == "underline":
            formatted_text = f"_{original_text}_"  # Подчеркивание как курсив
        elif entity.type == "strikethrough":
            formatted_text = f"~~{original_text}~~"
        elif entity.type == "blockquote":
            # Для blockquote добавляем > в начало каждой строки
            lines = original_text.split('\n')
            formatted_lines = [f"> {line}" if line.strip() else ">" for line in lines]
            formatted_text = '\n'.join(formatted_lines)
        else:
            formatted_text = original_text
        
        # Заменяем текст в списке символов
        new_chars = list(formatted_text)
        chars[start:end] = new_chars
        
        # Обновляем смещение
        offset += len(new_chars) - (end - start)
    
    # Дополнительно обрабатываем цитаты по кавычкам
    result = ''.join(chars)
    result = enhance_quotes_formatting(result)
    
    return result

def enhance_quotes_formatting(text: str) -> str:
    """
    Дополнительно улучшает форматирование цитат по кавычкам
    """
    lines = text.split('\n')
    enhanced_lines = []
    
    for line in lines:
        # Если строка начинается с кавычки и не является уже blockquote
        if (line.strip().startswith(('"', '«', '"')) and 
            not line.strip().startswith('>')):
            enhanced_lines.append(f"> {line}")
        else:
            enhanced_lines.append(line)
    
    return '\n'.join(enhanced_lines)
