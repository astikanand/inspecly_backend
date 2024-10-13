from apis.inspection_apis.models import ImageWithBase64DataModel


def format_inspection_data(inspection) -> dict:
    return {
        "id": str(inspection["_id"]),
        "original_image": None if inspection["original_image"] is None else ImageWithBase64DataModel.from_image(inspection["original_image"]), 
        "processed_image": None if inspection["processed_image"] is None else ImageWithBase64DataModel.from_image(inspection["processed_image"]),
        "inspection_status": inspection["inspection_status"],
        "total_nuts": inspection["total_nuts"],
        "aligned_nuts": inspection["aligned_nuts"],
        "misaligned_nuts": inspection["misaligned_nuts"],
        "non_marked_nuts": inspection["non_marked_nuts"],
        "created": inspection["updated"],
        "updated": inspection["updated"],
    }
