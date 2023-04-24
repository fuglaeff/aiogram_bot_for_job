from handlers.animals_handler import register_duckture_handlers
from handlers.base_handlers import register_base_handlers
from handlers.exchange_handlers import register_exchange_handlers
from handlers.poll_handler import register_poll_handlers
from handlers.weather_handlers import register_weather_handlers


__all__ = [
    'register_duckture_handlers',
    'register_weather_handlers',
    'register_exchange_handlers',
    'register_poll_handlers',
    'register_base_handlers',
]
