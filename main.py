import asyncio

from bot import telegram_bot, dp, set_commands
import handlers


async def main():
    handlers.register_base_handlers(dp)
    handlers.register_weather_handlers(dp)
    handlers.register_duckture_handlers(dp)
    handlers.register_exchange_handlers(dp)
    handlers.register_poll_handlers(dp)

    await set_commands(telegram_bot)

    await dp.start_polling()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
