import os
from pprint import pprint
from random import randint
from dotenv import load_dotenv
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from VKinder_bot.bot_funcs import get_params_from_vk_user_info, search_vk_users, get_opposite_sex
from VKinder_bot.keyboard import create_start_keyboard, create_search_keyboard, create_full_keyboard
from VKinder_db.database import check_user, add_user, add_to_favorites, get_user_id_db, get_favorites, \
    check_favourites_user, check_user_in_not_interested, add_to_not_interested

load_dotenv()


def main():
    token = os.getenv('BOT_KEY')
    service_token = os.getenv('ACCESS_TOKEN')

    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()

    start_keyboard = create_start_keyboard()
    search_keyboard = create_search_keyboard()
    full_keyboard = create_full_keyboard()

    longpoll = VkLongPoll(vk_session)

    current_index = 0
    search_results = []

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            text = event.text.lower()
            user_id = event.user_id
            # Приветствие бота
            if text == 'привет':
                greeting_message = 'Я бот для знакомств. Нажми кнопку "Старт" чтобы начать.'
                vk.messages.send(
                    user_id=user_id,
                    message=greeting_message,
                    keyboard=start_keyboard.get_keyboard(),
                    random_id=randint(1, 2 ** 31)
                )

            if text == 'старт':
                user = check_user(user_id)
                if not user:
                    add_user(user_id)
                    message = 'Привет! Давай подберем тебе пару? Нажми кнопку "Начать поиск" и ПОГНАЛИ!!!'
                    vk.messages.send(
                        user_id=user_id,
                        message=message,
                        keyboard=search_keyboard.get_keyboard(),
                        random_id=randint(1, 2 ** 31)
                    )
                    continue
                else:
                    vk.messages.send(
                        user_id=user_id,
                        message='Привет! Давай подберем тебе пару? Нажми кнопку "Начать поиск" и ПОГНАЛИ!!!',
                        keyboard=search_keyboard.get_keyboard(),
                        random_id=randint(1, 2 ** 31)
                    )
            # Запуск поиска пользователей
            if text == 'начать поиск':
                params_for_search_matches = get_params_from_vk_user_info(service_token=service_token, user_id=user_id)
                sex = get_opposite_sex(params_for_search_matches['sex'])
                age = params_for_search_matches['age']
                city = params_for_search_matches['city']
                user_id_db = get_user_id_db(user_id)
                search_results = search_vk_users(sex=sex, age=age, city=city, service_token=service_token, user_id_db=user_id_db)
                current_index = 0
                if search_results:
                    pprint(search_results)
                    user = search_results[current_index]
                    message = f"{user.get('name')}\n{user.get('profile_link')}"

                    if user.get('attachment'):
                        vk.messages.send(
                            user_id=user_id,
                            message=message,
                            attachment=user.get('attachment'),
                            keyboard=full_keyboard.get_keyboard(),
                            random_id=randint(1, 2 ** 31)
                        )
                    else:
                        vk.messages.send(
                            user_id=user_id,
                            message='Нет результатов поиска.',
                            keyboard=full_keyboard.get_keyboard(),
                            random_id=randint(1, 2 ** 31)
                        )
            # Перемещение по найденным пользователям
            elif text == 'следующий':
                if search_results and current_index < len(search_results) - 1:
                    current_index += 1
                    user = search_results[current_index]
                    message = f"{user.get('name')}\n{user.get('profile_link')}"
                    vk.messages.send(
                        user_id=user_id,
                        message=message,
                        attachment=user.get('attachment'),
                        keyboard=full_keyboard.get_keyboard(),
                        random_id=randint(1, 2 ** 31)
                    )
                else:
                    vk.messages.send(
                        user_id=user_id,
                        message='Нет следующих результатов.',
                        keyboard=full_keyboard.get_keyboard(),
                        random_id=randint(1, 2 ** 31)
                    )

            elif text == 'предыдущий':
                if search_results and current_index > 0:
                    current_index -= 1
                    user = search_results[current_index]
                    message = f"{user.get('name')}\n{user.get('profile_link')}"
                    vk.messages.send(
                        user_id=user_id,
                        message=message,
                        attachment=user.get('attachment'),
                        keyboard=full_keyboard.get_keyboard(),
                        random_id=randint(1, 2 ** 31)
                    )
                else:
                    vk.messages.send(
                        user_id=user_id,
                        message='Нет предыдущих результатов.',
                        keyboard=full_keyboard.get_keyboard(),
                        random_id=randint(1, 2 ** 31)
                    )

            # Добавление неинтересующего пользователя в соответствующую таблицу БД, с целью исключения повторного поиска
            elif text == 'не интересует':
                result = search_results[current_index]
                not_interested_vk_id = result["user_match_id"]
                not_interested_user_id = check_user_in_not_interested(not_interested_vk_id)
                if not not_interested_user_id:
                    add_to_not_interested(user_id=get_user_id_db(user_id), not_interested_vk_id=not_interested_vk_id)
                    vk.messages.send(
                        user_id=user_id,
                        message='Добавлено в не интересующие.',
                        keyboard=full_keyboard.get_keyboard(),
                        random_id=randint(1, 2 ** 31)
                    )
                else:
                    vk.messages.send(
                        user_id=user_id,
                        message='Уже добавлен в не интересующие.',
                        keyboard=full_keyboard.get_keyboard(),
                        random_id=randint(1, 2 ** 31)
                    )
            # Добавление интересующего пользователя в соответствующую таблицу БД (избранные)
            elif text == 'в избранное':
                result = search_results[current_index]
                favorite_vk_id = result["user_match_id"]
                favorite_user_id = check_favourites_user(favorite_vk_id)
                if not favorite_user_id:
                    add_to_favorites(user_id=get_user_id_db(user_id), favorite_vk_id=favorite_vk_id)
                    vk.messages.send(
                        user_id=user_id,
                        message='Добавлено в избранное.',
                        keyboard=full_keyboard.get_keyboard(),
                        random_id=randint(1, 2 ** 31)
                    )
                else:
                    vk.messages.send(
                        user_id=user_id,
                        message='Уже добавлен в избранное.',
                        keyboard=full_keyboard.get_keyboard(),
                        random_id=randint(1, 2 ** 31)
                    )

            # Вывод в чат всех избранных пользователей
            elif text == 'показать избранное':
                result = [user for user in search_results
                          if user["user_match_id"] in get_favorites(get_user_id_db(user_id))]
                favorite_message = ""
                for user in result:
                    favorite_message += f"{user.get('name')}\n{user.get('profile_link')}\n"
                if favorite_message:
                    vk.messages.send(
                        user_id=user_id,
                        message=favorite_message,
                        keyboard=full_keyboard.get_keyboard(),
                        random_id=randint(1, 2 ** 31)
                    )
                else:
                    vk.messages.send(
                        user_id=user_id,
                        message='Нет избранных пользователей.',
                        keyboard=full_keyboard.get_keyboard(),
                        random_id=randint(1, 2 ** 31)
                    )

            # Выход из бота
            elif text == 'выход':
                vk.messages.send(
                    user_id=user_id,
                    message='До новых встреч!',
                    keyboard=search_keyboard.get_keyboard(),
                    random_id=randint(1, 2 ** 31)
                )



if __name__ == '__main__':
    main()
