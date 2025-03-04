from fastapi import FastAPI
from app.auth.routes import oauth_route

app = FastAPI()

app.include_router(oauth_route, tags=["oauth"])
