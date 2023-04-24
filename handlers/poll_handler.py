import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils import exceptions

from bot import telegram_bot
from fsm import PollFSM
from handlers.base_handlers import BASE_CANCEL_SUFFIX, BASE_ERROR_TEXT

POLL_START_TEXT = 'Ввиди вопрос для опроса'
POLL_QUESTION_TEXT = (
    'Введи варианты ответа (каждый вариант начинай с новой строки) н-р:\n' +
    'Вариант 1\n' +
    'Вариант 2\n' +
    'Вариант 3\n' +
    'Вариант 4\n'
)
POLL_OPTIONS_TEXT = 'Введи айди чата'
POLL_CHAT_ID_NO_VALID_TEXT = 'Это не похоже на айди чата'
POLL_NOT_VALID_QUESTION_TEXT = 'Длина вопроса для опроса должна быть от 1 до 300 символов'
POLL_NOT_VALID_CNT_OPTIONS_TEXT = 'В опросе должно быть от 2 до 10 вариантов ответа'
POLL_NOT_VALID_OPTION_LENGTH_TEXT = 'Длина варианта ответа должна быть от 1 до 100 символов'
POLL_CHAT_NOT_FOUND_TEXT = 'Я не нашел такой чат, попробуй еще раз'
POLL_CHAT_INVALID_ID_TEXT = 'Похоже меня нет в этой группе, пригласи и попробуй снова'


async def poll_start(message: types.Message, state: FSMContext) -> None:
    # заводим состояние (FSM) и предлагаем следующее действие пользователю
    await state.set_state(PollFSM.wait_poll_question.state)
    await message.answer(POLL_START_TEXT + BASE_CANCEL_SUFFIX)


async def poll_take_question(message: types.Message, state: FSMContext) -> None:
    # проверяем введенные данные
    if not 0 < len(message.text) < 301:
        await message.answer(POLL_NOT_VALID_QUESTION_TEXT + BASE_CANCEL_SUFFIX)
        return

    # запоминаем валидированные данные и предлагаем следующее действие
    await state.update_data(question=message.text)
    await state.set_state(PollFSM.wait_poll_options.state)
    await message.answer(POLL_QUESTION_TEXT + BASE_CANCEL_SUFFIX)


async def poll_take_options(message: types.Message, state: FSMContext) -> None:
    # проверяем введенные данные
    options = message.text.strip().split('\n')
    if not 1 < len(options) < 11:
        await message.answer(POLL_NOT_VALID_CNT_OPTIONS_TEXT + BASE_CANCEL_SUFFIX)
        return

    if max(len(op) for op in options) > 100 or min(len(op) for op in options) == 0:
        await message.answer(POLL_NOT_VALID_OPTION_LENGTH_TEXT + BASE_CANCEL_SUFFIX)
        return

    # запоминаем валидированные данные и предлагаем следующее действие
    await state.update_data(options=options)
    await state.set_state(PollFSM.wait_chat_id.state)
    await message.answer(POLL_OPTIONS_TEXT + BASE_CANCEL_SUFFIX)


async def poll_take_chat_id(message: types.Message, state: FSMContext) -> None:
    # проверяем введенные данные
    if not (message.text.isdigit() or
            message.text[0] == '-' and message.text[1:].isdigit()
            ):
        await message.answer(POLL_CHAT_ID_NO_VALID_TEXT + BASE_CANCEL_SUFFIX)
        return

    # отправляем опрос в чат (при ошибке просим изменить чат айди)
    poll_data = await state.get_data()
    try:
        await telegram_bot.send_poll(message.text, poll_data['question'], poll_data['options'])
        await state.finish()
    except exceptions.ChatNotFound as ex:
        logging.error(ex)
        await message.answer(POLL_CHAT_NOT_FOUND_TEXT + BASE_CANCEL_SUFFIX)
    except exceptions.InvalidPeerID as ex:
        logging.error(ex)
        await message.answer(POLL_CHAT_INVALID_ID_TEXT + BASE_CANCEL_SUFFIX)
    except Exception as ex:
        logging.error(ex)
        await message.answer(BASE_ERROR_TEXT + BASE_CANCEL_SUFFIX)


def register_poll_handlers(dp: Dispatcher) -> None:
    # регистрируем хэндлеры
    dp.register_message_handler(
        poll_start,
        lambda message: types.ChatType.PRIVATE == message.chat.type,
        commands='poll'
    )
    dp.register_message_handler(
        poll_take_question,
        lambda message: types.ChatType.PRIVATE == message.chat.type,
        state=PollFSM.wait_poll_question.state
    )
    dp.register_message_handler(
        poll_take_options,
        lambda message: types.ChatType.PRIVATE == message.chat.type,
        state=PollFSM.wait_poll_options.state
    )
    dp.register_message_handler(
        poll_take_chat_id,
        lambda message: types.ChatType.PRIVATE == message.chat.type,
        state=PollFSM.wait_chat_id.state
    )
