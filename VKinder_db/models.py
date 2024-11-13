import os
from dotenv import load_dotenv
from sqlalchemy import Integer, String, Column, BigInteger, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


load_dotenv()

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vk_id = Column(BigInteger, unique=True, nullable=False)


class NotInterest(Base):
    __tablename__ = "not interested"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    not_interested_vk_id = Column(BigInteger, unique=True, nullable=False)


class Favorite(Base):
    __tablename__ = 'favorites'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    favorite_vk_id = Column(BigInteger, unique=True, nullable=False)

# Создание подключения к БД
db_login = os.getenv('DB_LOGIN')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')
db_url = f'postgresql://{db_login}:{db_password}@localhost:5432/{db_name}'

# Создание движка базы данных
engine = create_engine(db_url)

# Создание всех таблиц в базе данных
# Base.metadata.drop(engine)
Base.metadata.create_all(engine)

# Создание сессии
Session = sessionmaker(bind=engine)
