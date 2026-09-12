"""
Comprehensive Automated Test Suite for CropMitra Location-Constrained Recommendations.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health():
    print("Testing GET /health...")
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "healthy"}
    print("[PASS] /health passed.")

def test_locations_api():
    print("\n--- Testing Location APIs ---")
    res = client.get("/api/locations/states")
    assert res.status_code == 200
    states = res.json()
    assert len(states) >= 30
    assert "Maharashtra" in states

    res_mh = client.get("/api/locations/districts?state=Maharashtra")
    assert res_mh.status_code == 200
    dists = res_mh.json()
    assert "Akola" in dists
    assert "Kolhapur" in dists
    assert "Latur" in dists
    print(f"[PASS] /api/locations/states and districts verified.")

def test_1_akola_hard_filter():
    print("\n--- Test 1: Maharashtra + Akola (Hard Location Constraint) ---")
    payload = {
        "state": "Maharashtra",
        "district": "Akola",
        "water_availability": "medium",
        "soil_type": "loamy",
        "previous_crop": "Wheat"
    }
    res = client.post("/api/recommend", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["location"]["district"] == "Akola"
    assert data["location"]["match_level"] == "district"

    recs = data["recommendations"]
    rec_names = [r["crop"].lower() for r in recs]
    print(f"Akola Returned Candidates: {[r['crop'] for r in recs]}")

    # Akola crops in CSV: Cotton, Soybean, Jowar (Sorghum), Wheat, Tur (Pigeon Pea)
    # RICE MUST NEVER BE RETURNED FOR AKOLA
    assert "rice" not in rec_names, "CRITICAL ERROR: Rice was returned for Akola despite not being in Akola's location crop list!"
    
    # Verify all returned crops are from Akola's valid set
    akola_valid = {"cotton", "soybean", "jowar (sorghum)", "wheat", "pigeon peas (tur)", "jowar", "tur"}
    for r in recs:
        assert r["crop"].lower() in akola_valid or any(v in r["crop"].lower() for v in ["soybean", "cotton", "jowar", "wheat", "pigeon"]), f"Unexpected crop {r['crop']} for Akola"
    print("[PASS] Test 1 Passed: Rice correctly excluded; only Akola location-supported crops recommended.")

def test_2_kolhapur_hard_filter():
    print("\n--- Test 2: Maharashtra + Kolhapur ---")
    # Kolhapur crops in CSV: Sugarcane, Rice, Groundnut, Soybean, Jowar (Sorghum)
    payload = {
        "state": "Maharashtra",
        "district": "Kolhapur",
        "water_availability": "high",
        "soil_type": "clay",
        "previous_crop": "Wheat"
    }
    res = client.post("/api/recommend", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["location"]["match_level"] == "district"
    recs = data["recommendations"]
    print(f"Kolhapur Returned Candidates: {[r['crop'] for r in recs]}")

    kolhapur_valid_roots = ["sugarcane", "rice", "groundnut", "soybean", "jowar"]
    for r in recs:
        c_low = r["crop"].lower()
        assert any(root in c_low for root in kolhapur_valid_roots), f"Unexpected crop {r['crop']} for Kolhapur"
    print("[PASS] Test 2 Passed: Kolhapur returned location-supported crops (Sugarcane, Rice, Groundnut, Soybean, Jowar).")

def test_3_latur_hard_filter():
    print("\n--- Test 3: Maharashtra + Latur ---")
    # Latur crops in CSV: Soybean, Cotton, Jowar (Sorghum), Wheat, Tur (Pigeon Pea)
    payload = {
        "state": "Maharashtra",
        "district": "Latur",
        "water_availability": "medium",
        "soil_type": "loamy",
        "previous_crop": "Wheat"
    }
    res = client.post("/api/recommend", json=payload)
    assert res.status_code == 200
    data = res.json()
    recs = data["recommendations"]
    print(f"Latur Returned Candidates: {[r['crop'] for r in recs]}")

    rec_names = [r["crop"].lower() for r in recs]
    assert "rice" not in rec_names, "Rice must not be in Latur's candidate set."
    latur_valid_roots = ["soybean", "cotton", "jowar", "wheat", "pigeon", "tur"]
    for r in recs:
        c_low = r["crop"].lower()
        assert any(root in c_low for root in latur_valid_roots), f"Unexpected crop {r['crop']} for Latur"
    print("[PASS] Test 3 Passed: Latur candidates strictly match location crop registry.")

def test_4_unknown_district_fallback():
    print("\n--- Test 4: Unknown District State-Level Fallback ---")
    payload = {
        "state": "Maharashtra",
        "district": "UnknownField777",
        "water_availability": "medium",
        "soil_type": "loamy",
        "previous_crop": "Wheat"
    }
    res = client.post("/api/recommend", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["location"]["match_level"] == "state"
    assert data["location"]["location_supported"] is True
    assert len(data["recommendations"]) == 3
    print(f"[PASS] Test 4 Passed: Unknown district correctly fell back to match_level='state'.")

def test_5_unknown_state_ml_fallback():
    print("\n--- Test 5: Unknown State ML-Only Fallback ---")
    payload = {
        "state": "AtlantisRegion",
        "district": "PlotXYZ",
        "water_availability": "medium",
        "soil_type": "loamy",
        "previous_crop": "Wheat"
    }
    res = client.post("/api/recommend", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["location"]["match_level"] == "none"
    assert data["location"]["location_supported"] is False
    assert len(data["recommendations"]) == 3
    print(f"[PASS] Test 5 Passed: Unknown location correctly fell back to match_level='none'.")

def test_database_and_fertilizer():
    print("\n--- Test 6: Database & Fertilizer Integration ---")
    fert_res = client.post("/api/fertilizer", json={
        "crop": "Soybean",
        "soil_type": "Loamy",
        "nitrogen": 40,
        "phosphorus": 20,
        "potassium": 20
    })
    assert fert_res.status_code == 200

    save_payload = {
        "state": "Maharashtra",
        "district": "Akola",
        "location_match_level": "district",
        "water_availability": "Medium",
        "soil_type": "Loamy",
        "previous_crop": "Wheat",
        "recommended_crop": "Soybean",
        "ml_score": 0.88,
        "final_score": 8.6,
        "fertilizer_name": "14-35-14",
        "nitrogen": 40,
        "phosphorus": 20,
        "potassium": 20
    }
    save_res = client.post("/api/recommendations/save", json=save_payload)
    assert save_res.status_code == 200
    rec_id = save_res.json()["id"]

    list_res = client.get("/api/recommendations")
    assert list_res.status_code == 200
    records = list_res.json()
    matching = [r for r in records if r["id"] == rec_id]
    assert len(matching) == 1
    assert matching[0]["location_match_level"] == "district"
    print(f"[PASS] Database successfully recorded location_match_level='district' for record id={rec_id}")

if __name__ == "__main__":
    test_health()
    test_locations_api()
    test_1_akola_hard_filter()
    test_2_kolhapur_hard_filter()
    test_3_latur_hard_filter()
    test_4_unknown_district_fallback()
    test_5_unknown_state_ml_fallback()
    test_database_and_fertilizer()
    print("\n==================================================================")
    print("ALL 5 HARD-FILTERING & LOCATION CONSTRAINT TESTS PASSED 100%!")
    print("==================================================================")
