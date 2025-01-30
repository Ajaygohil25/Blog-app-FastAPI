from fastapi import FastAPI
from authentication import auth
from core.database import engine
from core.models import Base
from routers import users, blog

app = FastAPI()
app.include_router(users.router)
app.include_router(blog.router)
# app.include_router(auth.router)

Base.metadata.create_all(engine)

@app.get("/")
async def root():
    return {"message": "Welcome you are on root !"}

