"""
Crop Rotation Dataset Generator and Validator for CropMitra.
Generates an authoritative multi-sheet Excel workbook (crop_rotation_dataset.xlsx)
and runtime CSV matrix (crop_rotation_matrix.csv) from canonical CropMitra crop vocabulary.
"""
import os
import re
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from typing import Dict, Any, List, Tuple

from backend.ml.crop_normalizer import DISPLAY_NAMES, normalize_crop_name, canonical_display_name

# Target file paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
XLSX_PATH = os.path.join(DATA_DIR, "crop_rotation_dataset.xlsx")
CSV_PATH = os.path.join(DATA_DIR, "crop_rotation_matrix.csv")

# 1. Structured Crop Characteristics Dictionary
CROP_TAXONOMY: Dict[str, Dict[str, Any]] = {
    # Cereals & Millets
    "rice": {
        "name": "Rice",
        "group": "Cereal",
        "rooting": "Shallow Fibrous (20-40 cm)",
        "nutrient_demand": "High",
        "nitrogen_fixing": "No",
        "water_demand": "High",
        "role": "Major Staple / Wetland Feeder",
        "benefit": "Prepares paddy field structure; benefits from succeeding legumes like Chickpea/Lentil.",
        "notes": "Flooded cultivation creates anaerobic soil conditions that benefit from post-monsoon aeration."
    },
    "wheat": {
        "name": "Wheat",
        "group": "Cereal",
        "rooting": "Moderate Fibrous (30-60 cm)",
        "nutrient_demand": "Medium",
        "nitrogen_fixing": "No",
        "water_demand": "Medium",
        "role": "Rabi Cereal Staple",
        "benefit": "Standard cool-season cereal; optimal following Kharif legumes like Soybean, Groundnut, or Pigeon Peas.",
        "notes": "Continuous wheat monocropping increases Phalaris minor weed pressure and root pathogens."
    },
    "maize": {
        "name": "Maize",
        "group": "Cereal",
        "rooting": "Moderate Fibrous (40-80 cm)",
        "nutrient_demand": "High",
        "nitrogen_fixing": "No",
        "water_demand": "Medium",
        "role": "Heavy Feeding Cereal / Fodder",
        "benefit": "High biomass producer; requires nitrogen restoration from preceding or succeeding pulses.",
        "notes": "Heavy potassium and nitrogen extractor; should not follow another heavy cereal continuously."
    },
    "jowar": {
        "name": "Jowar (Sorghum)",
        "group": "Cereal",
        "rooting": "Deep Fibrous (60-120 cm)",
        "nutrient_demand": "Medium",
        "nitrogen_fixing": "No",
        "water_demand": "Low",
        "role": "Drought-Tolerant Coarse Cereal",
        "benefit": "Extensive root system breaks subsoil compaction; scavenges residual nutrients efficiently.",
        "notes": "Can produce allelopathic root exudates that suppress weeds in subsequent pulse crops."
    },
    "bajra": {
        "name": "Bajra (Pearl Millet)",
        "group": "Cereal",
        "rooting": "Deep Fibrous (60-100 cm)",
        "nutrient_demand": "Low",
        "nitrogen_fixing": "No",
        "water_demand": "Low",
        "role": "Arid / Dryland Millet",
        "benefit": "Highly resilient in sandy/arid soils; ideal rotation partner with low-water legumes like Moth Beans.",
        "notes": "Low nutrient extraction rate helps preserve soil organic moisture."
    },
    "ragi": {
        "name": "Ragi",
        "group": "Cereal",
        "rooting": "Shallow Fibrous (20-40 cm)",
        "nutrient_demand": "Low",
        "nitrogen_fixing": "No",
        "water_demand": "Low",
        "role": "Nutritious Finger Millet",
        "benefit": "Low input requirement; leaves good root biomass in light red/laterite soils.",
        "notes": "Rotates effectively with groundnut, pulses, and vegetables in semi-arid zones."
    },
    "millets": {
        "name": "Millets",
        "group": "Cereal",
        "rooting": "Moderate Fibrous (30-60 cm)",
        "nutrient_demand": "Low",
        "nitrogen_fixing": "No",
        "water_demand": "Low",
        "role": "Climate-Resilient Small Grain",
        "benefit": "Tolerates poor soil fertility; acts as an effective low-input break crop.",
        "notes": "Enhances microbial diversity in dryland soils."
    },

    # Legumes & Pulses
    "soybean": {
        "name": "Soybean",
        "group": "Legume/Pulse",
        "rooting": "Moderate Taproot (40-70 cm)",
        "nutrient_demand": "Medium",
        "nitrogen_fixing": "Yes",
        "water_demand": "Medium",
        "role": "Commercial Nitrogen-Fixing Legume",
        "benefit": "Fixes 40-80 kg N/ha; enriches topsoil with leaf litter and improves subsequent wheat/jowar yields.",
        "notes": "Optimal preceding crop for Wheat, Jowar, or Maize in central and western India."
    },
    "pigeonpeas": {
        "name": "Pigeon Peas (Tur)",
        "group": "Legume/Pulse",
        "rooting": "Deep Taproot (100-150 cm)",
        "nutrient_demand": "Low",
        "nitrogen_fixing": "Yes",
        "water_demand": "Low",
        "role": "Deep-Rooted Restorative Pulse",
        "benefit": "Deep taproots channel subsoil nutrients, fix substantial nitrogen, and break plow-pan compaction.",
        "notes": "Excellent rotation/intercrop partner with Cotton, Soybean, and Sorghum."
    },
    "chickpea": {
        "name": "Chickpea",
        "group": "Legume/Pulse",
        "rooting": "Deep Taproot (60-100 cm)",
        "nutrient_demand": "Low",
        "nitrogen_fixing": "Yes",
        "water_demand": "Low",
        "role": "Rabi Restorative Pulse",
        "benefit": "Fixes atmospheric nitrogen during cool season; utilizes residual moisture after Rice or Maize.",
        "notes": "Continuous chickpea cropping increases Fusarium wilt and Ascochyta blight pathogen pressure."
    },
    "kidneybeans": {
        "name": "Kidney Beans",
        "group": "Legume/Pulse",
        "rooting": "Moderate Taproot (30-50 cm)",
        "nutrient_demand": "Medium",
        "nitrogen_fixing": "Yes",
        "water_demand": "Medium",
        "role": "High-Value Pulse Crop",
        "benefit": "Contributes to soil biological health; rotates well with maize and winter cereals.",
        "notes": "Moderate nitrogen-fixing capacity compared to soybean or cowpea."
    },
    "mothbeans": {
        "name": "Moth Beans",
        "group": "Legume/Pulse",
        "rooting": "Deep Taproot (50-90 cm)",
        "nutrient_demand": "Low",
        "nitrogen_fixing": "Yes",
        "water_demand": "Low",
        "role": "Arid Cover & Restorative Pulse",
        "benefit": "Dense ground cover prevents wind erosion in arid tracts; fixes nitrogen under moisture stress.",
        "notes": "Traditional companion and rotation partner with Bajra in desert soils."
    },
    "mungbean": {
        "name": "Mung Bean",
        "group": "Legume/Pulse",
        "rooting": "Shallow Taproot (25-45 cm)",
        "nutrient_demand": "Low",
        "nitrogen_fixing": "Yes",
        "water_demand": "Low",
        "role": "Short-Duration Catch Crop (60-70 days)",
        "benefit": "Rapid growth cycle fits between main seasons; incorporates green manure biomass rapidly.",
        "notes": "Ideal summer or catch crop preceding wheat, sugarcane, or mustard."
    },
    "blackgram": {
        "name": "Black Gram (Urad)",
        "group": "Legume/Pulse",
        "rooting": "Shallow Taproot (25-50 cm)",
        "nutrient_demand": "Low",
        "nitrogen_fixing": "Yes",
        "water_demand": "Medium",
        "role": "Short-Duration Restorative Pulse",
        "benefit": "Enriches soil fertility and provides rapid ground cover against weed growth.",
        "notes": "Widely used as rice-fallow pulse or Kharif legume."
    },
    "lentil": {
        "name": "Lentil (Masoor)",
        "group": "Legume/Pulse",
        "rooting": "Shallow Taproot (20-40 cm)",
        "nutrient_demand": "Low",
        "nitrogen_fixing": "Yes",
        "water_demand": "Low",
        "role": "Cool Season Restorative Pulse",
        "benefit": "Improves soil structure in heavy clay and alluvial rice-fallows with minimal moisture.",
        "notes": "Rotates effectively following wetland rice or kharif maize."
    },
    "pulses": {
        "name": "Pulses",
        "group": "Legume/Pulse",
        "rooting": "Moderate Taproot (30-60 cm)",
        "nutrient_demand": "Low",
        "nitrogen_fixing": "Yes",
        "water_demand": "Low",
        "role": "General Pulse / Soil Restorative",
        "benefit": "Enhances biological nitrogen fixation and microbial biomass across rotation cycles.",
        "notes": "Key component in sustainable crop sequence."
    },

    # Commercial & Fibre
    "cotton": {
        "name": "Cotton",
        "group": "Fibre",
        "rooting": "Deep Taproot (100-180 cm)",
        "nutrient_demand": "High",
        "nitrogen_fixing": "No",
        "water_demand": "Medium",
        "role": "Long-Duration Commercial Cash Crop",
        "benefit": "Deep root channels improve subsoil aeration; benefits significantly from legume breaks.",
        "notes": "Repeated cotton monoculture promotes Pink Bollworm and Verticillium wilt build-up."
    },
    "sugarcane": {
        "name": "Sugarcane",
        "group": "Sugar Crop",
        "rooting": "Deep Dense Root System (80-150 cm)",
        "nutrient_demand": "High",
        "nitrogen_fixing": "No",
        "water_demand": "High",
        "role": "Long-Duration Heavy Feeder (10-14 months)",
        "benefit": "Produces immense organic root biomass; leaves substantial trash residue.",
        "notes": "Extensive nutrient extraction demands restorative legume succession (Soybean, Groundnut, Gram) after ratoon cycles."
    },
    "jute": {
        "name": "Jute",
        "group": "Fibre",
        "rooting": "Moderate Taproot (40-70 cm)",
        "nutrient_demand": "Medium",
        "nitrogen_fixing": "No",
        "water_demand": "High",
        "role": "Wetland Fibre Crop",
        "benefit": "Sheds massive organic leaf litter (up to 1 tonne/ha) prior to harvest, restoring organic carbon.",
        "notes": "Excellent predecessor for late monsoon paddy in eastern deltaic regions."
    },
    "rubber": {
        "name": "Rubber",
        "group": "Plantation",
        "rooting": "Deep Perennial (200+ cm)",
        "nutrient_demand": "Medium",
        "nitrogen_fixing": "No",
        "water_demand": "High",
        "role": "Perennial Plantation Tree",
        "benefit": "Long-term perennial ground cover; legumes used primarily as understory cover crops in early years.",
        "notes": "Not an annual rotation crop; managed under multi-year plantation cycles."
    },
    "tobacco": {
        "name": "Tobacco",
        "group": "Commercial",
        "rooting": "Moderate Taproot (40-80 cm)",
        "nutrient_demand": "High",
        "nitrogen_fixing": "No",
        "water_demand": "Medium",
        "role": "Commercial Solanaceous Crop",
        "benefit": "Benefits from rotation with non-solanaceous cereals and pulses to suppress root-knot nematodes.",
        "notes": "Sensitive to soil-borne pathogens; avoid following potato, tomato, or chilli."
    },
    "tea": {
        "name": "Tea",
        "group": "Plantation",
        "rooting": "Deep Perennial (150+ cm)",
        "nutrient_demand": "Medium",
        "nitrogen_fixing": "No",
        "water_demand": "High",
        "role": "Perennial Acid-Soil Plantation",
        "benefit": "Continuous canopy preserves soil structure; cover crops used during rejuvenation pruning.",
        "notes": "Perennial crop; evaluated in long-term agroforestry context."
    },
    "coffee": {
        "name": "Coffee",
        "group": "Plantation",
        "rooting": "Deep Perennial (150+ cm)",
        "nutrient_demand": "Medium",
        "nitrogen_fixing": "No",
        "water_demand": "High",
        "role": "Shade-Grown Perennial Plantation",
        "benefit": "Maintains high soil organic carbon under multi-tier shade trees.",
        "notes": "Perennial agroforestry crop."
    },

    # Oilseeds
    "groundnut": {
        "name": "Groundnut",
        "group": "Legume/Pulse",
        "rooting": "Moderate Taproot (30-60 cm)",
        "nutrient_demand": "Low",
        "nitrogen_fixing": "Yes",
        "water_demand": "Low",
        "role": "Nitrogen-Fixing Oilseed Legume",
        "benefit": "Fixes nitrogen, loosens topsoil through pod development (pegging), and leaves residual fertility.",
        "notes": "Excellent Kharif or summer rotation preceding Wheat, Jowar, Maize, or Sugarcane."
    },
    "mustard": {
        "name": "Mustard",
        "group": "Oilseed",
        "rooting": "Deep Taproot (60-100 cm)",
        "nutrient_demand": "Medium",
        "nitrogen_fixing": "No",
        "water_demand": "Low",
        "role": "Rabi Brassica Oilseed / Biofumigant",
        "benefit": "Glucosinolate root exudates offer natural biofumigation effects, suppressing soil fungal pathogens.",
        "notes": "Rotates cleanly with Kharif rice, maize, or bajra."
    },
    "sunflower": {
        "name": "Sunflower",
        "group": "Oilseed",
        "rooting": "Deep Taproot (80-140 cm)",
        "nutrient_demand": "Medium",
        "nitrogen_fixing": "No",
        "water_demand": "Medium",
        "role": "Deep-Scavenging Oilseed",
        "benefit": "Deep root penetration retrieves leached nitrogen from subsoil horizons.",
        "notes": "Avoid continuous sunflower due to Sclerotinia head rot accumulation."
    },
    "sesame": {
        "name": "Sesame",
        "group": "Oilseed",
        "rooting": "Moderate Taproot (40-70 cm)",
        "nutrient_demand": "Low",
        "nitrogen_fixing": "No",
        "water_demand": "Low",
        "role": "Short-Duration Drought-Tolerant Oilseed",
        "benefit": "Low water footprint; leaves ground loose for succeeding rabi pulses.",
        "notes": "Ideal low-input catch crop."
    },
    "linseed": {
        "name": "Linseed",
        "group": "Oilseed",
        "rooting": "Moderate Fibrous (30-60 cm)",
        "nutrient_demand": "Low",
        "nitrogen_fixing": "No",
        "water_demand": "Low",
        "role": "Rabi Oilseed & Fibre Crop",
        "benefit": "Utilizes residual moisture in rice-fallows; low disease overlap with cereals.",
        "notes": "Good non-host crop for cereal cyst nematodes."
    },
    "castor": {
        "name": "Castor",
        "group": "Oilseed",
        "rooting": "Deep Taproot (100-160 cm)",
        "nutrient_demand": "Medium",
        "nitrogen_fixing": "No",
        "water_demand": "Low",
        "role": "Deep-Rooted Drought Hardy Oilseed",
        "benefit": "Extracts water from deep strata; breaks pest cycles of short-duration cereals.",
        "notes": "Long duration allows companion pulse intercropping."
    },
    "oilseeds": {
        "name": "Oilseeds",
        "group": "Oilseed",
        "rooting": "Moderate Taproot (40-70 cm)",
        "nutrient_demand": "Medium",
        "nitrogen_fixing": "No",
        "water_demand": "Low",
        "role": "General Oilseed Crop",
        "benefit": "Provides diversification away from continuous cereal monocultures.",
        "notes": "Balances nutrient utilization across soil profiles."
    },

    # Vegetables & Tubers
    "onion": {
        "name": "Onion",
        "group": "Vegetable",
        "rooting": "Shallow Fibrous (15-30 cm)",
        "nutrient_demand": "Medium",
        "nitrogen_fixing": "No",
        "water_demand": "Medium",
        "role": "Allium Cash Crop",
        "benefit": "Allium root exudates have natural fungicidal and anti-nematode properties.",
        "notes": "Do not follow garlic or leeks; ideal preceding or following pulses and cereals."
    },
    "potato": {
        "name": "Potato",
        "group": "Vegetable",
        "rooting": "Shallow Fibrous & Tuber (25-45 cm)",
        "nutrient_demand": "High",
        "nitrogen_fixing": "No",
        "water_demand": "Medium",
        "role": "High-Yielding Solanaceous Tuber",
        "benefit": "Intense tillage and ridging leaves mellow, weed-free seedbed for succeeding wheat or pulses.",
        "notes": "High potassium feeder; avoid following other solanaceous crops like Tomato or Chilli."
    },
    "tomato": {
        "name": "Tomato",
        "group": "Vegetable",
        "rooting": "Moderate Taproot (30-60 cm)",
        "nutrient_demand": "High",
        "nitrogen_fixing": "No",
        "water_demand": "Medium",
        "role": "Intensive Solanaceous Vegetable",
        "benefit": "High cash return crop; benefits from cereal/pulse succession to suppress bacterial wilt.",
        "notes": "Rotate with Poaceae (cereals) or Fabaceae (legumes) to break root-knot nematodes."
    },
    "garlic": {
        "name": "Garlic",
        "group": "Vegetable",
        "rooting": "Shallow Fibrous (15-25 cm)",
        "nutrient_demand": "Medium",
        "nitrogen_fixing": "No",
        "water_demand": "Medium",
        "role": "Allium Spice & Cash Crop",
        "benefit": "Natural sulfur compounds in root zone suppress soil-borne fungal pathogens.",
        "notes": "Rotates cleanly with pulses, maize, and rice."
    },
    "ginger": {
        "name": "Ginger",
        "group": "Spices",
        "rooting": "Shallow Rhizomatous (20-40 cm)",
        "nutrient_demand": "High",
        "nitrogen_fixing": "No",
        "water_demand": "High",
        "role": "Rhizomatous Spice Cash Crop",
        "benefit": "High economic return; requires fertile organic soils and rotation away from rhizome rot hosts.",
        "notes": "Follow with deep-rooted pulses or green manure crops."
    },
    "turmeric": {
        "name": "Turmeric",
        "group": "Spices",
        "rooting": "Moderate Rhizomatous (25-50 cm)",
        "nutrient_demand": "High",
        "nitrogen_fixing": "No",
        "water_demand": "High",
        "role": "Long-Duration Rhizome Spice (8-9 months)",
        "benefit": "Mellows soil profile through heavy mulching and organic cultivation.",
        "notes": "Rotates well with short-duration pulses, maize, or onion."
    },
    "chilli": {
        "name": "Chilli",
        "group": "Spices",
        "rooting": "Moderate Taproot (30-60 cm)",
        "nutrient_demand": "Medium",
        "nitrogen_fixing": "No",
        "water_demand": "Medium",
        "role": "Solanaceous Spice / Vegetable",
        "benefit": "Provides high market returns; requires non-solanaceous rotation partners.",
        "notes": "Rotate away from cotton and tomato to break common viral vector (thrips/whitefly) cycles."
    },
    "spices": {
        "name": "Spices",
        "group": "Spices",
        "rooting": "Moderate Taproot (30-60 cm)",
        "nutrient_demand": "Medium",
        "nitrogen_fixing": "No",
        "water_demand": "Medium",
        "role": "High-Value Commercial Spices",
        "benefit": "Diversifies farm enterprise and interrupts standard field-crop pest cycles.",
        "notes": "Maintain balanced fertility."
    },
    "vegetables": {
        "name": "Vegetables",
        "group": "Vegetable",
        "rooting": "Shallow to Moderate (20-50 cm)",
        "nutrient_demand": "Medium",
        "nitrogen_fixing": "No",
        "water_demand": "Medium",
        "role": "Diverse Horticultural Crops",
        "benefit": "Breaks cereal monoculture patterns; quick turnaround allows multiple cropping cycles.",
        "notes": "Rotate crop families (e.g. Cole crops -> Legumes -> Solanaceous -> Cucurbits)."
    },

    # Fruits & Horticulture
    "banana": {
        "name": "Banana",
        "group": "Fruit/Horticulture",
        "rooting": "Shallow to Deep Dense Mat (30-80 cm)",
        "nutrient_demand": "High",
        "nitrogen_fixing": "No",
        "water_demand": "High",
        "role": "Perennial / Semi-Perennial Giant Herb",
        "benefit": "Generates huge organic residue biomass when stalks are incorporated into soil.",
        "notes": "High potassium and nitrogen consumer; follow with restorative green manures or pulses before replanting."
    },
    "pomegranate": {
        "name": "Pomegranate",
        "group": "Fruit/Horticulture",
        "rooting": "Deep Perennial Shrub (100-180 cm)",
        "nutrient_demand": "Medium",
        "nitrogen_fixing": "No",
        "water_demand": "Low",
        "role": "Arid / Semi-Arid Perennial Fruit",
        "benefit": "Drought-tolerant perennial orchard crop; intercropped with short pulses in formative years.",
        "notes": "Orchard system; rotation rules apply during intercropping or field renewal."
    },
    "mango": {
        "name": "Mango",
        "group": "Fruit/Horticulture",
        "rooting": "Deep Taproot (200+ cm)",
        "nutrient_demand": "Medium",
        "nitrogen_fixing": "No",
        "water_demand": "Low",
        "role": "Perennial Fruit Tree",
        "benefit": "Extensive canopy and deep root system protect soil integrity for decades.",
        "notes": "Perennial orchard crop."
    },
    "grapes": {
        "name": "Grapes",
        "group": "Fruit/Horticulture",
        "rooting": "Deep Perennial Vine (100-200 cm)",
        "nutrient_demand": "High",
        "nitrogen_fixing": "No",
        "water_demand": "Medium",
        "role": "Commercial Viticulture Vine",
        "benefit": "High commercial value; cover crops planted in vine alleys prevent erosion.",
        "notes": "Specialized perennial vineyard system."
    },
    "apple": {
        "name": "Apple",
        "group": "Fruit/Horticulture",
        "rooting": "Deep Perennial Tree (150+ cm)",
        "nutrient_demand": "Medium",
        "nitrogen_fixing": "No",
        "water_demand": "Medium",
        "role": "Temperate Perennial Tree Fruit",
        "benefit": "Stabilizes hillside soils and maintains orchard floor microbial health.",
        "notes": "Perennial temperate fruit."
    },
    "orange": {
        "name": "Orange",
        "group": "Fruit/Horticulture",
        "rooting": "Deep Perennial Tree (120-180 cm)",
        "nutrient_demand": "Medium",
        "nitrogen_fixing": "No",
        "water_demand": "Medium",
        "role": "Subtropical Citrus Fruit",
        "benefit": "Perennial canopy cover; legumes grown in inter-row spaces enrich nitrogen.",
        "notes": "Citrus orchard system."
    },
    "papaya": {
        "name": "Papaya",
        "group": "Fruit/Horticulture",
        "rooting": "Moderate Fibrous (40-80 cm)",
        "nutrient_demand": "High",
        "nitrogen_fixing": "No",
        "water_demand": "Medium",
        "role": "Short-Lived Perennial Fruit (2-3 years)",
        "benefit": "Quick economic turnaround; benefits from non-solanaceous soil restoration afterwards.",
        "notes": "Follow with cereals or pulses to break viral/nematode pressure."
    },
    "coconut": {
        "name": "Coconut",
        "group": "Plantation",
        "rooting": "Dense Adventitious (100-200 cm)",
        "nutrient_demand": "Medium",
        "nitrogen_fixing": "No",
        "water_demand": "High",
        "role": "Coastal Perennial Palm",
        "benefit": "Multi-story cropping system accommodates pulses, spices, and tubers in understory.",
        "notes": "Perennial plantation palm."
    },
    "guava": {
        "name": "Guava",
        "group": "Fruit/Horticulture",
        "rooting": "Moderate to Deep (80-150 cm)",
        "nutrient_demand": "Low",
        "nitrogen_fixing": "No",
        "water_demand": "Low",
        "role": "Hardy Subtropical Fruit",
        "benefit": "Hardy fruit crop suitable for marginal soils.",
        "notes": "Perennial orchard crop."
    },
    "cashew": {
        "name": "Cashew",
        "group": "Fruit/Horticulture",
        "rooting": "Deep Taproot (150-250 cm)",
        "nutrient_demand": "Low",
        "nitrogen_fixing": "No",
        "water_demand": "Low",
        "role": "Coastal / Wasteland Plantation Tree",
        "benefit": "Fixes soil on degraded slopes; very low nutrient demand.",
        "notes": "Perennial plantation tree."
    },
    "watermelon": {
        "name": "Watermelon",
        "group": "Vegetable",
        "rooting": "Moderate Taproot (40-70 cm)",
        "nutrient_demand": "Medium",
        "nitrogen_fixing": "No",
        "water_demand": "Medium",
        "role": "Zaid Summer Cucurbit",
        "benefit": "Short duration summer crop; utilizes residual soil heat and moisture after rabi harvest.",
        "notes": "Rotates effectively following rice, wheat, or mustard."
    },
    "muskmelon": {
        "name": "Muskmelon",
        "group": "Vegetable",
        "rooting": "Moderate Taproot (35-65 cm)",
        "nutrient_demand": "Medium",
        "nitrogen_fixing": "No",
        "water_demand": "Medium",
        "role": "Zaid Summer Cucurbit",
        "benefit": "Quick summer cash crop; breaks weed cycles before Kharif sowing.",
        "notes": "Rotates cleanly after wheat or potato."
    }
}

# 2. Agronomic Rotation Rules Definitions
ROTATION_RULES_TABLE = [
    {
        "rule_id": "ROT-001",
        "rule_name": "Legume Succession After Heavy Cereal",
        "description": "Planting a nitrogen-fixing legume/pulse (e.g. Soybean, Pigeon Pea, Chickpea, Groundnut) after an exhaustive cereal (Wheat, Rice, Maize, Jowar).",
        "effect": "Restores biologically fixed nitrogen (30-80 kg N/ha), enhances microbial activity, and diversifies root depth.",
        "score_adjustment": "+0.35 (Score: 0.85, High, Prefer)"
    },
    {
        "rule_id": "ROT-002",
        "rule_name": "Cereal Succession After Restorative Legume",
        "description": "Planting a cereal crop (e.g. Wheat, Jowar, Maize, Rice) after a legume/pulse.",
        "effect": "Cereal exploits residual soil nitrogen and improved soil tilth left by the preceding pulse crop.",
        "score_adjustment": "+0.35 (Score: 0.85, High, Prefer)"
    },
    {
        "rule_id": "ROT-003",
        "rule_name": "Legume Restoration After Long-Duration Sugarcane",
        "description": "Planting an annual legume/pulse (Soybean, Groundnut, Gram) following intensive Sugarcane harvest/ratoon cycle.",
        "effect": "Breaks heavy nutrient extraction cycle, aerates subsoil, and replenishes nitrogen naturally without excessive synthetic inputs.",
        "score_adjustment": "+0.35 (Score: 0.85, High, Prefer)"
    },
    {
        "rule_id": "ROT-004",
        "rule_name": "Cereal Succession After Sugarcane",
        "description": "Planting a cereal grain (Wheat, Jowar, Maize) following Sugarcane.",
        "effect": "Feasible sequential rotation, but requires balanced nitrogen and phosphorus replenishment due to prior sugarcane extraction.",
        "score_adjustment": "+0.15 (Score: 0.65, Medium, Consider)"
    },
    {
        "rule_id": "ROT-005",
        "rule_name": "Oilseed Succession After Sugarcane",
        "description": "Planting an oilseed (Groundnut, Mustard, Sunflower) following Sugarcane.",
        "effect": "Diversifies crop family and nutrient uptake patterns; Groundnut provides nitrogen fixation benefit.",
        "score_adjustment": "+0.30 (Score: 0.80, High, Prefer)"
    },
    {
        "rule_id": "ROT-006",
        "rule_name": "Pulse / Legume Break After Cotton",
        "description": "Planting a pulse or legume after deep-rooted commercial Fibre (Cotton).",
        "effect": "Suppresses Pink Bollworm and Fusarium/Verticillium wilt fungal build-up; restores topsoil organic matter.",
        "score_adjustment": "+0.35 (Score: 0.85, High, Prefer)"
    },
    {
        "rule_id": "ROT-007",
        "rule_name": "Cereal Rotation After Cotton",
        "description": "Planting a shallow/moderate fibrous rooted cereal (Wheat, Jowar, Maize) after deep-rooted Cotton.",
        "effect": "Alternates nutrient zones between topsoil and deeper subsoil profiles, avoiding localized exhaustion.",
        "score_adjustment": "+0.30 (Score: 0.80, High, Prefer)"
    },
    {
        "rule_id": "ROT-008",
        "rule_name": "Repeated Monoculture Penalty",
        "description": "Cultivating the exact same crop consecutively (e.g. Maize -> Maize, Cotton -> Cotton, Wheat -> Wheat, Rice -> Rice).",
        "effect": "Depletes specific macro/micro-nutrient strata, accumulates host-specific pests, nematodes, and soil pathogens.",
        "score_adjustment": "-0.20 to -0.30 (Score: 0.30 - 0.40, Low, Avoid)"
    },
    {
        "rule_id": "ROT-009",
        "rule_name": "Same-Family Cereal-Cereal Succession",
        "description": "Sequential cultivation of different crops within the same Poaceae (cereal) family (e.g. Rice -> Wheat, Maize -> Wheat).",
        "effect": "Common agricultural practice in fertile irrigated tracts (e.g. Rice-Wheat cropping system); viable with proper fertilizer management but less restorative than legume rotation.",
        "score_adjustment": "+0.10 (Score: 0.60 - 0.65, Medium, Consider)"
    },
    {
        "rule_id": "ROT-010",
        "rule_name": "Biofumigant / Brassica Rotation",
        "description": "Planting Mustard / Brassica oilseeds in rotation with cereals or pulses.",
        "effect": "Glucosinolate root exudates offer natural biofumigation effects, suppressing soil fungal pathogens.",
        "score_adjustment": "+0.30 (Score: 0.80, High, Prefer)"
    },
    {
        "rule_id": "ROT-011",
        "rule_name": "Allium / Vegetable Break Rotation",
        "description": "Planting Onion, Garlic, or diverse vegetables in rotation with field crops.",
        "effect": "Diversifies cash income; allium root sulfur compounds deter fungal and bacterial pathogens.",
        "score_adjustment": "+0.25 (Score: 0.75 - 0.80, High, Prefer)"
    },
    {
        "rule_id": "ROT-012",
        "rule_name": "Solanaceous Monoculture Avoidance",
        "description": "Succession of solanaceous crops (Potato, Tomato, Chilli, Tobacco) directly after another solanaceous crop.",
        "effect": "High risk of Bacterial Wilt (Ralstonia solanacearum), Early/Late Blight, and Root-Knot Nematodes.",
        "score_adjustment": "-0.25 (Score: 0.35, Low, Avoid)"
    },
    {
        "rule_id": "ROT-013",
        "rule_name": "Perennial Orchard Management",
        "description": "Orchard and plantation fruit trees (Mango, Pomegranate, Apple, Orange, Coconut, Coffee).",
        "effect": "Multi-year perennial tree systems; evaluated in sustainable agroforestry / intercropping context.",
        "score_adjustment": "Score: 0.65 (Medium, Consider)"
    },
    {
        "rule_id": "ROT-014",
        "rule_name": "General Agronomic Cross-Family Diversification",
        "description": "Any general rotation pairing across different crop botanical families with balanced nutrient dynamics.",
        "effect": "Standard rotational benefit maintaining neutral to favorable soil biological equilibrium.",
        "score_adjustment": "Score: 0.70 (Medium-High, Consider)"
    }
]

# 3. Pairwise Rotation Evaluation Engine
def evaluate_pair(prev_key: str, new_key: str) -> Dict[str, Any]:
    """
    Evaluates the directional rotation suitability between previous_crop and new_crop.
    Applies explicit, transparent agronomic rules.
    """
    prev_info = CROP_TAXONOMY.get(prev_key)
    new_info = CROP_TAXONOMY.get(new_key)

    if not prev_info or not new_info:
        # Fallback for unlisted crops
        return {
            "previous_crop": canonical_display_name(prev_key),
            "new_crop": canonical_display_name(new_key),
            "compatibility": "Medium",
            "rotation_score": 0.50,
            "nutrient_effect": "Neutral",
            "nitrogen_effect": "No known impact",
            "root_pattern": "Standard",
            "water_compatibility": "Neutral",
            "pest_disease_break": "Neutral",
            "rotation_reason": f"Standard agricultural rotation following {canonical_display_name(prev_key)}.",
            "recommendation": "Consider",
            "confidence": "Low",
            "source_type": "Neutral Fallback",
            "notes": "Specific empirical rotation data unavailable; standard management recommended."
        }

    p_name = prev_info["name"]
    n_name = new_info["name"]
    p_group = prev_info["group"]
    n_group = new_info["group"]

    # Rule 8: Exact Same Crop (Monoculture)
    if prev_key == new_key:
        if "Perennial" in prev_info["rooting"] or p_group in ["Plantation", "Fruit/Horticulture"]:
            return {
                "previous_crop": p_name,
                "new_crop": n_name,
                "compatibility": "Medium",
                "rotation_score": 0.65,
                "nutrient_effect": "Steady Perennial Uptake",
                "nitrogen_effect": "Maintain organic mulching",
                "root_pattern": "Established Deep Rooting",
                "water_compatibility": "Established irrigation cycle",
                "pest_disease_break": "Requires regular orchard sanitation",
                "rotation_reason": f"Continuous perennial cultivation of {n_name}; maintain soil health with inter-row cover crops.",
                "recommendation": "Consider",
                "confidence": "High",
                "source_type": "Perennial Management Standard",
                "notes": "Orchard/plantation systems require canopy and tree health monitoring."
            }
        else:
            return {
                "previous_crop": p_name,
                "new_crop": n_name,
                "compatibility": "Low",
                "rotation_score": 0.35,
                "nutrient_effect": "Heavy Single-Zone Nutrient Depletion",
                "nitrogen_effect": "Exhausts available nitrogen pools",
                "root_pattern": "Identical Root Zone Compaction",
                "water_compatibility": "Identical moisture stress profile",
                "pest_disease_break": "High risk of pest and soil-borne disease accumulation",
                "rotation_reason": f"Consecutive cropping of {n_name} on the same field increases specialized pest pressure, weed resistance, and localized nutrient depletion.",
                "recommendation": "Avoid",
                "confidence": "High",
                "source_type": "Agronomic Monoculture Principle",
                "notes": "Rotate with a different crop family (e.g. pulses or oilseeds) to restore soil vitality."
            }

    # Rule 12: Solanaceous consecutive crops
    solanaceous_crops = {"potato", "tomato", "chilli", "tobacco"}
    if prev_key in solanaceous_crops and new_key in solanaceous_crops:
        return {
            "previous_crop": p_name,
            "new_crop": n_name,
            "compatibility": "Low",
            "rotation_score": 0.35,
            "nutrient_effect": "Heavy potassium & trace mineral depletion",
            "nitrogen_effect": "No restorative benefit",
            "root_pattern": "Shared shallow-moderate root profile",
            "water_compatibility": "Susceptible to soil waterlogging diseases",
            "pest_disease_break": "Critical risk of Bacterial Wilt (Ralstonia) and Early/Late Blight pathogen buildup",
            "rotation_reason": f"Successive planting of solanaceous {n_name} after {p_name} carries high risk of soil-borne blight and root-knot nematodes.",
            "recommendation": "Avoid",
            "confidence": "High",
            "source_type": "Plant Pathology Standard",
            "notes": "Rotate with cereals (Maize, Wheat) or pulses to break shared solanaceous diseases."
        }

    # Rule 3: Sugarcane -> Legume / Pulse
    if prev_key == "sugarcane" and (n_group == "Legume/Pulse" or prev_info["nitrogen_fixing"] == "Yes" or new_info["nitrogen_fixing"] == "Yes"):
        return {
            "previous_crop": p_name,
            "new_crop": n_name,
            "compatibility": "High",
            "rotation_score": 0.85,
            "nutrient_effect": "Restores biological balance after heavy nutrient extraction",
            "nitrogen_effect": "Enriches soil with biologically fixed nitrogen",
            "root_pattern": "Alternates deep cane roots with restorative legume nodulation",
            "water_compatibility": "Low to medium water requirement relieves heavy irrigation pressure",
            "pest_disease_break": "Interrupts sugarcane red rot and scale insect cycles",
            "rotation_reason": f"Excellent restorative rotation: {n_name} fixes atmospheric nitrogen and diversifies soil biology after long-duration {p_name}.",
            "recommendation": "Prefer",
            "confidence": "High",
            "source_type": "Sugarcane Research Institute Guideline",
            "notes": "Ideal post-sugarcane green manure or grain pulse succession."
        }

    # Rule 4 & 5: Sugarcane -> Cereal or Oilseed
    if prev_key == "sugarcane":
        if n_group == "Oilseed":
            return {
                "previous_crop": p_name,
                "new_crop": n_name,
                "compatibility": "High",
                "rotation_score": 0.80,
                "nutrient_effect": "Diversifies soil nutrient uptake horizons",
                "nitrogen_effect": "Moderate demand; benefits from sugarcane residue mineralization",
                "root_pattern": "Deep taproot explores lower subsoil layers",
                "water_compatibility": "Lower water requirement conserves farm water resources",
                "pest_disease_break": "Breaks sugarcane borer and root pest life cycles",
                "rotation_reason": f"Favorable succession: {n_name} provides effective crop family diversification following {p_name}.",
                "recommendation": "Prefer",
                "confidence": "High",
                "source_type": "Regional Cropping System Study",
                "notes": "Ensure basal fertilization matches soil test values."
            }
        elif n_group == "Cereal":
            return {
                "previous_crop": p_name,
                "new_crop": n_name,
                "compatibility": "Medium",
                "rotation_score": 0.65,
                "nutrient_effect": "Moderate nutrient demand following heavy sugarcane extraction",
                "nitrogen_effect": "Requires nitrogen top-dressing to support cereal tillering",
                "root_pattern": "Fibrous roots utilize upper soil profile tilth",
                "water_compatibility": "Compatible with standard irrigation",
                "pest_disease_break": "Good pest break from cane-specific borers",
                "rotation_reason": f"Feasible rotation: {n_name} utilizes the fine seedbed after {p_name}, but requires adequate fertilizer application.",
                "recommendation": "Consider",
                "confidence": "High",
                "source_type": "Agronomic Extension Guideline",
                "notes": "Test soil nitrogen and phosphorus before sowing."
            }

    # Rule 6 & 7: Fibre (Cotton) -> Legume or Cereal
    if prev_key == "cotton":
        if n_group == "Legume/Pulse" or new_info["nitrogen_fixing"] == "Yes":
            return {
                "previous_crop": p_name,
                "new_crop": n_name,
                "compatibility": "High",
                "rotation_score": 0.85,
                "nutrient_effect": "Replenishes topsoil organic carbon and nitrogen pools",
                "nitrogen_effect": "Biological nitrogen fixation restores depleted topsoil",
                "root_pattern": "Dense fibrous/nodulated roots improve soil aggregate stability",
                "water_compatibility": "Well-adapted to post-cotton moisture regimes",
                "pest_disease_break": "Breaks cotton bollworm, whitefly, and root-rot cycles",
                "rotation_reason": f"Optimal restorative sequence: {n_name} enriches soil nitrogen and interrupts {p_name} pest cycles.",
                "recommendation": "Prefer",
                "confidence": "High",
                "source_type": "Central Institute for Cotton Research",
                "notes": "Widely proven crop sequence in black and alluvial cotton belts."
            }
        elif n_group in ["Cereal", "Oilseed"]:
            return {
                "previous_crop": p_name,
                "new_crop": n_name,
                "compatibility": "High",
                "rotation_score": 0.80,
                "nutrient_effect": "Efficient uptake of residual nutrients from cotton field",
                "nitrogen_effect": "Utilizes residual fertility in deeper root channels",
                "root_pattern": "Alternates deep taproot with fibrous grain root system",
                "water_compatibility": "Conserves residual soil moisture",
                "pest_disease_break": "Breaks bollworm and sucking pest continuity",
                "rotation_reason": f"Favorable crop diversification: {n_name} follows deep-rooted {p_name} with complementary root architecture.",
                "recommendation": "Prefer",
                "confidence": "High",
                "source_type": "All India Coordinated Research Project",
                "notes": "Standard Kharif-Rabi sequence."
            }

    # Rule 1: Cereal -> Legume / Pulse
    if p_group == "Cereal" and (n_group == "Legume/Pulse" or new_info["nitrogen_fixing"] == "Yes"):
        return {
            "previous_crop": p_name,
            "new_crop": n_name,
            "compatibility": "High",
            "rotation_score": 0.85,
            "nutrient_effect": "Rebuilds fertility after nitrogen-demanding cereal harvest",
            "nitrogen_effect": "Legume nodules fix atmospheric nitrogen directly into the root zone",
            "root_pattern": "Taproot channels open soil compacted by fibrous cereal roots",
            "water_compatibility": "Moderate to low water demand complements seasonal moisture",
            "pest_disease_break": "Breaks cereal rusts, smuts, and armyworm cycles",
            "rotation_reason": f"Highly recommended rotation: planting legume {n_name} after cereal {p_name} restores soil nitrogen and breaks pest cycles.",
            "recommendation": "Prefer",
            "confidence": "High",
            "source_type": "ICAR Agronomic Standard",
            "notes": "Cornerstone of sustainable crop rotation systems across India."
        }

    # Rule 2: Legume / Pulse -> Cereal
    if (p_group == "Legume/Pulse" or prev_info["nitrogen_fixing"] == "Yes") and n_group == "Cereal":
        return {
            "previous_crop": p_name,
            "new_crop": n_name,
            "compatibility": "High",
            "rotation_score": 0.85,
            "nutrient_effect": "Maximizes yield response from residual legume nitrogen credit",
            "nitrogen_effect": "Cereal capitalizes on 30-50 kg/ha residual fixed nitrogen",
            "root_pattern": "Fibrous roots thrive in loosened, biologically active soil",
            "water_compatibility": "Standard cereal water management",
            "pest_disease_break": "Zero shared pathogen hosts between legume and cereal",
            "rotation_reason": f"Optimal succession: {n_name} gains substantial yield and vigor from residual nitrogen fixed by preceding {p_name}.",
            "recommendation": "Prefer",
            "confidence": "High",
            "source_type": "ICAR Cropping Systems Research",
            "notes": "Reduces synthetic nitrogen requirement by 15-25%."
        }

    # Legume -> Legume
    if p_group == "Legume/Pulse" and n_group == "Legume/Pulse":
        return {
            "previous_crop": p_name,
            "new_crop": n_name,
            "compatibility": "Medium",
            "rotation_score": 0.60,
            "nutrient_effect": "Maintains nitrogen fixation but may over-extract specific phosphorus pools",
            "nitrogen_effect": "Continued nitrogen fixation",
            "root_pattern": "Successive taproot exploration",
            "water_compatibility": "Compatible low water requirement",
            "pest_disease_break": "Potential risk of shared legume root-rot and wilt fungi build-up",
            "rotation_reason": f"Acceptable legume succession ({p_name} -> {n_name}), though alternating with a cereal or oilseed is preferred for pathogen management.",
            "recommendation": "Consider",
            "confidence": "High",
            "source_type": "Pulse Research Directorate",
            "notes": "Monitor soil phosphorus and rhizobium inoculation."
        }

    # Rule 9: Cereal -> Cereal (Different Crops)
    if p_group == "Cereal" and n_group == "Cereal":
        return {
            "previous_crop": p_name,
            "new_crop": n_name,
            "compatibility": "Medium",
            "rotation_score": 0.60,
            "nutrient_effect": "Cumulative macronutrient uptake across similar root zones",
            "nitrogen_effect": "Requires balanced synthetic/organic nitrogen application",
            "root_pattern": "Sequential fibrous root systems",
            "water_compatibility": "Requires planned irrigation management",
            "pest_disease_break": "Moderate break between different cereal species",
            "rotation_reason": f"Feasible cereal sequence ({p_name} -> {n_name}); viable with balanced fertilizer management, though rotating with a pulse is more restorative.",
            "recommendation": "Consider",
            "confidence": "High",
            "source_type": "All India Cropping Systems Research",
            "notes": "Ensure sufficient organic matter/manure incorporation."
        }

    # Rule 10: Oilseed (Mustard) as Biofumigant
    if new_key == "mustard" or prev_key == "mustard":
        return {
            "previous_crop": p_name,
            "new_crop": n_name,
            "compatibility": "High",
            "rotation_score": 0.80,
            "nutrient_effect": "Balanced nutrient uptake with biofumigation benefit",
            "nitrogen_effect": "Moderate nitrogen utilization",
            "root_pattern": "Deep taproot explores subsoil nutrient reserves",
            "water_compatibility": "Low water footprint conserves soil moisture",
            "pest_disease_break": "Mustard glucosinolates act as natural biofumigant against soil fungi",
            "rotation_reason": f"Favorable biofumigant rotation: {n_name} suppresses soil-borne pathogens and complements {p_name}.",
            "recommendation": "Prefer",
            "confidence": "High",
            "source_type": "Directorate of Rapeseed-Mustard Research",
            "notes": "Excellent rabi partner following Kharif cereals or pulses."
        }

    # Rule 11: Allium / Vegetable Succession
    if prev_key in ["onion", "garlic"] or new_key in ["onion", "garlic"]:
        return {
            "previous_crop": p_name,
            "new_crop": n_name,
            "compatibility": "High",
            "rotation_score": 0.80,
            "nutrient_effect": "Diversified nutrient extraction across shallow and deep root zones",
            "nitrogen_effect": "Efficient utilization of residual organic fertility",
            "root_pattern": "Alternates shallow bulb roots with deeper field crop roots",
            "water_compatibility": "Standard water management",
            "pest_disease_break": "Allium sulfur compounds provide natural fungicidal properties",
            "rotation_reason": f"Highly compatible rotation: {n_name} benefits from the clean, pathogen-reduced seedbed following {p_name}.",
            "recommendation": "Prefer",
            "confidence": "High",
            "source_type": "Horticultural Research Standard",
            "notes": "High economic diversification."
        }

    # General Cross-Group Diversification (Rule 14)
    return {
        "previous_crop": p_name,
        "new_crop": n_name,
        "compatibility": "High" if (p_group != n_group) else "Medium",
        "rotation_score": 0.75 if (p_group != n_group) else 0.65,
        "nutrient_effect": "Healthy cross-family nutrient diversification",
        "nitrogen_effect": "Standard balanced nutrient management",
        "root_pattern": f"Alternates {prev_info['rooting']} with {new_info['rooting']}",
        "water_compatibility": "Adaptable to prevailing seasonal moisture",
        "pest_disease_break": "Effective interruption of specialized pests between different plant families",
        "rotation_reason": f"Favorable crop diversification: rotating from {p_group} ({p_name}) to {n_group} ({n_name}) maintains balanced soil biology.",
        "recommendation": "Prefer" if (p_group != n_group) else "Consider",
        "confidence": "High",
        "source_type": "General Agronomic Rotation Principle",
        "notes": "Follow standard package of practices."
    }

# 4. Data Dictionary Definitions
DATA_DICTIONARY_TABLE = [
    {"column_name": "previous_crop", "description": "Display name of the crop harvested in the preceding season.", "data_type": "String", "allowed_values": "Canonical Crop Names", "example": "Sugarcane"},
    {"column_name": "new_crop", "description": "Display name of the proposed candidate crop to be cultivated.", "data_type": "String", "allowed_values": "Canonical Crop Names", "example": "Soybean"},
    {"column_name": "compatibility", "description": "Categorical rating of agronomic suitability for the succession.", "data_type": "String", "allowed_values": "High, Medium, Low", "example": "High"},
    {"column_name": "rotation_score", "description": "Normalized decision-support ranking score (0.00 to 1.00).", "data_type": "Float", "allowed_values": "0.00 - 1.00", "example": "0.85"},
    {"column_name": "nutrient_effect", "description": "Impact of the crop sequence on soil macronutrient and micronutrient balance.", "data_type": "String", "allowed_values": "Descriptive Text", "example": "Restores biological balance after heavy nutrient extraction"},
    {"column_name": "nitrogen_effect", "description": "Biological nitrogen fixation contribution or nitrogen demand profile.", "data_type": "String", "allowed_values": "Descriptive Text", "example": "Enriches soil with biologically fixed nitrogen"},
    {"column_name": "root_pattern", "description": "Root architecture alternation between shallow fibrous and deep taproot zones.", "data_type": "String", "allowed_values": "Descriptive Text", "example": "Alternates deep roots with restorative nodulation"},
    {"column_name": "water_compatibility", "description": "Moisture demand adaptation between preceding and succeeding seasons.", "data_type": "String", "allowed_values": "Descriptive Text", "example": "Low water requirement relieves irrigation pressure"},
    {"column_name": "pest_disease_break", "description": "Pathogen and insect pest life-cycle interruption efficacy.", "data_type": "String", "allowed_values": "Descriptive Text", "example": "Interrupts sugarcane red rot and scale insect cycles"},
    {"column_name": "rotation_reason", "description": "Plain-language agronomic explanation for farmer decision-support.", "data_type": "String", "allowed_values": "Descriptive Text", "example": "Excellent restorative rotation: Soybean fixes atmospheric nitrogen..."},
    {"column_name": "recommendation", "description": "Actionable decision directive for advisory ranking.", "data_type": "String", "allowed_values": "Prefer, Consider, Avoid", "example": "Prefer"},
    {"column_name": "confidence", "description": "Agronomic evidence confidence level for this specific crop pairing.", "data_type": "String", "allowed_values": "High, Medium, Low", "example": "High"},
    {"column_name": "source_type", "description": "Agronomic reference or institutional research classification.", "data_type": "String", "allowed_values": "Descriptive Text", "example": "ICAR Cropping Systems Research"},
    {"column_name": "notes", "description": "Practical field management and advisory notes.", "data_type": "String", "allowed_values": "Descriptive Text", "example": "Cornerstone of sustainable crop rotation systems."}
]

# 5. Main Dataset Generation Routine
def generate_dataset():
    print("==========================================================")
    print("CropMitra — Crop Rotation Dataset Generation & Validation")
    print("==========================================================")

    os.makedirs(DATA_DIR, exist_ok=True)
    crop_keys = sorted(list(CROP_TAXONOMY.keys()))
    print(f"Total Canonical Crops identified: {len(crop_keys)}")

    # 1. Build Crop Characteristics DataFrame
    characteristics_rows = []
    for k in crop_keys:
        info = CROP_TAXONOMY[k]
        characteristics_rows.append({
            "crop": info["name"],
            "crop_group": info["group"],
            "rooting_type": info["rooting"],
            "nutrient_demand": info["nutrient_demand"],
            "nitrogen_fixing": info["nitrogen_fixing"],
            "water_demand": info["water_demand"],
            "rotation_role": info["role"],
            "common_rotation_benefit": info["benefit"],
            "notes": info["notes"]
        })
    df_characteristics = pd.DataFrame(characteristics_rows)

    # 2. Build Rotation Rules DataFrame
    df_rules = pd.DataFrame(ROTATION_RULES_TABLE)

    # 3. Build Data Dictionary DataFrame
    df_dictionary = pd.DataFrame(DATA_DICTIONARY_TABLE)

    # 4. Generate Full Pairwise Rotation Matrix (N x N)
    matrix_rows = []
    seen_pairs = set()

    for p_key in crop_keys:
        for n_key in crop_keys:
            pair_id = (p_key, n_key)
            if pair_id in seen_pairs:
                raise ValueError(f"FATAL: Duplicate pair detected for {pair_id}!")
            seen_pairs.add(pair_id)

            eval_res = evaluate_pair(p_key, n_key)
            matrix_rows.append(eval_res)

    df_matrix = pd.DataFrame(matrix_rows)
    print(f"Generated {len(df_matrix)} directional rotation pair records.")

    # 6. Comprehensive Dataset Validation
    print("\n--- Running Dataset Validation Checks ---")
    
    # Check 1: Duplicate check
    dupes = df_matrix.duplicated(subset=["previous_crop", "new_crop"]).sum()
    assert dupes == 0, f"Validation Failed: {dupes} duplicate pairs found!"
    print("[PASS] 0 duplicate previous_crop -> new_crop pairs.")

    # Check 2: Null / Missing values
    null_counts = df_matrix.isnull().sum().to_dict()
    for col, count in null_counts.items():
        assert count == 0, f"Validation Failed: Column {col} contains {count} null values!"
    print("[PASS] 0 missing/null values across all columns.")

    # Check 3: Score bounds check
    invalid_scores = df_matrix[(df_matrix["rotation_score"] < 0.0) | (df_matrix["rotation_score"] > 1.0)]
    assert len(invalid_scores) == 0, f"Validation Failed: {len(invalid_scores)} scores outside [0.0, 1.0] range!"
    print("[PASS] All rotation_scores within valid [0.00, 1.00] range.")

    # Check 4: Valid Categorical Enums
    valid_compat = {"High", "Medium", "Low"}
    valid_recs = {"Prefer", "Consider", "Avoid"}
    valid_conf = {"High", "Medium", "Low"}

    assert set(df_matrix["compatibility"].unique()).issubset(valid_compat), "Invalid compatibility values!"
    assert set(df_matrix["recommendation"].unique()).issubset(valid_recs), "Invalid recommendation values!"
    assert set(df_matrix["confidence"].unique()).issubset(valid_conf), "Invalid confidence values!"
    print("[PASS] All compatibility, recommendation, and confidence values strictly adhere to allowed enums.")

    # 7. Export to Excel Workbook with 4 Styled Sheets
    print(f"\nWriting Excel Workbook to {XLSX_PATH}...")
    with pd.ExcelWriter(XLSX_PATH, engine="openpyxl") as writer:
        df_matrix.to_excel(writer, sheet_name="Rotation_Matrix", index=False)
        df_characteristics.to_excel(writer, sheet_name="Crop_Characteristics", index=False)
        df_rules.to_excel(writer, sheet_name="Rotation_Rules", index=False)
        df_dictionary.to_excel(writer, sheet_name="Data_Dictionary", index=False)

    # Style Excel Workbook with professional agricultural formatting
    wb = openpyxl.load_workbook(XLSX_PATH)
    header_fill = PatternFill(start_color="1B4332", end_color="1B4332", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    thin_border = Border(
        left=Side(style='thin', color='DDE5DF'),
        right=Side(style='thin', color='DDE5DF'),
        top=Side(style='thin', color='DDE5DF'),
        bottom=Side(style='thin', color='DDE5DF')
    )

    for sheetname in wb.sheetnames:
        ws = wb[sheetname]
        ws.views.sheetView[0].showGridLines = True
        
        # Style Header
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        # Style Rows and Auto-fit column widths
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = min(45, max(max_len + 4, 12))

    wb.save(XLSX_PATH)
    print(f"[PASS] Successfully generated and styled {XLSX_PATH} (4 sheets).")

    # 8. Export Runtime CSV for Instant In-Memory Startup
    df_matrix.to_csv(CSV_PATH, index=False)
    print(f"[PASS] Successfully generated runtime CSV: {CSV_PATH}")
    print("\n==========================================================")
    print("DATASET GENERATION AND VALIDATION COMPLETED 100% SUCCESFULLY!")
    print("==========================================================")

if __name__ == "__main__":
    generate_dataset()
