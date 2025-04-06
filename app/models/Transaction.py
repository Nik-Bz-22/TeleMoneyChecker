from sqlalchemy import Column, Integer, String, Date, DECIMAL, CHAR
from app.core.db import Base
from datetime import date


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    amount_uah = Column(DECIMAL(precision=7, scale=2), nullable=False)
    amount_usd = Column(DECIMAL(precision=7, scale=2), nullable=False)
    date = Column(Date, nullable=False, default=date.today(), index=True)
    telegram_user_id = Column(String, nullable=False)

    def __repr__(self):
        return f"<Transaction(id={self.id}, name={self.name}, amount_uah={self.amount_uah}, amount_usd={self.amount_usd}, date={self.date}, telegram_user_id={self.telegram_user_id})>"
