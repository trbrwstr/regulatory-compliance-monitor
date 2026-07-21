from fastapi import APIRouter, Depends

from auth import require_reviewer
from evaluation import evaluate_fixture

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])


@router.get("/fixture")
def run_fixture(_: str = Depends(require_reviewer)):
    result = evaluate_fixture("evaluation_fixtures.json")
    return result.__dict__
