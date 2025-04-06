from aiogram.fsm.state import StatesGroup, State

class AddExpenseState(StatesGroup):
    waiting_for_name = State()
    waiting_for_date = State()
    waiting_for_amount = State()

class ReportExpenseState(StatesGroup):
    waiting_for_start_date = State()
    waiting_for_end_date = State()

class DeleteExpenseState(StatesGroup):
    waiting_for_id = State()

class EditExpenseState(StatesGroup):
    waiting_for_id = State()
    waiting_for_new_name = State()
    waiting_for_new_amount = State()