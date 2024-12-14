from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional
from auth import require_admin_or_super_admin, get_current_user


router = APIRouter()

# Модели
class GameRequest(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str]
    console_id: Optional[int]
    company_id: Optional[int]
    genre_id: Optional[int]


class GameResponse(BaseModel):
    id: int
    description: Optional[str]
    title: str
    console: Optional[str]
    company: Optional[str]
    genre: Optional[str]


# Создание игры
@router.post("/games", response_model=GameResponse)
async def create_game(game: GameRequest, request: Request, user: dict = Depends(get_current_user) ):
    pool = request.state.pool

    query = """
        INSERT INTO games (title, description, console_id, company_id, genre_id)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id
    """

    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(query, game.title, game.description, game.console_id, game.company_id, game.genre_id)
            game_id = row["id"]

    return await get_game(game_id, request)

# Получение списка игр
@router.get("/games", response_model=List[GameResponse])
async def get_games(request: Request):
    pool = request.state.pool

    query = """
       SELECT id, title, description, company, console, genre FROM games_full_info
    """

    async with pool.acquire() as conn:
        rows = await conn.fetch(query)

    return [
        GameResponse(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            console=row["console"],
            company=row["company"],
            genre=row["genre"]
        )
        for row in rows
    ]

# Получение игры по ID
@router.get("/games/{game_id}", response_model=GameResponse)
async def get_game(game_id: int, request: Request):
    pool = request.state.pool

    query = """
       SELECT id, title, description, company, console, genre FROM games_full_info WHERE id=$1
    """

    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, game_id)

    if not row:
        raise HTTPException(status_code=404, detail="Game not found")

    return GameResponse(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        console=row["console"],
        company=row["company"],
        genre=row["genre"]
    )

# Обновление игры
@router.put("/games/{game_id}", response_model=GameResponse, dependencies=[Depends(get_current_user)])
async def update_game(game_id: int, game: GameRequest, request: Request):
    pool = request.state.pool

    update_fields = []

    if game.title:
        update_fields.append("title = $2")

    if game.console_id:
        update_fields.append("console_id = $3")

    if game.company_id:
        update_fields.append("company_id = $4")

    if game.genre_id:
        update_fields.append("genre_id = $5")
    
    if game.description:
        update_fields.append("description = $6")

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")


    query = f"""
        UPDATE games
        SET {', '.join(update_fields)}
        WHERE id = $1
        RETURNING id
    """

    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(query, game_id, game.title, game.console_id, game.company_id, game.genre_id, game.description)
            if not row:
                raise HTTPException(status_code=404, detail="Game not found")

    return await get_game(game_id, request)

# Удаление игры
@router.delete("/games/{game_id}", dependencies=[Depends(require_admin_or_super_admin)])
async def delete_game(game_id: int, request: Request):
    pool = request.state.pool

    query = "DELETE FROM games WHERE id = $1 RETURNING id"

    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, game_id)

    if not row:
        raise HTTPException(status_code=404, detail="Game not found")

    return {"message": "Game deleted successfully", "id": row["id"]}
