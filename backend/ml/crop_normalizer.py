"""
Centralized Crop Name Normalizer for CropMitra.
Provides canonical mapping across varying agricultural dataset terminologies.
"""
import re
from typing import Optional

CROP_SYNONYMS = {
    # Cereals
    "paddy": "rice",
    "basmati rice": "rice",
    "upland rice": "rice",
    "rice": "rice",
    "wheat": "wheat",
    "maize": "maize",
    "corn": "maize",
    "barley": "barley",
    "jowar": "jowar",
    "jowar (sorghum)": "jowar",
    "sorghum": "jowar",
    "bajra": "bajra",
    "bajra (pearl millet)": "bajra",
    "pearl millet": "bajra",
    "ragi": "ragi",
    "ragi (finger millet)": "ragi",
    "finger millet": "ragi",
    "mandua": "ragi",
    "millets": "millets",
    "millet": "millets",
    "kodo millet": "millets",
    "minor millets": "millets",

    # Pulses & Legumes
    "soybean": "soybean",
    "soyabean": "soybean",
    "chickpea": "chickpea",
    "chana": "chickpea",
    "gram": "chickpea",
    "bengal gram": "chickpea",
    "kidneybeans": "kidneybeans",
    "kidney beans": "kidneybeans",
    "rajma": "kidneybeans",
    "rajma (kidney beans)": "kidneybeans",
    "pigeonpeas": "pigeonpeas",
    "tur": "pigeonpeas",
    "tur (pigeon pea)": "pigeonpeas",
    "arhar": "pigeonpeas",
    "arhar (pigeon pea)": "pigeonpeas",
    "red gram": "pigeonpeas",
    "red gram (tur)": "pigeonpeas",
    "mothbeans": "mothbeans",
    "moth beans": "mothbeans",
    "mungbean": "mungbean",
    "mung bean": "mungbean",
    "moong": "mungbean",
    "green gram": "mungbean",
    "blackgram": "blackgram",
    "black gram": "blackgram",
    "urad": "blackgram",
    "lentil": "lentil",
    "lentils": "lentil",
    "lentil (masoor)": "lentil",
    "masoor": "lentil",
    "pulses": "pulses",
    "pea": "pulses",
    "peas": "pulses",

    # Commercial & Plantation
    "cotton": "cotton",
    "sugarcane": "sugarcane",
    "jute": "jute",
    "coffee": "coffee",
    "tea": "tea",
    "rubber": "rubber",
    "tobacco": "tobacco",

    # Oilseeds
    "groundnut": "groundnut",
    "peanut": "groundnut",
    "mustard": "mustard",
    "sunflower": "sunflower",
    "sesame": "sesame",
    "linseed": "linseed",
    "castor": "castor",
    "niger": "oilseeds",
    "oilseeds": "oilseeds",

    # Horticulture, Vegetables & Spices
    "pomegranate": "pomegranate",
    "banana": "banana",
    "mango": "mango",
    "grapes": "grapes",
    "grape": "grapes",
    "watermelon": "watermelon",
    "muskmelon": "muskmelon",
    "apple": "apple",
    "apples": "apple",
    "orange": "orange",
    "oranges": "orange",
    "citrus": "orange",
    "papaya": "papaya",
    "coconut": "coconut",
    "guava": "guava",
    "cashew": "cashew",
    "onion": "onion",
    "potato": "potato",
    "potatoes": "potato",
    "tomato": "tomato",
    "tomatoes": "tomato",
    "garlic": "garlic",
    "ginger": "ginger",
    "turmeric": "turmeric",
    "chilli": "chilli",
    "chillies": "chilli",
    "coriander": "spices",
    "cumin": "spices",
    "cardamom": "spices",
    "pepper": "spices",
    "spices": "spices",
    "vegetables": "vegetables",
    "seasonal vegetables": "vegetables"
}

DISPLAY_NAMES = {
    "rice": "Rice",
    "wheat": "Wheat",
    "maize": "Maize",
    "soybean": "Soybean",
    "cotton": "Cotton",
    "sugarcane": "Sugarcane",
    "chickpea": "Chickpea",
    "kidneybeans": "Kidney Beans",
    "pigeonpeas": "Pigeon Peas (Tur)",
    "mothbeans": "Moth Beans",
    "mungbean": "Mung Bean",
    "blackgram": "Black Gram (Urad)",
    "lentil": "Lentil (Masoor)",
    "pomegranate": "Pomegranate",
    "banana": "Banana",
    "mango": "Mango",
    "grapes": "Grapes",
    "watermelon": "Watermelon",
    "muskmelon": "Muskmelon",
    "apple": "Apple",
    "orange": "Orange",
    "papaya": "Papaya",
    "coconut": "Coconut",
    "jute": "Jute",
    "coffee": "Coffee",
    "jowar": "Jowar (Sorghum)",
    "bajra": "Bajra (Pearl Millet)",
    "groundnut": "Groundnut",
    "mustard": "Mustard",
    "pulses": "Pulses",
    "ragi": "Ragi",
    "millets": "Millets",
    "sunflower": "Sunflower",
    "sesame": "Sesame",
    "linseed": "Linseed",
    "castor": "Castor",
    "oilseeds": "Oilseeds",
    "rubber": "Rubber",
    "tea": "Tea",
    "tobacco": "Tobacco",
    "onion": "Onion",
    "potato": "Potato",
    "tomato": "Tomato",
    "garlic": "Garlic",
    "ginger": "Ginger",
    "turmeric": "Turmeric",
    "chilli": "Chilli",
    "spices": "Spices",
    "guava": "Guava",
    "cashew": "Cashew",
    "vegetables": "Vegetables"
}

def normalize_crop_name(name: str) -> str:
    """
    Cleans, strips punctuation, and maps a raw crop string to a canonical lower-case key.
    Uses exact lookup and word-boundary regex matching to avoid substring false positives.
    """
    if not name:
        return ""
    clean = name.strip().lower()
    # Remove leading 'and ' if split from text
    clean = re.sub(r"^and\s+", "", clean).strip()
    # Remove surrounding punctuation
    clean = clean.strip(".\u200b\"'()[]").strip()
    
    # 1. Exact match
    if clean in CROP_SYNONYMS:
        return CROP_SYNONYMS[clean]
        
    # Check normalized with parenthetical content
    clean_no_paren = re.sub(r"\(.*?\)", "", clean).strip()
    if clean_no_paren in CROP_SYNONYMS:
        return CROP_SYNONYMS[clean_no_paren]
    
    # 2. Check multi-word phrase contains (sorted by longest synonym key first)
    for syn_key in sorted(CROP_SYNONYMS.keys(), key=len, reverse=True):
        if len(syn_key) >= 3 and re.search(r'\b' + re.escape(syn_key) + r'\b', clean):
            return CROP_SYNONYMS[syn_key]
            
    return clean

def canonical_display_name(name: str) -> str:
    """Returns the user-friendly capitalized display name."""
    norm = normalize_crop_name(name)
    return DISPLAY_NAMES.get(norm, name.strip().title())
