from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional
from auth import require_admin_or_super_admin, get_current_user


router = APIRouter()

# Модели
class ConsoleRequest(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str]
    company_id: Optional[int]


class ConsoleResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    company: Optional[str]
    games_count: int


# Создание игры
@router.post("/consoles", response_model=ConsoleResponse)
async def create_console(console: ConsoleRequest, request: Request, user: dict = Depends(get_current_user) ):
    pool = request.state.pool

    query = """
        INSERT INTO consoles (title, description, company_id)
        VALUES ($1, $2, $3)
        RETURNING id
    """

    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(query, console.title, console.description, console.company_id)
            console_id = row["id"]

    return await get_console(console_id, request)

# Получение списка игр
@router.get("/consoles", response_model=List[ConsoleResponse])
async def get_consoles(request: Request):
    pool = request.state.pool

    query = """
       SELECT id, title, description, company, games_count FROM consoles_full_info
    """

    async with pool.acquire() as conn:
        rows = await conn.fetch(query)

    return [
        ConsoleResponse(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            company=row["company"],
            games_count=row["games_count"]
        )
        for row in rows
    ]

# Получение игры по ID
@router.get("/consoles/{console_id}", response_model=ConsoleResponse)
async def get_console(console_id: int, request: Request):
    pool = request.state.pool

    query = """
       SELECT id, title, description, company, games_count FROM consoles_full_info WHERE id=$1
    """

    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, console_id)

    if not row:
        raise HTTPException(status_code=404, detail="Console not found")

    return ConsoleResponse(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        company=row["company"],
        games_count=row["games_count"]
    )

# Обновление игры
@router.put("/consoles/{console_id}", response_model=ConsoleResponse, dependencies=[Depends(get_current_user)])
async def update_console(console_id: int, console: ConsoleRequest, request: Request):
    pool = request.state.pool

    update_fields = []

    if console.title:
        update_fields.append("title = $2")
    
    if console.description:
        update_fields.append("decription = $3")
    
    if console.company_id:
        update_fields.append("company_id = $4")

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")


    query = f"""
        UPDATE consoles
        SET {', '.join(update_fields)}
        WHERE id = $1
        RETURNING id
    """

    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(query, console_id, console.title, console.description, console.company_id)
            if not row:
                raise HTTPException(status_code=404, detail="Console not found")

    return await get_console(console_id, request)

# Удаление игры
@router.delete("/consoles/{console_id}", dependencies=[Depends(require_admin_or_super_admin)])
async def delete_console(console_id: int, request: Request):
    pool = request.state.pool

    query = "DELETE FROM consoles WHERE id = $1 RETURNING id"

    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, console_id)

    if not row:
        raise HTTPException(status_code=404, detail="Console not found")

    return {"message": "Console deleted successfully", "id": row["id"]}
