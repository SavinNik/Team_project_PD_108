from functools import wraps
from VKinder_db.models import Session, User, Favorite, NotInterest


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


@session_manager
def check_user(session, vk_id):
    user = session.query(User).filter(User.vk_id == vk_id).first()
    return user


@session_manager
def check_favourites_user(session, favorite_vk_id):
    user = session.query(Favorite).filter(Favorite.favorite_vk_id == favorite_vk_id).first()
    return user


@session_manager
def check_user_in_not_interested(session, not_interested_vk_id):
    user = session.query(NotInterest).filter(NotInterest.not_interested_vk_id == not_interested_vk_id).first()
    return user


@session_manager
def add_user(session, vk_id):
    new_user = User(vk_id=vk_id)
    session.add(new_user)


@session_manager
def add_to_not_interested(session, user_id, not_interested_vk_id):
    not_interested_user = NotInterest(user_id=user_id, not_interested_vk_id=not_interested_vk_id)
    session.add(not_interested_user)


@session_manager
def get_not_interested_users_id(session, user_id):
    not_interested_users = session.query(NotInterest).filter(NotInterest.user_id == user_id)
    not_interested_id_list = [user.not_interested_vk_id for user in not_interested_users]
    return not_interested_id_list


@session_manager
def add_to_favorites(session, user_id, favorite_vk_id):
    new_favorite = Favorite(user_id=user_id, favorite_vk_id=favorite_vk_id)
    session.add(new_favorite)


@session_manager
def get_user_id_db(session, vk_id):
    query = session.query(User).filter(User.vk_id == vk_id)
    for user in query:
        return user.id


@session_manager
def get_favorites(session, user_id):
    favorites = session.query(Favorite).filter(Favorite.user_id == user_id).all()
    id_list = [user.favorite_vk_id for user in favorites]
    return id_list
