from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.coin import Coin
from app.models.price_snapshot import PriceSnapshot
from app.models.market_event import MarketEvent


def check_percent_move_event(
    db: Session,
    symbol: str = "btc",
    window_minutes: int = 5,
    threshold_percent: float = 1.0,
    cooldown_minutes: int = 5,
) -> None:
    """
    If BTC moved by >= threshold_percent over the last window_minutes,
    insert a MarketEvent.

    Cooldown prevents spamming the same event every minute.
    """
    coin = db.query(Coin).filter(Coin.symbol == symbol).first()
    if coin is None:
        return

    now = datetime.now(timezone.utc)

    # 1) Get latest snapshot
    latest = (
        db.query(PriceSnapshot)
        .filter(PriceSnapshot.coin_id == coin.id)
        .order_by(PriceSnapshot.pulled_at.desc())
        .first()
    )
    if latest is None:
        return

    # 2) Find snapshot at or before (latest_time - window)
    target_time = latest.pulled_at - timedelta(minutes=window_minutes)

    start = (
        db.query(PriceSnapshot)
        .filter(PriceSnapshot.coin_id == coin.id)
        .filter(PriceSnapshot.pulled_at <= target_time)
        .order_by(PriceSnapshot.pulled_at.desc())
        .first()
    )
    if start is None:
        return  # not enough history yet

    start_price = float(start.price_usd)
    end_price = float(latest.price_usd)
    if start_price == 0:
        return

    percent_change = ((end_price - start_price) / start_price) * 100.0
    abs_change = abs(percent_change)

    if abs_change < threshold_percent:
        return

    # 3) Cooldown: if we created a similar event recently, skip
    cutoff = now - timedelta(minutes=cooldown_minutes)
    recent = (
        db.query(MarketEvent)
        .filter(MarketEvent.coin_id == coin.id)
        .filter(MarketEvent.event_type == "PCT_MOVE")
        .filter(MarketEvent.created_at >= cutoff)
        .order_by(MarketEvent.created_at.desc())
        .first()
    )
    if recent is not None:
        return

    direction = "UP" if percent_change > 0 else "DOWN"
    msg = f"{symbol.upper()} moved {percent_change:.2f}% ({direction}) in {window_minutes}m"

    event = MarketEvent(
        coin_id=coin.id,
        event_type="PCT_MOVE",
        message=msg,
        window_minutes=window_minutes,
        threshold_percent=threshold_percent,
        start_price_usd=start_price,
        end_price_usd=end_price,
        percent_change=percent_change,
        created_at=now,
    )
    db.add(event)
    db.commit()
