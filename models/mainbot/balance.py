"""
Balance models from mainbot - READ ONLY.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from models.mainbot.base import MainbotBase


class ActiveBalance(MainbotBase):
    """Active balance records from mainbot - READ ONLY."""
    __tablename__ = 'active_balances'

    paymentID = Column(Integer, primary_key=True, autoincrement=True)
    createdAt = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    userID = Column(Integer, ForeignKey('users.userID'))
    firstname = Column(String, nullable=False)
    surname = Column(String, nullable=True)
    amount = Column(DECIMAL(12, 2), nullable=False)
    status = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    link = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship('User', back_populates='active_balance_records')

    @property
    def formatted_amount(self):
        """Formatted amount with sign"""
        sign = '+' if self.amount > 0 else ''
        return f"{sign}${self.amount:,.2f}"

    @property
    def days_ago(self):
        """Days since transaction"""
        if self.createdAt:
            return (datetime.now(timezone.utc) - self.createdAt).days
        return 0


class PassiveBalance(MainbotBase):
    """Passive balance records from mainbot - READ ONLY."""
    __tablename__ = 'passive_balances'

    paymentID = Column(Integer, primary_key=True, autoincrement=True)
    createdAt = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    userID = Column(Integer, ForeignKey('users.userID'))
    firstname = Column(String, nullable=False)
    surname = Column(String, nullable=True)
    amount = Column(DECIMAL(12, 2), nullable=False)
    status = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    link = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship('User', back_populates='passive_balance_records')

    @property
    def formatted_amount(self):
        """Formatted amount with sign"""
        sign = '+' if self.amount > 0 else ''
        return f"{sign}${self.amount:,.2f}"

    @property
    def days_ago(self):
        """Days since transaction"""
        if self.createdAt:
            return (datetime.now(timezone.utc) - self.createdAt).days
        return 0