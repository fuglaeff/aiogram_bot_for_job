from aiogram.dispatcher.filters.state import State, StatesGroup

"""
Описываем интерфейсы FSM
"""


class WeatherFSM(StatesGroup):
    wait_location = State()


class ExchangeFSM(StatesGroup):
    wait_amount = State()
    wait_convert_to = State()


class PollFSM(StatesGroup):
    wait_poll_question = State()
    wait_poll_options = State()
    wait_chat_id = State()
