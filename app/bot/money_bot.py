from app.bot.handlers import get_report_handler, edit_transaction_handler, add_transaction_handler, delete_transaction_handler
from app.bot.bot_constants import API_TOKEN, BASE_API_URL, BotTexts, BotButtons
from app.bot.init_bot import bot, dp, menu_kb
from aiogram.fsm.context import FSMContext
from app.bot.init_logger import logger
from aiogram.filters import Command
from aiogram import types
import asyncio

if not API_TOKEN or not BASE_API_URL:
    raise ValueError("BOT_API_TOKEN and BASE_API_URL must be set in environment variables.")


@dp.message(lambda message: message.text.strip().upper() == BotButtons.STOP.value)
async def stop_operation(message: types.Message, state: FSMContext):
    if await state.get_state():
        await state.clear()
        logger.info("User %s cancelled operation", message.chat.id)
        await message.answer(BotTexts.STOP_ACTIVE.value, reply_markup=menu_kb)
    else:
        await message.answer(BotTexts.STOP_INACTIVE.value, reply_markup=menu_kb)

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    logger.info("User %s started bot", message.chat.id)
    await message.answer(BotTexts.MENU_TITLE.value, reply_markup=menu_kb)



async def main() -> None:
    logger.info("Bot polling started")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
