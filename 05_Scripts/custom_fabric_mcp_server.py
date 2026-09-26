#!/usr/bin/env python3
"""
Fabric MCP Server - Provides MCP tools to read semantic models from Fabric workspace
Implements the Model Context Protocol (stdio) for Claude Code integration
"""

import os
import sys
import json
import asyncio
import logging
from typing import Optional
import httpx

logging.basicConfig(level=logging.DEBUG, stream=sys.stderr, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration from environment
FABRIC_WORKSPACE_ID = os.getenv("FABRIC_WORKSPACE_ID", "9c06c853-c4ee-42ad-b784-9ad3c80e7f1d")
FABRIC_LAKEHOUSE_ID = os.getenv("FABRIC_LAKEHOUSE_ID", "0b4f9e6c-379c-493f-b707-0c857c8b8041")
FABRIC_TENANT_ID = os.getenv("FABRIC_TENANT_ID", "30afeb3b-d029-4c64-857b-bb0ad14b9a85")
SERVICE_PRINCIPAL_ID = os.getenv("SERVICE_PRINCIPAL_ID", "75a565ae-bdad-4d3e-88af-3c26eaae2868")
SERVICE_PRINCIPAL_SECRET = os.getenv("SERVICE_PRINCIPAL_SECRET", "Zrp8Q~XIXgcGXcJ7RIW384AC9LtVREjWNnT.6cwP")

# MCP Protocol version
MCP_VERSION = "2024-11-05"


class FabricMCPServer:
    """MCP Server for Fabric operations"""

    def __init__(self):
        self.access_token = None

    async def get_token(self) -> str:
        """Get access token for Fabric API"""
        if self.access_token:
            return self.access_token

        token_url = f"https://login.microsoftonline.com/{FABRIC_TENANT_ID}/oauth2/v2.0/token"

        data = {
            "client_id": SERVICE_PRINCIPAL_ID,
            "client_secret": SERVICE_PRINCIPAL_SECRET,
            "scope": "https://analysis.windows.net/powerbi/api/.default",
            "grant_type": "client_credentials"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(token_url, data=data, timeout=30)
                if response.status_code == 200:
                    self.access_token = response.json().get("access_token")
                    logger.info("Successfully obtained Fabric API token")
                    return self.access_token
                else:
                    logger.error(f"Token request failed: {response.text}")
                    raise Exception(f"Token request failed: {response.text}")
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise

    async def read_semantic_model(self, model_name: Optional[str] = None) -> dict:
        """Read semantic model(s) from Fabric workspace"""
        try:
            token = await self.get_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient() as client:
                # Fetch datasets
                url = f"https://api.powerbi.com/v1.0/myorg/groups/{FABRIC_WORKSPACE_ID}/datasets"
                logger.info(f"Fetching datasets from: {url}")
                response = await client.get(url, headers=headers, timeout=30)

                if response.status_code != 200:
                    error_msg = f"Failed to fetch datasets: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return {"error": error_msg}

                datasets = response.json().get("value", [])
                logger.info(f"Found {len(datasets)} dataset(s)")

                # Filter by name if specified
                if model_name:
                    datasets = [ds for ds in datasets if model_name.lower() in ds["name"].lower()]
                    logger.info(f"Filtered to {len(datasets)} dataset(s) matching '{model_name}'")

                result = {
                    "workspace_id": FABRIC_WORKSPACE_ID,
                    "models": []
                }

                for dataset in datasets:
                    dataset_id = dataset["id"]
                    dataset_name = dataset["name"]
                    logger.info(f"Processing dataset: {dataset_name}")

                    # Fetch tables
                    tables_url = f"https://api.powerbi.com/v1.0/myorg/groups/{FABRIC_WORKSPACE_ID}/datasets/{dataset_id}/tables"
                    tables_response = await client.get(tables_url, headers=headers, timeout=30)

                    if tables_response.status_code == 200:
                        tables = tables_response.json().get("value", [])
                        logger.info(f"Found {len(tables)} table(s) in {dataset_name}")

                        model_info = {
                            "name": dataset_name,
                            "id": dataset_id,
                            "created_date": dataset.get("createdDate"),
                            "modified_date": dataset.get("modifiedDate"),
                            "tables": []
                        }

                        for table in tables:
                            columns = table.get("columns", [])
                            table_info = {
                                "name": table.get("name"),
                                "description": table.get("description", ""),
                                "column_count": len(columns),
                                "columns": [
                                    {
                                        "name": col.get("name"),
                                        "type": col.get("dataType"),
                                        "description": col.get("description", "")
                                    }
                                    for col in columns
                                ]
                            }
                            model_info["tables"].append(table_info)

                        result["models"].append(model_info)

                return result

        except Exception as e:
            logger.error(f"Error reading semantic model: {e}")
            return {"error": str(e)}

    async def handle_request(self, request: dict) -> dict:
        """Handle MCP protocol requests"""
        method = request.get("method")
        logger.info(f"Handling request: {method}")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "protocolVersion": MCP_VERSION,
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "Fabric MCP Server",
                        "version": "1.0.0"
                    }
                }
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "tools": [
                        {
                            "name": "read_semantic_model",
                            "description": "Read semantic model from Fabric workspace. Returns complete schema with tables and columns.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "model_name": {
                                        "type": "string",
                                        "description": "Optional: Filter by model name (e.g., 'GitClaude')"
                                    }
                                },
                                "required": []
                            }
                        }
                    ]
                }
            }

        elif method == "tools/call":
            tool_name = request.get("params", {}).get("name")
            tool_args = request.get("params", {}).get("arguments", {})

            if tool_name == "read_semantic_model":
                logger.info(f"Calling read_semantic_model with args: {tool_args}")
                result = await self.read_semantic_model(tool_args.get("model_name"))
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }

        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {"code": -32601, "message": f"Method '{method}' not found"}
        }


async def main():
    """Main MCP server loop"""
    server = FabricMCPServer()
    logger.info("Fabric MCP Server started")

    try:
        while True:
            try:
                # Read from stdin
                line = sys.stdin.readline()
                if not line:
                    logger.info("EOF received, shutting down")
                    break

                request = json.loads(line)
                logger.debug(f"Received: {request}")

                # Handle request
                response = await server.handle_request(request)

                # Write to stdout
                print(json.dumps(response), flush=True)
                logger.debug(f"Sent response")

            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": "Parse error"}
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                logger.error(f"Request error: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32603, "message": str(e)}
                }
                print(json.dumps(error_response), flush=True)
    except KeyboardInterrupt:
        logger.info("Server interrupted")
    except Exception as e:
        logger.error(f"Fatal error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
