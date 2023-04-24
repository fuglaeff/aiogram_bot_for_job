from clients.base import BaseClient
from models import Coordinates, WeatherModel


class WeatherClient(BaseClient):
    base_url = 'https://api.openweathermap.org'
    weather_path = '/data/2.5/weather'
    city_path = '/geo/1.0/direct'
    base_params = {
        'appid': '48da60348d886a715f9de787adfd723b',
        'units': 'metric',
        'lang': 'ru',
    }

    async def _get_lat_lon_from_city_name(
        self,
        city_name: str,
        country_code: str | None = None
    ) -> tuple[float, float]:
        q = city_name
        if country_code is not None:
            q += f',{country_code}'
        params = {'q': q, 'limit': 1}

        response = await self.get(self.city_path, params)
        coord = Coordinates(**response[0])

        return coord.lat, coord.lon

    async def _get_weather_info(
            self, lat: float | None = None, lon: float | None = None) -> WeatherModel:
        resourse = await self.get(self.weather_path, params={'lat': lat, 'lon': lon})

        return WeatherModel(**resourse)

    async def get_weather(
        self,
        lat: float | None = None,
        lon: float | None = None,
        city_name: str | None = None,
        country_code: str | None = None
    ) -> WeatherModel:
        if city_name is not None:
            lat, lon = await self._get_lat_lon_from_city_name(city_name, country_code)

        return await self._get_weather_info(lat, lon)
