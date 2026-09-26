#!/usr/bin/env python3
"""
Check Fabric Lakehouse Contents
List all files and folders in your Lakehouse
"""

import sys
from pathlib import Path
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from azure.storage.filedatalake import DataLakeServiceClient

# Configuration
ONELAKE_ACCOUNT = "onelake"
ONELAKE_DOMAIN = "dfs.core.windows.net"
WORKSPACE_NAME = "fabricaena"
LAKEHOUSE_NAME = "githubclaude"

def list_lakehouse_contents():
    """List all files and folders in Lakehouse"""

    print("=" * 70)
    print("📂 FABRIC LAKEHOUSE CONTENTS")
    print("=" * 70)
    print(f"\n🏢 Workspace: {WORKSPACE_NAME}")
    print(f"🏪 Lakehouse: {LAKEHOUSE_NAME}")
    print(f"📍 OneLake: {ONELAKE_ACCOUNT}.{ONELAKE_DOMAIN}")

    try:
        # Authenticate
        print("\n🔐 Authenticating to Azure...")
        try:
            credential = DefaultAzureCredential()
            credential.get_token("https://storage.azure.com/.default")
            print("✅ Using default credentials")
        except Exception:
            print("   Switching to browser authentication...")
            credential = InteractiveBrowserCredential()

        # Create client
        account_url = f"https://{ONELAKE_ACCOUNT}.{ONELAKE_DOMAIN}"
        client = DataLakeServiceClient(account_url=account_url, credential=credential)

        # Get file system
        file_system = f"{WORKSPACE_NAME}/{LAKEHOUSE_NAME}/Files"
        file_system_client = client.get_file_system_client(file_system=file_system)

        print(f"\n✅ Connected to: {file_system}")
        print("\n" + "=" * 70)
        print("📂 LAKEHOUSE FILE STRUCTURE")
        print("=" * 70)

        # List paths
        paths = file_system_client.get_paths(recursive=True)

        files_list = []
        folders_set = set()

        for path in paths:
            if path.is_directory:
                folders_set.add(path.name)
                print(f"📁 {path.name}/")
            else:
                file_size = path.content_length / (1024 * 1024)  # Convert to MB
                files_list.append((path.name, file_size))
                print(f"   📄 {path.name:<50} ({file_size:>7.2f} MB)")

        # Summary
        print("\n" + "=" * 70)
        print("📊 SUMMARY")
        print("=" * 70)
        print(f"📁 Folders: {len(folders_set)}")
        print(f"📄 Files: {len(files_list)}")

        if files_list:
            total_size = sum(size for _, size in files_list)
            print(f"💾 Total Size: {total_size:.2f} MB")

        print("\n✅ Lakehouse connection successful!")
        print("\n" + "=" * 70)
        return True

    except Exception as e:
        print(f"\n❌ Error connecting to Lakehouse:")
        print(f"   {str(e)}")
        print("\n⚠️  Troubleshooting:")
        print("   1. Ensure you're logged in: az login")
        print("   2. Check workspace name: fabricaena")
        print("   3. Check lakehouse name: githubclaude")
        print("   4. Verify you have access permissions")
        return False

if __name__ == "__main__":
    try:
        success = list_lakehouse_contents()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
