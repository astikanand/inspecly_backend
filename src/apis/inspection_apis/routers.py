from typing import Optional

from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from apis.inspection_apis.models import InspectionModel
from apis.inspection_apis.services import InspectionService
from apis.utils.custom_logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/inspection/{inspection_id}", response_description="Get the Inspection data by Id")
async def get_inspection(request: Request, inspection_id: str):
    logger.info("Get inspection with id: %s", inspection_id)

    try:
        if found_inspection := await InspectionService.get_inspection_from_db(request.app.database, inspection_id):
            return found_inspection
        raise HTTPException(404, f"Error occurred: user with id - {inspection_id} not found")
    except Exception as ex:
        logger.exception("Exception Occurred while getting user with id: %s, %s", inspection_id, ex)
        raise HTTPException(500, "Unexpected Error occurred while getting the user") from ex


@router.post("/create-inspection", response_description="New Inspection Data")
async def add_new_inspection(request: Request, file: UploadFile = File(...)):
    logger.info("Create new inspection with request data")

    try:
        if created_inspection := await InspectionService.create_new_inspection(request.app.database, file):
            return created_inspection
        raise HTTPException(400, "Error Occurred: Bad request format")
    except Exception as ex:
        logger.exception("Exception Occurred while creating new inspection: %s", ex)
        raise HTTPException(500, "Unexpected Error occurred while creating new inspection") from ex

@router.put("/inspection/{inspection_id}", response_model=InspectionModel)
async def update_inspection(inspection_id: str, status: Optional[int] = None, processed_file: Optional[UploadFile] = File(None)):
    return await InspectionService.update_inspection(inspection_id, status, processed_file)

# @router.delete("/inspection/{inspection_id}")
# async def delete_inspection(inspection_id: str):
#     return await InspectionService.delete_inspection(inspection_id)
