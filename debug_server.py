"""Debug the server output"""

import subprocess
import sys
import time

# Start the server
process = subprocess.Popen(
    [sys.executable, "server/main.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Wait a moment for startup
time.sleep(1)

# Check if there's any immediate output
print("=== STDOUT ===")
try:
    stdout_data = process.stdout.read(1024)
    if stdout_data:
        print(repr(stdout_data))
    else:
        print("No stdout data")
except:
    print("Error reading stdout")

print("\n=== STDERR ===")
try:
    stderr_data = process.stderr.read(1024)
    if stderr_data:
        print(stderr_data)
    else:
        print("No stderr data")
except:
    print("Error reading stderr")

# Clean up
process.terminate()
process.wait()