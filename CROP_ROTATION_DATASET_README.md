# CropMitra — Crop Rotation Dataset & Agronomic Decision Support

> **Disclaimer**: This dataset provides general agronomic decision-support rules. It does not guarantee crop performance and should not replace local agronomic advice or soil testing.

---

## 1. Dataset Purpose
The CropMitra Crop Rotation Dataset provides deterministic, explainable agronomic sequence rules for Indian agricultural systems. Crop rotation is an essential sustainable farming practice that prevents soil nutrient depletion, breaks pest/weed cycles, enhances biological nitrogen fixation, and optimizes root zone utilization.

This dataset bridges machine learning predictions and field-level rotational planning by evaluating the biological compatibility of introducing candidate crops after specific previously harvested crops.

---

## 2. Dataset Structure
The dataset is published in two formats:
1. **Multi-sheet Excel Workbook**: `backend/data/crop_rotation_dataset.xlsx`
2. **Normalized Runtime Matrix**: `backend/data/crop_rotation_matrix.csv`

### Excel Workbook Sheets:
- **Sheet 1 (`Rotation_Matrix`)**: Full directional crop pair evaluation matrix (1,444+ rows) mapping `(previous_crop -> new_crop)` with rotation scores, compatibility tiers, directives, confidence, and agronomic reasoning.
- **Sheet 2 (`Crop_Characteristics`)**: Canonical agronomic attributes for all 51 crops (crop group, rooting depth, nutrient demand, nitrogen fixation capability, water requirements, rotation role, and common rotation benefits).
- **Sheet 3 (`Rotation_Rules`)**: The 14 explicit agronomic priority rules driving the matrix generation.
- **Sheet 4 (`Data_Dictionary`)**: Schema definition, allowed enums, data types, and scoring definitions for all dataset fields.

---

## 3. Crop Characteristics & Classification
The vocabulary is canonically extracted and normalized from `CropDataset-Enhanced.csv` (and related national agricultural registries) across 51 unique crops:

| Field Name | Description | Example Values |
|---|---|---|
| `crop` | Canonical Crop Display Name | `Soybean`, `Sugarcane`, `Wheat`, `Rice` |
| `crop_group` | Functional agronomic category | `Legume`, `Cereal`, `Cash Crop / Heavy Feeder`, `Oilseed`, `Fibre`, `Vegetable (Solanaceous)` |
| `rooting_type` | Root structure depth | `Deep Taproot`, `Fibrous / Shallow`, `Medium Taproot` |
| `nutrient_demand` | Baseline nutrient consumption | `High`, `Medium`, `Low` |
| `nitrogen_fixing` | Biological N-fixation ability | `Yes`, `No` |
| `water_demand` | Evapotranspiration requirement | `High`, `Medium`, `Low` |
| `rotation_role` | Functional role in sequence | `Soil Builder`, `Exhaustive Crop`, `Nutrient Restorer`, `Pest Break` |

---

## 4. Directional Rotation Rules Hierarchy
Crop rotation is fundamentally directional ($A \rightarrow B \neq B \rightarrow A$). The rules are prioritized deterministically:

1. **RULE_SAME_CROP_MONOCULTURE (Priority 10)**: Consecutive cropping of identical species (`Wheat -> Wheat`, `Rice -> Rice`, `Maize -> Maize`, `Cotton -> Cotton`) increases pest/disease risk and depletes specific root zones.
   - *Score*: `0.30 - 0.35`, *Compatibility*: `Low`, *Recommendation*: `Avoid`.
2. **RULE_SOLANACEOUS_MONOCULTURE (Priority 9)**: Rotating within the Solanaceae family (`Potato -> Tomato`, `Tomato -> Chilli`) perpetuates shared blight, wilt, and nematode cycles.
   - *Score*: `0.35`, *Compatibility*: `Low`, *Recommendation*: `Avoid`.
3. **RULE_SUGARCANE_TO_LEGUME (Priority 8)**: Sugarcane is an exhaustive long-duration feeder. Following it with nitrogen-fixing legumes (`Soybean`, `Groundnut`, `Chickpea`, `Lentil`) replenishes topsoil organic matter and biological nitrogen.
   - *Score*: `0.85`, *Compatibility*: `High`, *Recommendation*: `Prefer`.
4. **RULE_SUGARCANE_TO_HEAVY_CEREAL (Priority 7)**: Transitioning directly from Sugarcane to nutrient-demanding cereals (`Maize`, `Rice`) requires intensive fertility management.
   - *Score*: `0.65`, *Compatibility*: `Medium`, *Recommendation*: `Consider`.
5. **RULE_CEREAL_TO_LEGUME (Priority 6)**: Exhaustive shallow-rooted cereals (`Wheat`, `Rice`, `Maize`, `Barley`) rotated with deep-rooted nitrogen-fixing pulses restore soil fertility and break monoculture pest cycles.
   - *Score*: `0.85`, *Compatibility*: `High`, *Recommendation*: `Prefer`.
6. **RULE_LEGUME_TO_CEREAL (Priority 6)**: Cereals planted immediately after legumes leverage residual nitrogen fixed in nodules and benefit from improved soil structure.
   - *Score*: `0.85`, *Compatibility*: `High`, *Recommendation*: `Prefer`.
7. **RULE_FIBRE_TO_LEGUME (Priority 6)**: Cotton/Jute followed by legumes aids biological recovery and prevents soil compaction.
   - *Score*: `0.85`, *Compatibility*: `High`, *Recommendation*: `Prefer`.
8. **RULE_ROOT_DEPTH_COMPLEMENTARITY (Priority 5)**: Alternating deep taproot crops (`Cotton`, `Pigeonpea`, `Mustard`) with shallow fibrous root crops (`Wheat`, `Rice`) optimizes multi-tier soil nutrient and moisture uptake.
   - *Score*: `0.80`, *Compatibility*: `High`, *Recommendation*: `Prefer`.
9. **RULE_CONSECUTIVE_LEGUMES (Priority 5)**: Sequential pulse crops have moderate utility but may harbor root-rot pathogens.
   - *Score*: `0.60`, *Compatibility*: `Medium`, *Recommendation*: `Consider`.
10. **RULE_DEFAULT_BALANCED_ROTATION (Priority 1)**: General cross-group sequences with no acute antagonistic constraints.
    - *Score*: `0.65`, *Compatibility*: `Medium`, *Recommendation*: `Consider`.

---

## 5. Scoring & Categorical Meaning

### Numerical Scores
Component scores are normalized strictly in the $[0.0, 1.0]$ range:
- **High Compatibility (`0.80 - 0.85`)**: Agronomically synergistic sequence offering restorative benefits.
- **Medium Compatibility (`0.55 - 0.70`)**: Feasible sequence requiring balanced fertilization.
- **Low Compatibility (`0.30 - 0.40`)**: Monoculture or disease-carrying succession requiring strict mitigation.

### Categorical Tiers
- **Compatibility**: `High` | `Medium` | `Low` | `Unknown`
- **Recommendation Directive**: `Prefer` | `Consider` | `Avoid` | `Neutral`
- **Confidence Level**: `High` | `Medium` | `Low`

---

## 6. System Architecture & Multi-Factor Integration

```
                         FARMER INPUTS
                      (State, District, Soil, Water, Previous Crop)
                            │
                            ▼
                   State + District
                            │
                            ▼
              CropDataset-Enhanced.csv
             (Location Crop Registry Filter)
                            │
                  Location-Eligible Crops
                            │
                            ▼
             Water + Soil + Field Parameters
                            │
                            ▼
                     ML RANDOM FOREST
                   (Condition Suitability)
                            │
                     Candidate ML Scores
                            │
                            ▼
                 Water & Soil Compatibility
                            │
                            ▼
                  Crop Rotation Service
             (Previous Crop -> Candidate Crop)
                            │
                            ▼
                  Normalized Blended Score:
       base_score = 0.50*ml + 0.30*condition + 0.20*rotation
                            │
                            ▼
                 Location Priority Boost
                            │
                            ▼
              Final Recommendation & Fertilizer Plan
```

### Key Architectural Safeguards:
1. **Location Eligibility Primacy**: Location filtering from `CropDataset-Enhanced.csv` ensures only regionally adapted and cultivated crops are recommended. Rotation compatibility **cannot** introduce an unadapted crop into a district.
2. **Deterministic Outputs**: Elimination of non-deterministic random selection ensures stable, reproducible advice across identical field inputs.
3. **Safe Unknown Fallback**: Unrecognized crop pairs default to `score = 0.50`, `compatibility = "Unknown"`, `recommendation = "Consider"`, preventing pipeline crashes.
4. **Fast Runtime Performance**: The entire runtime matrix is loaded into an in-memory hash map at startup, enabling sub-millisecond $O(1)$ lookups per candidate.

---

## 7. Limitations & Context
- This decision-support system relies on general macro-level agronomic rules and district historical registries.
- Micro-climatic shifts, specific field pest outbreaks, local market demand, and irrigation infrastructure must be evaluated by local agricultural extension officers.
