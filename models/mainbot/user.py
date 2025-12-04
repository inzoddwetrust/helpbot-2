"""
User model from mainbot - READ ONLY.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime, timezone

from models.mainbot.base import MainbotBase


class User(MainbotBase):
    """User from mainbot database - READ ONLY."""
    __tablename__ = 'users'

    userID = Column(Integer, primary_key=True)
    createdAt = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    upline = Column(Integer, ForeignKey('users.telegramID'), nullable=True)
    lang = Column(String)
    firstname = Column(String)
    surname = Column(String, nullable=True)
    birthday = Column(String, nullable=True)
    address = Column(String, nullable=True)
    phoneNumber = Column(String, nullable=True)
    country = Column(String, nullable=True)
    passport = Column(String, nullable=True)
    city = Column(String, nullable=True)
    telegramID = Column(Integer, unique=True, nullable=False)
    email = Column(String, nullable=True)
    balanceActive = Column(DECIMAL(12, 2), default=0.00)
    balancePassive = Column(DECIMAL(12, 2), default=0.00)
    personalData = Column(JSON, nullable=True)
    lastActive = Column(DateTime, nullable=True)
    status = Column(String, default="active")
    notes = Column(Text, nullable=True)
    settings = Column(JSON, nullable=True)

    referrals = relationship('User',
                           foreign_keys=[upline],
                           back_populates='referrer',
                           remote_side=[telegramID])
    referrer = relationship('User',
                          foreign_keys=[upline],
                          back_populates='referrals',
                          remote_side=[upline],
                          uselist=False)

    # Other models
    purchases = relationship('Purchase', back_populates='user')
    payments = relationship('Payment', back_populates='user')
    received_bonuses = relationship('Bonus', foreign_keys='Bonus.userID', back_populates='user')
    generated_bonuses = relationship('Bonus', foreign_keys='Bonus.downlineID', back_populates='downline')
    active_balance_records = relationship('ActiveBalance', back_populates='user')
    passive_balance_records = relationship('PassiveBalance', back_populates='user')
    sent_transfers = relationship('Transfer', foreign_keys='Transfer.senderUserID', back_populates='sender')
    received_transfers = relationship('Transfer', foreign_keys='Transfer.receiverUserID', back_populates='receiver')

    # Properties for operator display
    @property
    def full_name(self):
        """Full name for display"""
        parts = []
        if self.firstname:
            parts.append(self.firstname)
        if self.surname:
            parts.append(self.surname)
        return ' '.join(parts) if parts else f"User {self.userID}"

    @property
    def total_balance(self):
        """Total balance (active + passive)"""
        return (self.balanceActive or 0) + (self.balancePassive or 0)

    @hybrid_property
    def kyc_status(self):
        """Returns KYC status from personalData JSON"""
        if self.personalData:
            kyc_data = self.personalData.get('kyc', {})
            if isinstance(kyc_data, dict):
                status = kyc_data.get('status', 'not_started')
                return "✅ Verified" if status == 'verified' else "❌ Not verified"
            return "✅ Verified" if kyc_data else "❌ Not verified"
        return "❌ Not verified"

    @hybrid_property
    def is_profile_filled(self):
        """Check if profile data is filled"""
        if self.personalData:
            return self.personalData.get('dataFilled', False)
        return False

    @property
    def isFilled(self):
        """Backward compatibility: reads from personalData.dataFilled"""
        return self.is_profile_filled

    @property
    def kyc(self):
        """Backward compatibility: reads from personalData.kyc.status"""
        if self.personalData:
            kyc_data = self.personalData.get('kyc', {})
            if isinstance(kyc_data, dict):
                return kyc_data.get('status') == 'verified'
        return False

    @property
    def profile_completeness(self):
        """Profile completeness percentage"""
        fields = [
            self.firstname, self.surname, self.email,
            self.phoneNumber, self.country, self.city,
            self.birthday, self.address, self.passport
        ]
        filled = sum(1 for f in fields if f)
        return int((filled / len(fields)) * 100)

    @property
    def days_since_registration(self):
        """Days since registration"""
        if self.createdAt:
            return (datetime.now(timezone.utc) - self.createdAt).days
        return 0

    @property
    def referral_count(self):
        """Number of direct referrals"""
        return len(self.referrals) if self.referrals else 0