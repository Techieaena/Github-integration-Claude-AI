"""
Medallion Architecture Pipeline - REMOTE ONLY
Direct streaming to Fabric Lakehouse (no local exports)
Bronze → Silver → Gold using OneLake

Dataset: E-Commerce Sales and Customer Analytics
https://www.kaggle.com/datasets/datascikhan/e-commerce-sales-and-customer-analytics
"""

import os
import sys
import io
from datetime import datetime
from typing import Dict, Tuple
import pandas as pd
import numpy as np
import kagglehub
from pathlib import Path
from fabric_lakehouse_connector import FabricLakehouseConnector

# ============================================================================
# CONFIGURATION
# ============================================================================

KAGGLE_DATASET = "datascikhan/e-commerce-sales-and-customer-analytics"
LAKEHOUSE_PATHS = {
    "bronze": "Files/Bronze",
    "silver": "Files/Silver",
    "gold": "Files/Gold",
    "logs": "Files/Logs"
}

# ============================================================================
# BRONZE LAYER - DIRECT STREAM TO LAKEHOUSE
# ============================================================================

class BronzeLayerRemote:
    """Download Kaggle data and stream directly to Bronze layer"""

    def __init__(self, connector: FabricLakehouseConnector):
        self.connector = connector
        self.raw_data = {}

    def download_and_stream_to_bronze(self) -> Dict[str, str]:
        """Download Kaggle dataset and stream CSV files to Bronze"""

        print("\n" + "=" * 70)
        print("📥 BRONZE LAYER - STREAMING KAGGLE DATA")
        print("=" * 70)

        try:
            # Create Bronze folder
            self.connector.create_directory(LAKEHOUSE_PATHS["bronze"])

            print(f"\n🐼 Downloading Kaggle dataset: {KAGGLE_DATASET}")
            dataset_path = kagglehub.dataset_download(KAGGLE_DATASET)
            print(f"✅ Dataset downloaded to: {dataset_path}")

            # Find and stream CSV files
            uploaded_files = {}
            csv_files = list(Path(dataset_path).glob("**/*.csv"))

            print(f"\n📂 Found {len(csv_files)} CSV files")
            print("-" * 70)

            for csv_file in csv_files:
                file_name = csv_file.stem
                print(f"\n📄 Processing: {file_name}")

                try:
                    # Load CSV into memory
                    df = pd.read_csv(csv_file)
                    print(f"   ├─ Rows: {len(df)}, Columns: {len(df.columns)}")
                    print(f"   ├─ Size: {csv_file.stat().st_size / 1024 / 1024:.2f} MB")

                    # Store in memory for later use
                    self.raw_data[file_name] = df

                    # Stream directly to lakehouse
                    # Create temporary file in memory for upload
                    temp_csv = f"temp_{file_name}.csv"
                    df.to_csv(temp_csv, index=False)

                    # Upload to Bronze layer
                    lakehouse_path = f"{LAKEHOUSE_PATHS['bronze']}/{file_name}.csv"
                    success = self.connector.upload_file(temp_csv, lakehouse_path)

                    if success:
                        uploaded_files[file_name] = lakehouse_path
                        print(f"   └─ ✅ Streamed to: {lakehouse_path}")
                    else:
                        print(f"   └─ ⚠️  Upload failed, but data cached in memory...")

                except Exception as e:
                    print(f"   └─ ❌ Error uploading: {e}")
                finally:
                    # Cleanup temp file
                    if os.path.exists(temp_csv):
                        try:
                            os.remove(temp_csv)
                        except:
                            pass

            print(f"\n✅ Bronze layer complete: {len(uploaded_files)} files uploaded")
            return uploaded_files

        except Exception as e:
            print(f"❌ Bronze layer failed: {e}")
            raise


# ============================================================================
# SILVER LAYER - TRANSFORM & STREAM
# ============================================================================

class SilverLayerRemote:
    """Transform data and stream to Silver layer (Delta format)"""

    def __init__(self, connector: FabricLakehouseConnector):
        self.connector = connector
        self.transformed_data = {}

    def standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to snake_case"""
        df.columns = [col.lower().replace(' ', '_').replace('-', '_') for col in df.columns]
        return df

    def clean_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean numeric columns"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            # Remove infinite values and fill NaN with 0
            df[col] = df[col].replace([np.inf, -np.inf], np.nan).fillna(0)

        return df

    def clean_date_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and parse date columns"""
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except:
                    pass

        return df

    def clean_customers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean customer data"""
        print("   🔄 Transforming: customers")

        df = df.copy()
        df = self.standardize_columns(df)

        # Remove duplicates using customer_id if available, else first column
        customer_id_cols = [col for col in df.columns if 'customer_id' in col.lower()]
        duplicate_subset = customer_id_cols if customer_id_cols else [df.columns[0]]
        df = df.drop_duplicates(subset=duplicate_subset)

        # Clean age column
        if 'age' in df.columns:
            df['age'] = pd.to_numeric(df['age'], errors='coerce').fillna(0).astype(int)

        # Remove rows with null customer_id
        if customer_id_cols:
            df = df.dropna(subset=customer_id_cols)

        df = self.clean_numeric_columns(df)

        return df

    def clean_orders(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean order data"""
        print("   🔄 Transforming: orders")

        df = df.copy()
        df = self.standardize_columns(df)

        # Remove duplicates
        order_id_cols = [col for col in df.columns if 'order_id' in col.lower()]
        if order_id_cols:
            df = df.drop_duplicates(subset=order_id_cols)
            df = df.dropna(subset=order_id_cols)

        df = self.clean_date_columns(df)
        df = self.clean_numeric_columns(df)

        return df

    def clean_products(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean product data"""
        print("   🔄 Transforming: products")

        df = df.copy()
        df = self.standardize_columns(df)

        # Remove duplicates
        product_id_cols = [col for col in df.columns if 'product_id' in col.lower()]
        if product_id_cols:
            df = df.drop_duplicates(subset=product_id_cols)
            df = df.dropna(subset=product_id_cols)

        df = self.clean_numeric_columns(df)

        return df

    def clean_sales(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean sales data"""
        print("   🔄 Transforming: sales")

        df = df.copy()
        df = self.standardize_columns(df)
        df = self.clean_date_columns(df)
        df = self.clean_numeric_columns(df)

        return df

    def transform_and_stream(self, raw_data: Dict[str, pd.DataFrame]) -> Dict[str, str]:
        """Transform all datasets and stream to Silver"""

        print("\n" + "=" * 70)
        print("🔄 SILVER LAYER - TRANSFORMATION & STREAMING")
        print("=" * 70)

        # Create Silver folder
        self.connector.create_directory(LAKEHOUSE_PATHS["silver"])

        streamed_files = {}

        for name, df in raw_data.items():
            print(f"\n📊 Processing: {name}")

            try:
                # Apply transformations based on table type
                if 'customer' in name.lower():
                    transformed_df = self.clean_customers(df)
                elif 'order' in name.lower():
                    transformed_df = self.clean_orders(df)
                elif 'product' in name.lower():
                    transformed_df = self.clean_products(df)
                elif 'sale' in name.lower():
                    transformed_df = self.clean_sales(df)
                else:
                    transformed_df = self.standardize_columns(df)
                    transformed_df = self.clean_numeric_columns(transformed_df)
                    transformed_df = self.clean_date_columns(transformed_df)

                print(f"   ✓ Cleaned: {len(transformed_df)} rows, {len(transformed_df.columns)} columns")

                # Save as Parquet (Delta format representation)
                temp_parquet = f"temp_{name}.parquet"
                transformed_df.to_parquet(temp_parquet, compression='snappy')

                # Stream to Silver layer
                lakehouse_path = f"{LAKEHOUSE_PATHS['silver']}/{name}.parquet"
                success = self.connector.upload_file(temp_parquet, lakehouse_path)

                if success:
                    streamed_files[name] = lakehouse_path
                    print(f"   └─ ✅ Streamed to: {lakehouse_path}")
                else:
                    print(f"   └─ ⚠️  Upload failed, but storing for Gold layer...")

                # Store transformed data for Gold layer (even if upload failed)
                self.transformed_data[name] = transformed_df

            except Exception as e:
                print(f"   ❌ Error transforming {name}: {e}")
            finally:
                # Cleanup temp file
                temp_parquet = f"temp_{name}.parquet"
                if os.path.exists(temp_parquet):
                    try:
                        os.remove(temp_parquet)
                    except:
                        pass

        print(f"\n✅ Silver layer complete: {len(streamed_files)} files streamed")
        return streamed_files


# ============================================================================
# GOLD LAYER - ANALYTICS & STREAMING
# ============================================================================

class GoldLayerRemote:
    """Create analytical tables and stream to Gold"""

    def __init__(self, connector: FabricLakehouseConnector):
        self.connector = connector

    def create_customer_analytics(self, customers: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame:
        """Create customer analytics table"""
        print("   📊 Creating: customer_analytics")

        analytics = customers.copy()

        # Add order metrics
        if not orders.empty and 'customer_id' in orders.columns:
            # Find order amount column (could be order_amount, amount, total, etc.)
            amount_col = next((col for col in orders.columns if 'amount' in col.lower() or 'total' in col.lower() or 'price' in col.lower()), None)
            order_id_col = next((col for col in orders.columns if 'order_id' in col.lower()), 'order_id')

            if amount_col:
                order_metrics = orders.groupby('customer_id').agg({
                    order_id_col: 'count',
                    amount_col: ['sum', 'mean']
                }).reset_index()

                order_metrics.columns = ['customer_id', 'total_orders', 'total_spent', 'avg_order_value']
            else:
                # If no amount column, just count orders
                order_metrics = orders.groupby('customer_id').agg({
                    order_id_col: 'count'
                }).reset_index()
                order_metrics.columns = ['customer_id', 'total_orders']
                order_metrics['total_spent'] = 0
                order_metrics['avg_order_value'] = 0

            if 'customer_id' in analytics.columns:
                analytics = analytics.merge(order_metrics, on='customer_id', how='left')
                analytics = analytics.fillna(0)

        return analytics

    def create_sales_analytics(self, orders: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
        """Create sales analytics table"""
        print("   📊 Creating: sales_analytics")

        sales = orders.copy()

        # Add product info
        if not products.empty and 'product_id' in orders.columns:
            # Get available product columns
            available_cols = [col for col in ['product_id', 'category', 'product_name', 'product_category'] if col in products.columns]
            if available_cols and 'product_id' in available_cols:
                products_clean = products[available_cols]
                if 'product_id' in sales.columns:
                    sales = sales.merge(products_clean, on='product_id', how='left')

        return sales

    def create_product_analytics(self, products: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame:
        """Create product analytics table"""
        print("   📊 Creating: product_analytics")

        analytics = products.copy()

        # Add sales metrics
        if not orders.empty and 'product_id' in orders.columns:
            order_id_col = next((col for col in orders.columns if 'order_id' in col.lower()), 'order_id')
            quantity_col = next((col for col in orders.columns if 'quantity' in col.lower() or 'qty' in col.lower()), None)

            if quantity_col:
                sales_metrics = orders.groupby('product_id').agg({
                    order_id_col: 'count',
                    quantity_col: 'sum'
                }).reset_index()
                sales_metrics.columns = ['product_id', 'times_sold', 'total_quantity']
            else:
                sales_metrics = orders.groupby('product_id').agg({
                    order_id_col: 'count'
                }).reset_index()
                sales_metrics.columns = ['product_id', 'times_sold']
                sales_metrics['total_quantity'] = 0

            if 'product_id' in analytics.columns:
                analytics = analytics.merge(sales_metrics, on='product_id', how='left')
                analytics = analytics.fillna(0)

        return analytics

    def create_and_stream_analytics(self, raw_data: Dict[str, pd.DataFrame]) -> Dict[str, str]:
        """Create all analytics tables and stream to Gold"""

        print("\n" + "=" * 70)
        print("📈 GOLD LAYER - ANALYTICS & STREAMING")
        print("=" * 70)

        # Create Gold folder
        self.connector.create_directory(LAKEHOUSE_PATHS["gold"])

        streamed_files = {}

        # Debug: show available dataframes
        print("\n   Available dataframes:")
        for name, df in raw_data.items():
            print(f"   - {name}: {len(df)} rows, columns: {list(df.columns)[:5]}...")

        # Extract dataframes with better selection logic
        # Try to find customer data with customer_id column
        customers = pd.DataFrame()
        for name, df in raw_data.items():
            if 'customer' in name.lower() and 'customer_id' in df.columns:
                customers = df
                print(f"\n   ✓ Selected '{name}' as customers")
                break
        if customers.empty:
            # Fallback: try any dataframe with customer_id
            for name, df in raw_data.items():
                if 'customer_id' in df.columns:
                    customers = df
                    print(f"\n   ⚠️  Selected '{name}' as customers (fallback)")
                    break

        # Try to find orders/order_items with customer_id and order_id
        orders = pd.DataFrame()
        for name, df in raw_data.items():
            if ('order' in name.lower() or 'sales' in name.lower()) and 'customer_id' in df.columns and 'order_id' in df.columns:
                orders = df
                print(f"   ✓ Selected '{name}' as orders")
                break

        # If no suitable orders found, try any order-like table with customer_id
        if orders.empty:
            for name, df in raw_data.items():
                if 'customer_id' in df.columns and 'order_id' in df.columns:
                    orders = df
                    print(f"   ⚠️  Selected '{name}' as orders (fallback)")
                    break

        # If still no orders, try any order-like table
        if orders.empty:
            for name, df in raw_data.items():
                if 'order' in name.lower() and len(df.columns) > 5:
                    orders = df
                    print(f"   ⚠️  Selected '{name}' as orders (may need column adjustment)")
                    break

        # Try to find products
        products = pd.DataFrame()
        for name, df in raw_data.items():
            if 'product' in name.lower() and 'product_id' in df.columns:
                products = df
                print(f"   ✓ Selected '{name}' as products")
                break
        if products.empty:
            # Fallback: try any dataframe with product_id
            for name, df in raw_data.items():
                if 'product_id' in df.columns:
                    products = df
                    print(f"   ⚠️  Selected '{name}' as products (fallback)")
                    break

        # Warn if no suitable dataframes found
        if customers.empty:
            print(f"   ⚠️  No customers dataframe found!")
        if orders.empty:
            print(f"   ⚠️  No orders dataframe found!")
        if products.empty:
            print(f"   ℹ️  No products dataframe found (optional)")

        # Create analytics tables
        analytics_tables = {}

        try:
            if not customers.empty and not orders.empty:
                print(f"\n📊 Processing: customer_analytics")
                analytics_tables['customer_analytics'] = self.create_customer_analytics(customers, orders)
        except Exception as e:
            print(f"   ⚠️  Error creating customer_analytics: {e}")

        try:
            if not orders.empty:
                print(f"\n📊 Processing: sales_analytics")
                analytics_tables['sales_analytics'] = self.create_sales_analytics(orders, products)
        except Exception as e:
            print(f"   ⚠️  Error creating sales_analytics: {e}")

        try:
            if not products.empty:
                print(f"\n📊 Processing: product_analytics")
                analytics_tables['product_analytics'] = self.create_product_analytics(products, orders)
        except Exception as e:
            print(f"   ⚠️  Error creating product_analytics: {e}")

        # Stream to Gold
        for name, df in analytics_tables.items():
            temp_parquet = f"temp_{name}.parquet"
            try:
                if df.empty:
                    print(f"   ⚠️  Skipping {name}: empty dataframe")
                    continue

                print(f"   ├─ Rows: {len(df)}, Columns: {len(df.columns)}")

                # Save as Parquet
                df.to_parquet(temp_parquet, compression='snappy')

                # Stream to Gold layer
                lakehouse_path = f"{LAKEHOUSE_PATHS['gold']}/{name}.parquet"
                success = self.connector.upload_file(temp_parquet, lakehouse_path)

                if success:
                    streamed_files[name] = lakehouse_path
                    print(f"   └─ ✅ Streamed to: {lakehouse_path}")
                else:
                    print(f"   └─ ⚠️  Upload failed, but continuing...")

            except Exception as e:
                print(f"   ❌ Error streaming {name}: {e}")
            finally:
                # Always cleanup temp file
                if os.path.exists(temp_parquet):
                    try:
                        os.remove(temp_parquet)
                    except:
                        pass

        print(f"\n✅ Gold layer complete: {len(streamed_files)} files streamed")
        return streamed_files


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main():
    """Execute medallion architecture pipeline - REMOTE ONLY"""

    print("\n" + "=" * 70)
    print("🏗️  MEDALLION ARCHITECTURE - REMOTE STREAMING PIPELINE")
    print("=" * 70)
    print(f"Dataset: {KAGGLE_DATASET}")
    print(f"Lakehouse: githubclaude")
    print(f"Mode: REMOTE (no local exports)")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    try:
        # Initialize Fabric connector
        print("\n🔗 Connecting to Fabric Lakehouse...")
        connector = FabricLakehouseConnector(use_interactive=False)
        connector.get_lakehouse_status()

        # BRONZE LAYER - Download & Stream
        print("\n" + "=" * 70)
        bronze = BronzeLayerRemote(connector)
        bronze_files = bronze.download_and_stream_to_bronze()

        # SILVER LAYER - Transform & Stream
        print("\n" + "=" * 70)
        silver = SilverLayerRemote(connector)
        silver_files = silver.transform_and_stream(bronze.raw_data)

        # GOLD LAYER - Analytics & Stream (use TRANSFORMED Silver data, not raw Bronze data)
        print("\n" + "=" * 70)
        gold = GoldLayerRemote(connector)
        gold_files = gold.create_and_stream_analytics(silver.transformed_data)

        # Summary
        print("\n" + "=" * 70)
        print("✅ PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print(f"\n📊 Summary:")
        print(f"   Bronze Layer: {len(bronze_files)} files")
        print(f"   Silver Layer: {len(silver_files)} files")
        print(f"   Gold Layer: {len(gold_files)} files")
        print(f"\n📁 All files in: githubclaude Lakehouse")
        print(f"🎯 Ready for Fabric SQL Analytical Queries!")
        print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # List final contents
        print("\n" + "=" * 70)
        print("📂 LAKEHOUSE STRUCTURE")
        print("=" * 70)

        for layer_name, path in LAKEHOUSE_PATHS.items():
            if layer_name != "logs":
                print(f"\n{layer_name.upper()}:")
                connector.list_files(path, recursive=False)

    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
