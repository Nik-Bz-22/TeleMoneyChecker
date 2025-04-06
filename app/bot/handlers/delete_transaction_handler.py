from app.bot.report_utils import send_excel_from_json, generate_full_report
from app.bot.bot_constants import BASE_API_URL, BotTexts, BotButtons
from app.bot.init_states import DeleteExpenseState
from aiogram.fsm.context import FSMContext
from app.bot.init_bot import dp, menu_kb
from app.bot.init_logger import logger
from aiogram import types
import httpx

@dp.message(lambda message: message.text == BotButtons.DELETE_EXPENSE.value)
async def delete_expense_start_handler(message: types.Message, state: FSMContext):
    logger.info("User %s initiated expense deletion", message.chat.id)
    await message.answer(BotTexts.SENDING_XLSX.value)
    report_data = await generate_full_report(message)
    if not report_data:
        await message.answer(BotTexts.TRY_AGAIN.value, reply_markup=menu_kb)
        return
    await send_excel_from_json(message.chat.id, report_data)
    await message.answer(BotTexts.DELETE_PROMPT.value)
    await state.set_state(DeleteExpenseState.waiting_for_id)

@dp.message(DeleteExpenseState.waiting_for_id)
async def delete_expense_get_id(message: types.Message, state: FSMContext):
    expense_id = message.text.strip()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{BASE_API_URL}/delete-transaction",
                params={"transaction_id": expense_id, "telegram_user_id": str(message.chat.id)}
            )
            response.raise_for_status()
    except Exception as e:
        logger.error("Error deleting expense for user %s: %s", message.chat.id, e)
        await message.answer(BotTexts.NOT_TRANSACTION.value + "\n" + BotTexts.TRY_AGAIN.value, reply_markup=menu_kb)
        await state.clear()
        return
    await message.answer(BotTexts.DELETE_SUCCESS.value.format(id=expense_id), reply_markup=menu_kb)
    logger.info("Expense %s deleted for user %s", expense_id, message.chat.id)
    await state.clear()
