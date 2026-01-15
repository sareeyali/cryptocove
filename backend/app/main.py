from fastapi import FastAPI

from app.api.prices import router as prices_router
from app.db.session import engine, Base
from app.models.coin import Coin
from app.models.price_snapshot import PriceSnapshot


app = FastAPI(title="CryptoCove API")

Base.metadata.create_all(bind=engine)

from app.api.snapshots import router as snapshots_router
app.include_router(snapshots_router)

@app.get("/")
def health():
    return {"status": "CryptoCove backend running"}

app.include_router(prices_router)
