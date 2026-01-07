from fastapi import APIRouter, HTTPException

from app.services.coingecko import CoinGeckoError, get_simple_price_usd

router = APIRouter(prefix="/price", tags=["prices"])

# Convenience endpoint for BTC
@router.get("/btc")
def get_btc_price():
    try:
        return get_simple_price_usd("bitcoin")
    except CoinGeckoError as e:
        raise HTTPException(status_code=502, detail=str(e))


# Generic endpoint (optional, but nice)
@router.get("/{coin_id}")
def get_coin_price(coin_id: str):
    coin_id = coin_id.strip().lower()
    if not coin_id:
        raise HTTPException(status_code=400, detail="coin_id cannot be empty")

    try:
        return get_simple_price_usd(coin_id)
    except CoinGeckoError as e:
        raise HTTPException(status_code=502, detail=str(e))
