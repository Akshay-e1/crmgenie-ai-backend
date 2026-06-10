from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import routes
from auth_routes import router as auth_router
from db import engine
from models import Base
from dotenv import load_dotenv
from interaction_routes import router as interaction_router
load_dotenv()
app = FastAPI()
from history_routes import router as history_router
from pdf_routes import router as pdf_router
from excel_routes import router as excel_router

# 🔥 CREATE TABLES
Base.metadata.create_all(bind=engine)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://crmgenieai.netlify.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)
app.include_router(auth_router)
app.include_router(interaction_router)
app.include_router(history_router)
app.include_router(pdf_router)
app.include_router(excel_router)