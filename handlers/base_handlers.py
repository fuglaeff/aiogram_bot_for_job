from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

BASE_CANCEL_SUFFIX = '\n\nДля отмены используй команду:\n/cancel'
BASE_ERROR_TEXT = 'В боте что-то поломалось, но мы скоро починим'
START_CMD_TEXT = 'Привет!'


async def cancel_state(message: types.Message, state: FSMContext) -> None:
    """
    Команда для отмены любого состояния
    :param message:
    :param state:
    :return:
    """
    msg_text = 'Нечего отменять)'

    # проверяем есть ли состояние и если да, то отменяем
    if await state.get_state() is not None:
        msg_text = 'Команда отменена'
        await state.finish()
    await message.answer(
        msg_text, reply_markup=types.ReplyKeyboardRemove())


async def start_cmd(message: types.Message) -> None:
    await message.answer(START_CMD_TEXT)


def register_base_handlers(dp: Dispatcher) -> None:
    # регистрируем хэндлеры
    dp.register_message_handler(start_cmd, commands='start')
    dp.register_message_handler(cancel_state, commands='cancel', state='*')
