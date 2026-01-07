from fastapi import FastAPI

from app.api.prices import router as prices_router

app = FastAPI(title="CryptoCove API")

@app.get("/")
def health():
    return {"status": "CryptoCove backend running"}

app.include_router(prices_router)
