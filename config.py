import os
from dataclasses import dataclass, field
from dotenv import load_dotenv
from typing import List

load_dotenv()

@dataclass
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: str = os.getenv("DB_PORT")
    DB_NAME: str = os.getenv("DB_NAME")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    ADMINS: List[int] = field(default_factory=list)

    def __post_init__(self):
        # Инициализируем ADMINS после создания экземпляра
        if os.getenv("ADMINS"):
            self.ADMINS = [int(num) for num in os.getenv("ADMINS").split(",")]
    
config = Config()

