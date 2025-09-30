from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # nanti bisa ganti ke domain frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI on Vercel!"}

@app.get("/time")
def get_time():
    import datetime
    return {"now": datetime.datetime.utcnow().isoformat()}

# adapter supaya FastAPI bisa jalan di serverless (Vercel)
handler = Mangum(app)
