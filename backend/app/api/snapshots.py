from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.coin import Coin
from app.models.price_snapshot import PriceSnapshot
from app.services.coingecko import get_simple_price_usd

router = APIRouter(prefix="/snapshots", tags=["snapshots"])


@router.post("/pull/btc")
def pull_btc_snapshot(db: Session = Depends(get_db)):
    # 1) Make sure BTC exists in coins table
    coin = db.query(Coin).filter(Coin.symbol == "btc").first()
    if coin is None:
        coin = Coin(symbol="btc", coingecko_id="bitcoin")
        db.add(coin)
        db.commit()
        db.refresh(coin)

    # 2) Fetch live price from CoinGecko
    price_data = get_simple_price_usd("bitcoin")
    price = price_data["usd"]


    # 3) Insert a new snapshot row
    snapshot = PriceSnapshot(
        coin_id=coin.id,
        price_usd=price,
        pulled_at=datetime.now(timezone.utc),
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    return {
        "coin": coin.symbol,
        "price_usd": float(snapshot.price_usd),
        "pulled_at": snapshot.pulled_at.isoformat(),
        "snapshot_id": snapshot.id,
    }


@router.get("/btc")
def get_btc_history(limit: int = 100, db: Session = Depends(get_db)):
    coin = db.query(Coin).filter(Coin.symbol == "btc").first()
    if coin is None:
        return []

    rows = (
        db.query(PriceSnapshot)
        .filter(PriceSnapshot.coin_id == coin.id)
        .order_by(PriceSnapshot.pulled_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {"price_usd": float(r.price_usd), "pulled_at": r.pulled_at.isoformat()}
        for r in rows
    ]
