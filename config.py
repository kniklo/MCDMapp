import os

class Config:
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASS = os.getenv('DB_PASS', '12345678')
    DB_HOST = os.getenv('DB_HOST', 'db')  # docker-compose сервіс
    DB_PORT = os.getenv('DB_PORT', '3306')  # Порт контейнера MySQL, 3306 за замовчуванням
    DB_NAME = os.getenv('DB_NAME', 'mcdmapp')

    SECRET_KEY = os.getenv('SECRET_KEY', 'you-should-change-this-to-a-secure-random-key')

    SQLALCHEMY_DATABASE_URI = (
        f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
