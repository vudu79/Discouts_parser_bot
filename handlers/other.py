from aiogram import types, Dispatcher
import json, string
from aiogram.types import ContentType, ParseMode
from aiogram.utils.emoji import emojize
from aiogram.utils.markdown import text, italic, code
from create_bot import dp, bot
from emoji import emojize


@dp.message_handler()
async def mat_filter_handler(message: types.Message):
    if {i.lower().translate(str.maketrans('', '', string.punctuation)) for i in message.text.split(' ')} \
            .intersection(set(json.load(open('json_mat.json')))) != set():
        await message.reply("Маты запрещены в чате")
        await message.delete()
    await message.reply(message.text)


@dp.message_handler(content_types=ContentType.ANY)
async def unknown_message(msg: types.Message):
    message_text = text(emojize('Я не знаю, что с этим делать :astonished:'),
                        italic('\nЯ просто напомню,'), 'что есть',
                        code('команда'), '/help', 'и кнопки внизу))')
    await msg.reply(message_text, parse_mode=ParseMode.MARKDOWN)




def register_handlers_other(dp: Dispatcher):
    dp.register_message_handler(mat_filter_handler)
    dp.register_message_handler(unknown_message, content_types=ContentType.ANY)

