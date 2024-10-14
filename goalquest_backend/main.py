from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # ตัวอย่างการนำเข้า CORS middleware

from . import config
from . import models
from . import routers

def create_app():
    settings = config.get_settings()
    app = FastAPI()

    # เพิ่ม middleware ที่ต้องการ
    app.add_middleware(
        CORSMiddleware,  # ตัวอย่าง middleware CORS
        allow_origins=["*"],  # ระบุที่มาที่อนุญาต เช่น ["https://example.com"]
        allow_credentials=True,
        allow_methods=["*"],  # ระบุวิธีที่อนุญาต เช่น ["GET", "POST"]
        allow_headers=["*"],  # ระบุ headers ที่อนุญาต เช่น ["Content-Type"]
    )

    models.init_db(settings)
    routers.init_router(app)

    @app.on_event("startup")
    async def on_startup():
        await models.create_all()

    return app