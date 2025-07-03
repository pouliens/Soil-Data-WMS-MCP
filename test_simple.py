"""Simple test of the DXT extension structure"""

import asyncio
import sys
import os

# Add server directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from utils import WMSClient, BoundingBox


async def test_wms_client():
    """Test the simplified WMS client"""
    print("Testing simplified WMS client...")
    
    client = WMSClient()
    
    # Test GetCapabilities
    print("\n1. Testing GetCapabilities...")
    try:
        capabilities = await client.get_capabilities()
        print(f"✓ Service: {capabilities['title']}")
        print(f"✓ Version: {capabilities['version']}")
        print(f"✓ Layers found: {len(capabilities['layers'])}")
        
        # Show first few layers
        if capabilities['layers']:
            print("\nFirst 5 layers:")
            for i, layer in enumerate(capabilities['layers'][:5]):
                print(f"  {i+1}. {layer['name']}: {layer['title']}")
                
    except Exception as e:
        print(f"✗ GetCapabilities failed: {e}")
        return False
        
    # Test layer search
    print("\n2. Testing layer search...")
    try:
        soil_layers = await client.search_layers("soil")
        print(f"✓ Found {len(soil_layers)} layers matching 'soil'")
        
    except Exception as e:
        print(f"✗ Layer search failed: {e}")
        
    # Test GetMap URL generation
    print("\n3. Testing GetMap URL generation...")
    try:
        # Use a simple bounding box for UK
        bbox = BoundingBox(
            min_x=-6.0, min_y=50.0,
            max_x=2.0, max_y=58.0,
            crs="EPSG:4326"
        )
        
        # Try to get a layer for mapping
        if capabilities['layers']:
            layer_name = capabilities['layers'][0]['name']
            map_url = await client.get_map(
                layers=[layer_name],
                bbox=bbox,
                width=400,
                height=300
            )
            print(f"✓ Generated map URL: {map_url[:100]}...")
            
    except Exception as e:
        print(f"✗ GetMap failed: {e}")
        
    print("\n✓ WMS Client tests completed!")
    return True


async def test_project_structure():
    """Test the project structure"""
    print("\nTesting project structure...")
    
    required_files = [
        "manifest.json",
        "requirements.txt",
        "server/main.py",
        "server/utils.py"
    ]
    
    base_dir = os.path.dirname(__file__)
    
    for file_path in required_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            print(f"✓ {file_path} exists")
        else:
            print(f"✗ {file_path} missing")
            return False
            
    print("✓ Project structure is correct!")
    return True


async def main():
    """Run all tests"""
    print("=" * 60)
    print("BGS Soil Data WMS - DXT Extension Test")
    print("=" * 60)
    
    # Test project structure
    structure_ok = await test_project_structure()
    
    # Test WMS client
    client_ok = await test_wms_client()
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Project Structure: {'✓ PASSED' if structure_ok else '✗ FAILED'}")
    print(f"WMS Client: {'✓ PASSED' if client_ok else '✗ FAILED'}")
    
    if structure_ok and client_ok:
        print("\n🎉 DXT extension is ready!")
        print("\nTo create the extension package:")
        print("  zip -r soil-data-wms.dxt manifest.json server/ requirements.txt")
        print("\nTo test the MCP server:")
        print("  python server/main.py")
    else:
        print("\n❌ Some tests failed.")


if __name__ == "__main__":
    asyncio.run(main())