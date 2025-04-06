from app.pydantic_validator import TransactionCreate, TransactionUpdate, DateRange, TransactionRead
from fastapi import FastAPI, Depends, HTTPException, Query, Request
from app.utils.currency import fetch_currency_rate
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.Transaction import Transaction
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy.future import select
from app.core.db import get_db
from typing import List
import logging


logger = logging.getLogger("uvicorn")
app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Completed request: {response.status_code}")
    return response


async def get_transaction_by_id(transaction_id: int, user_id: str, db: AsyncSession) -> Transaction:
    try:
        result = await db.execute(
            select(Transaction).where(Transaction.id == transaction_id, Transaction.telegram_user_id == user_id)
        )
        transaction = result.scalars().first()
        if transaction is None:
            logger.warning(f"Transaction ID={transaction_id} not found for user={user_id}")
            raise HTTPException(status_code=404, detail="Transaction not found")
        return transaction
    except Exception as e:
        logger.exception(f"Error fetching transaction ID={transaction_id} for user={user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/get-transaction", response_model=TransactionRead)
async def get_transaction(transaction_id: int, telegram_user_id: str, db: AsyncSession = Depends(get_db)):
    return await get_transaction_by_id(transaction_id, telegram_user_id, db)


@app.get("/get-transactions", response_model=List[TransactionRead])
async def get_transactions(telegram_user_id: str, date_range: DateRange = Depends(), db: AsyncSession = Depends(get_db)):
    try:
        query = select(Transaction).where(Transaction.telegram_user_id == telegram_user_id)

        if date_range.start and date_range.end:
            query = query.where(Transaction.date.between(date_range.start, date_range.end))
        elif date_range.start or date_range.end:
            logger.warning("Partial date range provided")
            raise HTTPException(status_code=400, detail="Both 'start' and 'end' dates must be provided")

        result = await db.execute(query)
        return result.scalars().all()
    except Exception as e:
        logger.exception(f"Error getting transactions for user={telegram_user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch transactions")


@app.post("/create-transaction", response_model=TransactionRead)
async def create_transaction(transaction: TransactionCreate, db: AsyncSession = Depends(get_db)):
    try:
        usd_rate = await fetch_currency_rate(transaction.date, currency="usd")
        amount_usd = (transaction.amount_uah / usd_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        new_transaction = Transaction(
            name=transaction.name,
            amount_uah=transaction.amount_uah,
            amount_usd=amount_usd,
            date=transaction.date,
            telegram_user_id=transaction.telegram_user_id
        )

        db.add(new_transaction)
        await db.commit()
        await db.refresh(new_transaction)

        logger.info(f"Created transaction ID={new_transaction.id} for user={transaction.telegram_user_id}")
        return new_transaction
    except Exception as e:
        logger.exception(f"Failed to create transaction: {e}")
        raise HTTPException(status_code=500, detail="Failed to create transaction")


@app.delete("/delete-transaction")
async def delete_transaction(transaction_id: int, telegram_user_id: str, db: AsyncSession = Depends(get_db)):
    try:
        transaction = await get_transaction_by_id(transaction_id, telegram_user_id, db)

        await db.delete(transaction)
        await db.commit()

        logger.info(f"Deleted transaction ID={transaction_id} for user={telegram_user_id}")
        return {"message": f"Transaction with ID={transaction_id} has been deleted."}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete transaction ID={transaction_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete transaction")


@app.put("/update-transaction", response_model=TransactionRead)
async def update_transaction(data: TransactionUpdate, db: AsyncSession = Depends(get_db)):
    try:
        transaction = await get_transaction_by_id(data.transaction_id, data.telegram_user_id, db)

        if data.date:
            transaction.date = data.date

        if data.amount_uah is not None:
            transaction.amount_uah = data.amount_uah
            usd_rate = await fetch_currency_rate(transaction.date, currency="usd")
            transaction.amount_usd = (data.amount_uah / usd_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if data.name:
            transaction.name = data.name

        await db.commit()
        await db.refresh(transaction)

        logger.info(f"Updated transaction ID={data.transaction_id} for user={data.telegram_user_id}")
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to update transaction ID={data.transaction_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update transaction")
