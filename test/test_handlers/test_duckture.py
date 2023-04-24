from unittest.mock import patch, AsyncMock

import pytest

from clients import ClientException
from handlers.animals_handler import send_duckture
from handlers.base_handlers import BASE_ERROR_TEXT


class GetDuckMock:
    def __init__(
        self,
        format_: str = 'png',
        link: str = 'link',
        ex: Exception | None = None
    ) -> None:
        self.format_ = format_
        self.link = link
        self.ex = ex

    def __call__(self, *args, **kwargs) -> tuple[str, str]:
        if self.ex is None:
            return self.format_, self.link

        raise self.ex


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'get_duck',
    [
        GetDuckMock(),
        GetDuckMock(format_='gif'),
        GetDuckMock(ex=ClientException()),
        GetDuckMock(ex=Exception()),
    ]
)
@patch('clients.DuckClient.get_duck')
@patch('aiogram.Bot.send_photo')
@patch('aiogram.Bot.send_animation')
@patch('aiogram.types.Message')
async def test_send_duckture(
        message_mock, send_animation_mock, send_photo_mock, duck_mock, get_duck):
    duck_mock.side_effect = get_duck
    message_mock.answer = AsyncMock()
    message_mock.chat.id = 1

    await send_duckture(message_mock)
    duck_mock.assert_called_once()

    if get_duck.ex is not None:
        message_mock.answer.assert_called_once()
        if isinstance(get_duck.ex, ClientException):
            assert message_mock.answer.call_args.args[0] == str(get_duck.ex)
        else:
            assert message_mock.answer.call_args.args[0] == BASE_ERROR_TEXT

        send_photo_mock.assert_not_called()
        send_animation_mock.assert_not_called()

    elif get_duck.format_ == 'png':
        send_photo_mock.assert_called_once()
        assert send_photo_mock.call_args.args[0] == message_mock.chat.id
        assert send_photo_mock.call_args.args[1] == get_duck.link

        send_animation_mock.assert_not_called()
        message_mock.answer.assert_not_called()

    elif get_duck.format_ == 'gif':
        send_animation_mock.assert_called_once()
        assert send_animation_mock.call_args.args[0] == message_mock.chat.id
        assert send_animation_mock.call_args.args[1] == get_duck.link

        send_photo_mock.assert_not_called()
        message_mock.answer.assert_not_called()
