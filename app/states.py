from aiogram.fsm.state import State, StatesGroup


class ProductSearch(StatesGroup):
    waiting_query = State()


class ReviewFlow(StatesGroup):
    waiting_rating = State()
    waiting_text = State()


class SupportFlow(StatesGroup):
    waiting_message = State()


class ConsultationFlow(StatesGroup):
    waiting_goal = State()
    waiting_lifestyle = State()
    waiting_format = State()


class ReminderFlow(StatesGroup):
    waiting_date = State()


class AdminBroadcastFlow(StatesGroup):
    waiting_text = State()

