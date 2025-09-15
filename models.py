"""SQLAlchemy models for CtrlBot."""

from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Enum, ForeignKey, 
    Integer, JSON, String, Text, UniqueConstraint, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class PostStatus(enum.Enum):
    """Статусы постов."""
    draft = "draft"
    published = "published"
    scheduled = "scheduled"
    failed = "failed"
    cancelled = "cancelled"
    deleted = "deleted"


class Channel(Base):
    """Модель канала."""
    __tablename__ = "channels"

    id = Column(BigInteger, primary_key=True)
    tg_channel_id = Column(BigInteger, unique=True, nullable=False)
    title = Column(Text)
    timezone = Column(Text, default="Europe/Moscow")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    posts = relationship("Post", back_populates="channel", cascade="all, delete-orphan")
    tags = relationship("Tag", back_populates="channel", cascade="all, delete-orphan")
    series = relationship("Series", back_populates="channel", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="channel", cascade="all, delete-orphan")
    digests = relationship("Digest", back_populates="channel", cascade="all, delete-orphan")


class Tag(Base):
    """Модель тега."""
    __tablename__ = "tags"

    id = Column(BigInteger, primary_key=True)
    channel_id = Column(BigInteger, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, nullable=False)
    color = Column(String(7), default="#3498db")  # HEX цвет
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    channel = relationship("Channel", back_populates="tags")
    posts = relationship("Post", secondary="post_tags", back_populates="tags")

    # Constraints
    __table_args__ = (
        UniqueConstraint("channel_id", "name", name="uq_tag_channel_name"),
        Index("ix_tags_channel_id", "channel_id"),
    )


class Series(Base):
    """Модель серии постов."""
    __tablename__ = "series"

    id = Column(BigInteger, primary_key=True)
    channel_id = Column(BigInteger, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    channel = relationship("Channel", back_populates="series")
    posts = relationship("Post", back_populates="series")

    # Constraints
    __table_args__ = (
        UniqueConstraint("channel_id", "title", name="uq_series_channel_title"),
        Index("ix_series_channel_id", "channel_id"),
    )


class Post(Base):
    """Модель поста."""
    __tablename__ = "posts"

    id = Column(BigInteger, primary_key=True)
    channel_id = Column(BigInteger, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, nullable=False)
    title = Column(Text)
    body_md = Column(Text, nullable=False)
    body_html = Column(Text)
    status = Column(Enum(PostStatus), default=PostStatus.draft, nullable=False)
    scheduled_at = Column(DateTime(timezone=True))
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Медиа данные
    media_data = Column(JSON)
    
    # Telegram данные
    tg_message_id = Column(BigInteger)
    tg_chat_id = Column(BigInteger)
    
    # Метаданные
    entities = Column(JSON)  # Telegram entities для форматирования
    views_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    
    # Связи
    series_id = Column(BigInteger, ForeignKey("series.id", ondelete="SET NULL"))
    
    # Relationships
    channel = relationship("Channel", back_populates="posts")
    series = relationship("Series", back_populates="posts")
    tags = relationship("Tag", secondary="post_tags", back_populates="posts")

    # Constraints and indexes
    __table_args__ = (
        Index("ix_posts_channel_id", "channel_id"),
        Index("ix_posts_user_id", "user_id"),
        Index("ix_posts_status", "status"),
        Index("ix_posts_scheduled_at", "scheduled_at"),
        Index("ix_posts_created_at", "created_at"),
        Index("ix_posts_published_at", "published_at"),
    )


class PostTag(Base):
    """Связующая таблица постов и тегов."""
    __tablename__ = "post_tags"

    post_id = Column(BigInteger, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(BigInteger, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)

    # Constraints
    __table_args__ = (
        Index("ix_post_tags_post_id", "post_id"),
        Index("ix_post_tags_tag_id", "tag_id"),
    )


class Reminder(Base):
    """Модель напоминания."""
    __tablename__ = "reminders"

    id = Column(BigInteger, primary_key=True)
    channel_id = Column(BigInteger, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False)
    time = Column(String(5), nullable=False)  # HH:MM format
    message = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    channel = relationship("Channel", back_populates="reminders")

    # Constraints
    __table_args__ = (
        UniqueConstraint("channel_id", "time", name="uq_reminder_channel_time"),
        Index("ix_reminders_channel_id", "channel_id"),
    )


class Digest(Base):
    """Модель дайджеста."""
    __tablename__ = "digests"

    id = Column(BigInteger, primary_key=True)
    channel_id = Column(BigInteger, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    period = Column(String(20), nullable=False)  # weekly, monthly
    sent_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    channel = relationship("Channel", back_populates="digests")

    # Constraints
    __table_args__ = (
        Index("ix_digests_channel_id", "channel_id"),
        Index("ix_digests_period", "period"),
        Index("ix_digests_sent_at", "sent_at"),
    )
