from unittest.mock import patch, AsyncMock

import pytest

from clients import ClientException
from fsm import ExchangeFSM
from handlers.exchange_handlers import (exchange_take_from_info, EXCHANGE_TO_CONVERT_TEXT, EXCHANGE_NOT_VALID_FROM_TEXT,
                                        exchange_take_to_info, EXCHANGE_NOT_VALID_TO_TEXT
                                        )
from handlers.base_handlers import BASE_ERROR_TEXT, BASE_CANCEL_SUFFIX
from models import ExchangeModel

TEST_API_RESP = '''{
    "success": true,
    "query": {
        "from": "GBP",
        "to": "JPY",
        "amount": 25
    },
    "info": {
        "timestamp": 1519328414,
        "rate": 148.972231
    },
    "historical": "",
    "date": "2018-02-22",
    "result": 3724.305775
}'''


class ConvertMock:
    to_return = ExchangeModel.parse_raw(TEST_API_RESP)

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
    'msg_text, amount, from_',
    [
        ('150.08 RUB', '150.08', 'RUB'),
        ('150 RUB', '150', 'RUB'),
        ('150RUB', '150', 'RUB'),
        ('RUB', None, None),
        ('150', None, None),
        ('150.', None, None),
        ('150.RUB', None, None),
    ]
)
@patch('aiogram.types.Message')
@patch('aiogram.dispatcher.FSMContext')
async def test_exchange_take_from_info(
        state_mock, message_mock, msg_text, amount, from_):

    message_mock.answer = AsyncMock()
    message_mock.text = msg_text

    state_mock.set_state = AsyncMock()
    state_mock.update_data = AsyncMock()

    await exchange_take_from_info(message_mock, state_mock)

    message_mock.answer.assert_called_once()

    if amount is None and from_ is None:
        assert message_mock.answer.call_args.args[0] == EXCHANGE_NOT_VALID_FROM_TEXT + BASE_CANCEL_SUFFIX
        return

    state_mock.update_data.assert_called_once()
    state_mock.set_state.assert_called_once()

    assert state_mock.update_data.call_args.kwargs == {
        'amount': amount,
        'from_': from_,
    }
    assert state_mock.set_state.call_args.args[0] == ExchangeFSM.wait_convert_to.state
    assert message_mock.answer.call_args.args[0] == EXCHANGE_TO_CONVERT_TEXT + BASE_CANCEL_SUFFIX


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'msg_text, msg_valid, convert_mock',
    [
        ('USD', True, ConvertMock()),
        ('USD', True, ConvertMock(ex=ClientException())),
        ('USD', True, ConvertMock(ex=Exception())),
        ('123', False, ConvertMock()),
        ('', False, ConvertMock()),
        ('1as3', False, ConvertMock()),
    ]
)
@patch('clients.ExchangeClient.convert')
@patch('aiogram.types.Message')
@patch('aiogram.dispatcher.FSMContext')
async def test_exchange_take_to_info(
        state_mock, message_mock, exchange_mock, msg_text, msg_valid, convert_mock):
    exchange_mock.side_effect = convert_mock
    message_mock.answer = AsyncMock()
    message_mock.text = msg_text

    state_mock.finish = AsyncMock()
    state_mock.get_data = AsyncMock()
    state_mock.get_data.return_value = {
        'amount': '150',
        'from_': 'RUB',
    }

    await exchange_take_to_info(message_mock, state_mock)

    message_mock.answer.assert_called_once()

    if not msg_valid:
        assert message_mock.answer.call_args.args[0] == EXCHANGE_NOT_VALID_TO_TEXT + BASE_CANCEL_SUFFIX
        return

    state_mock.finish.assert_called_once()
    state_mock.get_data.assert_called_once()

    exchange_mock.assert_called_once()
    assert exchange_mock.call_args.kwargs == {
        **state_mock.get_data.return_value,
        'to': msg_text,
    }

    if isinstance(convert_mock.ex, ClientException):
        assert message_mock.answer.call_args.args[0] == str(convert_mock.ex)
    elif isinstance(convert_mock.ex, Exception):
        assert message_mock.answer.call_args.args[0] == BASE_ERROR_TEXT
    else:
        assert message_mock.answer.call_args.args[0] == convert_mock.to_return.make_text_message()
