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
    inline_location_btn = types.KeyboardButton(
        'Поделиться локацией', request_location=True)
    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True).add(inline_location_btn)
    await state.set_state(WeatherFSM.wait_location.state)
    await message.answer(
        WEATHER_START_TEXT + BASE_CANCEL_SUFFIX, reply_markup=kb)


async def weather_with_location_from_btn(
        message: types.Message, state: FSMContext) -> None:
    try:
        weather_result = await weather.get_weather(
            lat=message.location.latitude, lon=message.location.longitude)
        await message.answer(
            weather_result.make_text_message(), reply_markup=types.ReplyKeyboardRemove())
    except ClientException as ex:
        await message.answer(str(ex))
    except Exception as ex:
        await message.answer(BASE_ERROR_TEXT)
    finally:
        await state.finish()


async def weather_with_location_from_text(
        message: types.Message, state: FSMContext) -> None:
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
        await message.answer(str(ex))
    except Exception as ex:
        await message.answer(BASE_ERROR_TEXT)
    finally:
        await state.finish()


def register_weather_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(
        weather_start,
        lambda message: message.chat.type == types.ChatType.PRIVATE,
        commands='weather'
    )
    dp.register_message_handler(
        weather_with_location_from_btn,
        lambda message: message.chat.type == types.ChatType.PRIVATE,
        content_types='location',
        state=WeatherFSM.wait_location.state
    )
    dp.register_message_handler(
        weather_with_location_from_text,
        lambda message: message.chat.type == types.ChatType.PRIVATE,
        state=WeatherFSM.wait_location.state
    )
