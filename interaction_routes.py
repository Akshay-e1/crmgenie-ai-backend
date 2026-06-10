from fastapi import APIRouter
from database import interactions_collection

router = APIRouter()


@router.post("/save-interaction")
def save_interaction(data: dict):

    result = interactions_collection.insert_one(data)

    return {
        "message": "Interaction Saved Successfully",
        "id": str(result.inserted_id)
    }