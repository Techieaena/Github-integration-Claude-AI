"""
Read Fabric Semantic Model using VS Code authentication
Leverages VS Code's built-in Fabric extension credentials
"""

import os
import json
import requests
import subprocess
from pathlib import Path
from datetime import datetime

print("\n" + "=" * 100)
print(" FABRIC SEMANTIC MODEL READER - VS Code Authentication")
print("=" * 100 + "\n")

WORKSPACE_ID = "9c06c853-c4ee-42ad-b784-9ad3c80e7f1d"
LAKEHOUSE_ID = "0b4f9e6c-379c-493f-b707-0c857c8b8041"
LAKEHOUSE_NAME = "githubclaude"

try:
    # Step 1: Get token from VS Code's credential store via Azure CLI
    print("[*] Step 1: Getting access token from VS Code/Azure CLI...")

    # Try to get token using Azure CLI with VS Code stored credentials
    result = subprocess.run(
        [
            "az", "account", "get-access-token",
            "--resource", "https://api.powerbi.com",
            "--query", "accessToken",
            "-o", "tsv"
        ],
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        print(f"[ERROR] Azure CLI failed: {result.stderr}")
        print("\n[TIP] Make sure to login first:")
        print("   az login --tenant '30afeb3b-d029-4c64-857b-bb0ad14b9a85'")
        exit(1)

    access_token = result.stdout.strip()

    if not access_token:
        print("[ERROR] No token received")
        exit(1)

    print(f"[OK] Access token obtained\n")

    # Step 2: Fetch datasets from Fabric
    print("[*] Step 2: Fetching datasets from Fabric workspace...")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    datasets_url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/datasets"
    datasets_response = requests.get(datasets_url, headers=headers, timeout=30)

    if datasets_response.status_code != 200:
        print(f"[ERROR] Failed to fetch datasets: {datasets_response.status_code}")
        print(f"[RESPONSE] {datasets_response.text}")
        exit(1)

    datasets = datasets_response.json().get("value", [])
    print(f"[OK] Found {len(datasets)} semantic model(s)\n")

    # Step 3: Process each dataset
    print("=" * 100)
    print(" SEMANTIC MODELS")
    print("=" * 100 + "\n")

    semantic_models = {}

    for dataset in datasets:
        dataset_id = dataset["id"]
        dataset_name = dataset["name"]

        print(f"[DATASET] {dataset_name}")
        print(f"          ID: {dataset_id}")
        print(f"          Created: {dataset.get('createdDate', 'N/A')}")
        print(f"          Modified: {dataset.get('modifiedDate', 'N/A')}")

        # Get tables
        tables_url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/datasets/{dataset_id}/tables"
        tables_response = requests.get(tables_url, headers=headers, timeout=30)

        if tables_response.status_code == 200:
            tables = tables_response.json().get("value", [])
            print(f"          Tables: {len(tables)}")

            dataset_info = {
                "id": dataset_id,
                "name": dataset_name,
                "created_date": dataset.get("createdDate"),
                "modified_date": dataset.get("modifiedDate"),
                "tables": []
            }

            for table in tables:
                table_name = table.get("name")
                columns = table.get("columns", [])

                table_info = {
                    "name": table_name,
                    "description": table.get("description", ""),
                    "source_expression": table.get("sourceExpression", ""),
                    "columns": []
                }

                for col in columns:
                    col_info = {
                        "name": col.get("name"),
                        "type": col.get("dataType"),
                        "description": col.get("description", "")
                    }
                    table_info["columns"].append(col_info)

                dataset_info["tables"].append(table_info)
                print(f"             - {table_name} ({len(columns)} columns)")

            semantic_models[dataset_name] = dataset_info

        print()

    # Step 4: Save to file
    output_path = Path("02_SemanticModel/fabric_semantic_model_vscode.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_data = {
        "workspace_id": WORKSPACE_ID,
        "lakehouse_id": LAKEHOUSE_ID,
        "lakehouse_name": LAKEHOUSE_NAME,
        "exported_date": datetime.now().isoformat(),
        "source": "Fabric API via VS Code Authentication",
        "semantic_models": semantic_models
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print("=" * 100)
    print(f"[OK] Semantic models exported to: {output_path}")
    print(f"[SUMMARY] Total datasets: {len(semantic_models)}")
    for model_name, model_info in semantic_models.items():
        print(f"   - {model_name}: {len(model_info['tables'])} tables")
    print("=" * 100 + "\n")

except subprocess.TimeoutExpired:
    print("[ERROR] Request timed out")
    exit(1)
except Exception as e:
    print(f"[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
