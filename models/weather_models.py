from pydantic import BaseModel, Field, validator


class Coordinates(BaseModel):
    lat: float
    lon: float


class WeatherDesc(BaseModel):
    description: str

    @validator('description')
    def validate_deg(cls, value: str) -> str:
        return value.title()


class WeatherMain(BaseModel):
    temp: float
    feels_like: float
    pressure: float
    humidity: float
    temp_min: float
    temp_max: float

    @validator('pressure')
    def validate_pressure(cls, value: float) -> float:
        return round(value * 0.75, 2)


class Wind(BaseModel):
    speed: float
    deg: str
    gust: float | None = None

    @validator('deg')
    def validate_deg(cls, value: str) -> str:
        return convert_wind_deg_to_human(float(value))


class RainSnow(BaseModel):
    last_hour: float = Field(default=None, alias='1h')
    last_three_hour: float = Field(default=None, alias='3h')


class WeatherModel(BaseModel):
    """
    Pydantic модель для работы с json ответами от API
    """
    weather: list[WeatherDesc]
    main: WeatherMain
    wind: Wind | None = None
    rain: RainSnow | None = None
    snow: RainSnow | None = None

    def make_text_message(self) -> str:
        # формируем сообщение
        text = self.weather[0].description
        text += (
            '\n\nТемпература:\n' +
            f'{self.main.temp_min}°C...{self.main.temp}°C...{self.main.temp_max}°C\n' +
            f'Ощущается как: {self.main.feels_like}°C'
        )
        text += f'\n\nДавление: {self.main.pressure} мм. рт. ст.'
        text += f'\nВлажность: {self.main.humidity}%'
        if self.wind is not None:
            text += (f'\n\nВетер: {self.wind.deg}{self.wind.speed} м/с' +
                     (f'\nс порывами до {self.wind.gust} м/с' if self.wind.gust is not None else '')
                     )
        if self.rain is not None:
            precipitation = self.rain.last_hour
            precipitation_text = 'за последний час'
            if self.rain.last_three_hour is not None:
                precipitation = self.rain.last_three_hour
                precipitation_text = 'за последние три часа'

            text += f'\n\nОсадков выпало {precipitation} мм. {precipitation_text}'

        if self.snow is not None:
            precipitation = self.snow.last_hour
            precipitation_text = 'за последний час'
            if self.snow.last_three_hour is not None:
                precipitation = self.snow.last_three_hour
                precipitation_text = 'за последние три часа'

            text += f'\n\nСнега выпало {precipitation} мм. {precipitation_text}'

        return text


def convert_wind_deg_to_human(value: float | int) -> str:
    """
    Функция для перевода градусов в юзерфрендли формат направления ветра
    :param value:
    :return:
    """
    if 348.75 <= value or value < 11.25:
        return '↓'
    elif 11.25 <= value < 78.75:
        return '↙'
    elif 78.75 <= value < 101.25:
        return '←'
    elif 101.25 <= value < 168.75:
        return '↖'
    elif 168.75 <= value < 191.25:
        return '↑'
    elif 191.25 <= value < 258.75:
        return '↗'
    elif 258.75 <= value < 281.25:
        return '→'
    else:
        return '↘'
