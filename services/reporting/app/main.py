"""Reporting Service FastAPI application.

This service aggregates sales data, generates daily/monthly reports,
top products reports, and exports reports in JSON/CSV formats.
It subscribes to order and product events via Kafka.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routes.report import router as report_router
from app.events.kafka_consumer import start_consumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - starts Kafka consumer on startup."""
    logger.info("Starting Reporting Service...")
    consumer_task = asyncio.create_task(start_consumer())
    yield
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        logger.info("Kafka consumer task cancelled")


app = FastAPI(lifespan=lifespan)
app.include_router(report_router)


@app.get("/health")
async def health_check():
    """Health check endpoint.

    Returns:
        dict: Service health status.
    """
    return {"status": "healthy", "service": "reporting-service"}


@app.get("/")
async def root():
    """Root endpoint providing service metadata.

    Returns:
        dict: Service name and version.
    """
    return {"message": "Reporting Service API", "version": "0.1.0"}
