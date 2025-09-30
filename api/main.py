from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello from FastAPI on Vercel 🚀"}

handler = Mangum(app)  # <--- wajib, agar Vercel bisa invoke
