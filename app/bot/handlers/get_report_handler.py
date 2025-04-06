from app.bot.bot_constants import BASE_API_URL, BotTexts, BotButtons
from app.bot.report_utils import send_excel_from_json
from app.bot.init_states import ReportExpenseState
from aiogram.fsm.context import FSMContext
from app.bot.init_bot import dp, menu_kb
from app.bot.init_logger import logger
from datetime import datetime
from decimal import Decimal
from aiogram import types
import httpx


@dp.message(lambda message: message.text == BotButtons.REPORT_EXPENSE.value)
async def report_expense_start_handler(message: types.Message, state: FSMContext):
    logger.info("User %s initiated report generation", message.chat.id)
    await message.answer(BotTexts.REPORT_PROMPT_START.value)
    await state.set_state(ReportExpenseState.waiting_for_start_date)

@dp.message(ReportExpenseState.waiting_for_start_date)
async def report_expense_get_start(message: types.Message, state: FSMContext):
    try:
        start_date = datetime.strptime(message.text, "%d.%m.%Y").date()
    except ValueError:
        logger.warning("User %s entered invalid start date: %s", message.chat.id, message.text)
        await message.answer(BotTexts.REPORT_PROMPT_START.value)
        return
    await state.update_data(start_date=start_date)
    await message.answer(BotTexts.REPORT_PROMPT_END.value)
    await state.set_state(ReportExpenseState.waiting_for_end_date)

@dp.message(ReportExpenseState.waiting_for_end_date)
async def report_expense_get_end(message: types.Message, state: FSMContext):
    try:
        end_date = datetime.strptime(message.text, "%d.%m.%Y").date()
    except ValueError:
        logger.warning("User %s entered invalid end date: %s", message.chat.id, message.text)
        await message.answer(BotTexts.REPORT_PROMPT_END.value)
        return
    data = await state.get_data()
    if data["start_date"] > end_date:
        await message.answer(BotTexts.DATE_ORDER_ERROR.value)
        logger.warning("User %s provided start date greater than end date", message.chat.id)
        return

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_API_URL}/get-transactions",
                params={
                    "start": data["start_date"].isoformat(),
                    "end": end_date.isoformat(),
                    "telegram_user_id": str(message.chat.id)
                }
            )
            response.raise_for_status()
    except Exception as e:
        logger.error("Error fetching report for user %s: %s", message.chat.id, e)
        await message.answer(BotTexts.TRY_AGAIN.value, reply_markup=menu_kb)
        await state.clear()
        return

    transactions = response.json()
    if not transactions:
        await message.answer(
            f'У вас немає витрат за період з {data["start_date"]} по {end_date}',
            reply_markup=menu_kb
        )
        await state.clear()
        return

    await message.answer(
        BotTexts.REPORT_SUCCESS.value.format(start_date=data["start_date"], end_date=end_date)
    )
    await send_excel_from_json(message.chat.id, transactions, start_date=data["start_date"], end_date=end_date)
    total_uah = sum(Decimal(item["amount_uah"]) for item in transactions)
    total_usd = sum(Decimal(item["amount_usd"]) for item in transactions)
    await message.answer(
        f'💳 Загальна сума в UAH: {total_uah}\n💲 Загальна сума в USD: {total_usd}',
        reply_markup=menu_kb
    )
    logger.info("Report generated for user %s", message.chat.id)
    await state.clear()