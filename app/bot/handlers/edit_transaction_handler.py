from app.bot.report_utils import send_excel_from_json, generate_full_report
from app.bot.bot_constants import BASE_API_URL, BotTexts, BotButtons
from app.bot.init_states import EditExpenseState
from aiogram.fsm.context import FSMContext
from app.bot.init_bot import dp, menu_kb
from app.bot.init_logger import logger
from aiogram import types
import httpx

@dp.message(lambda message: message.text == BotButtons.EDIT_EXPENSE.value)
async def edit_expense_start_handler(message: types.Message, state: FSMContext):
    logger.info("User %s initiated expense edit", message.chat.id)
    await message.answer(BotTexts.SENDING_XLSX.value)
    report_data = await generate_full_report(message)
    if not report_data:
        await message.answer(BotTexts.NOT_TRANSACTION.value + "\n" + BotTexts.TRY_AGAIN.value, reply_markup=menu_kb)
        return
    await send_excel_from_json(message.chat.id, report_data)
    await message.answer(BotTexts.EDIT_PROMPT_ID.value)
    await state.set_state(EditExpenseState.waiting_for_id)

@dp.message(EditExpenseState.waiting_for_id)
async def edit_expense_get_id(message: types.Message, state: FSMContext):
    expense_id = message.text.strip()
    await state.update_data(expense_id=expense_id)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_API_URL}/get-transaction",
                params={"transaction_id": expense_id, "telegram_user_id": str(message.chat.id)}
            )
            response.raise_for_status()
    except Exception as e:
        logger.error("Error retrieving expense for edit for user %s: %s", message.chat.id, e)
        await message.answer(BotTexts.TRY_AGAIN.value, reply_markup=menu_kb)
        await state.clear()
        return
    transaction = response.json()
    if status_message := transaction.get("message"):
        await message.answer(status_message, reply_markup=menu_kb)
        await state.clear()
        return

    info_str = BotTexts.PRINT_TRANSACTION_TEMPLATE.value.format(name=transaction["name"], amount_uah=transaction["amount_uah"], amount_usd=transaction["amount_usd"], id=transaction["id"], date=transaction["date"])

    await message.answer(BotTexts.EDIT_INFO.value.format(id=expense_id, info=info_str))
    await message.answer(BotTexts.EDIT_PROMPT_NEW_NAME.value)
    await state.set_state(EditExpenseState.waiting_for_new_name)

@dp.message(EditExpenseState.waiting_for_new_name)
async def edit_expense_get_new_name(message: types.Message, state: FSMContext):
    new_name = message.text.strip()
    await state.update_data(new_name=new_name)
    await message.answer(BotTexts.EDIT_PROMPT_NEW_AMOUNT.value)
    await state.set_state(EditExpenseState.waiting_for_new_amount)

@dp.message(EditExpenseState.waiting_for_new_amount)
async def edit_expense_get_new_amount(message: types.Message, state: FSMContext):
    try:
        new_amount = float(message.text.strip())
    except Exception as e:
        logger.error("Error parsing new amount for user %s: %s", message.chat.id, e)
        await message.answer(BotTexts.TRY_AGAIN.value, reply_markup=menu_kb)
        return
    data = await state.get_data()
    expense_id = data.get("expense_id")
    new_name = data.get("new_name")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{BASE_API_URL}/update-transaction",
                json={
                    "name": new_name,
                    "amount_uah": new_amount,
                    "telegram_user_id": str(message.chat.id),
                    "transaction_id": expense_id
                }
            )
            response.raise_for_status()
    except Exception as e:
        logger.error("Error updating expense for user %s: %s", message.chat.id, e)
        await message.answer(BotTexts.TRY_AGAIN.value, reply_markup=menu_kb)
        return
    transaction = response.json()
    updated_str = BotTexts.PRINT_TRANSACTION_TEMPLATE.value.format(name=transaction["name"], amount_uah=transaction["amount_uah"], amount_usd=transaction["amount_usd"], id=transaction["id"], date=transaction["date"])

    await message.answer(BotTexts.EDIT_SUCCESS.value.format(id=expense_id) + updated_str, reply_markup=menu_kb)
    logger.info("Expense %s updated for user %s", expense_id, message.chat.id)
    await state.clear()
