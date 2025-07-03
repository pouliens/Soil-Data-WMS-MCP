"""Test the MCP server implementation"""

import subprocess
import json
import asyncio
import sys


async def test_mcp_server():
    """Test the MCP server by sending JSON-RPC requests"""
    print("Testing MCP server...")
    
    # Start the server process
    process = subprocess.Popen(
        [sys.executable, "server/main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Test 1: List tools
        print("\n1. Testing tools/list...")
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        process.stdin.write(json.dumps(request) + '\n')
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            if "result" in response and "tools" in response["result"]:
                tools = response["result"]["tools"]
                print(f"✓ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"  - {tool['name']}: {tool['description']}")
            else:
                print(f"✗ Unexpected response: {response}")
        else:
            print("✗ No response received")
        
        # Test 2: Call get_soil_data_summary
        print("\n2. Testing get_soil_data_summary...")
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "get_soil_data_summary",
                "arguments": {}
            }
        }
        
        process.stdin.write(json.dumps(request) + '\n')
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            if "result" in response and "content" in response["result"]:
                print("✓ get_soil_data_summary works")
                # Parse the content
                content = response["result"]["content"][0]["text"]
                summary = json.loads(content)
                print(f"  Found {len(summary['soil_data_types'])} soil data types")
            else:
                print(f"✗ Unexpected response: {response}")
        else:
            print("✗ No response received")
        
        # Test 3: Call get_capabilities
        print("\n3. Testing get_capabilities...")
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_capabilities",
                "arguments": {}
            }
        }
        
        process.stdin.write(json.dumps(request) + '\n')
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            if "result" in response and "content" in response["result"]:
                print("✓ get_capabilities works")
                # Parse the content
                content = response["result"]["content"][0]["text"]
                capabilities = json.loads(content)
                print(f"  Service: {capabilities['title']}")
                print(f"  Layers: {len(capabilities['layers'])}")
            else:
                print(f"✗ Unexpected response: {response}")
        else:
            print("✗ No response received")
            
    finally:
        # Clean up
        process.terminate()
        process.wait()
    
    print("\n✓ MCP server test completed!")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())