from aiogram import types, Dispatcher

from bot import telegram_bot, duck_pictures
from clients import ClientException
from handlers.base_handlers import BASE_ERROR_TEXT


async def send_duckture(message: types.Message) -> None:
    try:
        type_, url = await duck_pictures.get_duck()

        sender = telegram_bot.send_photo
        if type_ == 'gif':
            sender = telegram_bot.send_animation

        await sender(message.chat.id, url)
    except ClientException as ex:
        await message.answer(str(ex))
    except Exception as ex:
        await message.answer(BASE_ERROR_TEXT)


def register_duckture_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(send_duckture, commands='duckture')
