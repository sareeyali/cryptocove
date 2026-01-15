from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.coin import Coin
from app.models.market_event import MarketEvent

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/btc")
def get_btc_events(limit: int = 50, db: Session = Depends(get_db)):
    coin = db.query(Coin).filter(Coin.symbol == "btc").first()
    if coin is None:
        return []

    rows = (
        db.query(MarketEvent)
        .filter(MarketEvent.coin_id == coin.id)
        .order_by(MarketEvent.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "event_type": r.event_type,
            "message": r.message,
            "window_minutes": r.window_minutes,
            "threshold_percent": float(r.threshold_percent),
            "start_price_usd": float(r.start_price_usd),
            "end_price_usd": float(r.end_price_usd),
            "percent_change": float(r.percent_change),
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]
