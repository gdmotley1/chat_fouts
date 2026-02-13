from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import JSON, Column, Field, SQLModel


class JobStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    external_id: str = Field(index=True)
    title: str
    price: str
    description: str
    image_urls: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    local_images: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class VideoTemplate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(unique=True, index=True)
    name: str
    duration_seconds: int
    scene_count: int
    config: dict = Field(default_factory=dict, sa_column=Column(JSON))


class RenderJob(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(index=True)
    template_key: str
    status: JobStatus = Field(default=JobStatus.queued)
    progress: float = 0.0
    error: Optional[str] = None
    variant_index: int = 1
    output_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ExportAsset(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(index=True)
    job_id: int = Field(index=True)
    caption: str
    hashtags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    hooks: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    ctas: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    filename: str
    location: str
    srt_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BrandVoice(SQLModel, table=True):
    id: Optional[int] = Field(default=1, primary_key=True)
    tone: str = "minimalist"
    banned_phrases: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    preferred_ctas: list[str] = Field(default_factory=lambda: ["Shop now", "Tap to get yours"] , sa_column=Column(JSON))
