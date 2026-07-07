from fastapi import APIRouter, HTTPException

from agents.pipeline import analyze
from agents.schemas import AnalysisResult
from app.schemas import AnalyzeRequest

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResult)
def analyze_hook(request: AnalyzeRequest) -> AnalysisResult:
    if not request.hook_text.strip():
        raise HTTPException(status_code=422, detail="hook_text cannot be empty")
    return analyze(request.hook_text)
