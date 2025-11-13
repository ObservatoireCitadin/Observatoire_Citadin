from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    insee_code = Column(String(50), nullable=False, unique=True, index=True)

    indicators = relationship("Indicator", back_populates="city", cascade="all, delete-orphan")


