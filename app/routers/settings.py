from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from db.database import dm
from db.models import Settings

router = APIRouter(
    prefix="/api/settings",
    tags=["settings"],
    responses={404: {"description": "Not found"}},
)

class SettingUpdate(BaseModel):
    value: str

@router.get("/{key}")
def get_setting(key: str):
    """Получение значения настройки по ключу"""
    print(key)
    value = dm.db_settings.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail="Setting not found")
    return {"key": key, "value": value}

@router.put("/{key}")
def update_setting(key: str, setting: SettingUpdate):
    """Обновление значения настройки"""
    try:
        dm.db_settings.set(key, setting.value)
        return {"key": key, "value": setting.value}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/")
def get_all_settings():
    """Получение всех настроек"""
    settings = dm.session.query(Settings).all()
    return [{"key": setting.key, "value": setting.value} for setting in settings]