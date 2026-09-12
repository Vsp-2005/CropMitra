"""
SQLAlchemy ORM models for CropMitra.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Float
from backend.app.database.session import Base

class RecommendationRecord(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    state = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    location_match_level = Column(String(50), default="district", nullable=True)
    water_availability = Column(String(50), nullable=False)
    soil_type = Column(String(50), nullable=False)
    previous_crop = Column(String(100), nullable=False)
    recommended_crop = Column(String(100), nullable=False)
    suitability_score = Column(Integer, nullable=True)
    model_score = Column(Float, nullable=True)
    ml_score = Column(Float, nullable=True)
    final_score = Column(Float, nullable=True)
    fertilizer_name = Column(String(100), nullable=True)
    nitrogen = Column(Integer, nullable=True)
    phosphorus = Column(Integer, nullable=True)
    potassium = Column(Integer, nullable=True)
    model_version = Column(String(50), default="2.0.0", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "state": self.state,
            "district": self.district,
            "location_match_level": self.location_match_level,
            "water_availability": self.water_availability,
            "soil_type": self.soil_type,
            "previous_crop": self.previous_crop,
            "recommended_crop": self.recommended_crop,
            "suitability_score": self.suitability_score,
            "ml_score": self.ml_score or self.model_score,
            "final_score": self.final_score,
            "fertilizer_name": self.fertilizer_name,
            "nitrogen": self.nitrogen,
            "phosphorus": self.phosphorus,
            "potassium": self.potassium,
            "model_version": self.model_version,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
