import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routers import metadata, flashcards, sessions
from app.database import SessionLocal
from app.services.session_service import abandon_stale_sessions, get_sprint_session, complete_sprint_session


async def stale_session_watcher():
    """每 60 秒掃描一次，將超過 15 分鐘仍是 in_progress 的 session 標為 abandoned"""
    while True:
        await asyncio.sleep(60)
        db = SessionLocal()
        try:
            count = abandon_stale_sessions(db, timeout_seconds=900)
            if count:
                print(f"[Watcher] Abandoned {count} stale session(s)")
        finally:
            db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(stale_session_watcher())
    yield
    task.cancel()


app = FastAPI(title="Sprint Reader API", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(metadata.router)
app.include_router(flashcards.router)
app.include_router(sessions.router)


@app.websocket("/ws/sessions/{sprint_id}")
async def session_websocket(websocket: WebSocket, sprint_id: str):
    await websocket.accept()
    print(f"[WS] Session {sprint_id} connected")
    try:
        # 保持連線直到客戶端斷開
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        # 連線斷開 → 立即檢查是否需要標記為 abandoned
        print(f"[WS] Session {sprint_id} disconnected")
        db = SessionLocal()
        try:
            from datetime import datetime, timezone, timedelta
            TW_TZ = timezone(timedelta(hours=8))
            session = get_sprint_session(db, sprint_id)
            if session and session.completion_status == "in_progress":
                session.completion_status = "abandoned"
                session.end_timestamp = datetime.now(TW_TZ).isoformat()
                db.commit()
                print(f"[WS] Session {sprint_id} marked as abandoned")
        except Exception as e:
            print(f"[WS] Error abandoning session {sprint_id}: {e}")
        finally:
            db.close()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(metadata.router)
app.include_router(flashcards.router)
app.include_router(sessions.router)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "presprint.html")

@app.get("/reader", response_class=HTMLResponse)
def reader_page(request: Request):
    return templates.TemplateResponse(request, "reader.html")

@app.get("/handoff", response_class=HTMLResponse)
def handoff_page(request: Request):
    return templates.TemplateResponse(request, "handoff.html")