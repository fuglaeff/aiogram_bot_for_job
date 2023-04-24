from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand

from clients import DuckClient, WeatherClient, ExchangeClient

telegram_bot = Bot(token='6138957666:AAG3y8qvXPSHw9ILsaW979d7tljUvqzR_VU')
dp = Dispatcher(telegram_bot, storage=MemoryStorage())

duck_pictures = DuckClient()
weather = WeatherClient()
exchange = ExchangeClient()


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command='/duckture', description='Получить рандомную фоточку уточки'),
        BotCommand(command='/weather', description='Посмотреть какая сейчас погода'),
        BotCommand(command='/exchange', description='Перевести кровно-заработанные в другую валюту')
    ]
    await bot.set_my_commands(commands)
