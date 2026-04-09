import pandas as pd
from pathlib import Path

# -----------------------------------
# File paths
# -----------------------------------
BASE_DIR = Path(__file__).resolve().parent
EXCEL_FILE = BASE_DIR / "NT_Species_List_Fauna.xlsx"
OUTPUT_FILE = BASE_DIR / "nt_species_threatened_cleaned.xlsx"

# -----------------------------------
# Config
# -----------------------------------
THREAT_CATEGORIES = ["CR", "EN", "VU"]

# Exact sheet names from your workbook
TARGET_SHEETS = ["FROGS", "BIRDS", "MAMMALS", "REPTILES", "FISH", "INVERTEBRATES"]

COLUMN_RENAME_MAP = {
    "CATEGORY": "category",
    "CLASS": "class_name",
    "ORDER": "order_name",
    "FAMILY": "family",
    "GENUS": "genus",
    "SPECIES": "species_name",
    "SUBSPECIES": "subspecies",
    "COMMON NAME": "common_name",
    "SCIENTIFIC NAME": "scientific_name",
    "TERRITORY PARKS AND WILDLIFE ACT CLASSIFICATION": "nt_classification",
    "INTRODUCED STATUS": "introduced_status",
}

# -----------------------------------
# Helpers
# -----------------------------------
def clean_text(value):
    if pd.isna(value):
        return pd.NA
    value = str(value).strip()
    value = " ".join(value.split())
    if value == "":
        return pd.NA
    return value


def clean_classification(value):
    if pd.isna(value):
        return pd.NA
    value = str(value).strip().upper()
    value = " ".join(value.split())
    if value == "":
        return pd.NA
    return value


def load_all_sheets(file_path):
    xls = pd.ExcelFile(file_path)
    available_sheets = xls.sheet_names
    print("Available sheets:", available_sheets)

    dataframes = []

    for sheet in TARGET_SHEETS:
        if sheet in available_sheets:
            print(f"Reading sheet: {sheet}")
            df = pd.read_excel(file_path, sheet_name=sheet, header=4)
            df["SOURCE_SHEET"] = sheet
            dataframes.append(df)
        else:
            print(f"Skipping missing sheet: {sheet}")

    if not dataframes:
        raise ValueError("None of the target sheets were found in the Excel file.")

    combined_df = pd.concat(dataframes, ignore_index=True)
    return combined_df


def standardize_columns(df):
    df.columns = [str(col).strip().upper() for col in df.columns]
    return df


def keep_needed_columns(df):
    needed_cols = list(COLUMN_RENAME_MAP.keys()) + ["SOURCE_SHEET"]
    existing_cols = [col for col in needed_cols if col in df.columns]
    df = df[existing_cols].copy()
    return df


def rename_columns(df):
    rename_map = COLUMN_RENAME_MAP.copy()
    if "SOURCE_SHEET" in df.columns:
        rename_map["SOURCE_SHEET"] = "source_sheet"
    df = df.rename(columns=rename_map)
    return df


def create_scientific_name(df):
    if "scientific_name" not in df.columns:
        df["scientific_name"] = pd.NA

    if "genus" in df.columns and "species_name" in df.columns:
        missing_scientific = df["scientific_name"].isna()
        df.loc[missing_scientific, "scientific_name"] = (
            df.loc[missing_scientific, "genus"].fillna("") + " " +
            df.loc[missing_scientific, "species_name"].fillna("")
        ).str.strip()

    return df


def clean_dataframe(df):
    for col in df.columns:
        if col == "nt_classification":
            df[col] = df[col].apply(clean_classification)
        else:
            df[col] = df[col].apply(clean_text)

    df = df.dropna(how="all")

    if "species_name" in df.columns:
        df = df[df["species_name"].notna()].copy()

    df = create_scientific_name(df)

    if "nt_classification" in df.columns:
        df = df[df["nt_classification"].notna()].copy()
        df = df[df["nt_classification"].isin(THREAT_CATEGORIES)].copy()

    dedupe_cols = [
        col for col in [
            "class_name",
            "order_name",
            "family",
            "genus",
            "species_name",
            "subspecies",
            "common_name",
            "scientific_name",
            "nt_classification",
        ] if col in df.columns
    ]

    if dedupe_cols:
        df = df.drop_duplicates(subset=dedupe_cols)

    df = df.reset_index(drop=True)
    return df


def reorder_columns(df):
    preferred_order = [
        "category",
        "class_name",
        "order_name",
        "family",
        "genus",
        "species_name",
        "subspecies",
        "common_name",
        "scientific_name",
        "nt_classification",
        "introduced_status",
        "source_sheet",
    ]
    final_cols = [col for col in preferred_order if col in df.columns]
    return df[final_cols]


def main():
    print("Loading all target sheets...")
    df = load_all_sheets(EXCEL_FILE)

    print("Standardizing columns...")
    df = standardize_columns(df)

    print("Keeping needed columns only...")
    df = keep_needed_columns(df)

    print("Renaming columns...")
    df = rename_columns(df)

    print("Cleaning and filtering data...")
    df = clean_dataframe(df)

    print("Reordering columns...")
    df = reorder_columns(df)

    print("\nSummary:")
    print(f"Total threatened species rows: {len(df)}")

    if "nt_classification" in df.columns:
        print("\nNT classification counts:")
        print(df["nt_classification"].value_counts(dropna=False))

    if "source_sheet" in df.columns:
        print("\nRows by source sheet:")
        print(df["source_sheet"].value_counts(dropna=False))

    df.to_excel(OUTPUT_FILE, index=False)
    print(f"\nDone. Saved file here:\n{OUTPUT_FILE}")


if __name__ == "__main__":
    main()