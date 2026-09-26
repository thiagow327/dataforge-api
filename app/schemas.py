from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


# ---------- Registros ----------
class RecordIn(BaseModel):
    data: date | None = None
    produto: str | None = None
    cep: str | None = None
    valor: float | None = None


class RecordOut(RecordIn):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ---------- Datasets ----------
class DatasetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    records: list[RecordIn] = Field(default_factory=list)


class DatasetUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)


class DatasetOut(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
    record_count: int
    model_config = ConfigDict(from_attributes=True)


class DatasetDetail(DatasetOut):
    records: list[RecordOut]


class DatasetList(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[DatasetOut]
