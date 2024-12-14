from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional
from auth import require_admin_or_super_admin, get_current_user


router = APIRouter()

# Модели
class CompanyRequest(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str]


class CompanyResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    games_count: int


# Создание игры
@router.post("/companies", response_model=CompanyResponse)
async def create_company(company: CompanyRequest, request: Request, user: dict = Depends(get_current_user) ):
    pool = request.state.pool

    query = """
        INSERT INTO companies (title, description)
        VALUES ($1, $2)
        RETURNING id
    """

    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(query, company.title, company.description)
            company_id = row["id"]

    return await get_company(company_id, request)

# Получение списка игр
@router.get("/companies", response_model=List[CompanyResponse])
async def get_companies(request: Request):
    pool = request.state.pool

    query = """
       SELECT id, title, description, games_count FROM companies
    """

    async with pool.acquire() as conn:
        rows = await conn.fetch(query)

    return [
        CompanyResponse(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            games_count=row["games_count"]
        )
        for row in rows
    ]

# Получение игры по ID
@router.get("/companies/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: int, request: Request):
    pool = request.state.pool

    query = """
       SELECT id, title, description, games_count FROM companies WHERE id=$1
    """

    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, company_id)

    if not row:
        raise HTTPException(status_code=404, detail="Company not found")

    return CompanyResponse(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        games_count=row["games_count"]
    )

# Обновление игры
@router.put("/companies/{company_id}", response_model=CompanyResponse, dependencies=[Depends(get_current_user)])
async def update_company(company_id: int, company: CompanyRequest, request: Request):
    pool = request.state.pool

    update_fields = []

    if company.title:
        update_fields.append("title = $2")
    
    if company.description:
        update_fields.append("decription = $3")

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")


    query = f"""
        UPDATE companies
        SET {', '.join(update_fields)}
        WHERE id = $1
        RETURNING id
    """

    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(query, company_id, company.title, company.description)
            if not row:
                raise HTTPException(status_code=404, detail="Company not found")

    return await get_company(company_id, request)

# Удаление игры
@router.delete("/companies/{company_id}", dependencies=[Depends(require_admin_or_super_admin)])
async def delete_company(company_id: int, request: Request):
    pool = request.state.pool

    query = "DELETE FROM companies WHERE id = $1 RETURNING id"

    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, company_id)

    if not row:
        raise HTTPException(status_code=404, detail="Company not found")

    return {"message": "Company deleted successfully", "id": row["id"]}
