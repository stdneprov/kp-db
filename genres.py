from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional
from auth import require_admin_or_super_admin, get_current_user


router = APIRouter()

# Модели
class GenreRequest(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str]


class GenreResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    games_count: int


# Создание игры
@router.post("/genres", response_model=GenreResponse)
async def create_genre(genre: GenreRequest, request: Request, user: dict = Depends(get_current_user) ):
    pool = request.state.pool

    query = """
        INSERT INTO genres (title, description)
        VALUES ($1, $2)
        RETURNING id
    """

    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(query, genre.title, genre.description)
            genre_id = row["id"]

    return await get_genre(genre_id, request)

# Получение списка игр
@router.get("/genres", response_model=List[GenreResponse])
async def get_genres(request: Request):
    pool = request.state.pool

    query = """
       SELECT id, title, description, games_count FROM genres
    """

    async with pool.acquire() as conn:
        rows = await conn.fetch(query)

    return [
        GenreResponse(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            games_count=row["games_count"]
        )
        for row in rows
    ]

# Получение игры по ID
@router.get("/genres/{genre_id}", response_model=GenreResponse)
async def get_genre(genre_id: int, request: Request):
    pool = request.state.pool

    query = """
       SELECT id, title, description, games_count FROM genres WHERE id=$1
    """

    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, genre_id)

    if not row:
        raise HTTPException(status_code=404, detail="Genre not found")

    return GenreResponse(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        games_count=row["games_count"]
    )

# Обновление игры
@router.put("/genres/{genre_id}", response_model=GenreResponse, dependencies=[Depends(get_current_user)])
async def update_genre(genre_id: int, genre: GenreRequest, request: Request):
    pool = request.state.pool

    update_fields = []

    if genre.title:
        update_fields.append("title = $2")
    
    if genre.description:
        update_fields.append("decription = $3")

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")


    query = f"""
        UPDATE genres
        SET {', '.join(update_fields)}
        WHERE id = $1
        RETURNING id
    """

    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(query, genre_id, genre.title, genre.description)
            if not row:
                raise HTTPException(status_code=404, detail="Genre not found")

    return await get_genre(genre_id, request)

# Удаление игры
@router.delete("/genres/{genre_id}", dependencies=[Depends(require_admin_or_super_admin)])
async def delete_genre(genre_id: int, request: Request):
    pool = request.state.pool

    query = "DELETE FROM genres WHERE id = $1 RETURNING id"

    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, genre_id)

    if not row:
        raise HTTPException(status_code=404, detail="Genre not found")

    return {"message": "Genre deleted successfully", "id": row["id"]}
