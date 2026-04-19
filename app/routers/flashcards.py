import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import FlashcardPages
from app.schemas import FlashcardListResponse, FlashcardPageResponse

router = APIRouter(prefix="/api/modules", tags=["Flashcards"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{module_id}/flashcards", response_model=FlashcardListResponse)
def get_flashcards(module_id: str, db: Session = Depends(get_db)):
    pages = (
        db.query(FlashcardPages)
        .filter(FlashcardPages.module_id == module_id)
        .order_by(FlashcardPages.sequence_number.asc())
        .all()
    )

    if not pages:
        raise HTTPException(status_code=404, detail="Flashcards not found for this module")

    return FlashcardListResponse(
        module_id=module_id,
        pages=[
            FlashcardPageResponse(
                page_id=page.page_id,
                sequence_number=page.sequence_number,
                title=page.page_title,
                domain_tag=page.domain_tag,
                page_content_json=json.loads(page.page_content_json)
            )
            for page in pages
        ]
    )