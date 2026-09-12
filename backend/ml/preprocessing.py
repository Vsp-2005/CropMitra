"""
Preprocessing and Agronomic Knowledge Module for CropMitra.

Provides:
- Mapping from user field inputs (Soil Type, Water Availability) to scientific ranges.
- Agronomic crop rotation scoring matrix.
- Crop metadata definitions for all candidate crops in the national registry.
"""
from typing import Dict, Any, List, Tuple
import numpy as np

# Soil characteristics profile based on agronomic standards
SOIL_PROFILES: Dict[str, Dict[str, Any]] = {
    "sandy": {
        "ph": 6.2,
        "n_range": (30, 60),
        "p_range": (20, 40),
        "k_range": (20, 40),
        "typical_fert_soil": "Sandy",
        "description": "Well-drained, light texture with lower nutrient and water retention."
    },
    "clay": {
        "ph": 7.0,
        "n_range": (70, 110),
        "p_range": (45, 75),
        "k_range": (35, 60),
        "typical_fert_soil": "Clayey",
        "description": "Dense, heavy soil with high water retention and rich nutrient capacity."
    },
    "loamy": {
        "ph": 6.6,
        "n_range": (60, 95),
        "p_range": (40, 65),
        "k_range": (35, 55),
        "typical_fert_soil": "Loamy",
        "description": "Balanced texture with optimal drainage, aeration, and nutrient availability."
    },
    "silty": {
        "ph": 6.5,
        "n_range": (55, 85),
        "p_range": (35, 60),
        "k_range": (30, 50),
        "typical_fert_soil": "Loamy",
        "description": "Fertile, fine-grained soil with good water retention and smooth texture."
    },
    "peaty": {
        "ph": 5.4,
        "n_range": (45, 75),
        "p_range": (25, 45),
        "k_range": (25, 45),
        "typical_fert_soil": "Red",
        "description": "High organic matter content, naturally acidic with high moisture capacity."
    },
    "chalky": {
        "ph": 7.8,
        "n_range": (35, 65),
        "p_range": (30, 55),
        "k_range": (30, 50),
        "typical_fert_soil": "Sandy",
        "description": "Alkaline, free-draining soil often containing calcium carbonate."
    }
}

# Water availability profile mapping to rainfall (mm) and humidity (%)
WATER_PROFILES: Dict[str, Dict[str, Any]] = {
    "low": {
        "rainfall_range": (35.0, 75.0),
        "humidity_range": (40.0, 60.0),
        "description": "Arid or rain-fed dry conditions; best for drought-tolerant crops."
    },
    "medium": {
        "rainfall_range": (75.0, 150.0),
        "humidity_range": (60.0, 75.0),
        "description": "Moderate rainfall or standard canal/borewell irrigation."
    },
    "high": {
        "rainfall_range": (150.0, 260.0),
        "humidity_range": (75.0, 90.0),
        "description": "High rainfall or abundant water supply; ideal for wetland/paddy crops."
    }
}

# Comprehensive Crop Metadata and Ideal Condition Benchmarks
CROP_METADATA: Dict[str, Dict[str, Any]] = {
    "rice": {"water": "High", "soil": "Clay, Loamy", "season": "Kharif (Monsoon)", "type": "Cereal", "ideal_n": 80, "ideal_p": 45, "ideal_k": 40, "ideal_ph": 6.5, "ideal_rain": 200},
    "wheat": {"water": "Medium", "soil": "Loamy, Clay", "season": "Rabi (Winter)", "type": "Cereal", "ideal_n": 75, "ideal_p": 40, "ideal_k": 35, "ideal_ph": 6.8, "ideal_rain": 90},
    "maize": {"water": "Medium", "soil": "Loamy, Sandy", "season": "Kharif / Rabi", "type": "Cereal", "ideal_n": 75, "ideal_p": 45, "ideal_k": 20, "ideal_ph": 6.5, "ideal_rain": 110},
    "soybean": {"water": "Medium", "soil": "Loamy, Clay", "season": "Kharif", "type": "Legume / Oilseed", "ideal_n": 35, "ideal_p": 50, "ideal_k": 30, "ideal_ph": 6.6, "ideal_rain": 100},
    "cotton": {"water": "Medium", "soil": "Black, Clay, Loamy", "season": "Kharif", "type": "Fiber / Cash Crop", "ideal_n": 115, "ideal_p": 45, "ideal_k": 20, "ideal_ph": 7.0, "ideal_rain": 80},
    "sugarcane": {"water": "High", "soil": "Loamy, Clay", "season": "Annual (10-12 months)", "type": "Cash Crop", "ideal_n": 95, "ideal_p": 55, "ideal_k": 45, "ideal_ph": 6.8, "ideal_rain": 180},
    "jowar": {"water": "Low to Medium", "soil": "Loamy, Clay, Sandy", "season": "Kharif / Rabi", "type": "Cereal / Millet", "ideal_n": 50, "ideal_p": 30, "ideal_k": 25, "ideal_ph": 6.7, "ideal_rain": 65},
    "bajra": {"water": "Low", "soil": "Sandy, Loamy", "season": "Kharif", "type": "Cereal / Millet", "ideal_n": 45, "ideal_p": 25, "ideal_k": 25, "ideal_ph": 7.0, "ideal_rain": 50},
    "groundnut": {"water": "Low to Medium", "soil": "Sandy, Loamy", "season": "Kharif / Summer", "type": "Legume / Oilseed", "ideal_n": 30, "ideal_p": 45, "ideal_k": 35, "ideal_ph": 6.4, "ideal_rain": 70},
    "pigeonpeas": {"water": "Low to Medium", "soil": "Loamy, Sandy, Clay", "season": "Kharif", "type": "Legume / Pulse", "ideal_n": 25, "ideal_p": 65, "ideal_k": 20, "ideal_ph": 6.5, "ideal_rain": 75},
    "chickpea": {"water": "Low", "soil": "Loamy, Clay", "season": "Rabi (Winter)", "type": "Legume / Pulse", "ideal_n": 40, "ideal_p": 65, "ideal_k": 80, "ideal_ph": 7.2, "ideal_rain": 65},
    "kidneybeans": {"water": "Medium", "soil": "Loamy, Sandy", "season": "Kharif", "type": "Legume / Pulse", "ideal_n": 20, "ideal_p": 60, "ideal_k": 20, "ideal_ph": 5.8, "ideal_rain": 110},
    "mothbeans": {"water": "Low", "soil": "Sandy, Loamy", "season": "Kharif", "type": "Legume / Pulse", "ideal_n": 20, "ideal_p": 45, "ideal_k": 20, "ideal_ph": 6.8, "ideal_rain": 45},
    "mungbean": {"water": "Low to Medium", "soil": "Loamy, Sandy", "season": "Kharif / Summer", "type": "Legume / Pulse", "ideal_n": 20, "ideal_p": 45, "ideal_k": 20, "ideal_ph": 6.7, "ideal_rain": 55},
    "blackgram": {"water": "Medium", "soil": "Loamy, Clay", "season": "Kharif / Summer", "type": "Legume / Pulse", "ideal_n": 40, "ideal_p": 65, "ideal_k": 20, "ideal_ph": 7.0, "ideal_rain": 65},
    "lentil": {"water": "Low", "soil": "Loamy, Clay", "season": "Rabi", "type": "Legume / Pulse", "ideal_n": 20, "ideal_p": 65, "ideal_k": 20, "ideal_ph": 6.9, "ideal_rain": 50},
    "mustard": {"water": "Low to Medium", "soil": "Loamy, Sandy", "season": "Rabi", "type": "Oilseed", "ideal_n": 50, "ideal_p": 35, "ideal_k": 30, "ideal_ph": 6.8, "ideal_rain": 60},
    "onion": {"water": "Medium", "soil": "Loamy, Sandy", "season": "Rabi / Kharif", "type": "Vegetable", "ideal_n": 60, "ideal_p": 40, "ideal_k": 40, "ideal_ph": 6.5, "ideal_rain": 85},
    "potato": {"water": "Medium", "soil": "Loamy, Sandy", "season": "Rabi", "type": "Tuber / Vegetable", "ideal_n": 65, "ideal_p": 50, "ideal_k": 45, "ideal_ph": 5.8, "ideal_rain": 90},
    "pomegranate": {"water": "Low to Medium", "soil": "Loamy, Sandy", "season": "Perennial / Annual", "type": "Horticulture", "ideal_n": 20, "ideal_p": 20, "ideal_k": 40, "ideal_ph": 6.8, "ideal_rain": 105},
    "banana": {"water": "High", "soil": "Loamy, Clay", "season": "Year-round", "type": "Horticulture", "ideal_n": 100, "ideal_p": 75, "ideal_k": 50, "ideal_ph": 6.0, "ideal_rain": 180},
    "mango": {"water": "Low to Medium", "soil": "Loamy, Sandy, Alluvial", "season": "Perennial", "type": "Horticulture", "ideal_n": 20, "ideal_p": 25, "ideal_k": 30, "ideal_ph": 6.0, "ideal_rain": 95},
    "grapes": {"water": "Medium", "soil": "Sandy, Loamy", "season": "Annual / Pruning cycle", "type": "Horticulture", "ideal_n": 25, "ideal_p": 130, "ideal_k": 200, "ideal_ph": 6.0, "ideal_rain": 70},
    "watermelon": {"water": "Medium", "soil": "Sandy, Loamy", "season": "Zaid (Summer)", "type": "Cucurbit", "ideal_n": 100, "ideal_p": 20, "ideal_k": 50, "ideal_ph": 6.5, "ideal_rain": 50},
    "muskmelon": {"water": "Medium", "soil": "Sandy, Loamy", "season": "Zaid (Summer)", "type": "Cucurbit", "ideal_n": 100, "ideal_p": 20, "ideal_k": 50, "ideal_ph": 6.3, "ideal_rain": 25},
    "apple": {"water": "Medium", "soil": "Loamy, Clay", "season": "Temperate perennial", "type": "Horticulture", "ideal_n": 20, "ideal_p": 135, "ideal_k": 200, "ideal_ph": 6.0, "ideal_rain": 110},
    "orange": {"water": "Medium", "soil": "Loamy, Sandy", "season": "Perennial", "type": "Horticulture", "ideal_n": 20, "ideal_p": 15, "ideal_k": 10, "ideal_ph": 7.0, "ideal_rain": 110},
    "papaya": {"water": "Medium to High", "soil": "Loamy, Sandy", "season": "Year-round", "type": "Horticulture", "ideal_n": 50, "ideal_p": 60, "ideal_k": 50, "ideal_ph": 6.7, "ideal_rain": 140},
    "coconut": {"water": "High", "soil": "Sandy, Loamy, Coastal", "season": "Perennial", "type": "Plantation", "ideal_n": 20, "ideal_p": 15, "ideal_k": 30, "ideal_ph": 6.0, "ideal_rain": 175},
    "cotton": {"water": "Medium", "soil": "Black, Clay, Loamy", "season": "Kharif", "type": "Fiber / Cash Crop", "ideal_n": 115, "ideal_p": 45, "ideal_k": 20, "ideal_ph": 7.0, "ideal_rain": 80},
    "jute": {"water": "High", "soil": "Clay, Loamy, Alluvial", "season": "Kharif", "type": "Fiber / Cash Crop", "ideal_n": 80, "ideal_p": 45, "ideal_k": 40, "ideal_ph": 6.7, "ideal_rain": 175},
    "coffee": {"water": "High", "soil": "Loamy, Peaty, Red", "season": "Perennial Plantation", "type": "Plantation", "ideal_n": 100, "ideal_p": 30, "ideal_k": 30, "ideal_ph": 6.8, "ideal_rain": 160},
    "vegetables": {"water": "Medium", "soil": "Loamy, Sandy", "season": "Seasonal", "type": "Horticulture", "ideal_n": 60, "ideal_p": 40, "ideal_k": 35, "ideal_ph": 6.5, "ideal_rain": 90}
}

# Crop rotation compatibility matrix
ROTATION_RULES = {
    "cereal": {
        "legume": 1.25,     # Cereals followed by nitrogen-fixing legumes restore soil health
        "cereal": 0.80,     # Repeating cereals depletes specific nutrients and increases weed/pest pressure
        "fiber": 1.0,
        "cash": 0.95
    },
    "legume": {
        "cereal": 1.25,     # Legumes leave residual nitrogen beneficial for cereals like Wheat, Rice, Maize, Jowar
        "legume": 0.85,     # Consecutive legumes increase root rot/fusarium risks
        "fiber": 1.10,
        "cash": 1.05
    },
    "fiber": {
        "legume": 1.20,     # Fiber (cotton) followed by pulses aids soil restoration
        "cereal": 1.05,
        "fiber": 0.75      # Monocropping cotton promotes bollworm & wilt accumulation
    },
    "cash": {
        "legume": 1.20,
        "cereal": 1.05,
        "cash": 0.80
    }
}

def get_crop_category(crop_name: str) -> str:
    """Classifies a crop into broad agronomic category for rotation rules."""
    c = crop_name.lower().strip()
    if c in ["rice", "wheat", "maize", "corn", "barley", "millets", "jowar", "bajra"]:
        return "cereal"
    if c in ["soybean", "pulses", "chickpea", "kidneybeans", "pigeonpeas", "mothbeans", "mungbean", "blackgram", "lentil", "groundnut"]:
        return "legume"
    if c in ["cotton", "jute"]:
        return "fiber"
    if c in ["sugarcane", "tobacco", "coffee", "tea"]:
        return "cash"
    return "other"

def calculate_rotation_modifier(previous_crop: str, candidate_crop: str) -> Tuple[float, str, bool]:
    """
    Calculates agronomic rotation multiplier, explanation, and boolean compatibility flag.
    """
    prev_cat = get_crop_category(previous_crop)
    cand_cat = get_crop_category(candidate_crop)
    
    if prev_cat == "other" or cand_cat == "other":
        return 1.0, f"Compatible crop rotation following {previous_crop}.", True
    
    multiplier = ROTATION_RULES.get(prev_cat, {}).get(cand_cat, 1.0)
    is_compatible = multiplier >= 0.90
    
    if prev_cat == "cereal" and cand_cat == "legume":
        reason = f"Excellent rotation: planting legume {candidate_crop} after cereal {previous_crop} replenishes soil nitrogen."
    elif prev_cat == "legume" and cand_cat == "cereal":
        reason = f"Optimal succession: {candidate_crop} benefits from the residual nitrogen fixed by preceding {previous_crop}."
    elif prev_cat == cand_cat and prev_cat in ["cereal", "fiber"]:
        reason = f"Repeating {candidate_crop} consecutively after {previous_crop} carries a minor rotation penalty to prevent pest accumulation."
    elif prev_cat == "fiber" and cand_cat == "legume":
        reason = f"Ideal restorative rotation: {candidate_crop} restores soil organic structure after {previous_crop}."
    else:
        reason = f"Agronomically compatible crop rotation following {previous_crop}."
        
    return multiplier, reason, is_compatible
