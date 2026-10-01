"""
AEGIS MCP Stdio Server — Standard Model Context Protocol Interface
Allows external MCP clients (Claude Desktop, Cursor, Goose, Custom AI Agents)
to connect directly to AEGIS Climate Intelligence tools via stdin/stdout.

Configuration for claude_desktop_config.json:
{
  "mcpServers": {
    "aegis-climate": {
      "command": "python",
      "args": ["-m", "mcp_hub.stdio_server"],
      "cwd": "/path/to/AEGIS"
    }
  }
}
"""
import sys
import json
import logging
from typing import Dict, Any

from mcp_hub.registry import TOOLS_REGISTRY
from mcp_hub.hub import execute_tool_logic

logging.basicConfig(level=logging.ERROR, stream=sys.stderr)
logger = logging.getLogger("aegis.mcp_stdio")


def handle_rpc_message(msg: Dict[str, Any]) -> Dict[str, Any]:
    req_id = msg.get("id")
    method = msg.get("method", "")
    params = msg.get("params", {})

    # 1. MCP initialize handshake
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": False}
                },
                "serverInfo": {
                    "name": "aegis-climate-mcp-server",
                    "version": "1.0.0",
                    "description": "AEGIS Autonomous Multi-Agent Climate & Financial Risk Engine"
                }
            }
        }

    # 2. MCP tools/list
    if method in ("tools/list", "list_tools"):
        tools = [
            {
                "name": k,
                "description": v.get("description", ""),
                "inputSchema": v.get("parameters", {})
            }
            for k, v in TOOLS_REGISTRY.items()
        ]
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": tools}
        }

    # 3. MCP tools/call
    if method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        if not tool_name or tool_name not in TOOLS_REGISTRY:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}
            }
        try:
            res = execute_tool_logic(tool_name, tool_args)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {"type": "text", "text": json.dumps(res, indent=2)}
                    ],
                    "isError": False
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32000, "message": f"Execution error in '{tool_name}': {str(e)}"}
            }

    # 4. Direct method invocation
    if method in TOOLS_REGISTRY:
        try:
            res = execute_tool_logic(method, params)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": res
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32000, "message": str(e)}
            }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method '{method}' not recognized"}
    }


def main():
    """Main loop reading JSON-RPC lines from standard input."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
            response = handle_rpc_message(msg)
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
