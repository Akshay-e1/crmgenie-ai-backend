from fastapi import APIRouter
from database import interactions_collection

router = APIRouter()

@router.get("/history/{user_id}")
def get_history(user_id: str):

    records = list(
        interactions_collection.find(
            {"user_id": user_id},
            {"_id": 0}
        )
    )

    for i, record in enumerate(records, start=1):
        record["serial_no"] = i

    return records