from datetime import datetime, timezone, timedelta
from uuid import uuid4

TW_TZ = timezone(timedelta(hours=8))

from sqlalchemy.orm import Session

from app.models import SprintSessions, LearningJourneyMap


def create_sprint_session(db: Session, agent_id: str, module_id: str) -> SprintSessions:
    # 自動放棄同一 agent 的舊 in_progress session
    if agent_id:
        stale_sessions = (
            db.query(SprintSessions)
            .filter(
                SprintSessions.agent_id == agent_id,
                SprintSessions.completion_status == "in_progress"
            )
            .all()
        )
        now = datetime.now(TW_TZ).isoformat()
        for stale in stale_sessions:
            stale.completion_status = "abandoned"
            stale.end_timestamp = now
        if stale_sessions:
            db.commit()

    sprint_id = f"SPRINT_{uuid4().hex[:8].upper()}"

    session = SprintSessions(
        sprint_id=sprint_id,
        agent_id=agent_id,
        module_id=module_id,
        start_timestamp=datetime.now(TW_TZ).isoformat(),  # UTC+8 台灣時間
        end_timestamp=None,
        remaining_time=420,
        tab_switch_count=0,
        is_paused=0,
        completion_status="in_progress"
    )

    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_sprint_session(db: Session, sprint_id: str) -> SprintSessions | None:
    return db.query(SprintSessions).filter(SprintSessions.sprint_id == sprint_id).first()


def pause_sprint_session(db: Session, session: SprintSessions, remaining_time: int) -> SprintSessions:
    session.remaining_time = remaining_time
    session.is_paused = 1
    session.tab_switch_count += 1

    db.commit()
    db.refresh(session)
    return session


def resume_sprint_session(db: Session, session: SprintSessions, remaining_time: int) -> SprintSessions:
    session.remaining_time = remaining_time
    session.is_paused = 0

    db.commit()
    db.refresh(session)
    return session


def update_sprint_progress(db: Session, session: SprintSessions, remaining_time: int) -> SprintSessions:
    session.remaining_time = remaining_time

    db.commit()
    db.refresh(session)
    return session


def abandon_stale_sessions(db: Session, timeout_seconds: int = 900) -> int:
    """將 start_timestamp 超過 timeout_seconds 仍是 in_progress 的 session 標為 abandoned。
    sprint 最長 420 秒，預設 15 分鐘後視為殘留。"""
    now = datetime.now(TW_TZ)
    stale = (
        db.query(SprintSessions)
        .filter(SprintSessions.completion_status == "in_progress")
        .all()
    )
    count = 0
    for s in stale:
        if not s.start_timestamp:
            continue
        try:
            started = datetime.fromisoformat(s.start_timestamp)
        except ValueError:
            continue
        if (now - started).total_seconds() > timeout_seconds:
            s.completion_status = "abandoned"
            s.end_timestamp = now.isoformat()
            count += 1
    if count:
        db.commit()
    return count


def complete_sprint_session(
    db: Session,
    session: SprintSessions,
    completion_status: str,
    remaining_time: int
) -> SprintSessions:
    session.remaining_time = remaining_time
    session.completion_status = completion_status
    session.is_paused = 0
    session.end_timestamp = datetime.now(TW_TZ).isoformat()  # UTC+8 台灣時間

    # 產生遞增的 journey_id（J001, J002, ...）
    existing_count = db.query(LearningJourneyMap).count()
    journey_id = f"J{existing_count + 1:03d}"

    journey = LearningJourneyMap(
        journey_id=journey_id,
        sprint_id=session.sprint_id,
        quiz_session_id=None
    )
    db.add(journey)

    db.commit()
    db.refresh(session)
    return session