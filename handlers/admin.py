import asyncio

from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import RetryAfter

from create_bot import dp, bot
from client.http_client import *
from database import DBase
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from keyboards import inline_keyboard_lang, inline_keyboard_category


gifs = dict()
dbase = DBase()
storage = MemoryStorage()
leng_type = ""
leng_phrase = ""

categories_callback = CallbackData("CategorY__", "page", "category_name")

category_list = get_categories_tenor_req()


def get_pagination_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    has_next_page = len(category_list) > page + 1

    if page != 0:
        keyboard.add(
            InlineKeyboardButton(
                text="👈",
                callback_data=categories_callback.new(page=page - 1,
                                                      category_name=f'{category_list[page - 1]["searchterm"]}')
            )
        )

    keyboard.add(
        InlineKeyboardButton(
            text=f'Показать все из "{str.capitalize(category_list[page]["searchterm"])}"',
            callback_data=f'category__{category_list[page]["searchterm"]}"'
        )
    )

    if has_next_page:
        keyboard.add(
            InlineKeyboardButton(
                text="👉",
                callback_data=categories_callback.new(page=page + 1,
                                                      category_name=f'{category_list[page + 1]["searchterm"]}')
            )
        )

    return keyboard


@dp.message_handler(Text(equals="Популярные категории", ignore_case=True), state=None)
async def category_index_handler(message: types.Message):
    await bot.send_message(message.from_user.id,
                           "Показать все категории или по одной, но с превью?",
                           reply_markup=InlineKeyboardMarkup(row_width=2).row(
                               InlineKeyboardButton(text="Все сразу", callback_data="collect_cat__yes"),
                               InlineKeyboardButton(text="По одной", callback_data="collect_cat__no")))


@dp.callback_query_handler(Text(startswith="collect_cat__"), state=None)
async def show_type_category_callback_hendler(collback: types.CallbackQuery):
    callback_user_id = collback.from_user.id
    res = collback.data.split("__")[1]
    if res == "yes":
        for teg in category_list:
            inline_keyboard_category.insert(
                InlineKeyboardButton(text=f'{teg["searchterm"]}', callback_data=f'category__{teg["searchterm"]}'))

        await bot.send_message(callback_user_id,
                               'В каждой категории по несколько вариантов популярных гифок. Нажмите на любую для просмотра.',
                               reply_markup=inline_keyboard_category)
        await collback.answer()
    else:
        if res == "no":
            category_one = category_list[0]
            keyboard = get_pagination_keyboard()  # Page: 0

            await bot.send_animation(
                chat_id=callback_user_id,
                animation=category_one["image"],
                reply_markup=keyboard
            )


@dp.callback_query_handler(categories_callback.filter())
async def paginate_category_callback_handler(query: CallbackQuery, callback_data: dict):
    page = int(callback_data.get("page"))
    category_one = category_list[page]
    keyboard = get_pagination_keyboard(page=page)

    await bot.send_animation(
        chat_id=query.from_user.id,
        animation=category_one["image"],
        reply_markup=keyboard
    )


@dp.callback_query_handler(Text(startswith="category__"), state=None)
async def show_list_category_colaback_hendler(collback: types.CallbackQuery):
    callback_user_id = collback.from_user.id
    res = collback.data.split("__")[1]
    await collback.answer(f'Выбрана категория {res}')
    gifs_from_tenor_list = get_category_list_tenor_req(res)
    for gif in gifs_from_tenor_list:
        try:
            await bot.send_animation(callback_user_id, gif, reply_markup=InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(text="Сохранить в базу", callback_data="save__")))
        except RetryAfter as e:
            await asyncio.sleep(e.timeout)
    await collback.answer()



class FSMSearch(StatesGroup):
    subj = State()
    limit = State()


# Машина состояний для searchAPI________________________________________________________________________________________
# Запускаем машину состояния FSMAdmin хэндлером

@dp.message_handler(Text(equals="Найти по слову", ignore_case=True))
async def choose_lang_handler(message: types.Message):
    await message.answer("Выберите язык на котором будете писать запрос", reply_markup=inline_keyboard_lang)


@dp.callback_query_handler(Text(startswith="leng__"), state=None)
async def colaback_hendler_lang_start_search(collback: types.CallbackQuery):
    res = collback.data.split("__")[1]
    print(f'Выбран язык - {res}')
    global leng_type
    global leng_phrase
    if res == "rus_":
        leng_type = "ru"
        leng_phrase = "русском языке"
        print(leng_type)
    elif res == "engl_":
        leng_type = "en"
        leng_phrase = "английском языке"
        print(leng_type)
    await FSMSearch.subj.set()
    await collback.answer()
    await bot.send_message(collback.from_user.id, f'Напишите ключевое слово поиска на {leng_phrase}')


# Выход из состояния
@dp.message_handler(state="*", commands='отмена')
@dp.message_handler(Text(equals=['отмена', 'Отменить поиск'], ignore_case=True), state="*")
async def cansel_state_search(maseege: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await maseege.reply("Ok, отменяем)")
    await maseege.answer("Что будем искать?)")


# Устанавливаем машину состояния в состояние приема фото и запрашиваем у пользователя файл
@dp.message_handler(state=FSMSearch.subj)
async def load_subj_sm_search(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['subj'] = message.text
    await FSMSearch.next()
    await message.answer("Сколько найти? Максимальное количество - 1000 gifs. Пишите число, это например 1, 2, 22))")


# Устанавливаем машину состояния в состояние приема названия и запрашиваем у пользователя текст
@dp.message_handler(state=FSMSearch.limit)
async def load_limit_sm_search(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['limit'] = message.text
    await FSMSearch.next()
    await message.answer("Okey, я запомнил. Произвожу поиск ...")
    async with state.proxy() as data:
        list_gifs = search_req(data["subj"], data["limit"], leng_type)
        for gif in list_gifs:
            await bot.send_animation(message.from_user.id, gif, reply_markup=InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(text="Сохранить в базу", callback_data="save__")))
        await message.answer("Сделано, жду команд!")
    await state.finish()


# Машина состояний для randomAPI________________________________________________________________________________________


class FSMRandom(StatesGroup):
    subj = State()


@dp.message_handler(Text(equals="Случайная по слову", ignore_case=True), state=None)
async def cm_start_random(message: types.Message):
    await FSMRandom.subj.set()
    await message.answer("Напишите ключевое слово для поиска на английском языке")


@dp.message_handler(state="*", commands='отмена')
@dp.message_handler(Text(equals=['отмена', 'Отменить поиск'], ignore_case=True), state="*")
async def cansel_state_random(maseege: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await maseege.answer("Ok, отменяем)")
    await maseege.answer("Что будем искать?)")


@dp.message_handler(state=FSMRandom.subj)
async def load_subj_sm_random(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['subj'] = message.text
    await FSMSearch.next()
    await message.answer("Okey, я запомнил. Произвожу поиск ...")
    async with state.proxy() as data:
        await bot.send_animation(message.from_user.id, random_req(data['subj']),
                                 reply_markup=InlineKeyboardMarkup(row_width=1).add(
                                     InlineKeyboardButton(text="Сохранить в базу", callback_data="save__")))
    await state.finish()
    await message.answer("Сделано, жду команд!")


# Машина состояний для translateAPI________________________________________________

class FSMTranslate(StatesGroup):
    phrase = State()


@dp.message_handler(Text(equals="Гифка под фразу", ignore_case=True), state=None)
async def cm_start_translate(message: types.Message):
    await FSMTranslate.phrase.set()
    await message.answer("Напишите любую фразу на английском языке")


@dp.message_handler(state="*", commands='отмена')
@dp.message_handler(Text(equals=['отмена', 'Отменить поиск'], ignore_case=True), state="*")
async def cansel_state_translate(maseege: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await maseege.reply("Ok, отменяем)")
    await maseege.answer("Что будем искать?)")


@dp.message_handler(state=FSMTranslate.phrase)
async def load_subj_sm_translate(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phrase'] = message.text
    await FSMTranslate.next()
    await message.answer("Okey, я запомнил. Произвожу поиск ...")
    async with state.proxy() as data:
        await bot.send_animation(message.from_user.id, translate_req(data['phrase']),
                                 reply_markup=InlineKeyboardMarkup(row_width=1).add(
                                     InlineKeyboardButton(text="Сохранить в базу", callback_data="save__")))
    await state.finish()
    await message.answer("Сделано, жду команд!")


# trendAPI_________________________________________________________________

@dp.message_handler(Text(equals="Популярные гифки"))
async def trand_api(message: types.Message):
    await message.answer("Минутку, произвожу поиск...")
    global gifs
    gifs.clear()
    gifs = trend_req()
    for item in gifs.items():
        await bot.send_animation(message.from_user.id, item[1],
                                 reply_markup=InlineKeyboardMarkup(row_width=1).add(
                                     InlineKeyboardButton(text="Сохранить в базу", callback_data="save__")))
    await message.answer("Сделано, жду команд!")



@dp.callback_query_handler(Text(startswith="save_"))
async def colaback_hendler(collback: types.CallbackQuery):
    res = collback.data.split("_")[1]
    # dbase.save_gif(gifs[res])
    # print(gifs[res])
    await collback.answer("В разработке...")


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(category_index_handler, Text(equals="Популярные категории", ignore_case=True),
                                state=None)
    dp.register_callback_query_handler(show_type_category_callback_hendler, Text(startswith="collect_cat__"),
                                       state=None)
    dp.register_callback_query_handler(paginate_category_callback_handler, categories_callback.filter())
    dp.register_callback_query_handler(show_list_category_colaback_hendler, Text(startswith="category__"), state=None)

    dp.register_message_handler(choose_lang_handler, Text(equals="Найти по слову", ignore_case=True))
    dp.register_callback_query_handler(colaback_hendler_lang_start_search, Text(startswith="leng__"), state=None)
    dp.register_message_handler(cansel_state_search, state="*", commands='отмена')
    dp.register_message_handler(load_subj_sm_search, state=FSMSearch.subj)
    dp.register_message_handler(load_limit_sm_search, state=FSMSearch.limit)

    dp.register_message_handler(cm_start_random, Text(equals="Случайная по слову", ignore_case=True), state=None)
    dp.register_message_handler(cansel_state_random, state="*", commands='отмена')
    dp.register_message_handler(load_subj_sm_random, state=FSMRandom.subj)

    dp.register_message_handler(cm_start_translate, Text(equals="Гифка под фразу", ignore_case=True), state=None)
    dp.register_message_handler(cansel_state_translate, state="*", commands='отмена')
    dp.register_message_handler(load_subj_sm_translate, state=FSMTranslate.phrase)

    dp.register_message_handler(trand_api, Text(equals="Популярные гифки"))
