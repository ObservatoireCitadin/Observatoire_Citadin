from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class Indicator(Base):
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(100), nullable=False, index=True)
    value = Column(Float, nullable=True)
    date = Column(Date, nullable=True, index=True)
    source = Column(String(255), nullable=True)

    city = relationship("City", back_populates="indicators")


