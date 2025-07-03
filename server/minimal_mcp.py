"""Minimal MCP implementation for when FastMCP is not available"""

import json
import sys
import asyncio
from typing import Dict, Any, List, Callable


class MinimalMCP:
    """Minimal MCP server implementation"""
    
    def __init__(self, name: str):
        self.name = name
        self.tools = {}
        
    def tool(self, name: str = None):
        """Decorator to register tools"""
        def decorator(func):
            tool_name = name or func.__name__
            self.tools[tool_name] = func
            return func
        return decorator
        
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            
            if method == "tools/list":
                return {
                    "tools": [
                        {
                            "name": name,
                            "description": func.__doc__ or f"Tool: {name}",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        }
                        for name, func in self.tools.items()
                    ]
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name in self.tools:
                    try:
                        result = await self.tools[tool_name](**arguments)
                        return {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(result, indent=2) if not isinstance(result, str) else result
                                }
                            ]
                        }
                    except Exception as e:
                        return {
                            "error": {
                                "code": -1,
                                "message": str(e)
                            }
                        }
                else:
                    return {
                        "error": {
                            "code": -1,
                            "message": f"Tool '{tool_name}' not found"
                        }
                    }
            else:
                return {
                    "error": {
                        "code": -1,
                        "message": f"Unknown method: {method}"
                    }
                }
        except Exception as e:
            return {
                "error": {
                    "code": -1,
                    "message": str(e)
                }
            }
    
    def run(self):
        """Run the MCP server with stdio transport"""
        print(f"Starting MCP server: {self.name}", file=sys.stderr)
        print("Available tools:", file=sys.stderr)
        for name, func in self.tools.items():
            print(f"  - {name}: {func.__doc__ or 'No description'}", file=sys.stderr)
        print("Server ready for MCP requests...", file=sys.stderr)
        
        asyncio.run(self._run_server())
    
    async def _run_server(self):
        """Run the MCP server loop"""
        while True:
            try:
                # Read JSON-RPC request from stdin
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line.strip())
                response = await self.handle_request(request)
                
                # Add JSON-RPC envelope
                json_rpc_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": response
                }
                
                # Write response to stdout
                print(json.dumps(json_rpc_response), flush=True)
                
            except json.JSONDecodeError:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id") if 'request' in locals() else None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)