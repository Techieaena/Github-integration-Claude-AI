"""
Medallion Architecture Pipeline Runner
Execute Bronze → Silver → Gold pipeline
"""

import sys
import time
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from medallion_pipeline_remote import main as run_pipeline


def print_banner():
    """Print pipeline banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║        🏗️  MEDALLION ARCHITECTURE DATA PIPELINE 🏗️              ║
    ║                                                                   ║
    ║              E-Commerce Sales & Customer Analytics              ║
    ║                     Kaggle → Fabric Lakehouse                    ║
    ║                                                                   ║
    ║  Bronze (Raw) → Silver (Clean) → Gold (Analytics)               ║
    ║                                                                   ║
    ║                    Remote Streaming (No Local Exports)           ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_requirements():
    """Check all required packages are installed"""
    print("\n🔍 Checking requirements...")
    print("-" * 70)

    requirements = {
        'pandas': 'pandas',
        'numpy': 'numpy',
        'kagglehub': 'kagglehub',
        'azure.identity': 'azure-identity',
        'azure.storage.filedatalake': 'azure-storage-file-datalake'
    }

    missing = []

    for module_name, package_name in requirements.items():
        try:
            __import__(module_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name}")
            missing.append(package_name)

    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print(f"\nInstall with:")
        print(f"   pip install {' '.join(missing)}")
        return False

    print("\n✅ All requirements met!")
    return True


def check_credentials():
    """Check if Kaggle credentials are configured"""
    print("\n🔐 Checking credentials...")
    print("-" * 70)

    # Check Kaggle
    kaggle_path = Path.home() / ".kaggle" / "kaggle.json"
    if kaggle_path.exists():
        print("✅ Kaggle credentials found")
    else:
        print("❌ Kaggle credentials not found")
        print("   Required: ~/.kaggle/kaggle.json")
        return False

    print("\n✅ All credentials configured!")
    return True


def main():
    """Main entry point"""

    print_banner()

    # Check requirements
    if not check_requirements():
        print("\n❌ Please install missing packages")
        sys.exit(1)

    # Check credentials
    if not check_credentials():
        print("\n❌ Please configure credentials")
        sys.exit(1)

    # Ready to go
    print("\n" + "=" * 70)
    print("🚀 STARTING PIPELINE")
    print("=" * 70)

    start_time = datetime.now()

    try:
        # Run pipeline
        run_pipeline()

        # Success
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print("\n" + "=" * 70)
        print("✅ PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print(f"\n⏱️  Duration: {duration:.0f} seconds ({duration/60:.1f} minutes)")
        print(f"📊 Data is now available in Fabric Lakehouse:")
        print(f"   Workspace: fabricaena")
        print(f"   Lakehouse: githubclaude")
        print(f"\n📁 Folder Structure:")
        print(f"   Files/")
        print(f"   ├── Bronze/     (Raw CSV data)")
        print(f"   ├── Silver/     (Cleaned Parquet/Delta)")
        print(f"   └── Gold/       (Analytical Parquet/Delta)")
        print(f"\n🔍 Next Steps:")
        print(f"   1. Open Fabric Workspace: fabricaena")
        print(f"   2. Navigate to Lakehouse: githubclaude")
        print(f"   3. Query Bronze/Silver/Gold data")
        print(f"   4. Create SQL Analytical Endpoint views")
        print(f"   5. Build Power BI reports")

        print("\n" + "=" * 70)

    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print("\n" + "=" * 70)
        print("❌ PIPELINE EXECUTION FAILED")
        print("=" * 70)
        print(f"\n⏱️  Duration: {duration:.0f} seconds")
        print(f"Error: {e}")

        import traceback
        print("\n📋 Detailed Error:")
        traceback.print_exc()

        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(0)
