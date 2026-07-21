from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@router.get("/version")
def version() -> dict:
    return {"version": "0.1.0"}
