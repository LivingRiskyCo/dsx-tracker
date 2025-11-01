"""
Clean Opponents_of_Opponents.csv to remove score strings and invalid entries
"""

import pandas as pd
import os

def clean_opponents_of_opponents():
    """Clean the opponents of opponents CSV file"""
    filename = "Opponents_of_Opponents.csv"

    if not os.path.exists(filename):
        print(f"[ERROR] {filename} not found")
        return False

    try:
        # Read the CSV
        df = pd.read_csv(filename, index_col=False)
        print(f"[OK] Loaded {filename} with {len(df)} rows")

        # Check columns
        if len(df.columns) < 2:
            print("[ERROR] CSV doesn't have enough columns")
            return False

        # Get the opponent of opponent column (second column)
        opp_opp_col = df.columns[1]

        # Filter out rows where the opponent_of_opponent looks like a score
        def is_not_score(entry):
            if pd.isna(entry):
                return False
            entry_str = str(entry).strip()

            # Remove spaces and check if it looks like a score (e.g., "4-4", "5-1")
            cleaned = entry_str.replace(' ', '').replace('-', '')
            if cleaned.isdigit() and len(cleaned) == 2:  # Like "44" or "51"
                return False

            # Check for dash pattern
            if ' - ' in entry_str or '-' in entry_str:
                parts = entry_str.replace(' ', '').split('-')
                if len(parts) == 2 and all(part.isdigit() for part in parts):
                    return False

            # Check for common invalid entries
            invalid_entries = ['', '-', 'N/A', 'n/a', 'null', 'NULL']
            if entry_str.lower() in invalid_entries:
                return False

            # Must contain at least 3 characters (likely a team name)
            if len(entry_str) < 3:
                return False

            return True

        # Filter the dataframe
        original_count = len(df)
        df_cleaned = df[df[opp_opp_col].apply(is_not_score)].copy()
        cleaned_count = len(df_cleaned)

        print(f"[OK] Filtered out {original_count - cleaned_count} invalid entries")
        print(f"[OK] Remaining valid entries: {cleaned_count}")

        if cleaned_count > 0:
            # Show some examples
            unique_opps = df_cleaned[opp_opp_col].dropna().unique()
            print(f"[OK] Unique opponents of opponents: {len(unique_opps)}")
            print("Sample cleaned entries:"
            for opp in sorted(unique_opps)[:10]:
                print(f"  - {opp}")

            # Save cleaned version
            df_cleaned.to_csv(filename, index=False)
            print(f"[OK] Saved cleaned data to {filename}")

            return True
        else:
            print("[WARNING] No valid entries remaining after cleaning")
            return False

    except Exception as e:
        print(f"[ERROR] Failed to clean {filename}: {e}")
        return False

if __name__ == "__main__":
    success = clean_opponents_of_opponents()
    if success:
        print("\n[SUCCESS] Opponents_of_Opponents.csv cleaned successfully!")
    else:
        print("\n[FAILED] Cleaning failed")
