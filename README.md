# CropMitra V2 — Location-Aware Agricultural Decision-Support System

CropMitra V2 is a clean, minimal, and explainable agricultural decision-support web application that recommends suitable crops and tailored fertilizer management plans based on field conditions and district-level location data.

```
                         ┌──────────────────┐
                         │     React UI     │
                         │                  │
                         │ Home             │
                         │ Crop Advisor     │
                         │ Result (Top 3)   │
                         │ Fertilizer Plan  │
                         │ Guides & About   │
                         │ Light/Dark Mode  │
                         └────────┬─────────┘
                                  │
                              REST API
                                  │
                         ┌────────▼─────────┐
                         │     FastAPI      │
                         │                  │
                         │ Validation       │
                         │ Location APIs    │
                         │ Recommendation   │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
             ┌──────▼──────┐             ┌─────▼──────┐
             │ Crop Service │             │ Fertilizer │
             │              │             │  Service   │
             └──────┬───────┘             └─────┬──────┘
                    │                            │
             ┌──────▼───────┐             ┌─────▼──────┐
             │ Crop ML Model│             │ Fertilizer │
             │ Random Forest│             │ Model/Logic│
             └──────┬───────┘             └────────────┘
                    │
             ┌──────▼────────┐
             │ Location Layer│ (CropDataset-Enhanced.csv)
             └──────┬─────────┘
                    │
             ┌──────▼────────┐
             │ Rotation Layer│
             └──────┬─────────┘
                    │
                    ▼
          Top 3 Ranked Recommendations
                    │
                    ▼
             ┌──────────────┐
             │ SQLite (V2)  │
             │ SQLAlchemy   │
             └──────────────┘
```

---

## 🌾 V2 New Features

- **Location-Aware Recommendation**: Seamlessly selects State and District (dynamically populated from `CropDataset-Enhanced.csv` across 36 Indian states & 728 districts).
- **Multiple Ranked Recommendations**: Returns Top 3 candidate crops with explicit suitability ratings (`High`, `Medium`, `Low`) and transparent composite scores (e.g. `8.6 / 10`).
- **Real Dark Mode & Theme Toggle**: High-contrast, accessibility-compliant dark theme tokens with `localStorage` persistence and zero-flash system preference fallback.
- **Meaningful Color System**: Purposeful color indicators (Green for High, Amber for Medium, Muted Red for Low) paired with clear text labels and icons.
- **Explainable Recommendation Reason**: Integrates location verification, water matching, soil pH, and rotation benefits.
- **Database Model V2**: Stores state, district, model score, final composite score, and model version (`2.0.0`).

---

## 🛠️ Tech Stack

- **Frontend**: React 18, Vite, Vanilla CSS Design System, Lucide Icons.
- **Backend**: Python 3.10+, FastAPI, Pydantic v2, Uvicorn.
- **Machine Learning**: Scikit-Learn (Random Forest), Pandas, NumPy, Joblib.
- **Database**: SQLite (local development) / PostgreSQL (production) via SQLAlchemy ORM.

---

## 📂 Project Structure

```text
p1/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py          # /api/recommend, /api/fertilizer, /api/crops, /api/recommendations
│   │   ├── database/
│   │   │   ├── session.py         # SQLAlchemy engine & session maker
│   │   │   └── models.py          # Recommendation ORM model
│   │   ├── schemas/
│   │   │   └── schemas.py         # Pydantic request/response models with validation
│   │   ├── services/
│   │   │   ├── crop_service.py    # Combines ML inference + agronomic rotation layer
│   │   │   └── fertilizer_service.py # Fertilizer nutrient calculation + application guidance
│   │   ├── config.py              # Environment configuration & CORS
│   │   └── main.py                # FastAPI entrypoint
│   ├── ml/
│   │   ├── preprocessing.py       # Agronomic profiles and rotation logic
│   │   ├── train_crop_model.py    # Crop Random Forest training script
│   │   ├── train_fert_model.py    # Fertilizer training script
│   │   └── models/                # Trained .joblib models and metadata JSON
│   ├── data/                      # Training datasets (soil info.csv, fertilizer.csv)
│   ├── requirements.txt
│   └── test_backend.py            # Automated integration test suite
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   └── Footer.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── CropAdvisor.jsx
│   │   │   ├── FarmingGuides.jsx
│   │   │   └── About.jsx
│   │   ├── services/
│   │   │   └── api.js             # API client
│   │   ├── App.jsx
│   │   ├── index.css              # Custom design system & print styles
│   │   └── main.jsx
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
│
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Quickstart Guide

### 1. Backend Setup & ML Training

From the root directory:

```bash
# 1. Install backend dependencies
pip install -r backend/requirements.txt

# 2. Train the ML models
python backend/ml/train_crop_model.py
python backend/ml/train_fert_model.py

# 3. Run automated backend test suite
python backend/test_backend.py

# 4. Start the FastAPI backend server
python -m uvicorn backend.app.main:app --reload --port 8000
```

The API will be available at `http://127.0.0.1:8000` and interactive Swagger docs at `http://127.0.0.1:8000/docs`.

---

### 2. Frontend Setup

From a new terminal:

```bash
# 1. Navigate to frontend folder
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 🔌 API Endpoints Contract

### 1. Get Available Crops
- **Endpoint**: `GET /api/crops`
- **Response**: `["Rice", "Wheat", "Maize", "Soybean", ...]`

### 2. Crop Recommendation
- **Endpoint**: `POST /api/recommend`
- **Request Body**:
  ```json
  {
    "water_availability": "medium",
    "soil_type": "loamy",
    "previous_crop": "maize"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "recommendation": {
      "crop": "Soybean",
      "suitability": "High",
      "score": 92,
      "water_requirement": "Medium",
      "soil_type": "Loamy",
      "previous_crop": "Maize",
      "growing_season": "Kharif",
      "reason": "Soybean is highly recommended. Medium water availability aligns with its Medium moisture requirement. Loamy soil provides ideal pH (6.6) and drainage characteristics for Soybean. Optimal succession: Soybean benefits from the nitrogen fixed by preceding Maize."
    }
  }
  ```

### 3. Fertilizer Plan
- **Endpoint**: `POST /api/fertilizer`
- **Request Body**:
  ```json
  {
    "crop": "Soybean",
    "soil_type": "Loamy",
    "nitrogen": 40,
    "phosphorus": 20,
    "potassium": 20
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "crop": "Soybean",
    "soil_type": "Loamy",
    "fertilizer_name": "14-35-14",
    "full_name": "NPK Complex (14-35-14)",
    "nitrogen": 40,
    "phosphorus": 20,
    "potassium": 20,
    "unit": "kg/acre",
    "npk_ratio": "14% Nitrogen, 35% Phosphorus, 14% Potassium",
    "explanation": "Recommended 14-35-14 provides the optimal N-P-K balance required by Soybean in Loamy soil.",
    "guidance": "Apply predominantly as a basal application during final land preparation or sowing. Suitable for soils with medium potassium.",
    "disclaimer": "Fertilizer requirements can vary based on soil testing, crop variety, and local conditions."
  }
  ```

### 4. Save Recommendation
- **Endpoint**: `POST /api/recommendations/save`
- **Response**: `{"success": true, "id": 1, "message": "Recommendation saved successfully."}`

### 5. List Saved Recommendations
- **Endpoint**: `GET /api/recommendations`

---

## 🧪 Testing Instructions

Run the backend verification suite:
```bash
python backend/test_backend.py
```

Build the frontend bundle:
```bash
cd frontend && npm run build
```
