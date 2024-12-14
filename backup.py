import subprocess
import settings
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from datetime import datetime
from auth import require_admin_or_super_admin

router = APIRouter()

@router.get("/backup", response_class=FileResponse, dependencies=[Depends(require_admin_or_super_admin)])
async def backup_database():
    """
    Создает резервную копию базы данных и возвращает SQL-дамп.
    """

    # Генерация имени файла
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dump_filename = f"backup_{settings.DB_NAME}_{timestamp}.sql"

    # Выполнение команды pg_dump
    dump_path = os.path.join("/tmp", dump_filename)  # Используем временную директорию для дампа

    try:
        result = subprocess.run(
            [
                "pg_dump",
                "-h", settings.DB_HOST,
                "-p", settings.DB_PORT,
                "-U", settings.DB_USER,
                "-F", "c",  # Формат SQL-дампа
                "-f", dump_path,
                settings.DB_NAME,
            ],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка создания дампа: {e.stderr}")

    # Возврат файла в ответе
    return FileResponse(
        path=dump_path,
        filename=dump_filename,
        media_type="application/sql",
        headers={"Content-Disposition": f"attachment; filename={dump_filename}"}
    )
