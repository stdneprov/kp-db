from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional
from auth import require_admin_or_super_admin, get_current_user
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Модели
class UserRequest(BaseModel):
    username: str = Field(..., max_length=255)
    password: Optional[str]
    role: Optional[str]


class UserResponse(BaseModel):
    id: int
    username: str = Field(..., max_length=255)
    role: str


# Создание игры
@router.post("/users", response_model=UserResponse)
async def create_user(user: UserRequest, request: Request, usr: dict = Depends(require_admin_or_super_admin) ):
    pool = request.state.pool

    query = """
        INSERT INTO users (username, role, password_hash)
        VALUES ($1, $2, $3)
        RETURNING id
    """

    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(query, user.username, user.role, hash_password(user.password))
            user_id = row["id"]

    return await get_user(user_id, request)

# Получение списка игр
@router.get("/users", response_model=List[UserResponse])
async def get_users(request: Request):
    pool = request.state.pool

    query = """
       SELECT id, username, role FROM users
    """

    async with pool.acquire() as conn:
        rows = await conn.fetch(query)

    return [
        UserResponse(
            id=row["id"],
            username=row["username"],
            role=row["role"],
        )
        for row in rows
    ]

# Получение игры по ID
@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, request: Request):
    pool = request.state.pool

    query = """
       SELECT id, username, role FROM users WHERE id=$1
    """

    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, user_id)

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=row["id"],
        username=row["username"],
        role=row["role"],
    )

# Обновление игры
@router.put("/users/{user_id}", response_model=UserResponse, dependencies=[Depends(require_admin_or_super_admin)])
async def update_user(user_id: int, user: UserRequest, request: Request):
    pool = request.state.pool

    update_fields = []

    if user.username:
        update_fields.append("username = $2")
    
    if user.password:
        update_fields.append("password_hash = $3")
    
    if user.role:
        update_fields.append("role = $4")

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")


    query = f"""
        UPDATE users
        SET {', '.join(update_fields)}
        WHERE id = $1
        RETURNING id
    """

    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(query, user_id, user.username, hash_password(user.password), user.role)
            if not row:
                raise HTTPException(status_code=404, detail="User not found")

    return await get_user(user_id, request)

# Удаление игры
@router.delete("/users/{user_id}", dependencies=[Depends(require_admin_or_super_admin)])
async def delete_user(user_id: int, request: Request):
    pool = request.state.pool

    query = "DELETE FROM users WHERE id = $1 RETURNING id"

    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, user_id)

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User deleted successfully", "id": row["id"]}
