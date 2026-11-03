from datetime import date, datetime, timezone
from typing import Optional
from sqlalchemy import Integer, String, Text, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class CaseModel(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    reporter_type: Mapped[str] = mapped_column(String(50), nullable=False)
    suspected_drug: Mapped[str] = mapped_column(String(200), nullable=False)
    reaction_description: Mapped[str] = mapped_column(Text, nullable=False)

    patient_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    patient_sex: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    drug_start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    reaction_start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    outcome: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    status: Mapped[str] = mapped_column(String(50), default="submitted", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

