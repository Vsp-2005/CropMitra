"""
Crop Recommendation Service for CropMitra.
Enforces Location-Supported Crops as a hard eligibility constraint,
followed by ML condition scoring, soil/water adaptation, and crop rotation adjustments.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
import joblib

from backend.ml.preprocessing import (
    SOIL_PROFILES,
    WATER_PROFILES,
    CROP_METADATA,
    calculate_rotation_modifier
)
from backend.ml.crop_normalizer import normalize_crop_name, canonical_display_name
from backend.app.services.location_service import location_service

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "ml", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "crop_model.joblib")
METADATA_PATH = os.path.join(MODEL_DIR, "crop_model_meta.json")

logger = logging.getLogger("cropmitra.crop_service")

class CropService:
    def __init__(self):
        self.model = None
        self.metadata = {}
        self.all_crops = []
        self._load_model()
        
    def _load_model(self):
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                if os.path.exists(METADATA_PATH):
                    with open(METADATA_PATH, "r") as f:
                        self.metadata = json.load(f)
                self.all_crops = self.metadata.get("all_crops", [])
                print(f"Crop model loaded successfully with {len(self.all_crops)} crop classes.")
            except Exception as e:
                print(f"Error loading crop model: {e}")
                self.model = None
        else:
            print(f"Crop model not found at {MODEL_PATH}")

    def get_available_crops(self) -> List[str]:
        """Returns capitalized list of available crops for dropdowns and reference."""
        standard_list = [
            "Rice", "Wheat", "Maize", "Soybean", "Cotton", "Sugarcane", 
            "Chickpea", "Kidney Beans", "Pigeon Peas (Tur)", "Moth Beans", "Mung Bean", 
            "Black Gram (Urad)", "Lentil (Masoor)", "Pomegranate", "Banana", "Mango", 
            "Grapes", "Watermelon", "Muskmelon", "Apple", "Orange", 
            "Papaya", "Coconut", "Jute", "Coffee", "Jowar (Sorghum)", "Bajra (Pearl Millet)",
            "Groundnut", "Mustard", "Pulses", "Vegetables", "Other", "Unknown"
        ]
        return standard_list

    def _compute_condition_similarity(
        self,
        crop_key: str,
        n_val: float,
        p_val: float,
        k_val: float,
        ph_val: float,
        rainfall_val: float
    ) -> float:
        """
        Computes agricultural condition compatibility score (0.0 to 1.0)
        between field parameters and crop agronomic profile.
        """
        meta = CROP_METADATA.get(crop_key, {})
        if not meta:
            return 0.65

        ideal_n = meta.get("ideal_n", 60)
        ideal_p = meta.get("ideal_p", 40)
        ideal_k = meta.get("ideal_k", 35)
        ideal_ph = meta.get("ideal_ph", 6.5)
        ideal_rain = meta.get("ideal_rain", 100)

        # Normalized Gaussian similarity distances
        diff_n = ((n_val - ideal_n) / 60.0) ** 2
        diff_p = ((p_val - ideal_p) / 40.0) ** 2
        diff_k = ((k_val - ideal_k) / 40.0) ** 2
        diff_ph = ((ph_val - ideal_ph) / 1.5) ** 2
        diff_rain = ((rainfall_val - ideal_rain) / 100.0) ** 2

        dist = (diff_n + diff_p + diff_k + diff_ph + diff_rain) / 5.0
        similarity = float(np.exp(-0.75 * dist))
        return round(float(similarity), 4)

    def recommend_crops(
        self,
        state: str,
        district: str,
        water_availability: str,
        soil_type: str,
        previous_crop: str
    ) -> Tuple[List[Dict[str, Any]], str, bool]:
        """
        Executes:
        1. Hard Location Candidate Filtering (from CropDataset-Enhanced.csv)
        2. ML condition prediction & scoring on eligible crops
        3. Water & Soil compatibility evaluation
        4. Crop rotation adjustment
        5. Final ranking returning top 3 eligible recommendations
        """
        water_key = water_availability.lower().strip()
        soil_key = soil_type.lower().strip()
        prev_key = previous_crop.lower().strip()
        
        # 1. HARD LOCATION CANDIDATE FILTERING
        eligible_crop_keys, match_level, is_loc_supported = location_service.get_eligible_crops(state, district)
        
        # Debug logging
        print(f"\n[CropMitra Recommendation Pipeline]")
        print(f"Selected Location: {district}, {state}")
        print(f"Location Match Level: {match_level}")
        print(f"Location-Supported Eligible Crops ({len(eligible_crop_keys)}): {eligible_crop_keys}")

        soil_prof = SOIL_PROFILES.get(soil_key, SOIL_PROFILES["loamy"])
        water_prof = WATER_PROFILES.get(water_key, WATER_PROFILES["medium"])
        
        n_val = float(np.mean(soil_prof["n_range"]))
        p_val = float(np.mean(soil_prof["p_range"]))
        k_val = float(np.mean(soil_prof["k_range"]))
        ph_val = float(soil_prof["ph"])
        rainfall_val = float(np.mean(water_prof["rainfall_range"]))
        humidity_val = float(np.mean(water_prof["humidity_range"]))
        temp_val = 26.5
        
        # Base Random Forest probability distribution
        rf_probs = {}
        if self.model is not None:
            features_df = pd.DataFrame([[n_val, p_val, k_val, temp_val, humidity_val, ph_val, rainfall_val]], 
                                       columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])
            classes = self.model.classes_
            raw_proba = self.model.predict_proba(features_df)[0]
            for c_name, p in zip(classes, raw_proba):
                rf_probs[str(c_name).lower()] = float(p)

        scored_candidates = []
        for crop_key in eligible_crop_keys:
            crop_meta = CROP_METADATA.get(crop_key, {})
            display_name = canonical_display_name(crop_key)

            # 2. ML Condition-Based Suitability Score (0.0 to 1.0)
            cond_sim = self._compute_condition_similarity(crop_key, n_val, p_val, k_val, ph_val, rainfall_val)
            rf_p = rf_probs.get(crop_key, 0.0)
            
            # Blend Random Forest probability (if available) with empirical condition similarity
            if rf_p > 0:
                ml_score = round(min(0.98, max(0.50, (cond_sim * 0.6) + (rf_p * 2.5 * 0.4))), 2)
            else:
                ml_score = round(min(0.96, max(0.50, cond_sim)), 2)

            # 3. Water Compatibility Check
            water_req = crop_meta.get("water", "Medium").lower()
            water_comp = "Good"
            water_mult = 1.0
            if "high" in water_key and "low" in water_req:
                water_mult = 0.65
                water_comp = "Moderate (Excess water)"
            elif "low" in water_key and "high" in water_req:
                water_mult = 0.35
                water_comp = "Poor (Requires more irrigation)"
            elif "medium" in water_key and "high" in water_req:
                water_mult = 0.88
                water_comp = "Fair (Adequate irrigation needed)"

            # 4. Soil Compatibility Check
            soil_suitable_list = crop_meta.get("soil", "").lower()
            soil_comp = "Good"
            soil_mult = 1.0
            if soil_key not in soil_suitable_list and soil_suitable_list:
                soil_comp = "Moderate"
                soil_mult = 0.88

            # 5. Crop Rotation Adjustment
            rot_mult, rot_reason, is_rot_compat = calculate_rotation_modifier(prev_key, crop_key)

            # Location match modifier
            loc_mult = 1.0
            if match_level == "district":
                loc_mult = 1.15
            elif match_level == "state":
                loc_mult = 1.05

            # Compute Final Scaled Score (0.0 to 10.0 scale)
            composite = ml_score * water_mult * soil_mult * rot_mult * loc_mult * 10.0
            final_score = round(min(9.8, max(3.0, composite)), 1)

            # Determine Suitability Tier
            if final_score >= 7.8:
                suitability = "High"
            elif final_score >= 5.5:
                suitability = "Medium"
            else:
                suitability = "Low"

            # Formulate explainable justification
            loc_text = ""
            if match_level == "district":
                loc_text = f"{display_name} is listed among the crops supported for {district} in the CropMitra location dataset and is compatible with the selected field conditions."
            elif match_level == "state":
                loc_text = f"{display_name} is widely cultivated across {state} and aligns with your field conditions."
            else:
                loc_text = f"{display_name} is agronomically suitable for the specified field conditions."

            full_reason = f"{loc_text} {water_availability.capitalize()} water availability and {soil_type.capitalize()} soil support its growth. {rot_reason}"

            scored_candidates.append({
                "crop": display_name,
                "crop_key": crop_key,
                "ml_score": ml_score,
                "final_score": final_score,
                "suitability": suitability,
                "location_supported": is_loc_supported,
                "water_compatibility": water_comp,
                "soil_compatibility": soil_comp,
                "rotation_compatible": is_rot_compat,
                "water_requirement": crop_meta.get("water", water_availability.capitalize()),
                "soil_type": soil_type.capitalize(),
                "previous_crop": previous_crop.capitalize(),
                "growing_season": crop_meta.get("season", "Kharif / Rabi"),
                "crop_type": crop_meta.get("type", "Field Crop"),
                "reason": full_reason,
                "baseline_npk": {
                    "n": int(crop_meta.get("ideal_n", n_val)),
                    "p": int(crop_meta.get("ideal_p", p_val)),
                    "k": int(crop_meta.get("ideal_k", k_val))
                }
            })

        # Sort descending by final composite score
        scored_candidates.sort(key=lambda x: x["final_score"], reverse=True)
        
        # Take top 3 recommendations
        top_recs = scored_candidates[:3]

        print(f"Final Ranked Candidates: {[r['crop'] + ' (' + str(r['final_score']) + ')' for r in top_recs]}")

        return top_recs, match_level, is_loc_supported

crop_service = CropService()
