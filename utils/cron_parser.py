"""
@file: utils/cron_parser.py
@description: Утилита для парсинга cron выражений в читаемый формат
@created: 2025-09-15
"""

def parse_cron_to_human(cron_expression: str) -> str:
    """
    Преобразует cron выражение в читаемый формат
    
    Args:
        cron_expression: Cron выражение (например, "0 12 * * *")
        
    Returns:
        Читаемое описание расписания
    """
    try:
        parts = cron_expression.strip().split()
        if len(parts) != 5:
            return cron_expression
        
        minute, hour, day, month, day_of_week = parts
        
        # Обрабатываем минуты
        if minute == "0":
            minute_text = ""
        elif minute == "*":
            minute_text = "каждую минуту"
        else:
            minute_text = f"в {minute} минут"
        
        # Обрабатываем часы
        if hour == "*":
            hour_text = "каждый час"
        else:
            hour_int = int(hour)
            if hour_int == 0:
                hour_text = "в полночь"
            elif hour_int < 12:
                hour_text = f"в {hour_int}:00"
            elif hour_int == 12:
                hour_text = "в полдень"
            else:
                hour_text = f"в {hour_int}:00"
        
        # Обрабатываем день месяца
        if day == "*":
            day_text = ""
        else:
            day_text = f" {day} числа"
        
        # Обрабатываем месяц
        if month == "*":
            month_text = ""
        else:
            months = [
                "", "января", "февраля", "марта", "апреля", "мая", "июня",
                "июля", "августа", "сентября", "октября", "ноября", "декабря"
            ]
            month_int = int(month)
            if 1 <= month_int <= 12:
                month_text = f" {months[month_int]}"
            else:
                month_text = f" {month} месяца"
        
        # Обрабатываем день недели
        if day_of_week == "*":
            week_text = ""
        else:
            days = ["воскресенье", "понедельник", "вторник", "среда", "четверг", "пятница", "суббота"]
            week_int = int(day_of_week)
            if 0 <= week_int <= 6:
                week_text = f" по {days[week_int]}м"
            else:
                week_text = f" по {day_of_week} дню недели"
        
        # Формируем результат
        if minute == "0" and day == "*" and month == "*" and day_of_week == "*":
            # Ежедневно в определенное время
            return f"Ежедневно {hour_text}"
        elif minute == "0" and day != "*" and month == "*" and day_of_week == "*":
            # Ежемесячно в определенный день
            return f"Ежемесячно {day_text}{month_text} в {hour_text}"
        elif minute == "0" and day == "*" and month == "*" and day_of_week != "*":
            # Еженедельно в определенный день
            return f"Еженедельно{week_text} в {hour_text}"
        elif minute == "0" and day == "*" and month != "*" and day_of_week == "*":
            # Ежегодно в определенный месяц
            return f"Ежегодно{month_text} в {hour_text}"
        else:
            # Сложное расписание
            result_parts = []
            if hour_text:
                result_parts.append(hour_text)
            if minute_text:
                result_parts.append(minute_text)
            if day_text:
                result_parts.append(day_text)
            if month_text:
                result_parts.append(month_text)
            if week_text:
                result_parts.append(week_text)
            
            return " ".join(result_parts) if result_parts else cron_expression
            
    except (ValueError, IndexError):
        return cron_expression

def get_common_schedules():
    """Возвращает список популярных расписаний"""
    return [
        {"cron": "0 9 * * *", "description": "Ежедневно в 9:00"},
        {"cron": "0 12 * * *", "description": "Ежедневно в 12:00"},
        {"cron": "0 18 * * *", "description": "Ежедневно в 18:00"},
        {"cron": "0 21 * * *", "description": "Ежедневно в 21:00"},
        {"cron": "0 9 * * 1", "description": "Каждый понедельник в 9:00"},
        {"cron": "0 9 * * 5", "description": "Каждую пятницу в 9:00"},
        {"cron": "0 9 1 * *", "description": "1 числа каждого месяца в 9:00"},
        {"cron": "0 9 15 * *", "description": "15 числа каждого месяца в 9:00"},
    ]
