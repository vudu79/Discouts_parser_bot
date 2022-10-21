from aiogram import types, Dispatcher
from keyboards import reply_keyboard
from create_bot import dp, bot
from aiogram.utils import exceptions
from aiogram.utils.callback_data import CallbackData



@dp.errors_handler(exception=exceptions.RetryAfter)
async def exception_handler(update: types.Update, exception: exceptions.RetryAfter):
    await bot.send_message(update.message.from_user.id, "Не надо мне тут спамить!!!")

    return True

@dp.message_handler(commands=['start', 'help'])
async def start_handler(message : types.Message):
    await bot.send_message(message.from_user.id, f'Привет, {message.from_user.first_name}!')
    await bot.send_message(message.from_user.id, 'Это бот для поиска гифок в интернете разными способами))', reply_markup=reply_keyboard)
    await bot.send_message(message.from_user.id, "Как будем искать? тыц 👇")


def register_handlers_client(dp : Dispatcher):
    dp.register_message_handler(start_handler, commands=['start', 'help'])
    dp.register_errors_handler(exception_handler, exception=exceptions.RetryAfter)
