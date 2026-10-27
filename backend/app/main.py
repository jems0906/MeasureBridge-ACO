from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.routes import care_gaps, imports, measures, reports, workflows
from app.config import settings
from app.models import engine


app = FastAPI(title="MeasureBridge ACO", version="1.0.0", description="Synthetic educational workspace. No real patient information. Not a CMS submission system.")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins.split(","), allow_methods=["GET", "POST", "PUT"], allow_headers=["Content-Type"])
for router in (imports.router, measures.router, care_gaps.router, workflows.router, reports.router):
    app.include_router(router)


@app.get("/api/health")
def health():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "ok", "mode": "synthetic_educational_only"}