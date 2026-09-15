"""Crop Rotation Service for CropMitra.

Provides deterministic agronomic evaluation for crop sequences based on the
curated and validated crop rotation matrix.
Loads the runtime CSV dataset into an in-memory hash map at startup for O(1) lookups.
"""

from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from backend.ml.crop_normalizer import normalize_crop_name

logger = logging.getLogger("cropmitra.rotation")

# In-memory rotation registry: (norm_prev, norm_new) -> rotation detail dict
_ROTATION_CACHE: Dict[tuple[str, str], Dict[str, Any]] = {}
_INITIALIZED: bool = False

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
ROTATION_CSV_PATH = DATA_DIR / "crop_rotation_matrix.csv"

FALLBACK_ROTATION: Dict[str, Any] = {
    "rotation_score": 0.50,
    "compatibility": "Unknown",
    "recommendation": "Consider",
    "reason": "No specific rotation information is available for this crop pair.",
    "confidence": "Low",
    "rule_applied": "UNKNOWN_PAIR_FALLBACK",
}


def load_rotation_data(csv_path: Optional[Path] = None) -> None:
    """Load normalized rotation matrix CSV into memory once."""
    global _ROTATION_CACHE, _INITIALIZED
    path = csv_path or ROTATION_CSV_PATH

    if not path.exists():
        logger.warning(
            "Rotation matrix CSV not found at %s. Rotation service will use fallbacks.",
            path,
        )
        _ROTATION_CACHE = {}
        _INITIALIZED = True
        return

    cache: Dict[tuple[str, str], Dict[str, Any]] = {}
    try:
        with open(path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                prev_crop = row.get("previous_crop", "").strip()
                new_crop = row.get("new_crop", "").strip()
                if not prev_crop or not new_crop:
                    continue

                norm_prev = normalize_crop_name(prev_crop)
                norm_new = normalize_crop_name(new_crop)

                try:
                    score = float(row.get("rotation_score", 0.50))
                except (ValueError, TypeError):
                    score = 0.50

                cache[(norm_prev, norm_new)] = {
                    "previous_crop": prev_crop,
                    "new_crop": new_crop,
                    "rotation_score": score,
                    "compatibility": row.get("compatibility", "Neutral"),
                    "recommendation": row.get("recommendation", "Consider"),
                    "reason": row.get("rotation_reason") or row.get("reason", "Standard rotation sequence."),
                    "confidence": row.get("confidence", "Medium"),
                    "rule_applied": row.get("rule_applied", ""),
                }

        _ROTATION_CACHE = cache
        _INITIALIZED = True
        logger.info("Loaded %d crop rotation pairs into memory.", len(_ROTATION_CACHE))
    except Exception as exc:
        logger.error("Failed to load crop rotation matrix: %s", exc)
        _ROTATION_CACHE = {}
        _INITIALIZED = True


# Preload rotation matrix upon module import
load_rotation_data()


def get_rotation_details(previous_crop: Optional[str], new_crop: Optional[str]) -> Dict[str, Any]:
    """Return full rotation metadata for a directional (previous_crop -> new_crop) pair.

    Gracefully falls back to neutral unknown profile if either crop is unspecified or not found.
    """
    if not _INITIALIZED:
        load_rotation_data()

    if not previous_crop or not new_crop:
        res = dict(FALLBACK_ROTATION)
        res["previous_crop"] = previous_crop or "None"
        res["new_crop"] = new_crop or "None"
        return res

    norm_prev = normalize_crop_name(previous_crop)
    norm_new = normalize_crop_name(new_crop)

    if (norm_prev, norm_new) in _ROTATION_CACHE:
        return dict(_ROTATION_CACHE[(norm_prev, norm_new)])

    # Crop pair is unknown / unlisted
    res = dict(FALLBACK_ROTATION)
    res["previous_crop"] = previous_crop
    res["new_crop"] = new_crop
    return res


def get_rotation_score(previous_crop: Optional[str], new_crop: Optional[str]) -> float:
    """Return normalized rotation compatibility score [0.0 - 1.0]."""
    details = get_rotation_details(previous_crop, new_crop)
    return float(details.get("rotation_score", 0.50))


def get_rotation_compatibility(previous_crop: Optional[str], new_crop: Optional[str]) -> str:
    """Return categorical compatibility: 'High', 'Medium', 'Low', or 'Unknown'."""
    details = get_rotation_details(previous_crop, new_crop)
    return str(details.get("compatibility", "Unknown"))


def get_rotation_recommendation(previous_crop: Optional[str], new_crop: Optional[str]) -> str:
    """Return recommendation directive: 'Prefer', 'Consider', 'Avoid', or 'Neutral'."""
    details = get_rotation_details(previous_crop, new_crop)
    return str(details.get("recommendation", "Consider"))


def get_rotation_reason(previous_crop: Optional[str], new_crop: Optional[str]) -> str:
    """Return concise agronomic explanation for this sequence."""
    details = get_rotation_details(previous_crop, new_crop)
    return str(details.get("reason", "No specific rotation information is available for this crop pair."))
