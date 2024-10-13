from datetime import datetime
from typing import Optional
import base64

from pydantic import BaseModel


class ImageWithBase64DataModel(BaseModel):
    filename: str
    content_type: str
    size: int
    image_data: Optional[str]  # Base64-encoded string

    @classmethod
    def to_image(cls, filename, content_type, original_image_data):
        return cls(
            filename=filename,
            content_type=content_type,
            size=len(original_image_data),
            image_data=base64.b64encode(original_image_data).decode('utf-8'),
        )

    @classmethod
    def from_image(cls, image_doc):
        return cls(
            filename=image_doc["filename"],
            content_type=image_doc["content_type"],
            size=image_doc["size"],
            image_data=image_doc["image_data"] if image_doc.get("image_data") else None
        )
    

class InspectionModel(BaseModel):
    original_image: Optional[ImageWithBase64DataModel]
    processed_image: Optional[ImageWithBase64DataModel]
    inspection_status: int
    total_nuts: int
    aligned_nuts: int
    misaligned_nuts: int
    non_marked_nuts: int
    created: datetime
    updated: datetime

    class Config:
        from_attributes = True


class InspectionUpdateModel(BaseModel):
    processed_image: Optional[ImageWithBase64DataModel]
    inspection_status: int
    total_nuts: int
    aligned_nuts: int
    misaligned_nuts: int
    non_marked_nuts: int
    updated: datetime