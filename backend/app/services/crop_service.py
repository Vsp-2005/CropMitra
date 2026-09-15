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
)
from backend.ml.crop_normalizer import normalize_crop_name, canonical_display_name, DISPLAY_NAMES
from backend.app.services.location_service import location_service
from backend.app.services.rotation_service import get_rotation_details

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
        """Returns sorted capitalized list of available crops for dropdowns and reference."""
        crops = sorted(list(set(DISPLAY_NAMES.values())))
        if "Other" not in crops:
            crops.append("Other")
        return crops

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
        4. Crop rotation evaluation via Rotation Service
        5. Normalized blended scoring (0.50 ML + 0.30 Condition + 0.20 Rotation)
        6. Final ranking returning top 3 eligible recommendations
        """
        water_key = water_availability.lower().strip()
        soil_key = soil_type.lower().strip()
        prev_key = previous_crop.strip()
        
        # 1. HARD LOCATION CANDIDATE FILTERING
        eligible_crop_keys, match_level, is_loc_supported = location_service.get_eligible_crops(state, district)
        
        # Debug logging
        print(f"\n[CropMitra Recommendation Pipeline]")
        print(f"Selected Location: {district}, {state}")
        print(f"Location Match Level: {match_level}")
        print(f"Previous Crop: {prev_key}")
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

            # 2. ML Condition-Based Suitability Score (Normalized 0.0 to 1.0)
            cond_sim = self._compute_condition_similarity(crop_key, n_val, p_val, k_val, ph_val, rainfall_val)
            rf_p = rf_probs.get(crop_key, 0.0)
            
            # Blend Random Forest probability (if available) with condition similarity, bounded [0.0, 1.0]
            if rf_p > 0:
                ml_score = round(min(1.0, max(0.10, (cond_sim * 0.6) + (rf_p * 2.5 * 0.4))), 4)
            else:
                ml_score = round(min(1.0, max(0.10, cond_sim)), 4)

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

            # Combined Condition Score (Normalized 0.0 to 1.0)
            condition_score = round(min(1.0, max(0.10, cond_sim * water_mult * soil_mult)), 4)

            # 5. Crop Rotation Evaluation via Rotation Service
            rot_details = get_rotation_details(prev_key, crop_key)
            rotation_score = float(rot_details.get("rotation_score", 0.50))
            rotation_comp = str(rot_details.get("compatibility", "Neutral"))
            rotation_rec = str(rot_details.get("recommendation", "Consider"))
            rotation_reason = str(rot_details.get("reason", "Standard sequence."))
            is_rot_compat = (rotation_rec != "Avoid")

            # 6. Composite Normalized Score Formula:
            # base_score = 0.50 * ml_score + 0.30 * condition_score + 0.20 * rotation_score
            base_score = (
                0.50 * ml_score
                + 0.30 * condition_score
                + 0.20 * rotation_score
            )

            # Location match modifier for ranking among eligible candidates
            loc_mult = 1.0
            if match_level == "district":
                loc_mult = 1.05
            elif match_level == "state":
                loc_mult = 1.00

            composite = base_score * loc_mult
            final_score = round(min(9.9, max(2.0, composite * 10.0)), 1)

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

            full_reason = f"{loc_text} {water_availability.capitalize()} water availability and {soil_type.capitalize()} soil support its growth. {rotation_reason}"

            scored_candidates.append({
                "crop": display_name,
                "crop_key": crop_key,
                "ml_score": round(ml_score, 2),
                "condition_score": round(condition_score, 2),
                "rotation_score": round(rotation_score, 2),
                "rotation_compatibility": rotation_comp,
                "rotation_recommendation": rotation_rec,
                "rotation_reason": rotation_reason,
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

        # Sort descending deterministically by final composite score (with crop name tiebreaker)
        scored_candidates.sort(key=lambda x: (x["final_score"], x["ml_score"], x["crop"]), reverse=True)
        
        # Take top 3 recommendations
        top_recs = scored_candidates[:3]

        print(f"Final Ranked Candidates: {[r['crop'] + ' (Score: ' + str(r['final_score']) + ', Rot: ' + str(r['rotation_score']) + ')' for r in top_recs]}")

        return top_recs, match_level, is_loc_supported

crop_service = CropService()

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("CropMitra Recommendation Service — Standalone Execution Demo")
    print("=" * 80)
    
    test_scenarios = [
        ("Maharashtra", "Kolhapur", "Medium", "Loamy", "Wheat"),
        ("Maharashtra", "Kolhapur", "Medium", "Loamy", "Sugarcane"),
        ("Maharashtra", "Kolhapur", "Medium", "Loamy", "Soybean")
    ]
    
    for st, dist, water, soil, prev in test_scenarios:
        print(f"\n--- Testing Scenario: {dist}, {st} (Water: {water}, Soil: {soil}, Previous Crop: {prev}) ---")
        recs, match_lvl, is_loc = crop_service.recommend_crops(st, dist, water, soil, prev)
        for rank, r in enumerate(recs, 1):
            print(f"  Rank #{rank}: {r['crop']:<18} | Final Score: {r['final_score']} | ML: {r['ml_score']} | Cond: {r['condition_score']} | Rot: {r['rotation_score']} ({r['rotation_compatibility']}/{r['rotation_recommendation']})")
            print(f"          Reason: {r['rotation_reason']}")
    print("\n" + "=" * 80)
    print("Execution completed successfully.")
    print("=" * 80)

