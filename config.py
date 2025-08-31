import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "two-sensations")
    DB_USER: str = os.getenv("DB_USER", "sensbot")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    
config = Config()

