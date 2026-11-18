"""Analytics tables. Ola's SCRUM-138 is the only Alembic revision. Omar does not add one."""

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = {"schema": "analytics"}

    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    video_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    camera_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    media_ref: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(Text, nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    recorded_start_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    pipeline_version: Mapped[str] = mapped_column(Text, nullable=False)
    attempt: Mapped[int] = mapped_column(Integer, nullable=False)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Run(Base):
    __tablename__ = "runs"
    __table_args__ = {"schema": "analytics"}

    processing_run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analytics.jobs.job_id"),
        unique=True,
        nullable=False,
    )
    accepted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class OutboxCallback(Base):
    __tablename__ = "outbox_callbacks"
    __table_args__ = (
        CheckConstraint(
            "state IN ('pending', 'delivered', 'failed')",
            name="outbox_callbacks_state",
        ),
        {"schema": "analytics"},
    )

    outbox_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    target_path: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[dict] = mapped_column(JSONB, nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    state: Mapped[str] = mapped_column(Text, nullable=False)


class LiveCamera(Base):
    __tablename__ = "live_cameras"
    __table_args__ = (
        CheckConstraint("monitoring IN ('on', 'off')", name="live_cameras_monitoring"),
        CheckConstraint("mode IN ('rtsp_pull', 'push')", name="live_cameras_mode"),
        {"schema": "analytics"},
    )

    camera_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    config_version: Mapped[int] = mapped_column(Integer, nullable=False)
    monitoring: Mapped[str] = mapped_column(Text, nullable=False)
    mode: Mapped[str] = mapped_column(Text, nullable=False)
    rtsp_url: Mapped[str | None] = mapped_column(Text)
    rules: Mapped[list] = mapped_column(JSONB, nullable=False)
    worker_id: Mapped[str | None] = mapped_column(Text)


class SearchCall(Base):
    __tablename__ = "search_calls"
    __table_args__ = (
        CheckConstraint("hit_count >= 0", name="search_calls_hit_count_nonnegative"),
        {"schema": "analytics"},
    )

    search_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    include_tentative: Mapped[bool] = mapped_column(nullable=False)
    request_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    hit_count: Mapped[int] = mapped_column(Integer, nullable=False)
    called_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ClipJob(Base):
    __tablename__ = "clip_jobs"
    __table_args__ = (
        CheckConstraint("playback_start_ms >= 0", name="clip_jobs_start_nonnegative"),
        CheckConstraint(
            "playback_end_ms >= playback_start_ms",
            name="clip_jobs_end_after_start",
        ),
        CheckConstraint(
            "playback_end_ms - playback_start_ms <= 120000",
            name="clip_jobs_max_window",
        ),
        CheckConstraint("encoding_profile = 'h264_720p'", name="clip_jobs_profile"),
        CheckConstraint(
            "state IN ('queued', 'running', 'ready', 'failed')",
            name="clip_jobs_state",
        ),
        CheckConstraint(
            "(state = 'ready' AND clip_ref IS NOT NULL) OR (state <> 'ready' AND clip_ref IS NULL)",
            name="clip_jobs_ref_when_ready",
        ),
        {"schema": "analytics"},
    )

    clip_job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    result_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    video_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    media_ref: Mapped[str] = mapped_column(Text, nullable=False)
    playback_start_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    playback_end_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    encoding_profile: Mapped[str] = mapped_column(Text, nullable=False)
    state: Mapped[str] = mapped_column(Text, nullable=False)
    clip_ref: Mapped[str | None] = mapped_column(Text)
    accepted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
