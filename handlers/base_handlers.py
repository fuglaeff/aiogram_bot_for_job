from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

BASE_CANCEL_SUFFIX = '\n\nДля отмены используй команду:\n/cancel'
BASE_ERROR_TEXT = 'В боте что-то поломалось, но мы скоро починим'


async def cancel_state(message: types.Message, state: FSMContext) -> None:
    msg_text = 'Нечего отменять)'
    if await state.get_state() is not None:
        msg_text = 'Команда отменена'
        await state.finish()
    await message.answer(
        msg_text, reply_markup=types.ReplyKeyboardRemove())


def register_base_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(cancel_state, commands='cancel', state='*')
