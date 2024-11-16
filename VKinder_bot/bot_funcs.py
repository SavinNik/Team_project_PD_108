from pprint import pprint
import requests
from datetime import datetime

from vk_api import vk_api, exceptions

from VKinder_db.database import get_not_interested_users_id

# Получение параметров поиска на основании данных профиля пользователя ботом
def get_params_from_vk_user_info(service_token: str, user_id: int) -> dict:
    params = {
        'access_token': service_token,
        'v': '5.199',
        'user_ids': user_id,
        'fields': 'city, bdate, sex'
    }
    try:
        response = requests.get('https://api.vk.com/method/users.get', params=params)
        response.raise_for_status()
        profile_info = response.json()

        if 'response' in profile_info and len(profile_info['response']) > 0:
            user_data = profile_info['response'][0]
            birthday = user_data.get('bdate', '')
            if birthday:
                birthday_year = birthday.split(".")[-1]
                now_year = datetime.now().strftime('%Y')
                age = int(now_year) - int(birthday_year)
            else:
                age = None

            sex = user_data.get('sex', None)
            city = user_data.get('city', {}).get('id', None)

            result = {
                'age': age,
                'sex': sex,
                'city': city
            }
            return result
        else:
            print("Invalid response")
            return {}
    except requests.exceptions.RequestException as error:
        print(f'Error: {error}')
    except Exception as error:
        print(f'Unexpected error: {error}')

# Получение пола, противоположного полу пользователя ботом
def get_opposite_sex(sex_id: int) -> int:
    if sex_id == 1:
        return 2
    elif sex_id == 2:
        return 1
    else:
        return 0

# Получение топ-3 фото у найденных пользователей
def get_top_three_photo_from_profile(user_id: int, service_token: str) -> list:
    params = {
        'access_token': service_token,
        'v': 5.199,
        'owner_id': user_id,
        'album_id': 'profile',
        'extended': 1,
    }
    try:
        response = requests.get('https://api.vk.com/method/photos.get', params=params)
        result = response.json()['response']['items']
        photo_list = sorted(result, key=lambda x: x["likes"]["count"], reverse=True)[0:3]
        top_three_photo_id = [photo['id'] for photo in photo_list]
        return top_three_photo_id

    except requests.exceptions.RequestException as error:
        print(f'Error: {error}')
    except Exception as error:
        print(f'Unexpected error: {error}')


# Функция поиска пользователей по нужным параметрам
def search_vk_users(sex: int, age: int, city: int, service_token: str, user_id_db: int):
    vk_session = vk_api.VkApi(token=service_token)
    vk = vk_session.get_api()

    not_interested_ids = get_not_interested_users_id(user_id_db)

    try:
        users = vk.users.search(
            sex=sex,
            age_from=age,
            age_to=age,
            city=city,
            count=10,
            has_photo=1,
            fields='id, first_name, second_name, is_closed'
        )

        results = []
        for user in users['items']:
            if user['is_closed']:
                continue
            user_id = user['id']

            if user_id in not_interested_ids:
                continue

            profile_link = f"https://vk.com/id{user_id}"
            photo_id_list = get_top_three_photo_from_profile(user_id=user_id, service_token=service_token)
            result_dict = {'name': f"{user['first_name']} {user['last_name']}",
                           'user_match_id': user_id, 'profile_link': profile_link}

            if photo_id_list:
                attachment = ",".join([f'photo{user_id}_{photo_id}' for photo_id in photo_id_list])
                result_dict['attachment'] = attachment
                results.append(result_dict)

        return results

    except exceptions.ApiError as error:
        print(f"API Error: {error}")
        raise
    except Exception as error:
        print(f"Error: {error}")
        raise
