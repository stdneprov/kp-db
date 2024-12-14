from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# Создаем объект Jinja2Templates
templates = Jinja2Templates(directory="front")

# Создаем роутер
router = APIRouter()

# Главная страница, которая будет рендерить HTML-шаблон
@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Здесь передаем данные для шаблона
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/createGame", response_class=HTMLResponse)
async def read_root(request: Request):
    # Здесь передаем данные для шаблона
    return templates.TemplateResponse("createGame.html", {"request": request})

# Другой маршрут для рендеринга страницы
@router.get("/login", response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/consoles", response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse("consoles.html", {"request": request})

@router.get("/companies", response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse("companies.html", {"request": request})

@router.get("/genres", response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse("genres.html", {"request": request})

@router.get("/users", response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse("users.html", {"request": request})

@router.get("/createCompany", response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse("createCompany.html", {"request": request})

@router.get("/createConsole", response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse("createConsole.html", {"request": request})

@router.get("/createGenre", response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse("createGenre.html", {"request": request})

@router.get("/createUser", response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse("createUser.html", {"request": request})
