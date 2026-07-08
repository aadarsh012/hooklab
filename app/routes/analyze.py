import logging
import traceback

from fastapi import APIRouter, HTTPException

from agents.pipeline import analyze
from agents.schemas import AnalysisResult
from app.schemas import AnalyzeRequest

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze", response_model=AnalysisResult)
def analyze_hook(request: AnalyzeRequest) -> AnalysisResult:
    if not request.hook_text.strip():
        raise HTTPException(status_code=422, detail="hook_text cannot be empty")
    logger.info("POST /analyze — hook: '%s'", request.hook_text[:60])
    try:
        result = analyze(request.hook_text)
        logger.info("Analysis complete — score: %s", result.score_breakdown.label)
        return result
    except Exception as e:
        logger.error("Analysis failed: %s\n%s", e, traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
