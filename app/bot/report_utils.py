from app.bot.bot_constants import BASE_API_URL
from typing import List, Optional
from datetime import date
from aiogram import types
from io import BytesIO
import pandas as pd
import httpx

from app.bot.init_logger import logger

from app.bot.init_bot import bot


async def send_excel_from_json(chat_id: int, data: List[dict], start_date: Optional[date] = None, end_date: Optional[date] = None) -> None:
    logger.info("Generating Excel report with %d records for chat_id %s", len(data), chat_id)
    df = pd.DataFrame(data)
    desired_order = ["id", "name", "amount_uah", "amount_usd", "date"]
    df = df.reindex(columns=desired_order)
    if start_date and end_date:
        filename = f"report_{start_date}_{end_date}.xlsx"
    else:
        filename = "report.xlsx"
    output = BytesIO()
    try:
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
    except Exception as e:
        logger.error("Error generating Excel file: %s", e)
        raise
    output.seek(0)
    output.name = filename
    await bot.send_document(
        chat_id=chat_id,
        document=types.BufferedInputFile(output.getvalue(), filename)
    )
    logger.info("Excel report sent to chat_id %s", chat_id)

async def generate_full_report(message: types.Message) -> Optional[List[dict]]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_API_URL}/get-transactions",
                params={"telegram_user_id": str(message.chat.id)}
            )
            response.raise_for_status()
    except Exception as e:
        logger.error("Error fetching full report: %s", e)
        return None
    data = response.json()
    logger.info("Fetched %d transactions for report for chat_id %s", len(data), message.chat.id)
    return data
