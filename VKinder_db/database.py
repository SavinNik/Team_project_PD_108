from functools import wraps
from VKinder_db.models import Session, User, Favorite, NotInterest


# Создание декоратора сессии
def session_manager(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session = Session()
        try:
            result = func(session, *args, **kwargs)
            session.commit()
            return result
        except Exception as error:
            session.rollback()
            raise error
        finally:
            session.close()

    return wrapper


# Функция проверки наличия пользователя ботом в БД
@session_manager
def check_user(session, vk_id):
    user = session.query(User).filter(User.vk_id == vk_id).first()
    return user


# Функция проверки наличия найденного пользователя в таблице избранных БД
@session_manager
def check_favourites_user(session, favorite_vk_id):
    user = session.query(Favorite).filter(Favorite.favorite_vk_id == favorite_vk_id).first()
    return user


# Функция проверки наличия найденного пользователя в таблице неинтересующих БД
@session_manager
def check_user_in_not_interested(session, not_interested_vk_id):
    user = session.query(NotInterest).filter(NotInterest.not_interested_vk_id == not_interested_vk_id).first()
    return user


# Функция добавения пользователя ботом в БД
@session_manager
def add_user(session, vk_id):
    new_user = User(vk_id=vk_id)
    session.add(new_user)

# Функция добавения неинтересующего пользователя в БД
@session_manager
def add_to_not_interested(session, user_id, not_interested_vk_id):
    not_interested_user = NotInterest(user_id=user_id, not_interested_vk_id=not_interested_vk_id)
    session.add(not_interested_user)


# Функция получения из БД списка id неинтересующих пользователей
@session_manager
def get_not_interested_users_id(session, user_id):
    not_interested_users = session.query(NotInterest).filter(NotInterest.user_id == user_id)
    not_interested_id_list = [user.not_interested_vk_id for user in not_interested_users]
    return not_interested_id_list


# Функция добавения интересующего пользователя в таблицу избранные БД
@session_manager
def add_to_favorites(session, user_id, favorite_vk_id):
    new_favorite = Favorite(user_id=user_id, favorite_vk_id=favorite_vk_id)
    session.add(new_favorite)


# Функция получения id пользователя ботом из таблицы users БД
@session_manager
def get_user_id_db(session, vk_id):
    query = session.query(User).filter(User.vk_id == vk_id)
    for user in query:
        return user.id

# Функция получения из БД списка id избранных пользователей
@session_manager
def get_favorites(session, user_id):
    favorites = session.query(Favorite).filter(Favorite.user_id == user_id).all()
    id_list = [user.favorite_vk_id for user in favorites]
    return id_list
