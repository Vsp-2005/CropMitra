"""
Location Service for CropMitra.
Extracts, normalizes, and manages location-level crop distributions and district profiles
from CropDataset-Enhanced.csv as an authoritative eligibility constraint.
"""
import os
import re
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Set

from backend.ml.crop_normalizer import normalize_crop_name, canonical_display_name
from backend.ml.preprocessing import CROP_METADATA

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "CropDataset-Enhanced.csv")

def clean_district_name(raw_name: str, state_name: str) -> str:
    """Removes trailing state suffixes, pincodes, or extraneous text from address."""
    name = str(raw_name).strip()
    if "," in name:
        parts = [p.strip() for p in name.split(",")]
        name = parts[0]
    name = re.sub(r"\b\d{6}\b", "", name).strip()
    return name.title().strip()

class LocationService:
    def __init__(self):
        self.state_districts: Dict[str, List[str]] = {}
        self.district_data: Dict[str, Dict[str, Any]] = {}
        self.state_crops: Dict[str, Set[str]] = {}
        self._load_data()

    def _load_data(self):
        if not os.path.exists(DATA_PATH):
            print(f"Warning: Location dataset not found at {DATA_PATH}")
            return

        try:
            df = pd.read_csv(DATA_PATH)
            df = df.dropna(subset=['Region', 'Address'])

            for _, row in df.iterrows():
                raw_state = str(row['Region']).strip()
                raw_addr = str(row['Address']).strip()
                crop_str = str(row.get('Crop', '')).strip()

                if not raw_state or not raw_addr:
                    continue

                state = raw_state.title()
                district = clean_district_name(raw_addr, state)

                if not district:
                    continue

                # Parse crops list from the 'Crop' column
                crops_normalized = set()
                if crop_str and not crop_str.lower().startswith('urban'):
                    # Split comma-separated crops
                    for item in crop_str.split(','):
                        c_clean = item.strip()
                        if c_clean:
                            norm = normalize_crop_name(c_clean)
                            if norm:
                                crops_normalized.add(norm)

                lookup_key = f"{state.lower()}::{district.lower()}"

                if lookup_key not in self.district_data:
                    self.district_data[lookup_key] = {
                        "state": state,
                        "district": district,
                        "supported_crops": crops_normalized
                    }
                else:
                    self.district_data[lookup_key]["supported_crops"].update(crops_normalized)

                if state not in self.state_districts:
                    self.state_districts[state] = []
                    self.state_crops[state] = set()

                if district not in self.state_districts[state]:
                    self.state_districts[state].append(district)

                self.state_crops[state].update(crops_normalized)

            for state in self.state_districts:
                self.state_districts[state].sort()

            print(f"Location Service loaded {len(self.state_districts)} states and {len(self.district_data)} district records.")
        except Exception as e:
            print(f"Error loading location data: {e}")

    def get_states(self) -> List[str]:
        """Returns sorted list of all available states."""
        return sorted(list(self.state_districts.keys()))

    def get_districts(self, state: str) -> List[str]:
        """Returns sorted list of districts for a given state."""
        state_clean = state.strip().title()
        for st, dists in self.state_districts.items():
            if st.lower() == state_clean.lower():
                return dists
        return []

    def get_location_crops(self, state: str, district: str) -> List[str]:
        """Returns display names of crops registered for the selected location."""
        crops, _, _ = self.get_eligible_crops(state, district)
        return [canonical_display_name(c) for c in sorted(crops)]

    def get_eligible_crops(self, state: str, district: str) -> Tuple[List[str], str, bool]:
        """
        Extracts the authoritative eligible candidate crop list for the given location.
        Returns:
            - eligible_crops: List of normalized crop keys
            - match_level: 'district' | 'state' | 'none'
            - is_location_supported: bool
        """
        state_clean = state.strip().lower()
        dist_clean = district.strip().lower()
        key = f"{state_clean}::{dist_clean}"

        # Level 1: Exact District Match
        if key in self.district_data:
            crops = self.district_data[key]["supported_crops"]
            if crops:
                return sorted(list(crops)), "district", True

        # Try searching by district substring
        for lookup_k, data in self.district_data.items():
            if lookup_k.startswith(f"{state_clean}::") and (dist_clean in lookup_k or lookup_k.split("::")[1] in dist_clean):
                crops = data["supported_crops"]
                if crops:
                    return sorted(list(crops)), "district", True

        # Level 2: State-Level Fallback Match
        for st, crops in self.state_crops.items():
            if st.lower() == state_clean:
                if crops:
                    return sorted(list(crops)), "state", True

        # Level 3: Global ML Fallback
        all_crops = list(CROP_METADATA.keys())
        return all_crops, "none", False

location_service = LocationService()
