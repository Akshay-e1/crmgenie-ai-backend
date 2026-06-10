from fastapi import APIRouter
from fastapi.responses import FileResponse
from database import interactions_collection

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet

router = APIRouter()


@router.get("/export-pdf/{user_id}")
def export_pdf(user_id: str):

    records = list(
        interactions_collection.find(
            {"user_id": user_id}
        )
    )

    if not records:
        return {"error": "No records found"}

    username = records[0]["user_name"]

    filename = f"{username}_{user_id}_History.pdf"

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            f"<b>User Name:</b> {username}",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph(
            f"<b>User ID:</b> {user_id}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 20))

    for i, item in enumerate(records, start=1):

        elements.append(
            Paragraph(
                f"<b>Interaction #{i}</b>",
                styles["Heading2"]
            )
        )

        elements.append(
            Paragraph(
                f"HCP Name: {item.get('hcp_name')}",
                styles["Normal"]
            )
        )

        elements.append(
            Paragraph(
                f"Topics: {item.get('topics')}",
                styles["Normal"]
            )
        )

        elements.append(
            Paragraph(
                f"Sentiment: {item.get('sentiment')}",
                styles["Normal"]
            )
        )

        elements.append(
            Paragraph(
                f"Outcomes: {item.get('outcomes')}",
                styles["Normal"]
            )
        )

        elements.append(
            Paragraph(
                f"Follow Up: {item.get('follow_up')}",
                styles["Normal"]
            )
        )

        elements.append(
            Paragraph(
                f"Date: {item.get('date')}",
                styles["Normal"]
            )
        )

        elements.append(
            Paragraph(
                f"Time: {item.get('time')}",
                styles["Normal"]
            )
        )

        elements.append(Spacer(1, 20))

        elements.append(PageBreak())

    doc.build(elements)

    return FileResponse(
        filename,
        media_type="application/pdf",
        filename=filename
    )