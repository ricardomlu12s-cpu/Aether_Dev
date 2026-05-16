from __future__ import annotations

from fastapi import APIRouter

from ..config import APP_NAME, APP_VERSION, DATA_DIR
from ..database import database_file

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "app": APP_NAME,
        "version": APP_VERSION,
        "data_dir": str(DATA_DIR),
        "database": str(database_file()),
    }

