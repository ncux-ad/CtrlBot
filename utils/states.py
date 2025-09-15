# Utils: FSM states

from aiogram.fsm.state import State, StatesGroup

class PostCreationStates(StatesGroup):
    """Состояния для создания поста"""
    idle = State()  # Начальное состояние
    enter_text = State()  # Ввод текста поста
    preview = State()  # Предпросмотр поста
    add_tags = State()  # Добавление тегов
    choose_series = State()  # Выбор серии
    schedule = State()  # Планирование публикации
    enter_time = State()  # Ввод времени публикации
    waiting_schedule_time = State()  # Ожидание ввода времени для изменения отложенного поста
    confirm = State()  # Подтверждение

class PollCreationStates(StatesGroup):
    """Состояния для создания опроса"""
    idle = State()  # Начальное состояние
    enter_question = State()  # Ввод вопроса
    enter_options = State()  # Ввод вариантов ответов
    poll_settings = State()  # Настройки опроса (тип, анонимность и т.д.)
    preview = State()  # Предпросмотр опроса
    schedule = State()  # Планирование публикации
    enter_time = State()  # Ввод времени публикации
    confirm = State()  # Подтверждение

class AdminStates(StatesGroup):
    """Состояния для админских функций"""
    idle = State()
    channel_setup = State()  # Настройка канала
    tag_management = State()  # Управление тегами
    series_management = State()  # Управление сериями
    reminder_setup = State()  # Настройка напоминаний

class DigestStates(StatesGroup):
    """Состояния для дайджестов"""
    idle = State()
    create_weekly = State()  # Создание недельного дайджеста
    create_monthly = State()  # Создание месячного дайджеста
    export_settings = State()  # Настройки экспорта
