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
                CREATE TABLE IF NOT EXISTS seekers (
                    id BIGSERIAL PRIMARY KEY,
                    telegram_id BIGINT UNIQUE NOT NULL,
                    companion_telegram_id BIGINT,
                    username VARCHAR(100),
                    first_name VARCHAR(100),
                    language SMALLINT DEFAULT 1,
                    gender SMALLINT,
                    age SMALLINT,
                    interested_age SMALLINT,
                    is_active BOOLEAN DEFAULT TRUE NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')

            # Таблица доп.информации
            await connection.execute('''
                CREATE TABLE IF NOT EXISTS topics (
                    seeker_id BIGINT REFERENCES seekers(telegram_id),
                    word_1 BOOLEAN DEFAULT FALSE NOT NULL,
                    word_2 BOOLEAN DEFAULT FALSE NOT NULL,
                    word_3 BOOLEAN DEFAULT FALSE NOT NULL,
                    word_4 BOOLEAN DEFAULT FALSE NOT NULL,
                    word_5 BOOLEAN DEFAULT FALSE NOT NULL,
                    word_6 BOOLEAN DEFAULT FALSE NOT NULL,
                    word_7 BOOLEAN DEFAULT FALSE NOT NULL,
                    word_8 BOOLEAN DEFAULT FALSE NOT NULL,
                    word_9 BOOLEAN DEFAULT FALSE NOT NULL,
                    word_10 BOOLEAN DEFAULT FALSE NOT NULL,
                    word_11 BOOLEAN DEFAULT FALSE NOT NULL,
                    word_12 BOOLEAN DEFAULT FALSE NOT NULL,
                    word_13 BOOLEAN DEFAULT FALSE NOT NULL,
                    word_14 BOOLEAN DEFAULT FALSE NOT NULL,
                    word_15 BOOLEAN DEFAULT FALSE NOT NULL,
                    word_16 BOOLEAN DEFAULT FALSE NOT NULL,
                    word_17 BOOLEAN DEFAULT FALSE NOT NULL,
                    word_18 BOOLEAN DEFAULT FALSE NOT NULL,
                    word_19 BOOLEAN DEFAULT FALSE NOT NULL,
                    word_20 BOOLEAN DEFAULT FALSE NOT NULL
                )
            ''')

            # Таблица доп.информации
            await connection.execute('''
                CREATE TABLE IF NOT EXISTS preferences (
                    id BIGSERIAL PRIMARY KEY,
                    seeker_id BIGINT REFERENCES seekers(telegram_id),
                    city VARCHAR(100),
                    is_city_only BOOLEAN DEFAULT FALSE NOT NULL,
                    is_seekable BOOLEAN DEFAULT TRUE NOT NULL,
                    photo_required BOOLEAN DEFAULT FALSE NOT NULL
                )
            ''')

            # Таблица фотографий
            await connection.execute('''
                CREATE TABLE IF NOT EXISTS photos (
                    id BIGSERIAL PRIMARY KEY,
                    seeker_id BIGINT REFERENCES seekers(telegram_id),
                    photo text,
                    confirmed BOOLEAN DEFAULT FALSE NOT NULL
                )
            ''')

            # Таблица отклоненных анкет
            await connection.execute('''
                CREATE TABLE IF NOT EXISTS rejections (
                    seeker_id BIGINT REFERENCES seekers(telegram_id),
                    rejected_seeker_id BIGINT REFERENCES seekers(telegram_id),
                    created_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(seeker_id, rejected_seeker_id)
                )
            ''')

    async def add_user(self, telegram_id, username, first_name):
        async with self.pool.acquire() as connection:
            return await connection.fetchrow('''
                INSERT INTO seekers (telegram_id, username, first_name)
                VALUES ($1, $2, $3)
                ON CONFLICT (telegram_id) DO NOTHING
                RETURNING *
            ''', telegram_id, username, first_name)

    async def update_user_language(self, telegram_id, language):
        async with self.pool.acquire() as connection:
            await connection.execute('''
                UPDATE seekers SET language = $1 WHERE telegram_id = $2
            ''', language, telegram_id)

    async def update_user_gender(self, telegram_id, gender):
        async with self.pool.acquire() as connection:
            await connection.execute('''
                UPDATE seekers SET gender = $1 WHERE telegram_id = $2
            ''', gender, telegram_id)

    async def update_user_age(self, telegram_id, age):
        async with self.pool.acquire() as connection:
            await connection.execute('''
                UPDATE seekers SET age = $1 WHERE telegram_id = $2
            ''', age, telegram_id)

    async def update_user_interested_age(self, telegram_id, interested_age):
        async with self.pool.acquire() as connection:
            await connection.execute('''
                UPDATE seekers SET interested_age = $1 WHERE telegram_id = $2
            ''', interested_age, telegram_id)

    async def get_user(self, telegram_id):
        async with self.pool.acquire() as connection:
            return await connection.fetchrow('''
                SELECT s.*, p.city, p.is_city_only, p.is_seekable
                FROM seekers s
                LEFT JOIN preferences p ON s.telegram_id = p.seeker_id
                WHERE s.telegram_id = $1
            ''', telegram_id)

    async def add_rejection(self, seeker_id, rejected_seeker_id):
        async with self.pool.acquire() as connection:
            await connection.execute('''
                INSERT INTO rejections (seeker_id, rejected_seeker_id)
                VALUES ($1, $2)
                ON CONFLICT (seeker_id, rejected_seeker_id) DO NOTHING
            ''', seeker_id, rejected_seeker_id)

    async def get_seeker_id(self, telegram_id):
        async with self.pool.acquire() as connection:
            return await connection.fetchval('''
                SELECT telegram_id FROM seekers WHERE telegram_id = $1
            ''', telegram_id)

    async def get_random_user(self, current_user_id):
        async with self.pool.acquire() as connection:
            # Получаем данные текущего пользователя
            current_user = await connection.fetchrow('''
                SELECT 
                    s.*, p.is_seekable, p.city, p.is_city_only, p.photo_required
                FROM 
                    seekers s 
                    LEFT JOIN preferences p ON s.telegram_id = p.seeker_id 
                WHERE s.telegram_id = $1
            ''', current_user_id)
            if not current_user:
                return None

            current_user = dict(current_user)
            current_seeker_id = current_user['telegram_id']

            print(f"current_user={bool(current_user)}")

            # Получаем темы текущего пользователя
            current_topics = await self.get_user_topics(current_seeker_id)
            # Строим сложный запрос для поиска подходящего собеседника
            query = '''
                SELECT 
                    s.*, p.city, p.is_city_only 
                FROM 
                    seekers s
                    LEFT JOIN preferences p ON s.telegram_id = p.seeker_id
                    LEFT JOIN topics t ON s.telegram_id = t.seeker_id
                    LEFT JOIN photos ph ON s.telegram_id = ph.seeker_id
                WHERE s.telegram_id != $1
                AND s.is_active = TRUE
                AND s.companion_telegram_id IS NULL
                AND p.is_seekable = TRUE
                AND s.telegram_id NOT IN (
                    SELECT rejected_seeker_id FROM rejections WHERE seeker_id = $1
                )
            '''
            params = [current_user_id,]
            param_count = 2

            # 2. По противоположности пола
            if current_user['gender']:
                opposite_gender = 2 if current_user['gender'] == 1 else 1
                query += f" AND s.gender = ${param_count}"
                params.append(opposite_gender)
                param_count += 1

            # 4. По интересующему возрасту
            if current_user['interested_age']:
                query += f" AND s.age = ${param_count}"
                params.append(current_user['interested_age'])
                param_count += 1

            # 5. По городу (если включена настройка)
            if current_user.get('is_city_only') and current_user.get('city'):
                query += f" AND p.city = ${param_count}"
                params.append(current_user['city'])
                param_count += 1

            # 7. Только с фото (если включена настройка)
            if current_user.get('photo_required'):
                query += f" AND ph.photo IS NOT NULL AND ph.confirmed = TRUE"

            # 1. По полному соответствию тем (если есть выбранные темы)
            if current_topics:
                topic_conditions = []
                for topic_num in current_topics:
                    topic_conditions.append(f"t.word_{topic_num} = TRUE")

                if topic_conditions:
                    query += f" AND ({' AND '.join(topic_conditions)})"

            query += " ORDER BY RANDOM() LIMIT 1"

            result = await connection.fetchrow(query, *params)
            if result:
                user = dict(result)
                user['topics'] = await self.get_user_topics(user['telegram_id'])
                user['photo'] = await self.get_user_photo(user['telegram_id'])
                return user

            return None

    async def get_user_topics(self, seeker_id):
        async with self.pool.acquire() as connection:
            topics = await connection.fetchrow('''
                SELECT * FROM topics WHERE seeker_id = $1
            ''', seeker_id)

            if topics:
                selected_topics = []
                topics_dict = dict(topics)
                for i in range(1, 21):  # 20 тем
                    if topics_dict.get(f'word_{i}'):
                        selected_topics.append(i)
                return selected_topics
            return []

    async def update_topic(self, seeker_id, word_number, value):
        async with self.pool.acquire() as connection:
            # Проверяем, существует ли запись
            exists = await connection.fetchval('''
                SELECT 1 FROM topics WHERE seeker_id = $1
            ''', seeker_id)

            if not exists:
                # Создаем новую запись со всеми false
                columns = ['seeker_id'] + [f'word_{i}' for i in range(1, 21)]
                values = [seeker_id] + [False] * 20
                placeholders = ', '.join([f'${i + 1}' for i in range(len(values))])

                await connection.execute(f'''
                    INSERT INTO topics ({', '.join(columns)}) VALUES ({placeholders})
                ''', *values)

            # Обновляем конкретное поле
            await connection.execute(f'''
                UPDATE topics SET word_{word_number} = $1 WHERE seeker_id = $2
            ''', value, seeker_id)

    async def add_photo(self, seeker_id, photo):
        async with self.pool.acquire() as connection:
            # Удаляем старые фото пользователя
            await connection.execute('''
                DELETE FROM photos WHERE seeker_id = $1
            ''', seeker_id)

            # Добавляем новое фото
            await connection.execute('''
                INSERT INTO photos (seeker_id, photo, confirmed)
                VALUES ($1, $2, TRUE)
            ''', seeker_id, photo)

    async def get_user_photo(self, seeker_id):
        async with self.pool.acquire() as connection:
            return await connection.fetchval('''
                SELECT photo FROM photos WHERE seeker_id = $1 LIMIT 1
            ''', seeker_id) # AND confirmed = TRUE

    async def update_preferences(self, seeker_id, city=None, is_city_only=None, is_seekable=None, photo_required=None):
        async with self.pool.acquire() as connection:
            # Проверяем, существует ли запись
            # exists = await connection.fetchval('''
            #     SELECT 1 FROM preferences WHERE seeker_id = $1
            # ''', seeker_id)
            #
            # if not exists:
            #     # Создаем новую запись
            #     await connection.execute('''
            #         INSERT INTO preferences (seeker_id, city, is_city_only, is_seekable, photo_required)
            #         VALUES ($1, $2, $3, $4, $5)
            #     ''', seeker_id, city, is_city_only, is_seekable, photo_required)
            # else:
            # Обновляем существующую запись
            update_fields = []
            params = []
            param_count = 1

            if city is not None:
                update_fields.append(f"city = ${param_count}")
                params.append(city)
                param_count += 1

            if is_city_only is not None:
                update_fields.append(f"is_city_only = ${param_count}")
                params.append(is_city_only)
                param_count += 1

            if is_seekable is not None:
                update_fields.append(f"is_seekable = ${param_count}")
                params.append(is_seekable)
                param_count += 1

            if photo_required is not None:
                update_fields.append(f"photo_required = ${param_count}")
                params.append(photo_required)
                param_count += 1

            if update_fields:
                # params.append(seeker_id)
                await connection.execute(f'''
                    UPDATE preferences SET {', '.join(update_fields)} 
                    WHERE seeker_id = {seeker_id}
                ''', *params)

    async def remove_companion(self, telegram_id):
        async with self.pool.acquire() as connection:
            await connection.execute('''
                UPDATE seekers SET companion_telegram_id = NULL WHERE telegram_id = $1
            ''', telegram_id)

db = Database()
