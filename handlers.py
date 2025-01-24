from aiogram import Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from states import CalculationStates
from utils import calculate_income, generate_pdf

def register_handlers(dp, main_menu_keyboard):
    @dp.message_handler(commands="start")
    async def start_command_handler(message: types.Message):
        await message.answer(
            "Добро пожаловать в калькулятор доходности!\nВведите сумму, которую клиент хочет разместить в НСЖ:",
            reply_markup=main_menu_keyboard
        )
        await CalculationStates.nsj_amount.set()

    @dp.message_handler(state=CalculationStates.nsj_amount)
    async def nsj_input_handler(message: types.Message, state: FSMContext):
        try:
            nsj = float(message.text)
            if nsj < 300000:
                await message.answer("Сумма НСЖ не может быть меньше 300 000 рублей. Попробуйте ещё раз.")
                return
            cashback_rate = 34 if 300000 <= nsj < 500000 else 36
            await state.update_data(nsj_amount=nsj, cashback_rate=cashback_rate)
            await message.answer("Введите сумму, которую клиент хочет разместить на вкладе:", reply_markup=main_menu_keyboard)
            await CalculationStates.deposit_amount.set()
        except ValueError:
            await message.answer("Введите корректную сумму в виде числа.")

    @dp.message_handler(state=CalculationStates.deposit_amount)
    async def deposit_input_handler(message: types.Message, state: FSMContext):
        try:
            deposit = float(message.text)
            user_data = await state.get_data()
            nsj = user_data.get("nsj_amount")
            if deposit + nsj < 300000:
                await message.answer("Сумма вклада и НСЖ должна быть больше 300 000 рублей. Попробуйте ещё раз.")
                return
            await state.update_data(deposit_amount=deposit)
            tax_keyboard = InlineKeyboardMarkup(row_width=2)
            tax_keyboard.add(
                InlineKeyboardButton(text="13%", callback_data="tax_13"),
                InlineKeyboardButton(text="15%", callback_data="tax_15")
            )
            await message.answer("Выберите ставку налога:", reply_markup=tax_keyboard)
            await CalculationStates.tax_rate.set()
        except ValueError:
            await message.answer("Введите корректную сумму в виде числа.")

    @dp.callback_query_handler(Text(startswith="tax_"), state=CalculationStates.tax_rate)
    async def tax_input_handler(callback_query: types.CallbackQuery, state: FSMContext):
        tax_rate = 0.13 if callback_query.data == "tax_13" else 0.15
        await state.update_data(tax_rate=tax_rate)

        user_data = await state.get_data()
        nsj = user_data.get("nsj_amount")
        deposit = user_data.get("deposit_amount")
        cashback_rate = user_data.get("cashback_rate")
        result, comparison = calculate_income(nsj, deposit, tax_rate, cashback_rate)
        pdf_path = generate_pdf(result, comparison)

        with open(pdf_path, "rb") as pdf_file:
            await callback_query.message.answer_document(pdf_file, caption="Ваш расчет доходности готов!")
        await state.finish()

    @dp.message_handler(lambda message: message.text == "Вернуться на главную")
    async def back_to_main_handler(message: types.Message):
        await start_command_handler(message)
