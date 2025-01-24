from aiogram.dispatcher.filters.state import State, StatesGroup

class CalculationStates(StatesGroup):
    portfolio_amount = State()
    nsj_amount = State()
    deposit_amount = State()
    tax_rate = State()
