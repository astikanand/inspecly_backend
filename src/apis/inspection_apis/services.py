from datetime import datetime
from typing import Optional

from bson import ObjectId
from fastapi import HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase as AsyncIOMotorDB

from apis.inspection_apis.formatter import format_inspection_data
from apis.inspection_apis.models import (ImageWithBase64DataModel,
                                         InspectionModel,
                                         InspectionUpdateModel)
from apis.utils.custom_logger import get_logger
from config.setup import app_settings
from image_services.nut_bolt_alignment_check import get_alignment_checked_image

logger = get_logger(__name__)


class InspectionService:
    @staticmethod
    async def get_inspection_from_db(db: AsyncIOMotorDB, inspection_id: str) -> dict:
        logger.info("Get inspection date with id: %s from db", inspection_id)

        if found_inspection := await db[app_settings.INSPECTIOIN_COLLECTION].find_one({"_id": ObjectId(inspection_id)}):
            return format_inspection_data(found_inspection)


    @staticmethod
    async def create_new_inspection(db: AsyncIOMotorDB, new_inspection_data: UploadFile) -> InspectionModel:
        logger.info("Create new inspection in db")
        original_image_data = await new_inspection_data.read()
        filename, content_type = new_inspection_data.filename, new_inspection_data.content_type

        new_inspection_data = InspectionModel(
            original_image=ImageWithBase64DataModel.to_image(filename, content_type, original_image_data),
            processed_image=None,
            inspection_status=0,
            total_nuts=0,
            aligned_nuts=0,
            misaligned_nuts=0,
            non_marked_nuts=0,
            created=datetime.now(),
            updated=datetime.now(),
        )

        new_inspection = await db[app_settings.INSPECTIOIN_COLLECTION].insert_one(jsonable_encoder(new_inspection_data))
        created_inspection = await db[app_settings.INSPECTIOIN_COLLECTION].find_one({"_id": ObjectId(new_inspection.inserted_id)})

        alignment_result = get_alignment_checked_image(created_inspection["original_image"]["image_data"])
        result_image_data, total_nut_bolts, aligned_nuts_bolts, misaligned_nuts_bolts, non_marked_nuts_bolts  = alignment_result

        updated_inspection_data = InspectionUpdateModel(
            processed_image=ImageWithBase64DataModel.to_image(filename, content_type, result_image_data),
            inspection_status=int(total_nut_bolts == aligned_nuts_bolts),
            total_nuts=total_nut_bolts,
            aligned_nuts=aligned_nuts_bolts,
            misaligned_nuts=misaligned_nuts_bolts,
            non_marked_nuts=non_marked_nuts_bolts,
            updated=datetime.now(),
        )

        await db[app_settings.INSPECTIOIN_COLLECTION].update_one(
            {"_id": ObjectId(new_inspection.inserted_id)},
            {"$set": jsonable_encoder(updated_inspection_data)}
        )

        updated_inspection = await db[app_settings.INSPECTIOIN_COLLECTION].find_one({"_id": ObjectId(new_inspection.inserted_id)})

        return format_inspection_data(updated_inspection)



    @staticmethod
    async def update_inspection(
        db: AsyncIOMotorDB,
        inspection_id: str,
        status: Optional[int] = None,
        processed_file: Optional[UploadFile] = None) -> InspectionModel:
        update_data = {"updated": datetime.now()}

        if status is not None:
            update_data["inspection_status"] = status

        if processed_file:
            processed_image_data = await processed_file.read()
            processed_image_doc = {
                "filename": processed_file.filename,
                "content_type": processed_file.content_type,
                "size": len(processed_image_data),
                "image_data": processed_image_data,
            }
            update_data["processed_image"] = processed_image_doc

        # Update the inspection in MongoDB
        result = await db[app_settings.INSPECTIOIN_COLLECTION].update_one({"inspection_id": inspection_id}, {"$set": update_data})

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Inspection not found")

        # Return the updated inspection
        updated_inspection = await db[app_settings.INSPECTIOIN_COLLECTION].find_one({"_id": ObjectId(inspection_id)})
        return format_inspection_data(updated_inspection)

    @staticmethod
    async def delete_inspection(db: AsyncIOMotorDB, inspection_id: str):
        result = await db[app_settings.INSPECTIOIN_COLLECTION].delete_one({"inspection_id": inspection_id})

        if result.deleted_count == 1:
            return {"detail": "Inspection deleted successfully"}

        raise HTTPException(status_code=404, detail="Inspection not found")
