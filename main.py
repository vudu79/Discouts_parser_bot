import logging, os
import multiprocessing
from handlers import client, admin, other
from aiogram.utils.executor import start_webhook
from create_bot import TOKEN, bot, dp
from echo_server import run, HttpGetHandler, HTTPServer

HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'


# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv('PORT', default=8000)


async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(dispatcher):
    await bot.delete_webhook()


client.register_handlers_client(dp)
admin.register_handlers_admin(dp)
other.register_handlers_other(dp)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    #
    # start_webhook(
    #     dispatcher=dp,
    #     webhook_path=WEBHOOK_PATH,
    #     skip_updates=True,
    #     on_startup=on_startup,
    #     on_shutdown=on_shutdown,
    #     host=WEBAPP_HOST,
    #     port=WEBAPP_PORT,
    # )

    kwa1 = {
        "dispatcher": dp,
        "webhook_path": WEBHOOK_PATH,
        "skip_updates": True,
        "on_startup": on_startup,
        "on_shutdown": on_shutdown,
        "host": WEBAPP_HOST,
        "port": WEBAPP_PORT,
    }

    kwa2 = {
        "server_class" : HTTPServer,
        "handler_class": HttpGetHandler,
    }

    p1 = multiprocessing.Process(target=start_webhook, kwargs=kwa1)
    p2 = multiprocessing.Process(target=run, kwargs=kwa2)
    p1.start()
    p2.start()
