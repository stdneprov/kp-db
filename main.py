from fastapi import FastAPI
from asyncpg import create_pool
from settings import DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT
from login import router as login_router
from resetPassword import router as reset_password_router
from register import router as register_router
from genres import router as genres_router
from consoles import router as consoles_router
from companies import router as companies_router
from users import router as users_router
from games import router as games_router
from backup import router as backup_router
from front import router as front_router

app = FastAPI()

# Пул соединений
pool = None

@app.on_event("startup")
async def startup():
    global pool
    pool = await create_pool(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST,
        port=DB_PORT,
    )
    print("Database connection pool established")


@app.on_event("shutdown")
async def shutdown():
    global pool
    if pool:
        await pool.close()
        print("Database connection pool closed")


@app.middleware("http")
async def db_connection_middleware(request, call_next):
    request.state.pool = pool  # Передаем пул соединений через request.state
    response = await call_next(request)
    return response

# Подключение маршрутов
app.include_router(login_router, prefix="/api")
app.include_router(reset_password_router, prefix="/api")
app.include_router(register_router, prefix="/api")
app.include_router(genres_router, prefix="/api")
app.include_router(consoles_router, prefix="/api")
app.include_router(companies_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(games_router, prefix="/api")
app.include_router(backup_router, prefix="/api")
app.include_router(front_router, prefix="")
