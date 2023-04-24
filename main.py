import asyncio

from bot import telegram_bot, dp, set_commands
import handlers


async def main():
    # регистрируем хэндлеры
    handlers.register_base_handlers(dp)
    handlers.register_weather_handlers(dp)
    handlers.register_duckture_handlers(dp)
    handlers.register_exchange_handlers(dp)
    handlers.register_poll_handlers(dp)

    # устанавливаем команды
    await set_commands(telegram_bot)

    # пуллим бота (запускал локально, поэтому этот вариант более чем устраивает)
    # для вэб хуков делаем on_startup и on_shutdown, где устанавливаем вэбхуки
    await dp.start_polling()


if __name__ == '__main__':
    # запускаем бота
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
