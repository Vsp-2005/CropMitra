"""
Live Server End-to-End Verification for CropMitra V2.
"""
import urllib.request
import json

def verify_all_v2():
    print("--- 1. Verifying Vite Frontend Server ---")
    with urllib.request.urlopen('http://localhost:5173/') as resp:
        html = resp.read().decode('utf-8')
        assert '<title>CropMitra' in html
        print("[PASS] Vite frontend server is live on http://localhost:5173/")

    print("\n--- 2. Verifying FastAPI Backend & Health ---")
    with urllib.request.urlopen('http://127.0.0.1:8000/health') as resp:
        data = json.loads(resp.read().decode('utf-8'))
        assert data['status'] == 'healthy'
        print("[PASS] Backend health endpoint: healthy on http://127.0.0.1:8000")

    print("\n--- 3. Verifying /api/locations/states ---")
    with urllib.request.urlopen('http://127.0.0.1:8000/api/locations/states') as resp:
        states = json.loads(resp.read().decode('utf-8'))
        assert len(states) >= 30
        assert "Maharashtra" in states
        print(f"[PASS] /api/locations/states returned {len(states)} states")

    print("\n--- 4. Verifying /api/locations/districts?state=Maharashtra ---")
    with urllib.request.urlopen('http://127.0.0.1:8000/api/locations/districts?state=Maharashtra') as resp:
        districts = json.loads(resp.read().decode('utf-8'))
        assert len(districts) >= 10
        print(f"[PASS] /api/locations/districts (Maharashtra) returned {len(districts)} districts: {districts[:5]}")

    print("\n--- 5. Verifying /api/locations/crops?state=Maharashtra&district=Kolhapur ---")
    with urllib.request.urlopen('http://127.0.0.1:8000/api/locations/crops?state=Maharashtra&district=Kolhapur') as resp:
        data = json.loads(resp.read().decode('utf-8'))
        crops = data['crops'] if isinstance(data, dict) else data
        assert isinstance(crops, list)
        assert "Sugarcane" in crops
        assert "Soybean" in crops
        assert "Rice" in crops
        print(f"[PASS] /api/locations/crops (Kolhapur, Maharashtra) returned {len(crops)} crops: {crops}")

    print("\n--- 6. Verifying /api/recommend (Maharashtra + Pune) ---")
    req = urllib.request.Request(
        'http://127.0.0.1:8000/api/recommend',
        data=json.dumps({
            'state': 'Maharashtra',
            'district': 'Pune',
            'water_availability': 'medium',
            'soil_type': 'loamy',
            'previous_crop': 'Maize'
        }).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as resp:
        rec_res = json.loads(resp.read().decode('utf-8'))
        assert rec_res['success'] is True
        recs = rec_res['recommendations']
        assert len(recs) == 3
        print("[PASS] /api/recommend returned top 3 candidates:")
        for idx, r in enumerate(recs):
            print(f"       #{idx+1}: {r['crop']} (Suitability: {r['suitability']}, Score: {r['final_score']}/10, Location Supported: {r['location_supported']})")

    print("\n--- 7. Verifying /api/fertilizer ---")
    top_crop = recs[0]['crop']
    req_fert = urllib.request.Request(
        'http://127.0.0.1:8000/api/fertilizer',
        data=json.dumps({'crop': top_crop, 'soil_type': 'Loamy', 'nitrogen': 40, 'phosphorus': 20, 'potassium': 20}).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req_fert) as resp:
        fert_res = json.loads(resp.read().decode('utf-8'))
        assert fert_res['success'] is True
        print(f"[PASS] /api/fertilizer for {top_crop} returned: {fert_res['fertilizer_name']} ({fert_res['full_name']})")

    print("\n--- 8. Verifying /api/recommendations/save ---")
    req_save = urllib.request.Request(
        'http://127.0.0.1:8000/api/recommendations/save',
        data=json.dumps({
            'state': 'Maharashtra',
            'district': 'Pune',
            'water_availability': 'Medium',
            'soil_type': 'Loamy',
            'previous_crop': 'Maize',
            'recommended_crop': top_crop,
            'model_score': 0.88,
            'final_score': recs[0]['final_score'],
            'fertilizer_name': fert_res['fertilizer_name'],
            'nitrogen': 40,
            'phosphorus': 20,
            'potassium': 20
        }).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req_save) as resp:
        save_res = json.loads(resp.read().decode('utf-8'))
        assert save_res['success'] is True
        print(f"[PASS] /api/recommendations/save saved record id={save_res['id']}")

    print("\n=======================================================")
    print("ALL CROPMITRA V2 LIVE INTEGRATION CHECKS PASSED 100%!")
    print("=======================================================")

if __name__ == '__main__':
    verify_all_v2()
