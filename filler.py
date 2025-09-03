import os
import random
from itertools import count

from faker import Faker
import psycopg2
from psycopg2 import sql

# Настройки подключения к PostgreSQL
DB_CONFIG = {
    'host': 'localhost',
    'database': 'two_sensations',
    'user': 'sensbot',
    'password': 'kavana367',
    'port': '5432'
}

# Путь к папке с фотографиями
PHOTOS_FOLDER = 'fotos'


class DataGenerator:
    def __init__(self):
        self.fake = Faker()
        self.conn = None
        self.cursor = None

    def connect_to_db(self):
        """Подключение к базе данных"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor()
            print("Успешное подключение к базе данных")
        except Exception as e:
            print(f"Ошибка подключения: {e}")

    def disconnect_from_db(self):
        """Отключение от базы данных"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Отключение от базы данных")


    def run(self, count_per_table=100):
        """Основной метод для запуска генерации данных"""
        try:
            self.connect_to_db()
            print("Начало генерации данных...")
            for id in range(8 * 10 ** 9, 8 * 10 ** 9 + 10_000):

                self.generate_seeker_data(id)
                self.generate_preferences_data(id)
                self.generate_photo_data(id)
                self.generate_topics_data(id)

            print("Генерация данных завершена!")

        finally:
            self.disconnect_from_db()

    def get_random_photo(self):
        """Получение случайной фотографии из папки"""
        try:
            if not os.path.exists(PHOTOS_FOLDER):
                print(f"Папка {PHOTOS_FOLDER} не существует!")
                return None

            photos = [f for f in os.listdir(PHOTOS_FOLDER)
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

            if not photos:
                print("В папке нет фотографий!")
                return None

            random_photo = random.choice(photos)
            photo_path = os.path.join(PHOTOS_FOLDER, random_photo)

            # Чтение фотографии в бинарном режиме
            with open(photo_path, 'rb') as f:
                photo_data = f.read()

            return photo_data

        except Exception as e:
            print(f"Ошибка при чтении фотографии: {e}")
            return None

    def generate_seeker_data(self, id):
        try:
            insert_query = """
                INSERT INTO seekers (telegram_id, username, first_name, gender, age, interested_age)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            data = (
                id,
                self.fake.name(),
                self.fake.name(),
                random.randint(1, 2),
                random.randint(1, 5),
                random.randint(1, 5),
            )
            self.cursor.execute(insert_query, data)
            self.conn.commit()
        except Exception as e:
            print(f"Ошибка при заполнении seeker: {e}")
            self.conn.rollback()


    def generate_photo_data(self, id):
        try:
            insert_query = """
                UPDATE photos 
                SET
                    photo= %s,
                    confirmed = %s
                where 
                    seeker_id = %s
            """
            data = (
                self.get_random_photo(),
                True,
                id,
            )

            self.cursor.execute(insert_query, data)
            self.conn.commit()
        except Exception as e:
            print(f"Ошибка при заполнении photos: {e}")
            self.conn.rollback()

    def generate_preferences_data(self, id):
        try:
            insert_query = """
                UPDATE preferences
                SET
                    city = %s
                where 
                    seeker_id = %s
            """
            data = (
                self.fake.city(),
                id,
            )

            self.cursor.execute(insert_query, data)
            self.conn.commit()
        except Exception as e:
            print(f"Ошибка при заполнении preferences: {e}")
            self.conn.rollback()

    def generate_topics_data(self, id):
        try:
            insert_query = """
                UPDATE topics 
                SET
                    word_1 = %s,
                    word_2 = %s,
                    word_3 = %s,
                    word_4 = %s,
                    word_5 = %s,
                    word_6 = %s,
                    word_7 = %s,
                    word_8 = %s,
                    word_9 = %s,
                    word_10 = %s,
                    word_11 = %s,
                    word_12 = %s,
                    word_13 = %s,
                    word_14 = %s,
                    word_15 = %s,
                    word_16 = %s,
                    word_17 = %s,
                    word_18 = %s,
                    word_19 = %s,
                    word_20 = %s
                WHERE 
                    seeker_id = %s
            """
            data = [random.choice([True, False]) for _ in range(20)]
            data.append(id)

            self.cursor.execute(insert_query, tuple(data))
            self.conn.commit()
        except Exception as e:
            print(f"Ошибка при заполнении topics: {e}")
            self.conn.rollback()


if __name__ == "__main__":

    generator = DataGenerator()
    generator.run()
