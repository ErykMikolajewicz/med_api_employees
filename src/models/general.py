from typing import Dict, Annotated

from fastapi import Query, Depends


async def pagination(page_number: int = Query(1, gt=0),
                     page_size: int = Query(10, gt=0)) -> Dict[str, int]:
    page_size = min(100, page_size)
    offset = page_size*(page_number - 1)
    return {'offset': offset, 'page_size': page_size}

pagination_dependency = Annotated[dict[str, int], Depends(pagination)]

