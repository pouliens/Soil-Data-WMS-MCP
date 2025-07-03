"""Setup script for BGS Soil Data WMS MCP Extension"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies for BGS Soil Data WMS MCP Extension...")
    
    try:
        # Try to install fastmcp and pydantic
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'fastmcp>=2.0.0', 'pydantic>=2.0.0'])
        print("✓ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        print("\nTry installing manually:")
        print("  pip install fastmcp pydantic")
        return False

def test_installation():
    """Test if dependencies are working"""
    print("\nTesting installation...")
    
    try:
        import fastmcp
        import pydantic
        print("✓ FastMCP and Pydantic imported successfully!")
        
        # Test the server
        from server.main import main
        print("✓ Server module loaded successfully!")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("BGS Soil Data WMS MCP Extension Setup")
    print("=" * 60)
    
    # Install dependencies
    deps_ok = install_dependencies()
    
    if deps_ok:
        # Test installation
        test_ok = test_installation()
        
        if test_ok:
            print("\n🎉 Setup completed successfully!")
            print("\nTo run the MCP server:")
            print("  python server/main.py")
            print("\nTo create DXT package:")
            print("  zip -r soil-data-wms.dxt manifest.json server/ requirements.txt")
        else:
            print("\n❌ Setup completed but tests failed.")
    else:
        print("\n❌ Setup failed.")

if __name__ == "__main__":
    main()