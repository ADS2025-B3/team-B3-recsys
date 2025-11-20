from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/predict")
def predict():
    # placeholder logic
    return {"prediction": "result"}
