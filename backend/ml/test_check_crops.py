import pandas as pd
import os

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "CropDataset-Enhanced.csv")
df = pd.read_csv(CSV_PATH)

for loc in ['Akola', 'Kolhapur', 'Latur', 'Nagpur', 'Chhatrapati Sambhaji Nagar', 'Amravati', 'Pune', 'Nashik']:
    match = df[df['Address'].str.contains(loc, case=False, na=False)]
    for _, r in match.iterrows():
        print(f"{loc} ({r['Region']}) -> {r['Crop']}")
