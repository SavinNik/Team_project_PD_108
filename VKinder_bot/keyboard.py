from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def create_start_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('СТАРТ', color=VkKeyboardColor.PRIMARY)
    return keyboard


def create_search_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Начать поиск', color=VkKeyboardColor.PRIMARY)
    return keyboard


def create_full_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Предыдущий', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('Следующий', color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button('Не интересует', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_button('В избранное', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button('Показать избранное', color=VkKeyboardColor.POSITIVE)
    return keyboard