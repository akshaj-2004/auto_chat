from fastapi import FastAPI
from app.database import Base, engine
from app.routes.user import router as users_router
from app.routes.chat import router as chat_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users_router)
app.include_router(chat_router)
