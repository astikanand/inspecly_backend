from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi import FastAPI, File, UploadFile
from typing import Optional

from apis.inspection_apis.models import InspectionModel
from apis.inspection_apis.services import InspectionService

from apis.utils.custom_logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/inspection/{inspection_id}", response_model=InspectionModel)
async def get_inspection(request: Request, inspection_id: str):
    logger.info(f"Get inspection with id - {inspection_id}")

    try:
        if found_inspection := await InspectionService.get_inspection_from_db(request.app.database, inspection_id):
            return found_inspection
        else:
            raise HTTPException(404, f"Error occurred: user with id - {inspection_id} not found")
    except Exception as ex:
        logger.exception(f"Exception Occurred while getting user with id - {inspection_id}: {ex}")
        raise HTTPException(500, "Unexpected Error occurred while getting the user")


@router.post("/create-inspection", response_model=InspectionModel)
async def add_new_inspection(request: Request, new_inspection_data: UploadFile = File(...)):
    logger.info(f"Create new inspection with request data")

    try:
        if created_inspection := await InspectionService.create_new_inspection(request.app.database, new_inspection_data):
            return created_inspection
        else:
            raise HTTPException(400, "Error Occurred: Bad request format")
    except Exception as ex:
        logger.exception(f"Exception Occurred while creating new inspection: {ex}")
        raise HTTPException(500, "Unexpected Error occurred while creating new inspection")

@router.put("/inspection/{inspection_id}", response_model=InspectionModel)
async def update_inspection(inspection_id: str, status: Optional[int] = None, processed_file: Optional[UploadFile] = File(None)):
    return await InspectionService.update_inspection(inspection_id, status, processed_file)

@router.delete("/inspection/{inspection_id}")
async def delete_inspection(inspection_id: str):
    return await InspectionService.delete_inspection(inspection_id)


