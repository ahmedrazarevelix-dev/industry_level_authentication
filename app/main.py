from fastapi import FastAPI
from app.api.auth import router as auth_router

app = FastAPI(title="IL Structure API")

app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "API is running!"}
