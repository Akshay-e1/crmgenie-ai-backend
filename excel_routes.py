from fastapi import APIRouter
from fastapi.responses import FileResponse
from database import interactions_collection

from openpyxl import Workbook

router = APIRouter()


@router.get("/export-excel/{user_id}")
def export_excel(user_id: str):

    records = list(
        interactions_collection.find(
            {"user_id": user_id}
        )
    )

    if not records:
        return {"error": "No records found"}

    username = records[0].get("user_name", "User")

    excel_path = f"/tmp/{username}_{user_id}_History.xlsx"

    wb = Workbook()
    ws = wb.active

    ws.title = "Interaction History"

    # Header
    ws.append([
        "User Name",
        "User ID",
        "S.No",
        "HCP Name",
        "Topics",
        "Sentiment",
        "Outcomes",
        "Follow Up",
        "Date",
        "Time"
    ])

    # Data Rows
    for i, item in enumerate(records, start=1):

        ws.append([
            item.get("user_name", ""),
            item.get("user_id", ""),
            i,
            item.get("hcp_name", ""),
            item.get("topics", ""),
            item.get("sentiment", ""),
            item.get("outcomes", ""),
            item.get("follow_up", ""),
            item.get("date", ""),
            item.get("time", "")
        ])

    wb.save(excel_path)

    return FileResponse(
        path=excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"{username}_{user_id}_History.xlsx"
    )