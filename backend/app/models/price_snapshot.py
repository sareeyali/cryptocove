from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    coin_id: Mapped[int] = mapped_column(ForeignKey("coins.id"), index=True)

    price_usd: Mapped[float] = mapped_column(Numeric(18, 6))
    pulled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    coin = relationship("Coin")
