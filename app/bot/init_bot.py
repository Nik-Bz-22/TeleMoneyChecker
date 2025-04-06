from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from app.bot.bot_constants import API_TOKEN, BotButtons
from aiogram import Bot, Dispatcher

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BotButtons.ADD_EXPENSE.value)],
        [KeyboardButton(text=BotButtons.REPORT_EXPENSE.value)],
        [KeyboardButton(text=BotButtons.DELETE_EXPENSE.value)],
        [KeyboardButton(text=BotButtons.EDIT_EXPENSE.value)],
        [KeyboardButton(text=BotButtons.STOP.value)]
    ],
    resize_keyboard=True
)