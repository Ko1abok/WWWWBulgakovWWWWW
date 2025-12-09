
from aiogram.fsm.state import State, StatesGroup

class AuthStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_name = State()
    waiting_for_surname = State()
    waiting_for_gender = State()
    waiting_for_age = State()
    waiting_for_region = State()
    waiting_for_interests = State()
    waiting_for_photo = State()
    waiting_for_location = State()