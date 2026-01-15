from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.models.coin import Coin
from app.models.price_snapshot import PriceSnapshot
from app.services.coingecko import get_simple_price_usd


def ingest_btc_snapshot() -> None:
    """
    Runs in the background on a schedule.
    Pulls BTC price from CoinGecko and stores it in Supabase.
    """
    db = SessionLocal()
    try:
        # 1) Ensure BTC coin exists
        coin = db.query(Coin).filter(Coin.symbol == "btc").first()
        if coin is None:
            coin = Coin(symbol="btc", coingecko_id="bitcoin")
            db.add(coin)
            db.commit()
            db.refresh(coin)

        # 2) Fetch live price
        price_data = get_simple_price_usd("bitcoin")
        price_usd = price_data["usd"]

        # 3) Insert snapshot row
        snapshot = PriceSnapshot(
            coin_id=coin.id,
            price_usd=price_usd,
            pulled_at=datetime.now(timezone.utc),
        )
        db.add(snapshot)
        db.commit()

        # Optional: print log so you can see it working in terminal
        print(f"[ingest] btc=${price_usd} at {snapshot.pulled_at.isoformat()}")

    except Exception as e:
        # Keep the job from crashing silently
        print(f"[ingest][error] {e}")
        db.rollback()
    finally:
        db.close()
