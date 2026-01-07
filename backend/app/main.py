from fastapi import FastAPI

app = FastAPI(title="CryptoCove API")

@app.get("/")
def health():
    return {"status": "CryptoCove backend running"}
