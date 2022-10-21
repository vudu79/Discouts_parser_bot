from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

search_btn = KeyboardButton('Найти по слову')
trend_btn = KeyboardButton('Популярные гифки')
random_btn = KeyboardButton('Случайная по слову')
translate_btn = KeyboardButton('Гифка под фразу')
category_btn = KeyboardButton('Популярные категории')

cansel_btn = KeyboardButton('Отменить поиск')

# translate_btn = KeyboardButton('поделится номером телефона', request_contact=True)
# translate_btn = KeyboardButton('дать свою локацию', request_location=True)
reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
reply_keyboard.row(category_btn).row(search_btn, translate_btn).row(random_btn, trend_btn).row(cansel_btn)


inline_keyboard_lang = InlineKeyboardMarkup(row_width=2)
rus_button = InlineKeyboardButton(text="Русский", callback_data="leng__rus_")
english_button = InlineKeyboardButton(text="English", callback_data="leng__engl_")

inline_keyboard_lang.row(rus_button, english_button)

inline_keyboard_category = InlineKeyboardMarkup(row_width=3)



