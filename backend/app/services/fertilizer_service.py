"""
Fertilizer Recommendation Service for CropMitra.
Provides deterministic, explainable, and scientifically validated fertilizer recommendations
based on Crop, Soil Type, and NPK requirements.
"""
import os
import json
from typing import Dict, Any, Optional

METADATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "ml", "models", "fertilizer_meta.json")

# Standard fertilizer profiles
FERTILIZERS = {
    "Urea": {
        "full_name": "Urea (46-0-0)",
        "npk": {"n": 46, "p": 0, "k": 0},
        "description": "High-concentration Nitrogen fertilizer essential for vigorous vegetative growth, tillering, and dark green leaf canopy.",
        "guidance": "Apply in 2 to 3 split doses: 1/3 at basal stage, 1/3 during active tillering/branching, and 1/3 prior to flowering. Avoid broadcasting during high heat or before heavy rains to minimize volatilization and leaching."
    },
    "DAP": {
        "full_name": "Di-Ammonium Phosphate (18-46-0)",
        "npk": {"n": 18, "p": 46, "k": 0},
        "description": "High Phosphorus with starter Nitrogen, ideal for rapid root proliferation and seedling establishment.",
        "guidance": "Apply as a basal dose at the time of sowing or transplanting placed 3-5 cm below and to the side of seeds for maximum root uptake."
    },
    "14-35-14": {
        "full_name": "NPK Complex (14-35-14)",
        "npk": {"n": 14, "p": 35, "k": 14},
        "description": "Phosphorus-rich complete complex tailored for pulses, oilseeds, and tuber crops needing root vigor and balanced nutrition.",
        "guidance": "Apply predominantly as a basal application during final land preparation or sowing. Suitable for soils with medium potassium."
    },
    "28-28": {
        "full_name": "NPK Complex (28-28-0)",
        "npk": {"n": 28, "p": 28, "k": 0},
        "description": "High dual-nutrient blend for crops with high early vegetative and root development requirements.",
        "guidance": "Apply 50% as basal dose and 50% at 30-40 days after sowing during the peak vegetative flush."
    },
    "17-17-17": {
        "full_name": "Complete Balanced NPK (17-17-17)",
        "npk": {"n": 17, "p": 17, "k": 17},
        "description": "Equally balanced complete fertilizer ensuring uniform nutrient availability across all growth stages.",
        "guidance": "Ideal for loamy and alluvial soils. Apply half as basal dressing and remaining half in split irrigation/top-dressing intervals."
    },
    "20-20": {
        "full_name": "Ammonium Phosphate Sulphate (20-20-0-13S)",
        "npk": {"n": 20, "p": 20, "k": 0},
        "description": "Enriched with 13% active Sulphur, crucial for oilseed protein synthesis and pulse nodulation.",
        "guidance": "Apply during sowing. Sulphur component boosts oil content and leaf chlorophyll."
    },
    "10-26-26": {
        "full_name": "Potassium-Rich NPK (10-26-26)",
        "npk": {"n": 10, "p": 26, "k": 26},
        "description": "High Potassium & Phosphorus blend that reinforces disease resistance, grain filling, and drought tolerance.",
        "guidance": "Apply at basal stage and during reproductive/fruit development to ensure plump grains and sturdy stems."
    }
}

# Crop specific standard N-P-K recommendation rates (kg / acre)
CROP_NPK_RATES: Dict[str, Dict[str, int]] = {
    "rice": {"n": 48, "p": 24, "k": 24, "preferred_fert": "Urea"},
    "wheat": {"n": 48, "p": 24, "k": 16, "preferred_fert": "DAP"},
    "maize": {"n": 48, "p": 24, "k": 20, "preferred_fert": "17-17-17"},
    "soybean": {"n": 12, "p": 32, "k": 16, "preferred_fert": "14-35-14"},
    "cotton": {"n": 40, "p": 20, "k": 20, "preferred_fert": "20-20"},
    "sugarcane": {"n": 100, "p": 40, "k": 48, "preferred_fert": "Urea"},
    "chickpea": {"n": 10, "p": 25, "k": 15, "preferred_fert": "DAP"},
    "kidneybeans": {"n": 15, "p": 30, "k": 15, "preferred_fert": "14-35-14"},
    "pigeonpeas": {"n": 10, "p": 25, "k": 15, "preferred_fert": "14-35-14"},
    "mothbeans": {"n": 8, "p": 20, "k": 10, "preferred_fert": "DAP"},
    "mungbean": {"n": 8, "p": 20, "k": 10, "preferred_fert": "DAP"},
    "blackgram": {"n": 8, "p": 20, "k": 10, "preferred_fert": "20-20"},
    "lentil": {"n": 10, "p": 20, "k": 10, "preferred_fert": "DAP"},
    "pomegranate": {"n": 30, "p": 15, "k": 25, "preferred_fert": "10-26-26"},
    "banana": {"n": 80, "p": 30, "k": 90, "preferred_fert": "10-26-26"},
    "mango": {"n": 40, "p": 20, "k": 40, "preferred_fert": "17-17-17"},
    "grapes": {"n": 35, "p": 25, "k": 45, "preferred_fert": "10-26-26"},
    "watermelon": {"n": 35, "p": 20, "k": 30, "preferred_fert": "17-17-17"},
    "muskmelon": {"n": 35, "p": 20, "k": 30, "preferred_fert": "17-17-17"},
    "apple": {"n": 30, "p": 15, "k": 30, "preferred_fert": "17-17-17"},
    "orange": {"n": 35, "p": 20, "k": 25, "preferred_fert": "17-17-17"},
    "papaya": {"n": 45, "p": 30, "k": 45, "preferred_fert": "10-26-26"},
    "coconut": {"n": 50, "p": 25, "k": 75, "preferred_fert": "10-26-26"},
    "jute": {"n": 32, "p": 16, "k": 16, "preferred_fert": "Urea"},
    "coffee": {"n": 40, "p": 30, "k": 40, "preferred_fert": "17-17-17"}
}

def get_fertilizer_recommendation(
    crop: str,
    soil_type: str,
    nitrogen: Optional[int] = None,
    phosphorus: Optional[int] = None,
    potassium: Optional[int] = None
) -> Dict[str, Any]:
    """
    Computes reliable fertilizer plan with dosage and application guidelines.
    """
    crop_clean = crop.lower().strip()
    soil_clean = soil_type.lower().strip()
    
    # Get base rates for the crop
    base_rate = CROP_NPK_RATES.get(crop_clean, {"n": 35, "p": 20, "k": 20, "preferred_fert": "17-17-17"})
    
    req_n = nitrogen if (nitrogen is not None and nitrogen > 0) else base_rate["n"]
    req_p = phosphorus if (phosphorus is not None and phosphorus > 0) else base_rate["p"]
    req_k = potassium if (potassium is not None and potassium > 0) else base_rate["k"]
    
    # Soil nutrient adjustment
    if soil_clean == "sandy":
        # Sandy soils leach nitrogen and potassium; recommend split N and balanced K
        chosen_fert = "17-17-17" if req_k >= 20 else "28-28"
        explanation = f"Sandy soil requires split applications of {chosen_fert} to prevent nutrient leaching while maintaining steady nitrogen release."
    elif soil_clean in ["clay", "clayey"]:
        # Clay soils hold moisture & P well, benefit from targeted starter N or high-potassium
        chosen_fert = base_rate.get("preferred_fert", "DAP")
        explanation = f"Dense clay soil retains moisture effectively. Applying {chosen_fert} ensures immediate nutrient availability near root zones."
    elif soil_clean == "peaty":
        chosen_fert = "10-26-26"
        explanation = f"Peaty soil has high organic matter but benefits from phosphorus and potassium reinforcement like {chosen_fert}."
    else: # Loamy, Silty, Chalky
        chosen_fert = base_rate.get("preferred_fert", "17-17-17")
        explanation = f"Recommended {chosen_fert} provides the optimal N-P-K balance required by {crop.capitalize()} in {soil_type.capitalize()} soil."

    fert_details = FERTILIZERS.get(chosen_fert, FERTILIZERS["17-17-17"])
    
    return {
        "crop": crop.capitalize(),
        "soil_type": soil_type.capitalize(),
        "fertilizer_name": chosen_fert,
        "full_name": fert_details["full_name"],
        "nitrogen": req_n,
        "phosphorus": req_p,
        "potassium": req_k,
        "unit": "kg/acre",
        "explanation": explanation,
        "guidance": fert_details["guidance"],
        "npk_ratio": fert_details.get("npk_ratio", ""),
        "disclaimer": "Fertilizer requirements can vary based on soil testing, crop variety, and local conditions."
    }
