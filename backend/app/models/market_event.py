from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class MarketEvent(Base):
    __tablename__ = "market_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    coin_id: Mapped[int] = mapped_column(ForeignKey("coins.id"), index=True)

    event_type: Mapped[str] = mapped_column(String(50), index=True)
    message: Mapped[str] = mapped_column(String(255))

    window_minutes: Mapped[int] = mapped_column()
    threshold_percent: Mapped[float] = mapped_column(Numeric(10, 4))

    start_price_usd: Mapped[float] = mapped_column(Numeric(18, 6))
    end_price_usd: Mapped[float] = mapped_column(Numeric(18, 6))
    percent_change: Mapped[float] = mapped_column(Numeric(10, 4))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    coin = relationship("Coin")
