import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from bot import weather
from clients import ClientException
from fsm import WeatherFSM
from handlers.base_handlers import BASE_CANCEL_SUFFIX, BASE_ERROR_TEXT

WEATHER_START_TEXT = (
    'Поделись локацией с помощью кнопки на клавиатуре ' +
    'или введи название населенного пункта'
)


async def weather_start(message: types.Message, state: FSMContext) -> None:
    # заводим состояние (FSM) и предлагаем следующее действие пользователю
    inline_location_btn = types.KeyboardButton(
        'Поделиться локацией', request_location=True)
    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True).add(inline_location_btn)
    await state.set_state(WeatherFSM.wait_location.state)
    await message.answer(
        WEATHER_START_TEXT + BASE_CANCEL_SUFFIX, reply_markup=kb)


async def weather_with_location_from_btn(
        message: types.Message, state: FSMContext) -> None:
    # читаем координаты из location и пытаемся получить погоду,
    # при неудачи состояние пропадает
    try:
        weather_result = await weather.get_weather(
            lat=message.location.latitude, lon=message.location.longitude)
        await message.answer(
            weather_result.make_text_message(), reply_markup=types.ReplyKeyboardRemove())
    except ClientException as ex:
        logging.error(ex)
        await message.answer(str(ex))
    except Exception as ex:
        logging.error(ex)
        await message.answer(BASE_ERROR_TEXT)
    finally:
        await state.finish()


async def weather_with_location_from_text(
        message: types.Message, state: FSMContext) -> None:
    # читаем название города из текста и пытаемся получить погоду,
    # при неудачи состояние пропадает
    city_info = message.text.split(',')
    city_name = city_info[0].strip()
    country_code = None
    if len(city_info) > 1:
        country_code = city_info[1].strip()

    try:
        weather_result = await weather.get_weather(
            city_name=city_name, country_code=country_code)
        await message.answer(
            weather_result.make_text_message(), reply_markup=types.ReplyKeyboardRemove())
    except ClientException as ex:
        logging.error(ex)
        await message.answer(str(ex))
    except Exception as ex:
        logging.error(ex)
        await message.answer(BASE_ERROR_TEXT)
    finally:
        await state.finish()


def register_weather_handlers(dp: Dispatcher) -> None:
    # регистрируем хэндлеры
    dp.register_message_handler(
        weather_start,
        lambda message: types.ChatType.PRIVATE == message.chat.type,
        commands='weather'
    )
    dp.register_message_handler(
        weather_with_location_from_btn,
        lambda message: types.ChatType.PRIVATE == message.chat.type,
        content_types='location',
        state=WeatherFSM.wait_location.state
    )
    dp.register_message_handler(
        weather_with_location_from_text,
        lambda message: types.ChatType.PRIVATE == message.chat.type,
        state=WeatherFSM.wait_location.state
    )
