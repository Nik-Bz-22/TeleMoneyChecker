from app.bot.bot_constants import BASE_API_URL, BotTexts, BotButtons
from app.bot.init_states import AddExpenseState
from aiogram.fsm.context import FSMContext
from app.bot.init_bot import dp, menu_kb
from app.bot.init_logger import logger
from datetime import datetime
from aiogram import types
import httpx

@dp.message(lambda message: message.text == BotButtons.ADD_EXPENSE.value)
async def add_expense_start_handler(message: types.Message, state: FSMContext):
    logger.info("User %s initiated add expense", message.chat.id)
    await message.answer(BotTexts.ADD_PROMPT_NAME.value)
    await state.set_state(AddExpenseState.waiting_for_name)

@dp.message(AddExpenseState.waiting_for_name)
async def add_expense_get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(BotTexts.ADD_PROMPT_DATE.value)
    await state.set_state(AddExpenseState.waiting_for_date)

@dp.message(AddExpenseState.waiting_for_date)
async def add_expense_get_date(message: types.Message, state: FSMContext):
    try:
        expense_date = datetime.strptime(message.text, "%d.%m.%Y").date()
    except ValueError:
        logger.warning("User %s entered invalid date format: %s", message.chat.id, message.text)
        await message.answer(BotTexts.ADD_PROMPT_DATE.value)
        return
    await state.update_data(expense_date=expense_date)
    await message.answer(BotTexts.ADD_PROMPT_AMOUNT.value)
    await state.set_state(AddExpenseState.waiting_for_amount)

@dp.message(AddExpenseState.waiting_for_amount)
async def add_expense_get_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
    except Exception as e:
        logger.error("Error parsing amount for user %s: %s", message.chat.id, e)
        await message.answer(BotTexts.ADD_PROMPT_AMOUNT.value)
        return
    await state.update_data(amount=amount)
    data = await state.get_data()
    logger.info("Add expense data for user %s: %s", message.chat.id, data)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_API_URL}/create-transaction",
                json={
                    "name": data["name"],
                    "amount_uah": data["amount"],
                    "date": data["expense_date"].isoformat(),
                    "telegram_user_id": str(message.chat.id)
                }
            )
            response.raise_for_status()
    except Exception as e:
        logger.error("Error creating expense for user %s: %s", message.chat.id, e)
        await message.answer(BotTexts.TRY_AGAIN.value, reply_markup=menu_kb)
        await state.clear()
        return

    transaction = response.json()

    answer_str = BotTexts.PRINT_TRANSACTION_TEMPLATE.value.format(name=transaction["name"], amount_uah=transaction["amount_uah"], amount_usd=transaction["amount_usd"], id=transaction["id"], date=transaction["date"])
    logger.info("Expense created for user %s: %s", message.chat.id, transaction)
    await message.answer(BotTexts.ADD_SUCCESS.value + answer_str, reply_markup=menu_kb)
    await state.clear()