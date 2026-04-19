from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routers import metadata, flashcards, sessions

app = FastAPI(title="Sprint Reader API")

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