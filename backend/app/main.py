from fastapi import FastAPI

from app.api.prices import router as prices_router
from app.db.session import engine, Base
from app.models.coin import Coin
from app.models.price_snapshot import PriceSnapshot

from apscheduler.schedulers.background import BackgroundScheduler
from app.jobs.price_ingest import ingest_btc_snapshot



app = FastAPI(title="CryptoCove API")

Base.metadata.create_all(bind=engine)

from app.api.snapshots import router as snapshots_router
app.include_router(snapshots_router)

scheduler = BackgroundScheduler()

from datetime import datetime, timezone

@app.on_event("startup")
def start_scheduler():
    # Run once immediately so you can confirm it works
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

@app.get("/")
def health():
    return {"status": "CryptoCove backend running"}

app.include_router(prices_router)
