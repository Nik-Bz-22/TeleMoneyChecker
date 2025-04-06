import os
from enum import Enum

API_TOKEN = os.environ.get("BOT_API_TOKEN")
BASE_API_URL = os.environ.get("BASE_API_URL")


class BotTexts(Enum):
    MENU_TITLE = "Вітаємо! Оберіть функцію:"
    STOP_ACTIVE = "Операцію перервано. Повертаємося в головне меню."
    STOP_INACTIVE = "Немає активної операції. Ось головне меню:"
    NOT_TRANSACTION = "У вас ще нема транзакцій"
    ADD_PROMPT_NAME = "Введіть назву статті витрат (наприклад, 'Щомісячна сплата за інтернет'):"
    ADD_PROMPT_DATE = "Введіть дату витрат у форматі dd.mm.YYYY (наприклад, 19.03.2025):"
    ADD_PROMPT_AMOUNT = "Введіть суму витрат (число, у грн):"
    ADD_SUCCESS = "Нову витрату додано успішно:\n\n"
    REPORT_PROMPT_START = "Введіть дату початку періоду (dd.mm.YYYY):"
    REPORT_PROMPT_END = "Введіть дату кінця періоду (dd.mm.YYYY):"
    REPORT_SUCCESS = "Звіт за період з {start_date} по {end_date} формується..."
    DELETE_PROMPT = "Введіть ID статті витрат, яку потрібно видалити:"
    DELETE_SUCCESS = "Статтю витрат з ID {id} видалено."
    EDIT_PROMPT_ID = "Введіть ID статті витрат, яку потрібно відредагувати:"
    EDIT_INFO = "Інформація про статтю з ID {id}:\n\n{info}"
    EDIT_PROMPT_NEW_NAME = "Введіть нову назву статті витрат:"
    EDIT_PROMPT_NEW_AMOUNT = "Введіть нову суму витрат:"
    EDIT_SUCCESS = "Статтю витрат з ID {id} оновлено:\n\n"
    TRY_AGAIN = "Спробуйте ще раз"
    SENDING_XLSX = "Надсилаю список витрат (xlsx)..."
    DATE_ORDER_ERROR = "Дата початку повинна бути меншою за дату кінця. Спробуйте ще раз."
    PRINT_TRANSACTION_TEMPLATE = (
        "{name}\n"
        "💳: {amount_uah} UAH\n"
        "💲: {amount_usd} USD\n"
        "📅: {date}\n"
        "🆔: {id}"
    )

class BotButtons(Enum):
    ADD_EXPENSE = "Додати статтю витрат"
    REPORT_EXPENSE = "Отримати звіт витрат за період"
    DELETE_EXPENSE = "Видалити статтю витрат"
    EDIT_EXPENSE = "Відредагувати статтю витрат"
    STOP = "СТОП"
