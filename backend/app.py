from database import SessionLocal, engine
import models
import schemas
from dependencies import get_db
from rules_engine import RulesEngine
# Remove direct import from durable.rules as it's handled within RulesEngine
# from durable.rules import Engine, KnowledgeBase

# ... existing code ...

from fastapi import FastAPI

# Create the FastAPI application instance
app = FastAPI()

# Add a simple health check endpoint to verify routing is working
@app.get("/health")
def health_check():
    return {"status": "ok"}

# You can add your routes and other application logic below this line

# Example route:
# @app.get("/")
# def read_root():
#     return {"Hello": "World"}

# Example of including routers:
# from .routers import items, users
# app.include_router(items.router)
# app.include_router(users.router) 