"""
Export All Files to Fabric Lakehouse
Uploads all documentation, scripts, and configuration files
"""

import os
from pathlib import Path
from fabric_lakehouse_connector import FabricLakehouseConnector

# ============================================================================
# CONFIGURATION
# ============================================================================

DOCUMENTATION_PATH = "Files/Documentation"
SCRIPTS_PATH = "Files/Scripts"
CONFIG_PATH = "Files/Configuration"

# Files to export
FILES_TO_EXPORT = {
    # Documentation
    "Documentation": {
        "PIPELINE_README.md": "Documentation/",
        "QUICK_REFERENCE.md": "Documentation/",
        "SETUP_COMPLETE.md": "Documentation/",
        "README.md": "Documentation/",
    },
    # Python Scripts
    "Scripts": {
        "run_medallion_pipeline.py": "Scripts/",
        "medallion_pipeline_remote.py": "Scripts/",
        "fabric_lakehouse_connector.py": "Scripts/",
        "medallion_pipeline.py": "Scripts/",
        "auth_example.py": "Scripts/",
        "auto_authenticate.py": "Scripts/",
    },
    # Configuration
    "Configuration": {
        "requirements.txt": "Configuration/",
    }
}


def export_all_files():
    """Export all created files to Lakehouse"""

    print("\n" + "=" * 70)
    print("📤 EXPORTING ALL FILES TO FABRIC LAKEHOUSE")
    print("=" * 70)

    try:
        # Initialize connector
        print("\n🔗 Connecting to Fabric...")
        connector = FabricLakehouseConnector(use_interactive=False)

        # Create directories
        print("\n📁 Creating folder structure...")
        print("-" * 70)

        for folder_type, files in FILES_TO_EXPORT.items():
            for file_name, lakehouse_path in files.items():
                # Create directory if needed
                dir_path = lakehouse_path.rstrip("/")
                if dir_path:
                    connector.create_directory(dir_path)

        print("✅ Folder structure created\n")

        # Export files
        print("=" * 70)
        print("📄 UPLOADING FILES")
        print("=" * 70)

        total_uploaded = 0

        for folder_type, files in FILES_TO_EXPORT.items():
            print(f"\n{folder_type}:")
            print("-" * 70)

            for file_name, lakehouse_path in files.items():
                local_path = Path(file_name)

                if not local_path.exists():
                    print(f"   ⚠️  Not found: {file_name} (skipping)")
                    continue

                try:
                    # Get file size
                    file_size = local_path.stat().st_size
                    size_kb = file_size / 1024

                    # Upload file
                    full_lakehouse_path = f"{lakehouse_path}{file_name}"
                    success = connector.upload_file(str(local_path), full_lakehouse_path)

                    if success:
                        print(f"   ✅ {file_name} ({size_kb:.1f} KB)")
                        total_uploaded += 1

                except Exception as e:
                    print(f"   ❌ Error uploading {file_name}: {e}")

        # Summary
        print("\n" + "=" * 70)
        print("✅ FILE EXPORT COMPLETED")
        print("=" * 70)

        print(f"\n📊 Summary:")
        print(f"   Total files uploaded: {total_uploaded}")
        print(f"\n📁 Lakehouse structure:")
        print(f"   Files/")
        print(f"   ├── Documentation/   (All .md files)")
        print(f"   ├── Scripts/         (All .py files)")
        print(f"   ├── Configuration/   (requirements.txt)")
        print(f"   ├── Bronze/          (Raw data - CSV)")
        print(f"   ├── Silver/          (Cleaned data - Parquet)")
        print(f"   └── Gold/            (Analytics - Parquet)")

        print(f"\n🔍 View files in Fabric:")
        print(f"   1. Go to: https://app.fabric.microsoft.com")
        print(f"   2. Workspace: fabricaena")
        print(f"   3. Lakehouse: githubclaude")
        print(f"   4. Navigate to Files/Documentation, etc.")

        # List exported files
        print("\n" + "=" * 70)
        print("📂 LAKEHOUSE CONTENTS")
        print("=" * 70)

        for folder_type in FILES_TO_EXPORT.keys():
            if folder_type == "Documentation":
                connector.list_files(DOCUMENTATION_PATH, recursive=False)
            elif folder_type == "Scripts":
                connector.list_files(SCRIPTS_PATH, recursive=False)
            elif folder_type == "Configuration":
                connector.list_files(CONFIG_PATH, recursive=False)

        return total_uploaded

    except Exception as e:
        print(f"\n❌ Export failed: {e}")
        import traceback
        traceback.print_exc()
        raise


def main():
    """Main execution"""

    print("\n" + "=" * 70)
    print("🏢 FABRIC LAKEHOUSE FILE EXPORT")
    print("=" * 70)

    try:
        # Export all files
        count = export_all_files()

        print("\n" + "=" * 70)
        print("✅ SUCCESS - All files exported to Lakehouse!")
        print("=" * 70)
        print("\n📍 Access your files at:")
        print("   https://app.fabric.microsoft.com")
        print("   → fabricaena workspace")
        print("   → githubclaude lakehouse")
        print("   → Files folder")

    except Exception as e:
        print(f"\n❌ Export failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import sys
    main()
