import re

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from bot import exchange
from clients import ClientException
from fsm import ExchangeFSM
from handlers.base_handlers import BASE_CANCEL_SUFFIX, BASE_ERROR_TEXT

EXCHANGE_START_TEXT = (
    'Введи кол-во и название валюты для конвертации\n' +
    'н-р: 150.5 RUB'
)
EXCHANGE_NOT_VALID_FROM_TEXT = (
    'Неправильно введины данные, попробуй еще раз\n' +
    'вот пример: 150.5 RUB'
)
EXCHANGE_TO_CONVERT_TEXT = (
    'Теперь введи валюту, в которую будем конвертировать\n' +
    'н-р:\nRUB\nUSD\nGBP'
)
EXCHANGE_NOT_VALID_TO_TEXT = (
    'Неправильно введины данные, попробуй еще раз\n' +
    'вот пример:\nRUB\nUSD\nGBP'
)


async def exchange_start(message: types.Message, state: FSMContext) -> None:
    await state.set_state(ExchangeFSM.wait_amount.state)
    await message.answer(EXCHANGE_START_TEXT + BASE_CANCEL_SUFFIX)


async def exchange_take_from_info(message: types.Message, state: FSMContext):
    parsed_msg = re.search(r'^(?P<amount>\d+(\.\d+)?)\s?(?P<from_>[a-zA-Z]+)$', message.text)
    if not parsed_msg:
        await message.answer(
            EXCHANGE_NOT_VALID_FROM_TEXT + BASE_CANCEL_SUFFIX)
        return

    await state.update_data(
        amount=parsed_msg['amount'], from_=parsed_msg['from_'])
    await state.set_state(ExchangeFSM.wait_convert_to.state)
    await message.answer(
        EXCHANGE_TO_CONVERT_TEXT + BASE_CANCEL_SUFFIX)


async def exchange_take_to_info(message: types.Message, state: FSMContext) -> None:
    parsed_msg = re.search(r'^(?P<to>[a-zA-Z]+)$', message.text)
    if not parsed_msg:
        await message.answer(
            EXCHANGE_NOT_VALID_TO_TEXT + BASE_CANCEL_SUFFIX)
        return

    user_data = await state.get_data()
    try:
        convertation_result = await exchange.convert(
            amount=user_data['amount'], from_=user_data['from_'], to=parsed_msg['to'])
        await message.answer(convertation_result.make_text_message())
    except ClientException as ex:
        await message.answer(str(ex))
    except Exception as ex:
        await message.answer(BASE_ERROR_TEXT)
    finally:
        await state.finish()


def register_exchange_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(
        exchange_start,
        lambda message: message.chat.type == types.ChatType.PRIVATE,
        commands='exchange'
    )
    dp.register_message_handler(
        exchange_take_from_info,
        lambda message: message.chat.type == types.ChatType.PRIVATE,
        state=ExchangeFSM.wait_amount.state
    )
    dp.register_message_handler(
        exchange_take_to_info,
        lambda message: message.chat.type == types.ChatType.PRIVATE,
        state=ExchangeFSM.wait_convert_to.state
    )
