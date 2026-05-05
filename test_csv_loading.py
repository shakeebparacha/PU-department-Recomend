#!/usr/bin/env python
"""
Test script to verify CSV data loading works correctly
"""
import os
import sys
from pathlib import Path

os.chdir(Path(__file__).parent)
sys.path.insert(0, str(Path(__file__).parent))

# Test basic CSV loading without Django
import pandas as pd

data_dir = Path(__file__).parent / 'data'
csv_files = list(data_dir.glob('*.csv'))

print("CSV Loading Test")
print("=" * 50)
print(f"Data directory: {data_dir}")
print(f"CSV files found: {len(csv_files)}")

if csv_files:
    for csv_file in csv_files:
        print(f"\nTesting: {csv_file.name}")
        try:
            df = pd.read_csv(csv_file)
            print(f"  [OK] Loaded successfully")
            print(f"  - Rows: {len(df)}")
            print(f"  - Columns: {len(df.columns)}")
            print(f"  - Column names: {list(df.columns)}")
            
            if 'Merit_Percentage' in df.columns:
                valid_rows = len(df[df['Merit_Percentage'] > 0])
                print(f"  - Valid merit data rows: {valid_rows}")
                print(f"  [OK] Merit_Percentage column found and valid")
            else:
                print(f"  [FAIL] Merit_Percentage column NOT found")
        except Exception as e:
            print(f"  [FAIL] Error: {e}")
else:
    print("FAIL: No CSV files found in data directory!")
    sys.exit(1)

print("\n" + "=" * 50)
print("CSV loading test completed successfully!")
