"""
Upload Deployment Package to Fabric Lakehouse
"""

import os
import json
from pathlib import Path
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient

# Configuration
WORKSPACE_ID = "9c06c853-c4ee-42ad-b784-9ad3c80e7f1d"
LAKEHOUSE_ID = "0b4f9e6c-379c-493f-b707-0c857c8b8041"
STORAGE_ACCOUNT = "onelake.dfs.core.windows.net"
FILE_SYSTEM = f"{WORKSPACE_ID}/{LAKEHOUSE_ID}"

STAGING_DIR = r"C:\Users\admin\fabric_deployment"

print("="*80)
print("UPLOADING TO FABRIC LAKEHOUSE")
print("="*80)

print(f"\nConfiguration:")
print(f"  Storage Account: {STORAGE_ACCOUNT}")
print(f"  File System: {FILE_SYSTEM}")
print(f"  Staging Directory: {STAGING_DIR}")

try:
    # Authenticate using DefaultAzureCredential (uses az cli login)
    print("\nAuthenticating with Azure...")
    credential = DefaultAzureCredential()
    service_client = DataLakeServiceClient(f"https://{STORAGE_ACCOUNT}", credential=credential)
    file_system_client = service_client.get_file_system_client(file_system=FILE_SYSTEM)

    print("✓ Authenticated successfully\n")

    # Upload files recursively
    uploaded_count = 0
    upload_errors = []

    print("Uploading files...")
    print("-" * 80)

    for root, dirs, files in os.walk(STAGING_DIR):
        for file in files:
            local_path = os.path.join(root, file)

            # Calculate relative path for remote location
            relative_path = os.path.relpath(local_path, STAGING_DIR)
            remote_path = f"Files/{relative_path}".replace("\\", "/")

            try:
                # Read file
                with open(local_path, 'rb') as f:
                    file_data = f.read()

                # Get file client
                file_client = file_system_client.get_file_client(remote_path)

                # Upload file
                file_client.upload_data(file_data, overwrite=True)

                file_size = len(file_data) / 1024  # KB
                print(f"  ✓ {remote_path:<60} ({file_size:>7.2f} KB)")
                uploaded_count += 1

            except Exception as e:
                error_msg = f"  ! {remote_path}: {str(e)}"
                print(error_msg)
                upload_errors.append(error_msg)

    print("-" * 80)
    print(f"\n✓ Upload Complete: {uploaded_count} files uploaded")

    if upload_errors:
        print(f"\n! {len(upload_errors)} errors encountered:")
        for error in upload_errors:
            print(error)

    # Display final summary
    print("\n" + "="*80)
    print("FABRIC DEPLOYMENT SUMMARY")
    print("="*80)

    print(f"""
Lakehouse: githubclaude
Workspace: fabricaena

Folder Structure Created:
  📁 Files/
     ├─ 📁 Bronze/
     │   └─ README.md
     ├─ 📁 Silver/
     │   └─ README.md
     ├─ 📁 Gold/
     │   └─ README.md
     ├─ 📁 Documentation/
     │   └─ README.md
     ├─ 📁 Scripts/
     │   ├─ medallion_pipeline.ipynb
     │   ├─ gold_layer_transformation.sql
     │   └─ README.md
     └─ deployment_summary.json

Files Uploaded: {uploaded_count}
Status: {'SUCCESS ✓' if not upload_errors else f'PARTIAL - {len(upload_errors)} errors'}

Next Steps:
1. Open Fabric workspace: fabricaena
2. Open Lakehouse: githubclaude
3. Navigate to: Files/Scripts/
4. Import medallion_pipeline.ipynb as Notebook
5. Run notebook to start pipeline execution
6. Use gold_layer_transformation.sql in SQL Analytical Endpoint

Documentation:
- Files/Documentation/README.md - Transformation guide
- Files/Bronze/README.md - Raw data layer info
- Files/Silver/README.md - Cleaned data layer info
- Files/Gold/README.md - Analytics layer info

""")

    print("="*80)
    print("✓ Ready to use in Fabric!")
    print("="*80)

except Exception as e:
    print(f"\n✗ ERROR: {str(e)}")
    print("\nTroubleshooting:")
    print("  1. Ensure Azure CLI is authenticated: az login")
    print("  2. Verify you have access to the Fabric workspace")
    print("  3. Check that OneLake storage is accessible")
    print("  4. Alternatively, use Azure Storage Explorer for manual upload")
    print(f"\nStaging files are located at: {STAGING_DIR}")
