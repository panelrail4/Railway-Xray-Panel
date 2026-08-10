from fastapi import APIRouter, Depends, HTTPException
from ..security import require_admin
from ..xray.stats import query_all, parse_stats
router=APIRouter(prefix="/api/stats",tags=["stats"])
@router.get("")
def stats(_=Depends(require_admin)):
    try: return parse_stats(query_all())
    except Exception as e: raise HTTPException(status_code=503,detail=str(e))
