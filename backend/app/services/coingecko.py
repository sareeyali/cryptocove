import time
from typing import Any, Dict

import requests


class CoinGeckoError(Exception):
    pass


def get_simple_price_usd(coin_id: str) -> Dict[str, Any]:
    """
    Fetch the current USD price for a CoinGecko coin id (e.g., 'bitcoin', 'ethereum').

    Returns:
      {
        "coin_id": "bitcoin",
        "usd": 12345.67,
        "fetched_at_unix": 1234567890
      }
    """
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": coin_id, "vs_currencies": "usd"}

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        raise CoinGeckoError(f"CoinGecko request failed: {e}") from e
    except ValueError as e:
        raise CoinGeckoError("CoinGecko returned invalid JSON") from e

    if coin_id not in data or "usd" not in data[coin_id]:
        raise CoinGeckoError(f"Unexpected response for coin_id='{coin_id}': {data}")

    return {
        "coin_id": coin_id,
        "usd": float(data[coin_id]["usd"]),
        "fetched_at_unix": int(time.time()),
    }
