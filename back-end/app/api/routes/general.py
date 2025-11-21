from fastapi import APIRouter
from app.api.deps import SessionDep

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/predict")
def predict():
    # placeholder logic
    return {"prediction": "result"}

@router.get("/test")
def test_db(session: SessionDep):
    try:
        session.exec("SELECT 1")
        return {"status": "connected"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
