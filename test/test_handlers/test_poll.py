from unittest.mock import patch, AsyncMock

import pytest
from aiogram.utils.exceptions import ChatNotFound, InvalidPeerID

from fsm import PollFSM
from handlers.base_handlers import BASE_CANCEL_SUFFIX, BASE_ERROR_TEXT
from handlers.poll_handler import poll_take_question, POLL_NOT_VALID_QUESTION_TEXT, POLL_QUESTION_TEXT, \
    poll_take_options, POLL_OPTIONS_TEXT, POLL_NOT_VALID_CNT_OPTIONS_TEXT, POLL_NOT_VALID_OPTION_LENGTH_TEXT, \
    POLL_CHAT_ID_NO_VALID_TEXT, poll_take_chat_id, POLL_CHAT_NOT_FOUND_TEXT, POLL_CHAT_INVALID_ID_TEXT


class PollSenderMock:
    def __init__(self, ex: Exception | None = None) -> None:
        self.ex = ex

    def __call__(self, *args, **kwargs) -> None:
        if self.ex is not None:
            raise self.ex


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'msg_text, valid_msg',
    [
        ('Q' * 301, False),
        ('QWERTY', True),
        ('', False),
    ]
)
@patch('aiogram.types.Message')
@patch('aiogram.dispatcher.FSMContext')
async def test_poll_take_question(
        state_mock, message_mock, msg_text, valid_msg):

    message_mock.answer = AsyncMock()
    message_mock.text = msg_text

    state_mock.set_state = AsyncMock()
    state_mock.update_data = AsyncMock()

    await poll_take_question(message_mock, state_mock)

    message_mock.answer.assert_called_once()

    if not valid_msg:
        assert message_mock.answer.call_args.args[0] == POLL_NOT_VALID_QUESTION_TEXT + BASE_CANCEL_SUFFIX
        return

    state_mock.update_data.assert_called_once()
    state_mock.set_state.assert_called_once()

    assert state_mock.update_data.call_args.kwargs == {'question': message_mock.text}
    assert state_mock.set_state.call_args.args[0] == PollFSM.wait_poll_options.state
    assert message_mock.answer.call_args.args[0] == POLL_QUESTION_TEXT + BASE_CANCEL_SUFFIX


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'msg_text, anses, valid_msg',
    [
        ('Q\n' * 5, ['Q'] * 5, 'True'),
        ('Q\n' * 15, ['Q'] * 15, 'not_cnt'),
        ('Q\n', ['Q'], 'not_cnt'),
        (('Q' * 110 + '\n') * 2, ['Q' * 110 + '\n'] * 2, 'not_length'),
    ]
)
@patch('aiogram.types.Message')
@patch('aiogram.dispatcher.FSMContext')
async def test_poll_take_options(
        state_mock, message_mock, msg_text, anses, valid_msg):

    message_mock.answer = AsyncMock()
    message_mock.text = msg_text

    state_mock.set_state = AsyncMock()
    state_mock.update_data = AsyncMock()

    await poll_take_options(message_mock, state_mock)

    message_mock.answer.assert_called_once()

    if valid_msg == 'not_cnt':
        assert message_mock.answer.call_args.args[0] == POLL_NOT_VALID_CNT_OPTIONS_TEXT + BASE_CANCEL_SUFFIX
        return

    if valid_msg == 'not_length':
        assert message_mock.answer.call_args.args[0] == POLL_NOT_VALID_OPTION_LENGTH_TEXT + BASE_CANCEL_SUFFIX
        return

    state_mock.update_data.assert_called_once()
    state_mock.set_state.assert_called_once()

    assert state_mock.update_data.call_args.kwargs == {'options': anses}
    assert state_mock.set_state.call_args.args[0] == PollFSM.wait_chat_id.state
    assert message_mock.answer.call_args.args[0] == POLL_OPTIONS_TEXT + BASE_CANCEL_SUFFIX


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'msg_text, valid_msg, poll_sender_mock',
    [
        ('-123123123', 'not_ex', PollSenderMock(ex=ChatNotFound('mes'))),
        ('-123123123', 'not_ex', PollSenderMock(ex=InvalidPeerID('mes'))),
        ('-123123123', 'not_ex', PollSenderMock(ex=Exception())),
        ('-123123123', 'True', PollSenderMock()),
        ('1231a2331', 'not_msg', PollSenderMock()),
    ]
)
@patch('aiogram.types.Message')
@patch('aiogram.Bot.send_poll')
@patch('aiogram.dispatcher.FSMContext')
async def test_poll_take_chat_id(
        state_mock, send_poll_mock, message_mock, msg_text, valid_msg, poll_sender_mock):

    send_poll_mock.side_effect = poll_sender_mock
    message_mock.answer = AsyncMock()
    message_mock.text = msg_text

    state_mock.finish = AsyncMock()
    state_mock.get_data = AsyncMock()
    state_mock.get_data.return_value = {
        'question': 'Q',
        'options': ['Q'] * 5,
    }

    await poll_take_chat_id(message_mock, state_mock)

    if valid_msg != 'True':
        message_mock.answer.assert_called_once()

    if valid_msg == 'not_msg':
        assert message_mock.answer.call_args.args[0] == POLL_CHAT_ID_NO_VALID_TEXT + BASE_CANCEL_SUFFIX
        return

    state_mock.get_data.assert_called_once()

    if isinstance(poll_sender_mock.ex, ChatNotFound):
        assert message_mock.answer.call_args.args[0] == POLL_CHAT_NOT_FOUND_TEXT + BASE_CANCEL_SUFFIX
        return

    if isinstance(poll_sender_mock.ex, InvalidPeerID):
        assert message_mock.answer.call_args.args[0] == POLL_CHAT_INVALID_ID_TEXT + BASE_CANCEL_SUFFIX
        return

    if isinstance(poll_sender_mock.ex, Exception):
        assert message_mock.answer.call_args.args[0] == BASE_ERROR_TEXT + BASE_CANCEL_SUFFIX
        return

    assert send_poll_mock.call_args.args == (
        message_mock.text,
        state_mock.get_data.return_value['question'],
        state_mock.get_data.return_value['options'],
    )

    state_mock.finish.assert_called_once()
