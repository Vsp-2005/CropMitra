import pandas as pd
import os

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "CropDataset-Enhanced.csv")

def inspect():
    df = pd.read_csv(CSV_PATH)
    print(f"Total Rows: {len(df)}")
    print("Columns:", df.columns.tolist())
    
    # State / Region summary
    regions = df['Region'].dropna().unique()
    print(f"\nUnique Regions/States ({len(regions)}):", sorted(list(regions)))
    
    # Inspect crop listings
    print("\nSample Rows:")
    for idx, row in df.head(15).iterrows():
        print(f"[{row['Region']}] {row['Address']} -> {row['Crop']}")
        
    print("\nNull values count:")
    print(df.isnull().sum())
    
    # Check crops text values
    all_crops = set()
    for c_text in df['Crop'].dropna():
        # Split by comma
        for item in str(c_text).split(','):
            clean = item.strip()
            if clean and not clean.lower().startswith('urban'):
                all_crops.add(clean)
    print(f"\nExtracted Unique Crop Names ({len(all_crops)}):")
    print(sorted(list(all_crops)))

if __name__ == "__main__":
    inspect()
