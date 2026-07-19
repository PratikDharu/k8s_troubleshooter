from fastapi import APIRouter

from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.analyzer import Analyzer

router = APIRouter()
analyzer = Analyzer()


@router.get("/health")
def health():
    return {"status": "healthy"}


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    result = analyzer.analyze(request.text)
    return AnalyzeResponse(**result)
