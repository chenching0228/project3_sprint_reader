from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.schemas import (
    StartSessionRequest,
    StartSessionResponse,
    PauseResumeRequest,
    ProgressUpdateRequest,
    CompleteSessionRequest,
    SessionStateResponse,
    CompleteSessionResponse,
)
from app.services.session_service import (
    create_sprint_session,
    get_sprint_session,
    pause_sprint_session,
    resume_sprint_session,
    update_sprint_progress,
    complete_sprint_session,
)

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/start", response_model=StartSessionResponse)
def start_session(
    payload: StartSessionRequest,
    db: Session = Depends(get_db)
):
    session = create_sprint_session(
        db=db,
        agent_id=payload.agent_id,
        module_id=payload.module_id
    )

    return StartSessionResponse(
        sprint_id=session.sprint_id,
        module_id=session.module_id,
        remaining_time=session.remaining_time,
        tab_switch_count=session.tab_switch_count,
        is_paused=bool(session.is_paused),
        completion_status=session.completion_status
    )

@router.patch("/{sprint_id}/pause", response_model=SessionStateResponse)
def pause_session(
    sprint_id: str,
    payload: PauseResumeRequest,
    db: Session = Depends(get_db)
):
    session = get_sprint_session(db, sprint_id)

    if not session:
        raise HTTPException(status_code=404, detail="Sprint session not found")

    session = pause_sprint_session(
        db=db,
        session=session,
        remaining_time=payload.remaining_time
    )

    return SessionStateResponse(
        sprint_id=session.sprint_id,
        is_paused=bool(session.is_paused),
        tab_switch_count=session.tab_switch_count,
        remaining_time=session.remaining_time
    )

@router.patch("/{sprint_id}/resume", response_model=SessionStateResponse)
def resume_session(
    sprint_id: str,
    payload: PauseResumeRequest,
    db: Session = Depends(get_db)
):
    session = get_sprint_session(db, sprint_id)

    if not session:
        raise HTTPException(status_code=404, detail="Sprint session not found")

    session = resume_sprint_session(
        db=db,
        session=session,
        remaining_time=payload.remaining_time
    )

    return SessionStateResponse(
        sprint_id=session.sprint_id,
        is_paused=bool(session.is_paused),
        tab_switch_count=session.tab_switch_count,
        remaining_time=session.remaining_time
    )

@router.patch("/{sprint_id}/progress", response_model=SessionStateResponse)
def update_progress(
    sprint_id: str,
    payload: ProgressUpdateRequest,
    db: Session = Depends(get_db)
):
    session = get_sprint_session(db, sprint_id)

    if not session:
        raise HTTPException(status_code=404, detail="Sprint session not found")

    session = update_sprint_progress(
        db=db,
        session=session,
        remaining_time=payload.remaining_time
    )

    return SessionStateResponse(
        sprint_id=session.sprint_id,
        is_paused=bool(session.is_paused),
        tab_switch_count=session.tab_switch_count,
        remaining_time=session.remaining_time
    )

@router.patch("/{sprint_id}/complete", response_model=CompleteSessionResponse)
def complete_session(
    sprint_id: str,
    payload: CompleteSessionRequest,
    db: Session = Depends(get_db)
):
    session = get_sprint_session(db, sprint_id)

    if not session:
        raise HTTPException(status_code=404, detail="Sprint session not found")

    allowed_statuses = {"finished_early", "timed_out", "abandoned"}
    if payload.completion_status not in allowed_statuses:
        raise HTTPException(status_code=400, detail="Invalid completion status")

    session = complete_sprint_session(
        db=db,
        session=session,
        completion_status=payload.completion_status,
        remaining_time=payload.remaining_time
    )

    redirect_url = f"/quiz?session_id={session.sprint_id}&module_id={session.module_id}"

    return CompleteSessionResponse(
        sprint_id=session.sprint_id,
        session_id=session.sprint_id,
        completion_status=session.completion_status,
        redirect_url=redirect_url
    )