import asyncpg
from config import config

class Database:
    def __init__(self):
        self.pool = None

    async def create_pool(self):
        self.pool = await asyncpg.create_pool(
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        )

    async def create_tables(self):
        async with self.pool.acquire() as connection:
            # Таблица пользователей
            await connection.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    telegram_id BIGINT UNIQUE NOT NULL,
                    username VARCHAR(100),
                    first_name VARCHAR(100),
                    last_name VARCHAR(100),
                    language VARCHAR(10) DEFAULT 'ru',
                    gender VARCHAR(10),
                    age INTEGER,
                    photo TEXT,
                    topics JSONB DEFAULT '[]',
                    is_profile_completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')

            # Таблица отклоненных анкет
            await connection.execute('''
                CREATE TABLE IF NOT EXISTS rejections (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    rejected_user_id INTEGER REFERENCES users(id),
                    created_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(user_id, rejected_user_id)
                )
            ''')

    async def add_user(self, telegram_id, username, first_name, last_name):
        async with self.pool.acquire() as connection:
            return await connection.fetchrow('''
                INSERT INTO users (telegram_id, username, first_name, last_name)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (telegram_id) DO NOTHING
                RETURNING *
            ''', telegram_id, username, first_name, last_name)

    async def update_user_language(self, telegram_id, language):
        async with self.pool.acquire() as connection:
            await connection.execute('''
                UPDATE users SET language = $1 WHERE telegram_id = $2
            ''', language, telegram_id)

    async def update_user_profile(self, telegram_id, gender, age, photo, topics):
        async with self.pool.acquire() as connection:
            await connection.execute('''
                UPDATE users 
                SET gender = $1, age = $2, photo = $3, topics = $4, is_profile_completed = TRUE
                WHERE telegram_id = $5
            ''', gender, age, photo, topics, telegram_id)

    async def get_user(self, telegram_id):
        async with self.pool.acquire() as connection:
            return await connection.fetchrow('''
                SELECT * FROM users WHERE telegram_id = $1
            ''', telegram_id)

    async def get_random_user(self, current_user_id, excluded_ids):
        async with self.pool.acquire() as connection:
            return await connection.fetchrow('''
                SELECT * FROM users 
                WHERE id != $1 
                AND id NOT IN (SELECT rejected_user_id FROM rejections WHERE user_id = $1)
                AND is_profile_completed = TRUE
                ORDER BY RANDOM()
                LIMIT 1
            ''', current_user_id)

    async def add_rejection(self, user_id, rejected_user_id):
        async with self.pool.acquire() as connection:
            await connection.execute('''
                INSERT INTO rejections (user_id, rejected_user_id)
                VALUES ($1, $2)
                ON CONFLICT (user_id, rejected_user_id) DO NOTHING
            ''', user_id, rejected_user_id)

db = Database()

