"""
Pydantic validation schemas for CropMitra API.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator

VALID_WATER_LEVELS = {"low", "medium", "high"}
VALID_SOIL_TYPES = {"sandy", "clay", "clayey", "loamy", "silty", "peaty", "chalky"}

class LocationInfo(BaseModel):
    state: str
    district: str
    match_level: str = "district"
    location_supported: bool = True

class CropRecommendRequest(BaseModel):
    state: str = Field(..., description="Indian State/Region from dataset")
    district: str = Field(..., description="District/Location name")
    water_availability: str = Field(..., description="Field water availability: Low, Medium, High")
    soil_type: str = Field(..., description="Soil type: Sandy, Clay, Loamy, Silty, Peaty, Chalky")
    previous_crop: str = Field(..., description="Previously harvested crop on this plot")

    @field_validator("state")
    @classmethod
    def validate_state(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("State cannot be empty.")
        return clean

    @field_validator("district")
    @classmethod
    def validate_district(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("District cannot be empty.")
        return clean

    @field_validator("water_availability")
    @classmethod
    def validate_water(cls, v: str) -> str:
        clean = v.strip().lower()
        if clean not in VALID_WATER_LEVELS:
            raise ValueError(f"Invalid water availability '{v}'. Must be one of: Low, Medium, High.")
        return v.strip().capitalize()

    @field_validator("soil_type")
    @classmethod
    def validate_soil(cls, v: str) -> str:
        clean = v.strip().lower()
        if clean not in VALID_SOIL_TYPES:
            raise ValueError(f"Invalid soil type '{v}'. Must be one of: Sandy, Clay, Loamy, Silty, Peaty, Chalky.")
        return v.strip().capitalize()

    @field_validator("previous_crop")
    @classmethod
    def validate_prev_crop(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Previous crop cannot be empty.")
        return clean

class CropRecommendationDetail(BaseModel):
    crop: str
    ml_score: float
    final_score: float
    suitability: str
    location_supported: bool = True
    water_compatibility: str = "Good"
    soil_compatibility: str = "Good"
    rotation_compatible: bool = True
    water_requirement: str
    soil_type: str
    previous_crop: str
    growing_season: Optional[str] = None
    crop_type: Optional[str] = None
    reason: str
    baseline_npk: Optional[Dict[str, int]] = None

class CropRecommendResponse(BaseModel):
    success: bool = True
    location: LocationInfo
    recommendations: List[CropRecommendationDetail]

class FertilizerRequest(BaseModel):
    crop: str = Field(..., description="Target crop name")
    soil_type: str = Field(..., description="Soil type")
    nitrogen: Optional[int] = Field(None, ge=0, description="Nitrogen level in kg/acre (>= 0)")
    phosphorus: Optional[int] = Field(None, ge=0, description="Phosphorus level in kg/acre (>= 0)")
    potassium: Optional[int] = Field(None, ge=0, description="Potassium level in kg/acre (>= 0)")

    @field_validator("crop")
    @classmethod
    def validate_crop_name(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Crop name cannot be empty.")
        return clean

    @field_validator("soil_type")
    @classmethod
    def validate_fert_soil(cls, v: str) -> str:
        clean = v.strip().lower()
        if clean not in VALID_SOIL_TYPES:
            raise ValueError(f"Invalid soil type '{v}'. Must be one of: Sandy, Clay, Loamy, Silty, Peaty, Chalky.")
        return v.strip().capitalize()

class FertilizerResponse(BaseModel):
    success: bool = True
    crop: str
    soil_type: str
    fertilizer_name: str
    full_name: str
    nitrogen: int
    phosphorus: int
    potassium: int
    unit: str = "kg/acre"
    npk_ratio: str
    explanation: str
    guidance: str
    disclaimer: str

class SaveRecommendationRequest(BaseModel):
    state: Optional[str] = None
    district: Optional[str] = None
    location_match_level: Optional[str] = "district"
    water_availability: str
    soil_type: str
    previous_crop: str
    recommended_crop: str
    ml_score: Optional[float] = None
    final_score: Optional[float] = None
    fertilizer_name: Optional[str] = None
    nitrogen: Optional[int] = None
    phosphorus: Optional[int] = None
    potassium: Optional[int] = None

class RecommendationRecordResponse(BaseModel):
    id: int
    state: Optional[str] = None
    district: Optional[str] = None
    location_match_level: Optional[str] = "district"
    water_availability: str
    soil_type: str
    previous_crop: str
    recommended_crop: str
    ml_score: Optional[float] = None
    final_score: Optional[float] = None
    fertilizer_name: Optional[str] = None
    nitrogen: Optional[int] = None
    phosphorus: Optional[int] = None
    potassium: Optional[int] = None
    model_version: str = "2.0.0"
    created_at: Optional[str] = None

class SaveRecommendationResponse(BaseModel):
    success: bool = True
    id: int
    message: str
