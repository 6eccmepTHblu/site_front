from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import joinedload
from typing import Optional, Type, Literal
from contextlib import contextmanager

from .models import Word, Settings, Translation

SQLALCHEMY_DATABASE_URL = 'postgresql://vocabulary_kkxg_user:qAGXTDt2koaNHq5P9uMcuCvnyIeEyVXB@dpg-cukc47t6l47c73ca0jg0-a.oregon-postgres.render.com/vocabulary_kkxg'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=StaticPool,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

SETTING_PARAMS = Literal['translation_direction', 'check_method', 'max_repetitions']


class TranslationRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_translation(self, word_id: int, russian: str) -> Translation:
        word_db = WordRepository(self.session)
        word = word_db.get(word_id, include_translations=True)
        if not word:
            raise ValueError(f'Word with id {word_id} not found')

        translation = Translation(russian=russian, word_id=word_id)
        self.session.add(translation)
        self.session.commit()
        self.session.refresh(translation)
        return translation

    def update_translation(
        self, translation_id: int, new_russian: str
    ) -> Type[Translation]:
        translation = (
            self.session.query(Translation)
            .filter(Translation.id == translation_id)
            .first()
        )
        if not translation:
            raise ValueError(f'Translation with id {translation_id} not found')

        translation.russian = new_russian
        self.session.commit()
        self.session.refresh(translation)
        return translation

    def delete_translation(self, translation_id: int):
        translation = (
            self.session.query(Translation)
            .filter(Translation.id == translation_id)
            .first()
        )
        if not translation:
            raise ValueError(f'Translation with id {translation_id} not found')

        self.session.delete(translation)
        self.session.commit()

    def get_translations(self, word_id: int) -> list[Type[Translation]]:
        return (
            self.session.query(Translation).filter(Translation.word_id == word_id).all()
        )

    def get_translation(self, translation_id: int) -> Optional[Translation]:
        return (
            self.session.query(Translation)
            .filter(Translation.id == translation_id)
            .first()
        )


class WordRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, word_id: int, include_translations: bool = False) -> Optional[Word]:
        query = self.session.query(Word)
        if include_translations:
            query = query.options(joinedload(Word.translations))
        return query.filter(Word.id == word_id).first()

    def get_by_english(
        self, english: str, include_translations: bool = False
    ) -> Optional[Word]:
        query = self.session.query(Word)
        if include_translations:
            query = query.options(joinedload(Word.translations))
        return query.filter(Word.english == english).first()

    def get_all(
        self, skip: int = 0, limit: int = None, include_translations: bool = False
    ) -> list[Type[Word]]:
        query = self.session.query(Word)
        if include_translations:
            query = query.options(joinedload(Word.translations))
        if limit:
            return query.offset(skip).limit(limit).all()
        return query.offset(skip).all()

    def get_selected(self, include_translations: bool = False) -> list[Type[Word]]:
        query = self.session.query(Word).filter(Word.selected == True)
        if include_translations:
            query = query.options(joinedload(Word.translations))
        return query.all()

    def add(self, word: Word) -> Word:
        self.session.add(word)
        self.session.commit()
        self.session.refresh(word)
        return word

    def update(self, word: Word) -> Word:
        if not self.exists(word.english):
            self.add(word)
        else:
            self.session.commit()
            self.session.refresh(word)
        return word

    def delete(self, word: Word):
        self.session.delete(word)
        self.session.commit()

    def set_repetition_count(self, word: Word, count: int = 0):
        word.repetition_count = count
        word = self.update(word)
        return word

    def set_selected_status(
        self, word: Optional[Word] = None, status: bool = False
    ) -> list[Type[Word]] | Word:
        if word is None:
            # Получаем все слова и обновляем статус
            words = self.session.query(Word).all()
            for word in words:
                word.selected = status
        else:
            # Обновляем статус одного слова
            word.selected = status
        word = self.update(word)
        return word

    def set_remember_status(self, word: Word, status: bool = False) -> Word:
        word.remember = status
        self.update(word)
        return word


    def exists(self, english: str) -> bool:
        """
        Check if word exists in database

        Args:
            english: English word to check

        Returns:
            True if word exists, False otherwise
        """
        return bool(
            self.session.query(Word)
            .filter(Word.english.ilike(english.strip()))
            .first()
        )


class SettingsRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, key: SETTING_PARAMS) -> Optional[str]:
        setting = self.session.query(Settings).filter(Settings.key == key).first()
        return setting.value if setting else None

    def set(self, key: SETTING_PARAMS, value: str):
        setting = self.session.query(Settings).filter(Settings.key == key).first()
        if setting:
            setting.value = value
        else:
            new_setting = Settings(key=key, value=value)
            self.session.add(new_setting)
        self.session.commit()


class DatabaseManager:
    def __init__(self):
        self.session = SessionLocal()
        self.db_word = WordRepository(self.session)
        self.db_translation = TranslationRepository(self.session)
        self.db_settings = SettingsRepository(self.session)

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        try:
            yield self.session
            self.session.commit()
        except:
            self.session.rollback()
            raise
        finally:
            self.session.close()

    def __del__(self):
        self.session.close()


dm = DatabaseManager()


def get_db_manager():
    return dm
