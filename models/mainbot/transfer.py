"""
Transfer model from mainbot - READ ONLY.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from models.mainbot.base import MainbotBase


class Transfer(MainbotBase):
    """Transfer from mainbot database - READ ONLY."""
    __tablename__ = 'transfers'

    transferID = Column(Integer, primary_key=True, autoincrement=True)
    createdAt = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    senderUserID = Column(Integer, ForeignKey('users.userID'))
    senderFirstname = Column(String, nullable=False)
    senderSurname = Column(String, nullable=True)
    fromBalance = Column(String, nullable=False)
    amount = Column(DECIMAL(12, 2), nullable=False)  # FIXED: Float -> DECIMAL
    receiverUserID = Column(Integer, ForeignKey('users.userID'))  # FIXED: reciever -> receiver
    receiverFirstname = Column(String, nullable=False)
    receiverSurname = Column(String, nullable=True)
    toBalance = Column(String, nullable=False)
    status = Column(String, nullable=False)
    notes = Column(Text, nullable=True)

    # Relationships
    sender = relationship('User', foreign_keys=[senderUserID], backref='sent_transfers')
    receiver = relationship('User', foreign_keys=[receiverUserID], backref='received_transfers')  # FIXED

    @property
    def formatted_amount(self):
        """Formatted transfer amount"""
        return f"${self.amount:,.2f}"

    @property
    def balance_flow(self):
        """Balance flow description"""
        return f"{self.fromBalance} → {self.toBalance}"

    @property
    def sender_name(self):
        """Sender full name"""
        parts = [self.senderFirstname]
        if self.senderSurname:
            parts.append(self.senderSurname)
        return ' '.join(parts)

    @property
    def receiver_name(self):
        """Receiver full name"""
        parts = [self.receiverFirstname]
        if self.receiverSurname:
            parts.append(self.receiverSurname)
        return ' '.join(parts)

    @property
    def days_ago(self):
        """Days since transfer"""
        if self.createdAt:
            return (datetime.now(timezone.utc) - self.createdAt).days
        return 0