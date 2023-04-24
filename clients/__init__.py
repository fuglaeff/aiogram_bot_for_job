from clients.base import ClientException
from clients.weather import WeatherClient
from clients.animals import DuckClient
from clients.exchange import ExchangeClient


__all__ = [
    'WeatherClient',
    'DuckClient',
    'ExchangeClient',
    'ClientException',
]
