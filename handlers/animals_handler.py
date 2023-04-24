import logging

from aiogram import types, Dispatcher

from bot import telegram_bot, duck_pictures
from clients import ClientException
from handlers.base_handlers import BASE_ERROR_TEXT


async def send_duckture(message: types.Message) -> None:
    """
    Хэндлер для команды /ducktupe (duck + picture)
    :param message:
    :return:
    """
    try:
        type_, url = await duck_pictures.get_duck()

        sender = telegram_bot.send_photo
        if type_ == 'gif':
            sender = telegram_bot.send_animation

        await sender(message.chat.id, url)
    except ClientException as ex:
        logging.error(ex)
        await message.answer(str(ex))
    except Exception as ex:
        logging.error(ex)
        await message.answer(BASE_ERROR_TEXT)


def register_duckture_handlers(dp: Dispatcher) -> None:
    # Регистрируем хэндлеры
    dp.register_message_handler(send_duckture, commands='duckture')
