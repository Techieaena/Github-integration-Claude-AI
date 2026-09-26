"""
Fabric Lakehouse Connector - OneLake Integration
Upload and manage files in Fabric Lakehouse
"""

import os
import json
from pathlib import Path
from typing import Optional, List
import requests
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from azure.storage.filedatalake import DataLakeServiceClient
import time

# Fabric Configuration
TENANT_ID = "30afeb3b-d029-4c64-857b-bb0ad14b9a85"
WORKSPACE_ID = "9c06c853-c4ee-42ad-b784-9ad3c80e7f1d"
LAKEHOUSE_ID = "0b4f9e6c-379c-493f-b707-0c857c8b8041"
LAKEHOUSE_NAME = "githubclaude"

# OneLake Configuration
ONELAKE_ACCOUNT_NAME = "onelakecatalog"
ONELAKE_ENDPOINT = f"https://{ONELAKE_ACCOUNT_NAME}.dfs.core.windows.net"
ONELAKE_PATH = f"/{WORKSPACE_ID}/{LAKEHOUSE_ID}"


class FabricLakehouseConnector:
    """Connect and manage Fabric Lakehouse using OneLake API"""

    def __init__(self, tenant_id: str = TENANT_ID, use_interactive: bool = False):
        """
        Initialize Fabric Lakehouse connector

        Args:
            tenant_id: Azure Tenant ID
            use_interactive: Use interactive browser authentication
        """
        self.tenant_id = tenant_id
        self.credential = None
        self.service_client = None
        self.authenticate(use_interactive)

    def authenticate(self, use_interactive: bool = False):
        """Authenticate with Azure/Fabric"""
        print("🔐 Authenticating with Azure...")

        try:
            if use_interactive:
                self.credential = InteractiveBrowserCredential(tenant_id=self.tenant_id)
                print("   Using: Interactive Browser Authentication")
            else:
                self.credential = DefaultAzureCredential()
                print("   Using: Default Credential Chain")

            # Test token
            token = self.credential.get_token("https://storage.azure.com/.default")
            print(f"✅ Authenticated successfully")

            # Initialize DataLake Service Client
            self.service_client = DataLakeServiceClient(
                account_url=ONELAKE_ENDPOINT,
                credential=self.credential
            )

        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            raise

    def get_file_system_client(self):
        """Get file system client for OneLake"""
        try:
            # For OneLake, the file system name is workspace_id/lakehouse_id
            file_system_name = f"{WORKSPACE_ID}/{LAKEHOUSE_ID}"
            return self.service_client.get_file_system_client(file_system_name)
        except Exception as e:
            print(f"⚠️  File system client error: {e}")
            return None

    def create_directory(self, path: str) -> bool:
        """Create directory in lakehouse"""
        try:
            file_client = self.service_client.get_file_system_client(
                f"{WORKSPACE_ID}/{LAKEHOUSE_ID}"
            ).get_directory_client(path)
            file_client.create_directory()
            print(f"   ✓ Created directory: {path}")
            return True
        except Exception as e:
            if "PathAlreadyExistsError" in str(e) or "already exists" in str(e):
                print(f"   ℹ️  Directory already exists: {path}")
                return True
            print(f"   ⚠️  Error creating directory {path}: {e}")
            return False

    def upload_file(self, local_file_path: str, lakehouse_path: str) -> bool:
        """
        Upload a single file to lakehouse

        Args:
            local_file_path: Path to local file
            lakehouse_path: Path in lakehouse (e.g., "Files/Bronze/customers.csv")

        Returns:
            True if successful
        """
        try:
            local_path = Path(local_file_path)

            if not local_path.exists():
                print(f"   ❌ File not found: {local_file_path}")
                return False

            file_size_mb = local_path.stat().st_size / 1024 / 1024

            print(f"   📤 Uploading: {local_path.name} ({file_size_mb:.2f} MB)")

            # Get file client
            file_system_client = self.get_file_system_client()
            if not file_system_client:
                return False

            file_client = file_system_client.get_file_client(lakehouse_path)

            # Upload file
            with open(local_file_path, "rb") as data:
                file_client.upload_data(data, overwrite=True)

            print(f"   ✓ Uploaded: {lakehouse_path}")
            return True

        except Exception as e:
            print(f"   ❌ Upload failed: {e}")
            return False

    def upload_directory(self, local_dir: str, lakehouse_dir: str, pattern: str = "*") -> int:
        """
        Upload all files from a directory

        Args:
            local_dir: Local directory path
            lakehouse_dir: Target directory in lakehouse
            pattern: File pattern (default: all files)

        Returns:
            Number of files uploaded
        """
        print(f"\n📤 Uploading directory: {local_dir}")
        print(f"   → Destination: {lakehouse_dir}")
        print("-" * 70)

        local_path = Path(local_dir)

        if not local_path.exists():
            print(f"❌ Directory not found: {local_dir}")
            return 0

        # Create target directory
        self.create_directory(lakehouse_dir)

        uploaded_count = 0

        # Upload all files
        for file_path in local_path.rglob(pattern):
            if file_path.is_file():
                # Calculate relative path
                rel_path = file_path.relative_to(local_path)
                lakehouse_file_path = f"{lakehouse_dir}/{rel_path}".replace("\\", "/")

                # Create subdirectories if needed
                dir_path = str(Path(lakehouse_file_path).parent)
                if dir_path != lakehouse_dir:
                    self.create_directory(dir_path)

                # Upload file
                if self.upload_file(str(file_path), lakehouse_file_path):
                    uploaded_count += 1

        print(f"\n✅ Uploaded {uploaded_count} files to {lakehouse_dir}")
        return uploaded_count

    def download_file(self, lakehouse_path: str, local_file_path: str) -> bool:
        """Download file from lakehouse"""
        try:
            print(f"📥 Downloading: {lakehouse_path}")

            file_system_client = self.get_file_system_client()
            if not file_system_client:
                return False

            file_client = file_system_client.get_file_client(lakehouse_path)

            with open(local_file_path, "wb") as file_stream:
                download = file_client.download_file()
                file_stream.write(download.readall())

            print(f"   ✓ Downloaded to: {local_file_path}")
            return True

        except Exception as e:
            print(f"   ❌ Download failed: {e}")
            return False

    def list_files(self, lakehouse_path: str = "", recursive: bool = True) -> List[str]:
        """List files in lakehouse directory"""
        try:
            print(f"\n📂 Listing: {lakehouse_path if lakehouse_path else 'Root'}")

            file_system_client = self.get_file_system_client()
            if not file_system_client:
                return []

            files = []

            if lakehouse_path:
                dir_client = file_system_client.get_directory_client(lakehouse_path)
                items = dir_client.get_paths(recursive=recursive)
            else:
                items = file_system_client.get_paths(recursive=recursive)

            for item in items:
                files.append(item.name)
                print(f"   ├─ {item.name}")

            return files

        except Exception as e:
            print(f"⚠️  Error listing files: {e}")
            return []

    def get_file_info(self, lakehouse_path: str) -> Optional[dict]:
        """Get file information"""
        try:
            file_system_client = self.get_file_system_client()
            if not file_system_client:
                return None

            file_client = file_system_client.get_file_client(lakehouse_path)
            properties = file_client.get_file_properties()

            return {
                "path": lakehouse_path,
                "size": properties.get("size", 0),
                "modified": properties.get("last_modified"),
                "content_type": properties.get("content_settings", {}).get("content_type")
            }

        except Exception as e:
            print(f"⚠️  Error getting file info: {e}")
            return None

    def delete_file(self, lakehouse_path: str) -> bool:
        """Delete file from lakehouse"""
        try:
            file_system_client = self.get_file_system_client()
            if not file_system_client:
                return False

            file_client = file_system_client.get_file_client(lakehouse_path)
            file_client.delete_file()

            print(f"   ✓ Deleted: {lakehouse_path}")
            return True

        except Exception as e:
            print(f"   ❌ Delete failed: {e}")
            return False

    def create_sql_view(self, view_name: str, delta_path: str) -> Optional[str]:
        """Create SQL view for Delta table (Requires Fabric SQL endpoint)"""
        print(f"\n📊 Creating SQL view: {view_name}")

        sql_query = f"""
        CREATE VIEW [{view_name}] AS
        SELECT * FROM delta.`{delta_path}`
        """

        print(f"   Query: {sql_query}")
        return sql_query

    def get_lakehouse_status(self) -> dict:
        """Get lakehouse connection status"""
        print("\n" + "=" * 70)
        print("🏢 FABRIC LAKEHOUSE STATUS")
        print("=" * 70)

        try:
            status = {
                "workspace_name": LAKEHOUSE_NAME,
                "workspace_id": WORKSPACE_ID,
                "lakehouse_id": LAKEHOUSE_ID,
                "onelake_endpoint": ONELAKE_ENDPOINT,
                "authenticated": self.credential is not None,
                "service_client_ready": self.service_client is not None
            }

            for key, value in status.items():
                print(f"{key}: {value}")

            # Try to list files
            print("\n📂 Lakehouse Contents:")
            files = self.list_files("Files")

            return status

        except Exception as e:
            print(f"⚠️  Error: {e}")
            return None


def main():
    """Test Fabric Lakehouse connector"""

    print("=" * 70)
    print("🔗 FABRIC LAKEHOUSE CONNECTOR TEST")
    print("=" * 70)

    try:
        # Initialize connector
        connector = FabricLakehouseConnector(use_interactive=False)

        # Get status
        connector.get_lakehouse_status()

        # Create folder structure
        print("\n" + "=" * 70)
        print("📁 CREATING FOLDER STRUCTURE")
        print("=" * 70)

        folders = [
            "Files/Bronze",
            "Files/Silver",
            "Files/Gold",
            "Files/Logs"
        ]

        for folder in folders:
            connector.create_directory(folder)

        print("\n✅ Folder structure created")

        # List contents
        print("\n" + "=" * 70)
        connector.list_files("Files")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Ensure you're authenticated with Azure CLI: az login")
        print("2. Verify workspace and lakehouse IDs are correct")
        print("3. Check Fabric workspace permissions")


if __name__ == "__main__":
    main()
