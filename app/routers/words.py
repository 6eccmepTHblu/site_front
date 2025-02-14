from fastapi import APIRouter, HTTPException, Body
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from db.database import dm
from db.models import Word

class WordUpdate(BaseModel):
    id: int
    selected: bool = True
    repetition_count: int = 0

router = APIRouter(
    prefix="/api/words",
    tags=["words"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
def get_words():
    """Получение списка всех слов"""
    words = dm.db_word.get_all(include_translations=True)
    return jsonable_encoder(words)

@router.get("/selected")
def get_selected_words():
    """Получение списка выбранных слов"""
    words = dm.db_word.get_selected(include_translations=True)
    return jsonable_encoder(words)

@router.get("/{word_id}")
def get_word(word_id: int):
    """Получение одного слова по ID"""
    word = dm.db_word.get(word_id, include_translations=True)
    return jsonable_encoder(word)


@router.patch("/{word_id}")
def update_word(word_id: int, word_update: dict):
    """Обновление параметров слова"""
    word = dm.db_word.get(word_id)
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")

    for key, value in word_update.items():
        setattr(word, key, value)

    updated_word = dm.db_word.update(word)
    return jsonable_encoder(updated_word)

@router.post("/clear-selected")
def clear_selected_words():
    with dm.session_scope() as session:
        session.query(Word).update({Word.selected: False})
    return {"message": "All words have been unselected"}


@router.post("/select-words")
def select_words(words_to_update: list = Body(...)):
    """Выбор слов и обновление их статуса"""
    try:
        with dm.session_scope() as session:
            # Подготовка данных для массового обновления
            update_data = [
                {
                    "id": word['id'],
                    "selected": word.get('selected', True),
                    "repetition_count": word.get('repetition_count', 0)
                }
                for word in words_to_update
            ]

            # Выполнение массового обновления
            session.bulk_update_mappings(Word, update_data)

            return {"message": "ОК"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")