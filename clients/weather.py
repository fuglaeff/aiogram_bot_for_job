import os

from clients.base import BaseClient
from models import Coordinates, WeatherModel


class WeatherClient(BaseClient):
    """
    Класс, реализующий взаимодействие с API сервиса с погодой
    """

    base_url = 'https://api.openweathermap.org'
    weather_path = '/data/2.5/weather'
    city_path = '/geo/1.0/direct'
    base_params = {
        'appid': os.getenv('WEATHER_API'),
        'units': 'metric',
        'lang': 'ru',
    }

    async def _get_lat_lon_from_city_name(
        self,
        city_name: str,
        country_code: str | None = None
    ) -> tuple[float, float]:
        """
        Вспомогательный метод, для получиения координат из названия города
        """
        q = city_name
        if country_code is not None:
            q += f',{country_code}'
        params = {'q': q, 'limit': 1}

        response = await self.get(self.city_path, params)
        coord = Coordinates(**response[0])

        return coord.lat, coord.lon

    async def _get_weather_info(
            self, lat: float | None = None, lon: float | None = None) -> WeatherModel:
        """
        Вспомогательный метод, для получиения погоды по координатам
        """
        resource = await self.get(self.weather_path, params={'lat': lat, 'lon': lon})

        return WeatherModel(**resource)

    async def get_weather(
        self,
        lat: float | None = None,
        lon: float | None = None,
        city_name: str | None = None,
        country_code: str | None = None
    ) -> WeatherModel:
        """
        Основной метод, реализующий работу с веб сервисом
        """

        if city_name is not None:
            lat, lon = await self._get_lat_lon_from_city_name(city_name, country_code)

        return await self._get_weather_info(lat, lon)
