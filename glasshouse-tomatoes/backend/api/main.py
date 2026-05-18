"""
GlassHouse Tomatoes — FastAPI Backend
=====================================
Time-series ingestion and query API for soil monitoring nodes.
"""

import os
from datetime import datetime, timedelta
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Float, DateTime, Integer, select, func
from sqlalchemy.orm import declarative_base

# ─── Configuration ──────────────────────────────────────────────────────────
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://gh_user:changeme@localhost:5432/glasshouse",
)

Base = declarative_base()
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# ─── Database Models ────────────────────────────────────────────────────────
class Measurement(Base):
    __tablename__ = "measurements"
    __table_args__ = {"extend_existing": True}

    time = Column(DateTime(timezone=True), primary_key=True)
    node_id = Column(String(32), primary_key=True)
    vwc_percent = Column(Float)
    ec_ms_cm = Column(Float)
    temp_c = Column(Float)
    battery_mv = Column(Integer)
    rssi_dbm = Column(Integer)
    seq = Column(Integer)


# ─── Pydantic Schemas ───────────────────────────────────────────────────────
class MeasurementIn(BaseModel):
    node_id: str = Field(..., min_length=1, max_length=32)
    timestamp: datetime
    vwc_percent: float = Field(..., ge=0, le=100)
    ec_ms_cm: Optional[float] = None
    temp_c: Optional[float] = None
    battery_mv: Optional[int] = Field(None, ge=0, le=5000)
    rssi_dbm: Optional[int] = None
    seq: Optional[int] = None


class MeasurementOut(MeasurementIn):
    class Config:
        from_attributes = True


class NodeSummary(BaseModel):
    node_id: str
    latest_vwc: Optional[float]
    latest_temp: Optional[float]
    latest_battery_mv: Optional[int]
    last_seen: Optional[datetime]


# ─── Lifespan ───────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="GlassHouse Tomatoes API",
    version="1.0.0",
    lifespan=lifespan,
)


# ─── Endpoints ──────────────────────────────────────────────────────────────
@app.post("/api/v1/measurements", status_code=201)
async def ingest_measurement(data: MeasurementIn):
    """Ingest a single measurement from a sensor node."""
    async with async_session() as session:
        m = Measurement(
            time=data.timestamp,
            node_id=data.node_id,
            vwc_percent=data.vwc_percent,
            ec_ms_cm=data.ec_ms_cm,
            temp_c=data.temp_c,
            battery_mv=data.battery_mv,
            rssi_dbm=data.rssi_dbm,
            seq=data.seq,
        )
        session.add(m)
        await session.commit()
    return {"status": "ok"}


@app.get("/api/v1/measurements/latest", response_model=List[MeasurementOut])
async def get_latest_measurements(
    node_id: Optional[str] = None,
    limit: int = Query(10, ge=1, le=1000),
):
    """Get latest measurement(s). Optionally filter by node_id."""
    async with async_session() as session:
        stmt = select(Measurement).order_by(Measurement.time.desc())
        if node_id:
            stmt = stmt.where(Measurement.node_id == node_id)
        stmt = stmt.limit(limit)
        result = await session.execute(stmt)
        rows = result.scalars().all()
        return [
            MeasurementOut(
                node_id=r.node_id,
                timestamp=r.time,
                vwc_percent=r.vwc_percent,
                ec_ms_cm=r.ec_ms_cm,
                temp_c=r.temp_c,
                battery_mv=r.battery_mv,
                rssi_dbm=r.rssi_dbm,
                seq=r.seq,
            )
            for r in rows
        ]


@app.get("/api/v1/measurements/history", response_model=List[MeasurementOut])
async def get_history(
    node_id: str,
    hours: int = Query(24, ge=1, le=8760),
    bucket_minutes: Optional[int] = Query(None, ge=1, le=1440),
):
    """Get time-series history for a node, optionally bucketed."""
    async with async_session() as session:
        since = datetime.utcnow() - timedelta(hours=hours)
        stmt = (
            select(Measurement)
            .where(Measurement.node_id == node_id)
            .where(Measurement.time >= since)
            .order_by(Measurement.time.asc())
        )
        result = await session.execute(stmt)
        rows = result.scalars().all()
        return [
            MeasurementOut(
                node_id=r.node_id,
                timestamp=r.time,
                vwc_percent=r.vwc_percent,
                ec_ms_cm=r.ec_ms_cm,
                temp_c=r.temp_c,
                battery_mv=r.battery_mv,
                rssi_dbm=r.rssi_dbm,
                seq=r.seq,
            )
            for r in rows
        ]


@app.get("/api/v1/nodes", response_model=List[NodeSummary])
async def list_nodes():
    """List all registered nodes with their latest readings."""
    async with async_session() as session:
        subq = (
            select(
                Measurement.node_id,
                func.max(Measurement.time).label("last_seen"),
            )
            .group_by(Measurement.node_id)
            .subquery()
        )
        stmt = select(Measurement).join(
            subq,
            (Measurement.node_id == subq.c.node_id)
            & (Measurement.time == subq.c.last_seen),
        )
        result = await session.execute(stmt)
        rows = result.scalars().all()
        return [
            NodeSummary(
                node_id=r.node_id,
                latest_vwc=r.vwc_percent,
                latest_temp=r.temp_c,
                latest_battery_mv=r.battery_mv,
                last_seen=r.time,
            )
            for r in rows
        ]


@app.get("/health")
async def health():
    return {"status": "ok", "service": "glasshouse-api"}
