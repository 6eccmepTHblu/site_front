from typing import List

from fastapi import APIRouter, HTTPException, Body
from fastapi.encoders import jsonable_encoder

from db.database import dm
from db.models import Word

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
def select_words(word_ids: List[int] = Body(...)):
    """Выбор слов по списку ID"""
    selected_words = []
    with dm.session_scope() as session:
        for word_id in word_ids:
            word = session.query(Word).filter(Word.id == word_id).first()
            if word:
                word.selected = True
                word.repetition_count = 0
                selected_words.append(word)
            else:
                raise HTTPException(status_code=404, detail=f"Word with id {word_id} not found")

        session.commit()

    return jsonable_encoder(selected_words)