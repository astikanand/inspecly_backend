from datetime import datetime

from bson import ObjectId
from fastapi import UploadFile
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
    async def create_new_inspection(db: AsyncIOMotorDB, file: UploadFile) -> InspectionModel:
        logger.info("Create new inspection in db")
        original_image_data = await file.read()
        filename = file.filename

        new_inspection_data = InspectionModel(
            original_image=ImageWithBase64DataModel.to_image(filename, file.content_type, original_image_data),
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
        result_image_data, total_nut_bolts, aligned_nuts_bolts, misaligned_nuts_bolts, non_marked_nuts_bolts = alignment_result

        new_file_name = filename + "_processed." + filename.split(".") [-1]
        updated_inspection_data = InspectionUpdateModel(
            processed_image=ImageWithBase64DataModel.to_image(new_file_name, file.content_type, result_image_data),
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
