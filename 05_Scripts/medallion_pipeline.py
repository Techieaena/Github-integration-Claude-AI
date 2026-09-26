"""
Medallion Architecture Data Pipeline
Bronze → Silver → Gold
Kaggle dataset → Fabric Lakehouse

Dataset: E-Commerce Sales and Customer Analytics
https://www.kaggle.com/datasets/datascikhan/e-commerce-sales-and-customer-analytics
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from deltalake import write_deltalake
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient
import kagglehub
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# ============================================================================
# CONFIGURATION
# ============================================================================

# Fabric Configuration
TENANT_ID = "30afeb3b-d029-4c64-857b-bb0ad14b9a85"
WORKSPACE_ID = "9c06c853-c4ee-42ad-b784-9ad3c80e7f1d"
LAKEHOUSE_ID = "0b4f9e6c-379c-493f-b707-0c857c8b8041"
LAKEHOUSE_NAME = "githubclaude"

# Kaggle Configuration
KAGGLE_DATASET = "datascikhan/e-commerce-sales-and-customer-analytics"
LOCAL_DATA_DIR = Path("./kaggle_data")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRANSFORMED_FILES_DIR = PROJECT_ROOT / "01_DataLayer" / "Transformed_files"

# Lakehouse Paths
BRONZE_PATH = "Files/Raw_bronze"
TABLES_PATH = "Tables/NewSchema"
LOGS_PATH = "Files/Logs"


def bootstrap_windows_hadoop() -> None:
    """Provision the Windows Hadoop runtime used by Spark on local machines."""
    if os.name != "nt":
        return

    hadoop_home = Path(os.environ.get("HADOOP_HOME") or r"C:\hadoop")
    bin_dir = hadoop_home / "bin"
    winutils_path = bin_dir / "winutils.exe"

    try:
        if not winutils_path.exists():
            bin_dir.mkdir(parents=True, exist_ok=True)
            import urllib.request

            url = "https://github.com/steveloughran/winutils/raw/master/hadoop-3.0.0/bin/winutils.exe"
            urllib.request.urlretrieve(url, str(winutils_path))

        os.environ["HADOOP_HOME"] = str(hadoop_home)
        os.environ["PATH"] = str(bin_dir) + os.pathsep + os.environ.get("PATH", "")
    except Exception as exc:
        print(f"⚠️  Hadoop bootstrap warning: {exc}")

# ============================================================================
# SETUP SPARK SESSION
# ============================================================================

def create_spark_session() -> SparkSession:
    """Create and configure Spark session"""
    bootstrap_windows_hadoop()
    python_executable = sys.executable
    os.environ["PYSPARK_PYTHON"] = python_executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = python_executable
    print("🔧 Initializing Spark session...")

    spark = SparkSession.builder \
        .appName("MedallionArchipeline") \
        .getOrCreate()

    print("✅ Spark session created")
    return spark


# ============================================================================
# BRONZE LAYER - RAW DATA INGESTION
# ============================================================================

class BronzeLayer:
    """Raw data ingestion and upload"""

    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.local_data_dir = LOCAL_DATA_DIR

    def download_kaggle_dataset(self) -> Path:
        """Download dataset from Kaggle"""
        print("\n" + "=" * 70)
        print("📥 BRONZE LAYER - DOWNLOADING KAGGLE DATASET")
        print("=" * 70)

        try:
            print(f"🐼 Downloading: {KAGGLE_DATASET}")
            dataset_path = kagglehub.dataset_download(KAGGLE_DATASET)
            print(f"✅ Dataset downloaded to: {dataset_path}")
            return Path(dataset_path)
        except Exception as e:
            print(f"❌ Error downloading dataset: {e}")
            raise

    def get_csv_files(self, dataset_path: Path) -> Dict[str, Path]:
        """Find all CSV files in dataset"""
        print("\n📂 Scanning for CSV files...")

        csv_files = {}
        for csv_file in dataset_path.glob("**/*.csv"):
            file_name = csv_file.stem
            csv_files[file_name] = csv_file
            print(f"   ✓ Found: {file_name}.csv ({csv_file.stat().st_size / 1024 / 1024:.2f} MB)")

        return csv_files

    def load_raw_data(self, csv_files: Dict[str, Path]) -> Dict[str, pd.DataFrame]:
        """Load all CSV files"""
        print("\n📖 Loading CSV files...")

        dataframes = {}
        for name, path in csv_files.items():
            try:
                df = pd.read_csv(path)
                dataframes[name] = df
                print(f"   ✓ Loaded: {name} ({len(df)} rows, {len(df.columns)} columns)")
            except Exception as e:
                print(f"   ⚠️  Skipped {name}: {e}")

        return dataframes

    def upload_to_lakehouse(self, dataframes: Dict[str, pd.DataFrame], uploader) -> Dict[str, str]:
        """Upload CSV files to Bronze layer"""
        print("\n📤 Uploading to Bronze layer...")

        uploaded_files = {}
        TRANSFORMED_FILES_DIR.mkdir(parents=True, exist_ok=True)
        for name, df in dataframes.items():
            try:
                # Save locally as CSV
                csv_path = TRANSFORMED_FILES_DIR / f"temp_{name}.csv"
                df.to_csv(csv_path, index=False)

                # Upload to Lakehouse
                lakehouse_path = f"{BRONZE_PATH}/{name}.csv"
                uploader.upload_file_to_lakehouse(str(csv_path), lakehouse_path)

                uploaded_files[name] = lakehouse_path
                print(f"   ✓ Uploaded: {name}.csv → {lakehouse_path}")

                # Cleanup temp file
                csv_path.unlink()
            except Exception as e:
                print(f"   ❌ Failed to upload {name}: {e}")

        return uploaded_files


# ============================================================================
# SILVER LAYER - DATA TRANSFORMATION
# ============================================================================

class SilverLayer:
    """Data cleaning and standardization"""

    def __init__(self, spark: SparkSession):
        self.spark = spark

    def clean_customers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean customer data"""
        print("   🔄 Transforming: customers")

        df = df.copy()

        # Standardize column names
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]

        # Handle missing values
        df = df.dropna(subset=['customer_id'])

        # Remove duplicates
        df = df.drop_duplicates(subset=['customer_id'])

        # Standardize data types
        if 'age' in df.columns:
            df['age'] = pd.to_numeric(df['age'], errors='coerce').fillna(0).astype(int)

        return df

    def clean_orders(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean order data"""
        print("   🔄 Transforming: orders")

        df = df.copy()

        # Standardize column names
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]

        # Handle missing values
        df = df.dropna(subset=['order_id'])

        # Remove duplicates
        df = df.drop_duplicates(subset=['order_id'])

        # Parse dates
        date_columns = [col for col in df.columns if 'date' in col.lower()]
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

        # Numeric conversions
        numeric_columns = [col for col in df.columns if 'amount' in col.lower() or 'price' in col.lower() or 'quantity' in col.lower()]
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        return df

    def clean_products(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean product data"""
        print("   🔄 Transforming: products")

        df = df.copy()

        # Standardize column names
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]

        # Handle missing values
        df = df.dropna(subset=['product_id'])

        # Remove duplicates
        df = df.drop_duplicates(subset=['product_id'])

        # Numeric conversions
        numeric_columns = [col for col in df.columns if 'price' in col.lower() or 'cost' in col.lower()]
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        return df

    def clean_sales(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean sales data"""
        print("   🔄 Transforming: sales")

        df = df.copy()

        # Standardize column names
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]

        # Parse dates
        date_columns = [col for col in df.columns if 'date' in col.lower()]
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

        # Numeric conversions
        numeric_columns = [col for col in df.columns if 'amount' in col.lower() or 'quantity' in col.lower() or 'revenue' in col.lower()]
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        return df

    def transform_data(self, dataframes: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Transform all datasets"""
        print("\n" + "=" * 70)
        print("🔄 SILVER LAYER - DATA TRANSFORMATION")
        print("=" * 70)

        transformed = {}

        for name, df in dataframes.items():
            print(f"\nCleaning {name}...")
            normalized_name = name.lower()

            if normalized_name == 'customer_master':
                transformed['customers'] = self.clean_customers(df)
            elif normalized_name == 'order_items':
                transformed['orders'] = self.clean_orders(df)
            elif normalized_name == 'product_catalog':
                transformed['products'] = self.clean_products(df)
            elif normalized_name.startswith('ecommerce_sales_'):
                transformed['sales'] = self.clean_sales(df)
            else:
                transformed[name] = df

        return transformed

    def save_as_delta(self, dataframes: Dict[str, pd.DataFrame], uploader) -> Dict[str, str]:
        """Save transformed data as Parquet and upload it to the Silver layer."""
        print("\n" + "=" * 70)
        print("💾 SAVING SILVER TABLES TO PARQUET")
        print("=" * 70)

        saved_files = {}

        for name, df in dataframes.items():
            try:
                parquet_path = TRANSFORMED_FILES_DIR / f"temp_{name}.parquet"
                parquet_path.mkdir(parents=True, exist_ok=True)
                df.to_parquet(parquet_path / "part-00000.parquet", index=False)

                delta_path = TRANSFORMED_FILES_DIR / "delta_tables" / "Silver" / name
                write_deltalake(str(delta_path), df, mode="overwrite")

                lakehouse_path = f"{TABLES_PATH}/Silver_{name}"
                uploader.upload_directory(str(delta_path), lakehouse_path)

                saved_files[name] = lakehouse_path
                print(f"   ✓ Saved: {name} → {lakehouse_path}")

            except Exception as e:
                print(f"   ❌ Error saving {name}: {e}")

        return saved_files


# ============================================================================
# GOLD LAYER - ANALYTICAL INSIGHTS
# ============================================================================

class GoldLayer:
    """Business analytics and aggregations"""

    def __init__(self, spark: SparkSession):
        self.spark = spark

    def create_customer_analytics(self, customers_df: pd.DataFrame, orders_df: pd.DataFrame) -> pd.DataFrame:
        """Create customer analytics table"""
        print("   📊 Creating: customer_analytics")

        # Customer segmentation
        analytics = customers_df.copy()

        # Add metrics from orders
        if not orders_df.empty:
            amount_column = next(
                (column for column in ('order_amount', 'net_sales', 'gross_sales') if column in orders_df.columns),
                None,
            )
            aggregations: Dict[str, object] = {'order_id': 'count'}
            if amount_column:
                aggregations[amount_column] = ['sum', 'mean']

            order_metrics = orders_df.groupby('customer_id').agg(aggregations).reset_index()
            if amount_column:
                order_metrics.columns = ['customer_id', 'total_orders', 'total_spent', 'avg_order_value']
            else:
                order_metrics.columns = ['customer_id', 'total_orders']

            analytics = analytics.merge(order_metrics, on='customer_id', how='left')
            analytics = analytics.fillna(0)

        return analytics

    def create_sales_analytics(self, orders_df: pd.DataFrame, products_df: pd.DataFrame) -> pd.DataFrame:
        """Create sales analytics table"""
        print("   📊 Creating: sales_analytics")

        sales = orders_df.copy()

        # Add product information
        if not products_df.empty and 'product_id' in sales.columns and 'product_id' in products_df.columns:
            product_columns = ['product_id', 'product_name']
            category_column = next(
                (column for column in ('category', 'product_category') if column in products_df.columns),
                None,
            )
            if category_column:
                product_columns.append(category_column)
            sales = sales.merge(products_df[product_columns], on='product_id', how='left')

        # Calculate metrics
        if 'order_date' in sales.columns:
            sales['month'] = pd.to_datetime(sales['order_date']).dt.to_period('M').astype(str)

        return sales

    def create_product_analytics(self, products_df: pd.DataFrame, orders_df: pd.DataFrame) -> pd.DataFrame:
        """Create product analytics table"""
        print("   📊 Creating: product_analytics")

        analytics = products_df.copy()

        # Add sales metrics
        if not orders_df.empty and 'product_id' in orders_df.columns:
            sales_metrics = orders_df.groupby('product_id').agg({
                'order_id': 'count',
                'quantity': 'sum'
            }).reset_index()
            sales_metrics.columns = ['product_id', 'times_sold', 'total_quantity']

            analytics = analytics.merge(sales_metrics, on='product_id', how='left')
            analytics = analytics.fillna(0)

        return analytics

    def create_analytics_tables(self, dataframes: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Create all analytical tables"""
        print("\n" + "=" * 70)
        print("📈 GOLD LAYER - ANALYTICAL INSIGHTS")
        print("=" * 70)

        analytics = {}

        # Extract dataframes
        customers = dataframes.get('customers', pd.DataFrame())
        orders = dataframes.get('orders', pd.DataFrame())
        products = dataframes.get('products', pd.DataFrame())
        sales = dataframes.get('sales', pd.DataFrame())

        # Create analytics
        if not customers.empty and not sales.empty:
            analytics['customer_analytics'] = self.create_customer_analytics(customers, sales)

        if not sales.empty:
            analytics['sales_analytics'] = self.create_sales_analytics(sales, products)

        if not products.empty:
            analytics['product_analytics'] = self.create_product_analytics(products, orders)

        return analytics

    def save_as_delta(self, analytics: Dict[str, pd.DataFrame], uploader) -> Dict[str, str]:
        """Save analytical tables as Parquet and upload them to the Gold layer."""
        print("\n💾 Saving Gold layer to Parquet...")

        saved_files = {}

        for name, df in analytics.items():
            try:
                delta_path = TRANSFORMED_FILES_DIR / "delta_tables" / "Gold" / name
                write_deltalake(str(delta_path), df, mode="overwrite")

                lakehouse_path = f"{TABLES_PATH}/{name}"
                uploader.upload_directory(str(delta_path), lakehouse_path)

                saved_files[name] = lakehouse_path
                print(f"   ✓ Saved: {name} → {lakehouse_path}")

            except Exception as e:
                print(f"   ❌ Error saving {name}: {e}")

        return saved_files


# ============================================================================
# FABRIC LAKEHOUSE UPLOADER
# ============================================================================

class FabricLakehouseUploader:
    """Upload files to Fabric Lakehouse"""

    def __init__(self, workspace_name: str = "fabricaena", lakehouse_name: str = "githubclaude"):
        from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
        from azure.storage.filedatalake import DataLakeServiceClient

        self.workspace_name = workspace_name
        self.lakehouse_name = lakehouse_name
        self.account_url = "https://onelake.dfs.fabric.microsoft.com"

        # Try default credential first, fall back to browser auth
        try:
            self.credential = DefaultAzureCredential()
            self.credential.get_token("https://storage.azure.com/.default")
        except Exception:
            print("   Using browser authentication...")
            self.credential = InteractiveBrowserCredential()

    def upload_file_to_lakehouse(self, local_file_path: str, lakehouse_path: str) -> bool:
        """Upload a single file to Lakehouse"""
        try:
            from azure.storage.filedatalake import DataLakeServiceClient

            client = DataLakeServiceClient(account_url=self.account_url, credential=self.credential)
            file_system = f"{self.workspace_name}/{self.lakehouse_name}.Lakehouse"
            file_system_client = client.get_file_system_client(file_system=file_system)

            file_size_mb = Path(local_file_path).stat().st_size / (1024 * 1024)

            with open(local_file_path, 'rb') as data:
                file_system_client.get_file_client(lakehouse_path).upload_data(data, overwrite=True)

            print(f"   ✅ {Path(local_file_path).name:<45} ({file_size_mb:>6.2f} MB)")
            return True

        except Exception as e:
            print(f"   ❌ {Path(local_file_path).name:<45} Error: {str(e)}")
            return False

    def upload_directory(self, local_dir: str, lakehouse_path: str) -> bool:
        """Upload all files from a directory"""
        try:
            local_path = Path(local_dir)
            if not local_path.exists():
                print(f"   ❌ Directory not found: {local_dir}")
                return False

            uploaded_count = 0
            for file_path in local_path.rglob("*"):
                if not file_path.is_file():
                    continue
                relative_path = file_path.relative_to(local_path).as_posix()
                remote_path = f"{lakehouse_path}/{relative_path}"
                if self.upload_file_to_lakehouse(str(file_path), remote_path):
                    uploaded_count += 1

            return uploaded_count > 0

        except Exception as e:
            print(f"   ❌ Directory upload error: {str(e)}")
            return False


# ============================================================================
# UPLOAD RAW BRONZE FUNCTION
# ============================================================================

def upload_raw_bronze_to_lakehouse(workspace_name: str = "fabricaena", lakehouse_name: str = "githubclaude"):
    """Upload existing raw_bronze CSV files directly to Fabric Lakehouse"""

    print("\n" + "=" * 70)
    print("📤 UPLOADING RAW BRONZE FILES TO LAKEHOUSE")
    print("=" * 70)

    raw_bronze_dir = PROJECT_ROOT / "01_DataLayer" / "raw_bronze"

    # Check directory
    if not raw_bronze_dir.exists():
        print(f"❌ Error: Directory not found: {raw_bronze_dir}")
        return False

    # List files
    csv_files = list(raw_bronze_dir.glob("*.csv"))
    if not csv_files:
        print(f"❌ No CSV files found in: {raw_bronze_dir}")
        return False

    print(f"\n📁 Source: {raw_bronze_dir}")
    print(f"📍 Target: {workspace_name}/{lakehouse_name}/Files/Raw_bronze")
    print(f"📊 Files: {len(csv_files)}")

    # Show files
    total_size = 0
    for csv_file in sorted(csv_files):
        size_mb = csv_file.stat().st_size / (1024 * 1024)
        total_size += csv_file.stat().st_size
        print(f"   ✓ {csv_file.name:<45} ({size_mb:>7.2f} MB)")

    print(f"\n   Total: {total_size / (1024 * 1024):.2f} MB")

    # Confirm
    print("\n" + "=" * 70)
    response = input("👉 Continue with upload? (yes/no): ").strip().lower()
    if response != "yes":
        print("❌ Upload cancelled")
        return False

    # Connect and upload
    print("\n🔄 Uploading files...")
    print("-" * 70)

    try:
        uploader = FabricLakehouseUploader(workspace_name, lakehouse_name)

        # Upload all files
        uploaded = uploader.upload_directory(str(raw_bronze_dir), "Files/Raw_bronze")

        if uploaded:
            print("-" * 70)
            print("\n✅ Upload Complete!")
            print(f"\n📍 Access your files:")
            print(f"   Workspace: {workspace_name}")
            print(f"   Lakehouse: {lakehouse_name}")
            print(f"   Folder: Files/Raw_bronze")
            print(f"\n✅ All raw CSV files are now in Fabric Lakehouse!")
            return True
        else:
            print("\n❌ Upload failed - see errors above")
            return False

    except Exception as e:
        print(f"\n❌ Upload error: {str(e)}")
        print("\n⚠️  Troubleshooting:")
        print("   1. Ensure Azure credentials are configured: az login")
        print("   2. Check workspace and lakehouse names are correct")
        print("   3. Verify you have permissions to the Lakehouse")
        return False


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main():
    """Execute medallion architecture pipeline"""

    print("\n" + "=" * 70)
    print("🏗️  MEDALLION ARCHITECTURE DATA PIPELINE")
    print("=" * 70)
    print(f"Dataset: {KAGGLE_DATASET}")
    print(f"Lakehouse: {LAKEHOUSE_NAME}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    try:
        # Initialize
        spark = create_spark_session()
        uploader = FabricLakehouseUploader()

        # BRONZE LAYER
        bronze = BronzeLayer(spark)
        dataset_path = bronze.download_kaggle_dataset()
        csv_files = bronze.get_csv_files(dataset_path)
        raw_dataframes = bronze.load_raw_data(csv_files)
        bronze_files = bronze.upload_to_lakehouse(raw_dataframes, uploader)

        # SILVER LAYER
        silver = SilverLayer(spark)
        transformed_dataframes = silver.transform_data(raw_dataframes)
        silver_files = silver.save_as_delta(transformed_dataframes, uploader)
        if len(silver_files) != len(transformed_dataframes):
            raise RuntimeError(
                f"Silver layer incomplete: saved {len(silver_files)} of "
                f"{len(transformed_dataframes)} datasets"
            )

        # GOLD LAYER
        gold = GoldLayer(spark)
        analytics_dataframes = gold.create_analytics_tables(transformed_dataframes)
        gold_files = gold.save_as_delta(analytics_dataframes, uploader)
        if len(gold_files) != len(analytics_dataframes):
            raise RuntimeError(
                f"Gold layer incomplete: saved {len(gold_files)} of "
                f"{len(analytics_dataframes)} datasets"
            )

        # Summary
        print("\n" + "=" * 70)
        print("✅ PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print(f"\n📁 Bronze Layer: {len(bronze_files)} files")
        print(f"📁 Silver Layer: {len(silver_files)} files")
        print(f"📁 Gold Layer: {len(gold_files)} files")
        print(f"\n🏢 All data exported to: {LAKEHOUSE_NAME}")
        print(f"✅ Ready for SQL Analytical Endpoint queries!")

    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    main()
