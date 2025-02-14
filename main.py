import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import words
from app.routers import settings
from apscheduler.schedulers.background import BackgroundScheduler
import requests

app = FastAPI(title='Vocabulary API')

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(words.router)
app.include_router(settings.router)

# Функция для пинга сервера
def ping_server():
    try:
        response = requests.get("https://site-front-5j5u.onrender.com")
        print(f"Ping successful. Status code: {response.status_code}")
    except Exception as e:
        print(f"Ping failed. Error: {str(e)}")

# Настройка и запуск планировщика
scheduler = BackgroundScheduler()
scheduler.add_job(ping_server, 'interval', minutes=5)
scheduler.start()

# Добавьте эндпоинт для проверки работоспособности
@app.get("/api/health-check")
async def health_check():
    return {"status": "ok"}

if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)
