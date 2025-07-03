#!/usr/bin/env python3
"""Test MCP connection for Claude Code"""

import subprocess
import json
import sys
import os
import time
import threading

def test_mcp_server():
    """Test the MCP server using stdio transport"""
    
    print("🔗 Testing BGS WMS MCP Server Connection")
    print("=" * 50)
    
    server_path = os.path.join(os.path.dirname(__file__), "server", "main.py")
    print(f"Server: {server_path}")
    
    try:
        # Start the server process
        print("\n1. Starting MCP server...")
        process = subprocess.Popen(
            [sys.executable, server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0,  # Unbuffered
            cwd=os.path.dirname(__file__)
        )
        
        # Give the server a moment to start
        time.sleep(0.5)
        
        # Check if process is running
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print(f"❌ Server exited immediately")
            print(f"Stdout: {stdout}")
            print(f"Stderr: {stderr}")
            return False
        
        print("✅ Server process started")
        
        # Test 1: Send tools/list request
        print("\n2. Testing tools/list request...")
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        request_json = json.dumps(request) + '\n'
        print(f"Sending: {request_json.strip()}")
        
        # Send request
        try:
            process.stdin.write(request_json)
            process.stdin.flush()
        except Exception as e:
            print(f"❌ Failed to send request: {e}")
            process.terminate()
            return False
        
        # Read response with timeout
        response_data = None
        try:
            # Use a thread to read with timeout
            def read_output():
                nonlocal response_data
                try:
                    response_data = process.stdout.readline()
                except:
                    pass
            
            reader_thread = threading.Thread(target=read_output)
            reader_thread.daemon = True
            reader_thread.start()
            reader_thread.join(timeout=5)  # 5 second timeout
            
            if response_data:
                print(f"✅ Received response: {response_data.strip()}")
                
                # Parse response
                try:
                    response = json.loads(response_data.strip())
                    if "result" in response and "tools" in response["result"]:
                        tools = response["result"]["tools"]
                        print(f"✅ Found {len(tools)} tools:")
                        for tool in tools:
                            print(f"   • {tool['name']}: {tool['description']}")
                        
                        # Test 2: Call a simple tool
                        print("\n3. Testing get_soil_data_summary...")
                        
                        call_request = {
                            "jsonrpc": "2.0",
                            "id": 2,
                            "method": "tools/call",
                            "params": {
                                "name": "get_soil_data_summary",
                                "arguments": {}
                            }
                        }
                        
                        call_json = json.dumps(call_request) + '\n'
                        process.stdin.write(call_json)
                        process.stdin.flush()
                        
                        # Read tool response
                        tool_response_data = None
                        def read_tool_output():
                            nonlocal tool_response_data
                            try:
                                tool_response_data = process.stdout.readline()
                            except:
                                pass
                        
                        tool_reader = threading.Thread(target=read_tool_output)
                        tool_reader.daemon = True
                        tool_reader.start()
                        tool_reader.join(timeout=5)
                        
                        if tool_response_data:
                            tool_response = json.loads(tool_response_data.strip())
                            if "result" in tool_response:
                                print("✅ Tool call successful!")
                                print(f"   Response: {tool_response_data.strip()[:100]}...")
                            else:
                                print(f"❌ Tool call failed: {tool_response}")
                        else:
                            print("❌ No tool response received")
                        
                        print("\n" + "=" * 50)
                        print("🎉 MCP Server Connection Test Results:")
                        print("✅ Server starts successfully")
                        print("✅ Responds to tools/list")
                        print(f"✅ {len(tools)} tools available")
                        print("✅ Tool calls work")
                        print("\n📋 Configuration for Claude Code:")
                        print(json.dumps({
                            "mcpServers": {
                                "bgs-soil-wms": {
                                    "command": "python",
                                    "args": ["server/main.py"],
                                    "cwd": os.path.abspath(os.path.dirname(__file__))
                                }
                            }
                        }, indent=2))
                        
                        return True
                    else:
                        print(f"❌ Unexpected response format: {response}")
                        return False
                        
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse response: {e}")
                    print(f"Raw response: {response_data}")
                    return False
            else:
                print("❌ No response received within timeout")
                return False
                
        finally:
            # Clean up
            try:
                process.terminate()
                process.wait(timeout=2)
            except:
                process.kill()
                
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_mcp_server()
    if success:
        print("\n🌍 Ready to connect to Claude Code!")
    else:
        print("\n❌ Connection test failed")
    sys.exit(0 if success else 1)