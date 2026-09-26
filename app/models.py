from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(String(1000), default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    records: Mapped[list["DataRecord"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan"
    )
    analyses: Mapped[list["AnalysisResult"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan"
    )

    @property
    def record_count(self) -> int:
        return len(self.records)


class DataRecord(Base):
    __tablename__ = "data_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), index=True
    )
    data: Mapped[date | None] = mapped_column(Date, default=None)
    produto: Mapped[str | None] = mapped_column(String(200), default=None)
    cep: Mapped[str | None] = mapped_column(String(20), default=None)
    valor: Mapped[float | None] = mapped_column(Float, default=None)

    dataset: Mapped["Dataset"] = relationship(back_populates="records")


class AnalysisResult(Base):
    """Resultado devolvido pelo insight-service, cacheado (populado na Fase 5)."""

    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), index=True
    )
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    dataset: Mapped["Dataset"] = relationship(back_populates="analyses")
