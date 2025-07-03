#!/usr/bin/env python3
"""Test MCP connection for Claude Code"""

import subprocess
import json
import sys
import os

def test_mcp_connection():
    """Test if the MCP server can be connected to"""
    
    server_path = os.path.join(os.path.dirname(__file__), "server", "main.py")
    
    print("Testing MCP server connection...")
    print(f"Server path: {server_path}")
    
    try:
        # Start the server
        process = subprocess.Popen(
            [sys.executable, server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        # Send a tools/list request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        # Write request
        process.stdin.write(json.dumps(request) + '\n')
        process.stdin.flush()
        process.stdin.close()
        
        # Read response (with timeout)
        import signal
        def timeout_handler(signum, frame):
            raise TimeoutError("Server response timeout")
        
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(10)  # 10 second timeout
        
        try:
            output, error = process.communicate()
            signal.alarm(0)  # Cancel timeout
            
            if output:
                print("✅ Server responded successfully!")
                print("Response:", output[:200], "..." if len(output) > 200 else "")
                return True
            else:
                print("❌ No response from server")
                if error:
                    print("Stderr:", error)
                return False
                
        except TimeoutError:
            print("❌ Server response timeout")
            process.terminate()
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_mcp_connection()
    sys.exit(0 if success else 1)