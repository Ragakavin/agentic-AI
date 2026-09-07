import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.database.session import Base, engine, SessionLocal
from backend.app.database.seed import seed_database

# Import routers
from backend.app.api.auth import router as auth_router
from backend.app.api.invoices import router as invoices_router
from backend.app.api.vendors import router as vendors_router
from backend.app.api.purchase_orders import router as po_router
from backend.app.api.agents import router as agents_router
from backend.app.api.analytics import router as analytics_router
from backend.app.api.reports import router as reports_router
from backend.app.api.ai_assistant import router as ai_router
from backend.app.api.notifications import router as notifications_router
from backend.app.api.audit_logs import router as audit_router
from backend.app.api.settings import router as settings_router
from backend.app.api.demo import router as demo_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("InvoiceAgentApp")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables and auto-seed benchmark data
    logger.info("Initializing database schemas...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        logger.info("Checking & seeding benchmark demo data...")
        seed_database(db)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Seeding error: {e}", exc_info=True)
    finally:
        db.close()

    yield
    # Shutdown
    logger.info("Application shutting down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Full-Stack Agentic AI Invoice Analysis and Processing System using LLM & Specialized Agents",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static File Mounting
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")
app.mount("/reports-files", StaticFiles(directory=str(settings.REPORT_DIR)), name="reports-files")

# Register Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(invoices_router, prefix=settings.API_V1_STR)
app.include_router(vendors_router, prefix=settings.API_V1_STR)
app.include_router(po_router, prefix=settings.API_V1_STR)
app.include_router(agents_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(ai_router, prefix=settings.API_V1_STR)
app.include_router(notifications_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(settings_router, prefix=settings.API_V1_STR)
app.include_router(demo_router, prefix=settings.API_V1_STR)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.LLM_MODEL
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
