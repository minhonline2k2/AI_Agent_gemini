"""
models/rca.py - Bang rca_results (ket qua phan tich AI)
Moi incident co the co nhieu vong phan tich (round)
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Float, Boolean, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database import Base


class RCAResult(Base):
    __tablename__ = "rca_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), index=True)
    round_number = Column(Integer, default=1)                # Vong P->R->A->O thu may
    perceive_context = Column(JSONB)                         # Context thu thap duoc
    gemini_prompt = Column(Text)                             # Prompt gui cho Gemini
    gemini_response_raw = Column(Text)                       # Response goc tu Gemini
    executive_summary = Column(Text)                         # Tom tat
    probable_cause = Column(Text)                            # Nguyen nhan co the
    confidence = Column(Float, default=0.0)                  # Do tin cay 0.0 - 1.0
    missing_context = Column(JSONB, default=list)            # Thong tin con thieu
    next_checks = Column(JSONB, default=list)                # Buoc kiem tra tiep theo
    override_applied = Column(Boolean, default=False)        # Co bi override khong
    override_reason = Column(Text)                           # Ly do override
    override_details = Column(JSONB)                         # Chi tiet override
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
