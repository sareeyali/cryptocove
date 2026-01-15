from fastapi import FastAPI

from apscheduler.schedulers.background import BackgroundScheduler

from app.api.prices import router as prices_router
from app.api.snapshots import router as snapshots_router
from app.api.events import router as events_router

from app.db.session import engine, Base
from app.models.coin import Coin
from app.models.price_snapshot import PriceSnapshot
from app.models.market_event import MarketEvent


from app.jobs.price_ingest import ingest_btc_snapshot


# --------------------
# App setup
# --------------------

app = FastAPI(title="CryptoCove API")

# Create tables on startup
Base.metadata.create_all(bind=engine)

# Register API routes
app.include_router(prices_router)
app.include_router(snapshots_router)
app.include_router(events_router)


# --------------------
# Background scheduler
# --------------------

scheduler = BackgroundScheduler()


@app.on_event("startup")
def start_scheduler():
    # Run once immediately
    ingest_btc_snapshot()

    # Then run every 60 seconds
    scheduler.add_job(
        ingest_btc_snapshot,
        "interval",
        seconds=60,
        id="btc_ingest",
        replace_existing=True,
    )

    scheduler.start()
    print("[scheduler] started")


@app.on_event("shutdown")
def stop_scheduler():
    scheduler.shutdown()
    print("[scheduler] stopped")


# --------------------
# Health check
# --------------------

@app.get("/")
def health():
    return {"status": "CryptoCove backend running"}
