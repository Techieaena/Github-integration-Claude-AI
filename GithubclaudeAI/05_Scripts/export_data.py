"""
Export Raw and Transformed Data
Extracts and saves both Bronze (raw) and Silver (transformed) data to local CSV files
"""

import os
import pandas as pd
import kagglehub
from pathlib import Path
from medallion_pipeline_remote import SilverLayerRemote, KAGGLE_DATASET

# Export directories
EXPORT_DIR = Path("./exported_data")
EXPORT_RAW_DIR = EXPORT_DIR / "raw_bronze"
EXPORT_TRANSFORMED_DIR = EXPORT_DIR / "transformed_silver"


def create_export_dirs():
    """Create export directories"""
    EXPORT_RAW_DIR.mkdir(parents=True, exist_ok=True)
    EXPORT_TRANSFORMED_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ Export directories created:")
    print(f"   Raw data: {EXPORT_RAW_DIR.absolute()}")
    print(f"   Transformed data: {EXPORT_TRANSFORMED_DIR.absolute()}")


def download_kaggle_data():
    """Download Kaggle dataset"""
    print(f"\n📥 Downloading Kaggle dataset: {KAGGLE_DATASET}")
    dataset_path = kagglehub.dataset_download(KAGGLE_DATASET)
    print(f"✅ Dataset downloaded to: {dataset_path}")
    return dataset_path


def export_raw_data(dataset_path):
    """Export raw CSV data from Kaggle"""
    print("\n" + "=" * 70)
    print("📊 EXPORTING RAW BRONZE DATA")
    print("=" * 70)

    raw_data = {}
    csv_files = list(Path(dataset_path).glob("**/*.csv"))

    print(f"\n📂 Found {len(csv_files)} CSV files\n")

    for csv_file in csv_files:
        file_name = csv_file.stem
        print(f"📄 Processing: {file_name}")

        try:
            # Load CSV
            df = pd.read_csv(csv_file)
            raw_data[file_name] = df

            # Export to local CSV
            output_file = EXPORT_RAW_DIR / f"{file_name}.csv"
            df.to_csv(output_file, index=False)

            print(f"   ├─ Rows: {len(df):,}")
            print(f"   ├─ Columns: {len(df.columns)}")
            print(f"   ├─ Size: {csv_file.stat().st_size / 1024 / 1024:.2f} MB")
            print(f"   └─ ✅ Exported to: {output_file.name}\n")

        except Exception as e:
            print(f"   ❌ Error: {e}\n")

    print(f"✅ Raw data export complete: {len(raw_data)} files")
    return raw_data


def export_transformed_data(raw_data):
    """Transform and export Silver layer data"""
    print("\n" + "=" * 70)
    print("🔄 TRANSFORMING AND EXPORTING SILVER DATA")
    print("=" * 70)

    # Create dummy connector (we're not uploading, just transforming)
    class DummyConnector:
        def create_directory(self, path):
            pass

    silver = SilverLayerRemote(DummyConnector())
    transformed_data = {}

    print()
    for name, df in raw_data.items():
        print(f"📊 Transforming: {name}")

        try:
            # Apply transformations based on table type
            if 'customer' in name.lower():
                transformed_df = silver.clean_customers(df)
            elif 'order' in name.lower():
                transformed_df = silver.clean_orders(df)
            elif 'product' in name.lower():
                transformed_df = silver.clean_products(df)
            elif 'sale' in name.lower():
                transformed_df = silver.clean_sales(df)
            else:
                transformed_df = silver.standardize_columns(df)
                transformed_df = silver.clean_numeric_columns(transformed_df)
                transformed_df = silver.clean_date_columns(transformed_df)

            transformed_data[name] = transformed_df

            # Export to CSV
            output_file = EXPORT_TRANSFORMED_DIR / f"{name}.csv"
            transformed_df.to_csv(output_file, index=False)

            print(f"   ├─ Cleaned: {len(transformed_df):,} rows")
            print(f"   ├─ Columns: {len(transformed_df.columns)}")
            print(f"   ├─ Removed: {len(df) - len(transformed_df)} duplicate/invalid rows")
            print(f"   └─ ✅ Exported to: {output_file.name}\n")

        except Exception as e:
            print(f"   ❌ Error: {e}\n")

    print(f"✅ Transformed data export complete: {len(transformed_data)} files")
    return transformed_data


def compare_data(raw_data, transformed_data):
    """Compare raw vs transformed data"""
    print("\n" + "=" * 70)
    print("📊 RAW vs TRANSFORMED COMPARISON")
    print("=" * 70 + "\n")

    for name in raw_data.keys():
        if name in transformed_data:
            raw_df = raw_data[name]
            trans_df = transformed_data[name]

            print(f"📄 {name}:")
            print(f"   Raw:         {len(raw_df):,} rows × {len(raw_df.columns)} columns")
            print(f"   Transformed: {len(trans_df):,} rows × {len(trans_df.columns)} columns")
            print(f"   Removed:     {len(raw_df) - len(trans_df)} rows")
            print(f"   Columns changed: {set(raw_df.columns) != set(trans_df.columns)}")
            print()


def create_summary_report(raw_data, transformed_data):
    """Create a summary report"""
    print("\n" + "=" * 70)
    print("📋 EXPORT SUMMARY REPORT")
    print("=" * 70)

    total_raw_rows = sum(len(df) for df in raw_data.values())
    total_trans_rows = sum(len(df) for df in transformed_data.values())
    total_raw_size = sum(
        (EXPORT_RAW_DIR / f"{name}.csv").stat().st_size
        for name in raw_data.keys()
        if (EXPORT_RAW_DIR / f"{name}.csv").exists()
    )
    total_trans_size = sum(
        (EXPORT_TRANSFORMED_DIR / f"{name}.csv").stat().st_size
        for name in transformed_data.keys()
        if (EXPORT_TRANSFORMED_DIR / f"{name}.csv").exists()
    )

    print(f"\n📊 Data Statistics:")
    print(f"   Raw (Bronze) Layer:")
    print(f"      Tables: {len(raw_data)}")
    print(f"      Total Rows: {total_raw_rows:,}")
    print(f"      Total Size: {total_raw_size / 1024 / 1024:.2f} MB")

    print(f"\n   Transformed (Silver) Layer:")
    print(f"      Tables: {len(transformed_data)}")
    print(f"      Total Rows: {total_trans_rows:,}")
    print(f"      Total Size: {total_trans_size / 1024 / 1024:.2f} MB")

    print(f"\n   Data Reduction:")
    print(f"      Rows Removed: {total_raw_rows - total_trans_rows:,}")
    print(f"      Size Reduction: {(1 - total_trans_size / total_raw_size) * 100:.1f}%")

    print(f"\n📁 Export Locations:")
    print(f"   Raw: {EXPORT_RAW_DIR.absolute()}")
    print(f"   Transformed: {EXPORT_TRANSFORMED_DIR.absolute()}")

    print(f"\n📄 Files exported:")
    for name in raw_data.keys():
        raw_file = EXPORT_RAW_DIR / f"{name}.csv"
        trans_file = EXPORT_TRANSFORMED_DIR / f"{name}.csv"
        if raw_file.exists():
            print(f"   ✅ {raw_file.name}")
        if trans_file.exists():
            print(f"   ✅ {trans_file.name}")


def main():
    """Main export pipeline"""
    print("\n" + "=" * 70)
    print("🔄 DATA EXPORT - RAW & TRANSFORMED")
    print("=" * 70)

    try:
        # Create export directories
        create_export_dirs()

        # Download Kaggle data
        dataset_path = download_kaggle_data()

        # Export raw data
        raw_data = export_raw_data(dataset_path)

        # Transform and export
        transformed_data = export_transformed_data(raw_data)

        # Compare
        compare_data(raw_data, transformed_data)

        # Summary
        create_summary_report(raw_data, transformed_data)

        print("\n" + "=" * 70)
        print("✅ DATA EXPORT COMPLETED SUCCESSFULLY")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Export failed: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
