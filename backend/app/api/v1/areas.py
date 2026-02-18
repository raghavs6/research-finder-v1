from fastapi import APIRouter

from app.core.config import AREA_CONFERENCES
from app.models.schemas import AreaItem, AreasResponse

router = APIRouter(tags=["areas"])


@router.get("/areas", response_model=AreasResponse)
def get_areas() -> AreasResponse:
    areas = [
        AreaItem(name=name, conferences=list(confs))
        for name, confs in AREA_CONFERENCES.items()
    ]
    return AreasResponse(areas=areas)
