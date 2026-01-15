from app.db.session import SessionLocal
from app.jobs.price_ingest import ingest_btc_snapshot
from app.jobs.event_engine import check_percent_move_event

def run_btc_pipeline() -> None:
    ingest_btc_snapshot()

    db = SessionLocal()
    try:
        check_percent_move_event(db, symbol="btc", window_minutes=5, threshold_percent=1.0)
    finally:
        db.close()
