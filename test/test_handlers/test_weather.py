from unittest.mock import patch, AsyncMock

import pytest

from clients import ClientException
from handlers.weather_handlers import weather_with_location_from_btn, weather_with_location_from_text
from handlers.base_handlers import BASE_ERROR_TEXT
from models import WeatherModel

TEST_API_RESP = '''{
  "coord": {
    "lon": 10.99,
    "lat": 44.34
  },
  "weather": [
    {
      "id": 501,
      "main": "Rain",
      "description": "moderate rain",
      "icon": "10d"
    }
  ],
  "base": "stations",
  "main": {
    "temp": 298.48,
    "feels_like": 298.74,
    "temp_min": 297.56,
    "temp_max": 300.05,
    "pressure": 1015,
    "humidity": 64,
    "sea_level": 1015,
    "grnd_level": 933
  },
  "visibility": 10000,
  "wind": {
    "speed": 0.62,
    "deg": 349,
    "gust": 1.18
  },
  "rain": {
    "1h": 3.16
  },
  "clouds": {
    "all": 100
  },
  "dt": 1661870592,
  "sys": {
    "type": 2,
    "id": 2075663,
    "country": "IT",
    "sunrise": 1661834187,
    "sunset": 1661882248
  },
  "timezone": 7200,
  "id": 3163858,
  "name": "Zocca",
  "cod": 200
}'''


class GetWeatherMock:
    to_return = WeatherModel.parse_raw(TEST_API_RESP)

    def __init__(
        self,
        ex: Exception | None = None
    ) -> None:
        self.ex = ex

    def __call__(self, *args, **kwargs):
        if self.ex is None:
            return self.to_return

        raise self.ex


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'lat, lon, weather_out_mock',
    [
        (1, 1, GetWeatherMock()),
        (1, 1, GetWeatherMock(ex=ClientException())),
        (1, 1, GetWeatherMock(ex=Exception())),
    ]
)
@patch('clients.WeatherClient.get_weather')
@patch('aiogram.types.Message')
@patch('aiogram.dispatcher.FSMContext')
async def test_weather_with_location_from_btn(
        state_mock, message_mock, get_weather_mock, lat, lon, weather_out_mock):

    get_weather_mock.side_effect = weather_out_mock
    message_mock.answer = AsyncMock()
    message_mock.location.latitude = lat
    message_mock.location.longitude = lon
    state_mock.finish = AsyncMock()

    await weather_with_location_from_btn(message_mock, state_mock)
    get_weather_mock.assert_called_once()
    assert get_weather_mock.call_args.kwargs == {'lat': lat, 'lon': lon}

    message_mock.answer.assert_called_once()
    state_mock.finish.assert_called_once()

    if isinstance(weather_out_mock.ex, ClientException):
        assert message_mock.answer.call_args.args[0] == str(weather_out_mock.ex)
    elif isinstance(weather_out_mock.ex, Exception):
        assert message_mock.answer.call_args.args[0] == BASE_ERROR_TEXT
    else:
        assert message_mock.answer.call_args.args[0] == weather_out_mock.to_return.make_text_message()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'msg_text, weather_out_mock',
    [
        ('Москва, RU', GetWeatherMock()),
        ('Москва,RU', GetWeatherMock()),
        ('Москва', GetWeatherMock()),
        ('Москва', GetWeatherMock(ex=ClientException())),
        ('Москва', GetWeatherMock(ex=Exception())),
    ]
)
@patch('clients.WeatherClient.get_weather')
@patch('aiogram.types.Message')
@patch('aiogram.dispatcher.FSMContext')
async def test_weather_with_location_from_text(
        state_mock, message_mock, get_weather_mock, msg_text, weather_out_mock):

    get_weather_mock.side_effect = weather_out_mock
    message_mock.answer = AsyncMock()
    message_mock.text = msg_text
    state_mock.finish = AsyncMock()

    await weather_with_location_from_text(message_mock, state_mock)
    get_weather_mock.assert_called_once()
    msg_data = msg_text.split(',')
    assert get_weather_mock.call_args.kwargs == {
        'city_name': msg_data[0].strip(),
        'country_code': msg_data[1].strip() if len(msg_data) > 1 else None,
    }

    message_mock.answer.assert_called_once()
    state_mock.finish.assert_called_once()

    if isinstance(weather_out_mock.ex, ClientException):
        assert message_mock.answer.call_args.args[0] == str(weather_out_mock.ex)
    elif isinstance(weather_out_mock.ex, Exception):
        assert message_mock.answer.call_args.args[0] == BASE_ERROR_TEXT
    else:
        assert message_mock.answer.call_args.args[0] == weather_out_mock.to_return.make_text_message()
