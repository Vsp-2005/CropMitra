"""
Train Fertilizer Recommendation Model for CropMitra.
Trains a classifier on fertilizer.csv predicting recommended fertilizer based on Soil Type, Crop Type, N, P, K.
Also saves fertilizer nutrient profile and application guidelines.
"""
import os
import json
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "fertilizer.csv")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "fertilizer_model.joblib")
METADATA_PATH = os.path.join(MODEL_DIR, "fertilizer_meta.json")

# Standard fertilizer composition and agronomic guidance
FERTILIZER_GUIDELINES = {
    "Urea": {
        "full_name": "Urea (46-0-0)",
        "npk_ratio": "46% Nitrogen, 0% Phosphorus, 0% Potassium",
        "guidance": "High nitrogen source. Apply in split doses (e.g., basal and top-dressing during active vegetative growth). Avoid applying immediately before heavy rain to prevent leaching."
    },
    "DAP": {
        "full_name": "Di-Ammonium Phosphate (18-46-0)",
        "npk_ratio": "18% Nitrogen, 46% Phosphorus, 0% Potassium",
        "guidance": "Primary source of root-promoting phosphorus and starter nitrogen. Best applied at sowing or basal stage near the root zone."
    },
    "14-35-14": {
        "full_name": "NPK Complex (14-35-14)",
        "npk_ratio": "14% Nitrogen, 35% Phosphorus, 14% Potassium",
        "guidance": "High-phosphorus balanced complex. Suitable for pulse, oilseed, and root crops needing early root establishment and strong stalk formation."
    },
    "28-28": {
        "full_name": "NPK Complex (28-28-0)",
        "npk_ratio": "28% Nitrogen, 28% Phosphorus, 0% Potassium",
        "guidance": "Balanced nitrogen and phosphorus formula for vegetative growth and tillering in cereal crops."
    },
    "17-17-17": {
        "full_name": "Complete Balanced NPK (17-17-17)",
        "npk_ratio": "17% Nitrogen, 17% Phosphorus, 17% Potassium",
        "guidance": "Equal-ratio complete fertilizer. Suitable across diverse soil types for balanced leaf growth, flowering, and drought resistance."
    },
    "20-20": {
        "full_name": "Ammonium Phosphate Sulphate (20-20-0-13)",
        "npk_ratio": "20% Nitrogen, 20% Phosphorus, 0% Potassium + Sulphur",
        "guidance": "Supplies nitrogen, phosphorus, and essential sulphur. Highly beneficial for oilseeds, pulses, and cruciferous crops."
    },
    "10-26-26": {
        "full_name": "High Potassium NPK (10-26-26)",
        "npk_ratio": "10% Nitrogen, 26% Phosphorus, 26% Potassium",
        "guidance": "High potassium and phosphorus ratio. Promotes fruit/grain development, root strength, and pest/disease resistance."
    }
}

def train_and_save():
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    print(f"Loading fertilizer dataset from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    # Standardize column names
    df.columns = [c.strip() for c in df.columns]
    
    # Feature columns: Soil Type, Crop Type, Nitrogen, Potassium, Phosphorous
    # Map column names
    cat_features = ['Soil Type', 'Crop Type']
    num_features = ['Nitrogen', 'Potassium', 'Phosphorous']
    
    X = df[cat_features + num_features]
    y = df['Fertilizer Name']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), cat_features)
        ],
        remainder='passthrough'
    )
    
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("Training Fertilizer Model...")
    pipeline.fit(X_train, y_train)
    
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Fertilizer Model Accuracy: {acc * 100:.2f}%")
    
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Saved trained fertilizer model to {MODEL_PATH}")
    
    # Calculate average N, P, K requirement baseline per crop type from dataset
    crop_nutrients = df.groupby('Crop Type')[['Nitrogen', 'Phosphorous', 'Potassium']].mean().round(1).to_dict(orient='index')
    
    metadata = {
        "accuracy": float(acc),
        "fertilizer_types": [str(x) for x in df['Fertilizer Name'].unique()],
        "soil_types": [str(x) for x in df['Soil Type'].unique()],
        "crop_types": [str(x) for x in df['Crop Type'].unique()],
        "guidelines": FERTILIZER_GUIDELINES,
        "crop_nutrients": crop_nutrients
    }
    
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved fertilizer metadata to {METADATA_PATH}")

if __name__ == "__main__":
    train_and_save()
