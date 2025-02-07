from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.database import engine
from core.models import Base
from routers import users, blog

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(blog.router)
# app.include_router(auth.router)

Base.metadata.create_all(engine)

@app.get("/")
async def root():
    return {"message": "Welcome you are on root !"}

