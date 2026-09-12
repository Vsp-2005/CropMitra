"""
Train Crop Recommendation Model for CropMitra.
Trains a Random Forest Classifier on soil info.csv with calibrated probabilities.
Saves model to backend/ml/models/crop_model.joblib and metadata to crop_metadata.json.
"""
import os
import json
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "soil info.csv")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "crop_model.joblib")
METADATA_PATH = os.path.join(MODEL_DIR, "crop_model_meta.json")

def train_and_save():
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    print(f"Loading crop dataset from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    target = 'label'
    
    X = df[features]
    y = df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("Training Random Forest Classifier...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        random_state=42,
        class_weight='balanced'
    )
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Test Accuracy: {acc * 100:.2f}%")
    
    # Save model
    joblib.dump(model, MODEL_PATH)
    print(f"Saved trained crop model to {MODEL_PATH}")
    
    # Save metadata
    unique_crops = sorted(list(df['label'].unique()))
    metadata = {
        "features": features,
        "classes": [str(c) for c in model.classes_],
        "all_crops": [str(c) for c in unique_crops],
        "accuracy": float(acc),
        "total_samples": int(len(df))
    }
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved model metadata to {METADATA_PATH}")

if __name__ == "__main__":
    train_and_save()
