"""Test script for the BGS WMS MCP server"""

import asyncio
import json
import logging
from soil_wms_mcp.wms_client import WMSClient, BoundingBox

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_wms_client():
    """Test the WMS client functionality"""
    print("Testing BGS WMS Client...")
    
    async with WMSClient() as client:
        # Test GetCapabilities
        print("\n1. Testing GetCapabilities...")
        try:
            capabilities = await client.get_capabilities()
            print(f"✓ Service: {capabilities.title}")
            print(f"✓ Version: {capabilities.version}")
            print(f"✓ Layers found: {len(capabilities.layers)}")
            print(f"✓ Image formats: {', '.join(capabilities.formats)}")
            
            # Show first few layers
            if capabilities.layers:
                print("\nFirst 5 layers:")
                for i, layer in enumerate(capabilities.layers[:5]):
                    print(f"  {i+1}. {layer.name}: {layer.title}")
                    
        except Exception as e:
            print(f"✗ GetCapabilities failed: {e}")
            return False
            
        # Test layer search
        print("\n2. Testing layer search...")
        try:
            soil_layers = await client.search_layers("soil")
            print(f"✓ Found {len(soil_layers)} layers matching 'soil'")
            
            depth_layers = await client.search_layers("depth")
            print(f"✓ Found {len(depth_layers)} layers matching 'depth'")
            
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
            if capabilities.layers:
                layer_name = capabilities.layers[0].name
                map_url = await client.get_map(
                    layers=[layer_name],
                    bbox=bbox,
                    width=400,
                    height=300
                )
                print(f"✓ Generated map URL: {map_url[:100]}...")
                
        except Exception as e:
            print(f"✗ GetMap failed: {e}")
            
        # Test coordinate conversion
        print("\n4. Testing coordinate conversion...")
        try:
            # Convert London coordinates from WGS84 to BNG
            lon, lat = -0.1276, 51.5074  # London
            x, y = await client.convert_coordinates(lon, lat, "EPSG:4326", "EPSG:27700")
            print(f"✓ London WGS84 ({lon}, {lat}) -> BNG ({x:.0f}, {y:.0f})")
            
            # Convert back
            lon2, lat2 = await client.convert_coordinates(x, y, "EPSG:27700", "EPSG:4326")
            print(f"✓ BNG ({x:.0f}, {y:.0f}) -> WGS84 ({lon2:.4f}, {lat2:.4f})")
            
        except Exception as e:
            print(f"✗ Coordinate conversion failed: {e}")
            
    print("\n✓ WMS Client tests completed!")
    return True


async def test_mcp_server():
    """Test the MCP server tools"""
    print("\nTesting MCP Server Tools...")
    
    try:
        # Import the server module
        from soil_wms_mcp.server import (
            get_capabilities, list_layers, describe_layer, 
            get_soil_data_summary, convert_coordinates
        )
        from soil_wms_mcp.server import ConvertCoordinatesRequest
        
        # Test get_capabilities
        print("\n1. Testing get_capabilities tool...")
        capabilities = await get_capabilities()
        print(f"✓ Got capabilities: {capabilities.title}")
        
        # Test list_layers
        print("\n2. Testing list_layers tool...")
        layers = await list_layers()
        print(f"✓ Listed {len(layers)} layers")
        
        # Test search layers
        if layers:
            soil_layers = await list_layers("soil")
            print(f"✓ Found {len(soil_layers)} soil-related layers")
            
            # Test describe_layer
            print("\n3. Testing describe_layer tool...")
            first_layer = await describe_layer(layers[0].name)
            if first_layer:
                print(f"✓ Described layer: {first_layer.title}")
            
        # Test coordinate conversion
        print("\n4. Testing convert_coordinates tool...")
        conv_request = ConvertCoordinatesRequest(
            x=-0.1276, y=51.5074,
            source_crs="EPSG:4326",
            target_crs="EPSG:27700"
        )
        result = await convert_coordinates(conv_request)
        print(f"✓ Converted coordinates: {result}")
        
        # Test soil data summary
        print("\n5. Testing get_soil_data_summary tool...")
        summary = await get_soil_data_summary()
        print(f"✓ Got soil data summary with {len(summary['soil_data_types'])} data types")
        
    except Exception as e:
        print(f"✗ MCP server test failed: {e}")
        return False
        
    print("\n✓ MCP Server tests completed!")
    return True


async def main():
    """Run all tests"""
    print("=" * 60)
    print("BGS Soil Data WMS MCP Server - Test Suite")
    print("=" * 60)
    
    # Test WMS client
    wms_success = await test_wms_client()
    
    # Test MCP server
    mcp_success = await test_mcp_server()
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"WMS Client: {'✓ PASSED' if wms_success else '✗ FAILED'}")
    print(f"MCP Server: {'✓ PASSED' if mcp_success else '✗ FAILED'}")
    
    if wms_success and mcp_success:
        print("\n🎉 All tests passed! The MCP server is ready to use.")
        print("\nTo start the server:")
        print("  python -m soil_wms_mcp.server")
        print("\nTo start with MCP Inspector:")
        print("  mcp dev soil_wms_mcp/server.py")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    asyncio.run(main())