from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello from FastAPI on Vercel 🚀"}

# Penting: ini handler yang dipanggil Vercel
handler = Mangum(app)
