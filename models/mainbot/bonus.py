"""
Bonus model from mainbot - READ ONLY.
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, Text, DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from models.mainbot.base import MainbotBase


class Bonus(MainbotBase):
    """Bonus from mainbot database - READ ONLY."""
    __tablename__ = 'bonuses'

    bonusID = Column(Integer, primary_key=True, autoincrement=True)
    createdAt = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    userID = Column(Integer, ForeignKey('users.userID'), nullable=False)
    downlineID = Column(Integer, ForeignKey('users.userID'), nullable=True)
    purchaseID = Column(Integer, ForeignKey('purchases.purchaseID'), nullable=True)

    projectID = Column(Integer, nullable=True)
    optionID = Column(Integer, nullable=True)
    packQty = Column(Integer, nullable=True)
    packPrice = Column(DECIMAL(12, 2), nullable=True)  # FIXED: Float -> DECIMAL

    uplineLevel = Column(Integer, nullable=True)
    bonusRate = Column(DECIMAL(5, 2), nullable=False)  # FIXED: Float -> DECIMAL (percentage)
    bonusAmount = Column(DECIMAL(12, 2), nullable=False)  # FIXED: Float -> DECIMAL

    status = Column(String, default="pending")
    notes = Column(Text, nullable=True)

    # NEW FIELDS from jetup-2 (optional but good to have)
    commissionType = Column(String, nullable=True)  # differential/referral/pioneer/global_pool
    fromRank = Column(String, nullable=True)
    sourceRank = Column(String, nullable=True)
    compressionApplied = Column(Integer, nullable=True)

    # Relationships
    user = relationship('User', foreign_keys=[userID], back_populates='received_bonuses')
    downline = relationship('User', foreign_keys=[downlineID], back_populates='generated_bonuses')
    purchase = relationship('Purchase', backref='bonuses')

    @property
    def status_display(self):
        """Status with emoji"""
        status_map = {
            'pending': '⏳ Pending',
            'processing': '🔄 Processing',
            'paid': '✅ Paid',
            'cancelled': '❌ Cancelled',
            'error': '⚠️ Error'
        }
        return status_map.get(self.status, self.status)

    @property
    def formatted_amount(self):
        """Formatted bonus amount"""
        return f"${self.bonusAmount:,.2f}"

    @property
    def formatted_rate(self):
        """Formatted bonus rate as percentage"""
        return f"{self.bonusRate:.1f}%"

    @property
    def bonus_type(self):
        """Returns human-readable bonus type"""
        # Check new commissionType field first (jetup-2)
        if self.commissionType:
            type_map = {
                'differential': 'Differential Bonus',
                'referral': f'Referral Level {self.uplineLevel}',
                'pioneer': 'Pioneer Bonus',
                'global_pool': 'Global Pool',
                'investment_package': 'Investment Package Bonus'
            }
            return type_map.get(self.commissionType, self.commissionType)

        # Fallback to old logic (talentir)
        if self.downlineID:
            return f"Referral Level {self.uplineLevel or 'N/A'}"
        return "System Bonus"