from decimal import Decimal
from datetime import date
import asyncio
import httpx



async def fetch_currency_rate(date_to_check_currency:date, currency:str="usd") -> Decimal|None:
    url = f'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode={currency}&date={date_to_check_currency.strftime("%Y%m%d")}&json'

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code == 200:
        return Decimal(response.json()[0]["rate"])
    else:
        print(f"Request error: {response.status_code}")


if __name__ == "__main__":
    asyncio.run(fetch_currency_rate(date(2025,4,4)))
