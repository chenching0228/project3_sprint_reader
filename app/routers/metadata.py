import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import ModuleMetadata
from app.schemas import ModuleMetadataResponse

router = APIRouter(prefix="/api/modules", tags=["Metadata"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{module_id}/metadata", response_model=ModuleMetadataResponse)
def get_module_metadata(module_id: str, db: Session = Depends(get_db)):
    module = db.query(ModuleMetadata).filter(ModuleMetadata.module_id == module_id).first()

    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    return ModuleMetadataResponse(
        module_id=module.module_id,
        source_document=module.source_document,
        source=module.source,
        domains=json.loads(module.domain_tags_json),
        warning_text=module.warning_text
    )