"""
FastAPI Routes for CropMitra Decision-Support System.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.schemas.schemas import (
    CropRecommendRequest,
    CropRecommendResponse,
    LocationInfo,
    FertilizerRequest,
    FertilizerResponse,
    SaveRecommendationRequest,
    SaveRecommendationResponse,
    RecommendationRecordResponse
)
from backend.app.services.crop_service import crop_service
from backend.app.services.location_service import location_service
from backend.app.services.fertilizer_service import get_fertilizer_recommendation
from backend.app.database.session import get_db
from backend.app.database.models import RecommendationRecord

router = APIRouter(prefix="/api", tags=["recommendations"])

# ----------------- LOCATION APIS -----------------

@router.get("/locations/states", response_model=List[str])
def get_states():
    """Returns unique Indian States/Regions from CropDataset-Enhanced.csv."""
    return location_service.get_states()

@router.get("/locations/districts", response_model=List[str])
def get_districts(state: str = Query(..., description="Selected state name")):
    """Returns available districts for the selected state."""
    districts = location_service.get_districts(state)
    if not districts:
        return [state]
    return districts

@router.get("/locations/crops")
def get_location_crops(
    state: str = Query(..., description="Selected state"),
    district: str = Query(..., description="Selected district")
):
    """Returns crops historically registered or supported for the selected location."""
    crops = location_service.get_location_crops(state, district)
    return {
        "state": state,
        "district": district,
        "crops": crops
    }

# ----------------- CROPS & RECOMMENDATION -----------------

@router.get("/crops", response_model=List[str])
def get_crops():
    """Returns list of all available general crops for previous-crop selector."""
    return crop_service.get_available_crops()

@router.post("/recommend", response_model=CropRecommendResponse)
def recommend_crop(payload: CropRecommendRequest):
    """
    Applies Hard Location Filtering -> ML Condition Scoring -> Soil & Water Adaptation -> Crop Rotation Adjustment.
    Returns top 3 eligible recommendations.
    """
    try:
        recommendations, match_level, is_loc_supported = crop_service.recommend_crops(
            state=payload.state,
            district=payload.district,
            water_availability=payload.water_availability,
            soil_type=payload.soil_type,
            previous_crop=payload.previous_crop
        )
        return CropRecommendResponse(
            success=True,
            location=LocationInfo(
                state=payload.state,
                district=payload.district,
                match_level=match_level,
                location_supported=is_loc_supported
            ),
            recommendations=recommendations
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to process crop recommendation: {str(e)}"
        )

# ----------------- FERTILIZER API -----------------

@router.post("/fertilizer", response_model=FertilizerResponse)
def recommend_fertilizer(payload: FertilizerRequest):
    """
    Computes fertilizer guidance and nutrient recommendations based on crop and soil.
    """
    try:
        fert_plan = get_fertilizer_recommendation(
            crop=payload.crop,
            soil_type=payload.soil_type,
            nitrogen=payload.nitrogen,
            phosphorus=payload.phosphorus,
            potassium=payload.potassium
        )
        return FertilizerResponse(success=True, **fert_plan)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to process fertilizer recommendation: {str(e)}"
        )

# ----------------- DATABASE APIS -----------------

@router.post("/recommendations/save", response_model=SaveRecommendationResponse)
def save_recommendation(payload: SaveRecommendationRequest, db: Session = Depends(get_db)):
    """
    Saves a completed recommendation to the database.
    """
    try:
        record = RecommendationRecord(
            state=payload.state,
            district=payload.district,
            location_match_level=payload.location_match_level or "district",
            water_availability=payload.water_availability,
            soil_type=payload.soil_type,
            previous_crop=payload.previous_crop,
            recommended_crop=payload.recommended_crop,
            suitability_score=int(payload.final_score * 10) if payload.final_score is not None else 88,
            model_score=payload.ml_score,
            ml_score=payload.ml_score,
            final_score=payload.final_score,
            fertilizer_name=payload.fertilizer_name,
            nitrogen=payload.nitrogen,
            phosphorus=payload.phosphorus,
            potassium=payload.potassium,
            model_version="2.0.0"
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return SaveRecommendationResponse(
            success=True,
            id=record.id,
            message="Recommendation saved successfully."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save recommendation: {str(e)}"
        )

@router.get("/recommendations", response_model=List[RecommendationRecordResponse])
def list_recommendations(limit: int = 20, db: Session = Depends(get_db)):
    """
    Retrieves previous recommendations stored in the database.
    """
    try:
        records = db.query(RecommendationRecord).order_by(RecommendationRecord.created_at.desc()).limit(limit).all()
        return [
            RecommendationRecordResponse(
                id=r.id,
                state=r.state,
                district=r.district,
                location_match_level=r.location_match_level,
                water_availability=r.water_availability,
                soil_type=r.soil_type,
                previous_crop=r.previous_crop,
                recommended_crop=r.recommended_crop,
                ml_score=r.ml_score or r.model_score,
                final_score=r.final_score,
                fertilizer_name=r.fertilizer_name,
                nitrogen=r.nitrogen,
                phosphorus=r.phosphorus,
                potassium=r.potassium,
                model_version=r.model_version,
                created_at=r.created_at.isoformat() if r.created_at else None
            )
            for r in records
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recommendations: {str(e)}"
        )
