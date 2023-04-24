import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand

from clients import DuckClient, WeatherClient, ExchangeClient

# подключаем логирование, можно настроить на запись в файл или БД
logging.basicConfig(level=logging.INFO)

# получаем инстансы бота и деспетчера (для бота берем API из переменной окружения)
telegram_bot = Bot(os.getenv('TG_BOT_API'))
dp = Dispatcher(telegram_bot, storage=MemoryStorage())

# Получаем инстансы клиентов, которые будут использоваться в хэндлерах
duck_pictures = DuckClient()
weather = WeatherClient()
exchange = ExchangeClient()


async def set_commands(bot: Bot) -> None:
    """
    Функция для регистрации команд в кнопке Menu
    :param bot:
    :return:
    """
    commands = [
        BotCommand(command='/duckture', description='Получить рандомную фоточку уточки'),
        BotCommand(command='/weather', description='Посмотреть какая сейчас погода'),
        BotCommand(command='/exchange', description='Перевести кровно-заработанные в другую валюту'),
        BotCommand(command='/poll', description='Создать опрос для группы'),
    ]
    await bot.set_my_commands(commands)
