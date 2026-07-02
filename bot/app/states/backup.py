from aiogram.fsm.state import State, StatesGroup


class BackupForm(StatesGroup):
    waiting_for_file = State()
    waiting_for_confirmation = State()
