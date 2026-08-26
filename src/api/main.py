from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from src.api.routers import auth, health, logs, products, users, exporter
from src.api.infrastructure.database import init_db
from src.api.config import get_settings


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_ROOT = PROJECT_ROOT / "front"
TEMPLATES_ROOT = FRONTEND_ROOT / "templates"
STATIC_ROOT = FRONTEND_ROOT / "static"

settings = get_settings()
templates = Jinja2Templates(directory=str(TEMPLATES_ROOT))


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(logs.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(exporter.router)

app.mount("/static", StaticFiles(directory=str(STATIC_ROOT)), name="static")

@app.get("/{page_path:path}", include_in_schema=False)
async def render_page(request: Request, page_path: str):
    # Normalize path (e.g., "auth/login" or "auth/login.html" -> "auth/login")
    clean_path = page_path.strip("/")
    if clean_path.endswith(".html"):
        clean_path = clean_path[:-5]

    # Check authentication for protected routes
    is_login_page = clean_path == "auth/login"
    has_token = "access_token" in request.cookies

    if not is_login_page and not has_token:
        return RedirectResponse(url="/auth/login.html", status_code=307)

    # Determine template name
    template_name = f"{clean_path or 'index'}.html"

    template_path = (TEMPLATES_ROOT / template_name).resolve()
    if TEMPLATES_ROOT not in template_path.parents or template_path.suffix != ".html":
        raise HTTPException(status_code=404, detail="Page not found")
    if not template_path.is_file():
        raise HTTPException(status_code=404, detail="Page not found")

    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context={"settings": settings},
    )
