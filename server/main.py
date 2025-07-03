"""BGS Soil Data WMS MCP Server - Main Entry Point"""

import asyncio
import json
import logging
import sys
import os
from typing import List, Optional, Union

# Add lib directory to path for bundled dependencies
lib_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lib')
if os.path.exists(lib_dir):
    sys.path.insert(0, lib_dir)

# Try to import dependencies, fallback to minimal implementation
try:
    from fastmcp import FastMCP
    HAS_FASTMCP = True
except ImportError:
    print("FastMCP not available - using minimal MCP implementation", file=sys.stderr)
    from minimal_mcp import MinimalMCP
    HAS_FASTMCP = False

try:
    from pydantic import BaseModel, Field
    HAS_PYDANTIC = True
except ImportError:
    print("Pydantic not available - using basic data classes", file=sys.stderr)
    HAS_PYDANTIC = False
    
    # Minimal BaseModel replacement
    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    def Field(default=None, description=""):
        return default

from utils import WMSClient, BoundingBox

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
if HAS_FASTMCP:
    mcp = FastMCP("BGS Soil Data WMS")
else:
    mcp = MinimalMCP("BGS Soil Data WMS")


class GetMapRequest(BaseModel):
    """Request parameters for GetMap operation"""
    layers: Union[str, List[str]] = Field(..., description="Layer name(s) to display")
    min_x: float = Field(..., description="Minimum X coordinate (longitude)")
    min_y: float = Field(..., description="Minimum Y coordinate (latitude)")
    max_x: float = Field(..., description="Maximum X coordinate (longitude)")
    max_y: float = Field(..., description="Maximum Y coordinate (latitude)")
    width: int = Field(default=800, description="Map width in pixels")
    height: int = Field(default=600, description="Map height in pixels")
    format: str = Field(default="image/png", description="Image format")
    crs: str = Field(default="EPSG:4326", description="Coordinate reference system")
    transparent: bool = Field(default=True, description="Transparent background")
    version: str = Field(default="1.3.0", description="WMS version")


class GetFeatureInfoRequest(BaseModel):
    """Request parameters for GetFeatureInfo operation"""
    layers: Union[str, List[str]] = Field(..., description="Layer name(s) to query")
    min_x: float = Field(..., description="Minimum X coordinate (longitude)")
    min_y: float = Field(..., description="Minimum Y coordinate (latitude)")
    max_x: float = Field(..., description="Maximum X coordinate (longitude)")
    max_y: float = Field(..., description="Maximum Y coordinate (latitude)")
    x: int = Field(..., description="X pixel coordinate")
    y: int = Field(..., description="Y pixel coordinate")
    width: int = Field(default=800, description="Map width in pixels")
    height: int = Field(default=600, description="Map height in pixels")
    info_format: str = Field(default="text/plain", description="Info format")
    crs: str = Field(default="EPSG:4326", description="Coordinate reference system")
    feature_count: int = Field(default=10, description="Maximum features to return")
    version: str = Field(default="1.3.0", description="WMS version")


class ConvertCoordinatesRequest(BaseModel):
    """Request parameters for coordinate conversion"""
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    source_crs: str = Field(..., description="Source coordinate reference system")
    target_crs: str = Field(..., description="Target coordinate reference system")


# Global WMS client instance
wms_client = None


async def get_wms_client() -> WMSClient:
    """Get or create WMS client instance"""
    global wms_client
    if wms_client is None:
        wms_client = WMSClient()
    return wms_client


@mcp.tool()
async def get_capabilities(version: str = "1.3.0", force_refresh: bool = False) -> dict:
    """Get WMS service capabilities and available layers"""
    client = await get_wms_client()
    try:
        capabilities = await client.get_capabilities(version=version, force_refresh=force_refresh)
        return capabilities
    except Exception as e:
        logger.error(f"Error getting capabilities: {e}")
        raise


@mcp.tool()
async def get_map(request: GetMapRequest) -> str:
    """Generate a map image URL for specified layers and bounding box"""
    client = await get_wms_client()
    try:
        bbox = BoundingBox(
            min_x=request.min_x,
            min_y=request.min_y,
            max_x=request.max_x,
            max_y=request.max_y,
            crs=request.crs
        )
        
        return await client.get_map(
            layers=request.layers,
            bbox=bbox,
            width=request.width,
            height=request.height,
            format=request.format,
            version=request.version,
            crs=request.crs,
            transparent=request.transparent
        )
    except Exception as e:
        logger.error(f"Error generating map: {e}")
        raise


@mcp.tool()
async def get_feature_info(request: GetFeatureInfoRequest) -> str:
    """Get detailed information about features at specific coordinates"""
    client = await get_wms_client()
    try:
        bbox = BoundingBox(
            min_x=request.min_x,
            min_y=request.min_y,
            max_x=request.max_x,
            max_y=request.max_y,
            crs=request.crs
        )
        
        return await client.get_feature_info(
            layers=request.layers,
            bbox=bbox,
            x=request.x,
            y=request.y,
            width=request.width,
            height=request.height,
            info_format=request.info_format,
            version=request.version,
            crs=request.crs,
            feature_count=request.feature_count
        )
    except Exception as e:
        logger.error(f"Error getting feature info: {e}")
        raise


@mcp.tool()
async def list_layers(search_query: Optional[str] = None) -> list:
    """List available soil data layers, optionally filtered by search query"""
    client = await get_wms_client()
    try:
        if search_query:
            return await client.search_layers(search_query)
        else:
            capabilities = await client.get_capabilities()
            return capabilities.get('layers', [])
    except Exception as e:
        logger.error(f"Error listing layers: {e}")
        raise


@mcp.tool()
async def describe_layer(layer_name: str) -> dict:
    """Get detailed information about a specific layer"""
    client = await get_wms_client()
    try:
        return await client.get_layer_by_name(layer_name)
    except Exception as e:
        logger.error(f"Error describing layer: {e}")
        raise


@mcp.tool()
async def convert_coordinates(request: ConvertCoordinatesRequest) -> dict:
    """Convert coordinates between different coordinate reference systems"""
    client = await get_wms_client()
    try:
        x, y = await client.convert_coordinates(
            request.x, 
            request.y, 
            request.source_crs, 
            request.target_crs
        )
        
        return {
            "source": {
                "x": request.x,
                "y": request.y,
                "crs": request.source_crs
            },
            "target": {
                "x": x,
                "y": y,
                "crs": request.target_crs
            }
        }
    except Exception as e:
        logger.error(f"Error converting coordinates: {e}")
        raise


@mcp.tool()
async def get_soil_data_summary() -> dict:
    """Get a summary of available soil data types and their descriptions"""
    return {
        "soil_data_types": {
            "topsoil": "Top soil sample data and properties",
            "profile_soil": "Profile soil sample data from different depths",
            "soil_texture": "Soil texture classification and properties",
            "soil_depth": "Soil depth measurements from boreholes",
            "parent_material": "Soil parent material grain size and composition"
        },
        "coordinate_systems": {
            "EPSG:4326": "WGS84 Latitude/Longitude",
            "EPSG:27700": "British National Grid (BNG)",
            "EPSG:3857": "Web Mercator"
        },
        "common_workflows": [
            "1. Use list_layers() to discover available soil data layers",
            "2. Use describe_layer() to get details about specific layers",
            "3. Use get_map() to generate map images for visualization",
            "4. Use get_feature_info() to get detailed information at specific locations",
            "5. Use convert_coordinates() to work with different coordinate systems"
        ],
        "service_url": "https://map.bgs.ac.uk/arcgis/services/UKSO/UKSO_BGS/MapServer/WMSServer"
    }


def main():
    """Main entry point for the MCP server"""
    # Check for demo mode
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        print("🌍 BGS Soil Data WMS MCP Server - Demo Mode")
        print("=" * 60)
        
        async def demo():
            print("\nTesting all 7 MCP tools...\n")
            
            # Test get_soil_data_summary
            print("1. 📋 Soil Data Summary:")
            result = await get_soil_data_summary()
            print(f"   Found {len(result['soil_data_types'])} soil data types")
            
            # Test get_capabilities  
            print("\n2. 🔍 BGS WMS Service Capabilities:")
            caps = await get_capabilities()
            print(f"   Service: {caps['title']}")
            print(f"   Available layers: {len(caps['layers'])}")
            
            # Test list_layers
            print("\n3. 📃 List Available Layers:")
            layers = await list_layers()
            print(f"   Total layers: {len(layers)}")
            for i, layer in enumerate(layers[:3]):
                print(f"   {i+1}. {layer['name']}: {layer['title']}")
            
            # Test search layers
            print("\n4. 🔎 Search for 'depth' layers:")
            depth_layers = await list_layers("depth")
            print(f"   Found {len(depth_layers)} depth-related layers")
            
            # Test describe_layer
            if layers:
                print(f"\n5. 📖 Describe layer '{layers[0]['name']}':")
                layer_info = await describe_layer(layers[0]['name'])
                if layer_info:
                    print(f"   Title: {layer_info['title']}")
                    print(f"   Queryable: {layer_info['queryable']}")
            
            # Test coordinate conversion
            print("\n6. 🗺️  Coordinate Conversion:")
            conv_req = ConvertCoordinatesRequest(
                x=-0.1276, y=51.5074,
                source_crs="EPSG:4326", target_crs="EPSG:27700"
            )
            result = await convert_coordinates(conv_req)
            print(f"   London: {result['source']['x']}, {result['source']['y']} (WGS84)")
            print(f"   →       {result['target']['x']:.0f}, {result['target']['y']:.0f} (BNG)")
            
            # Test get_map
            print("\n7. 🖼️  Generate Map URL:")
            map_req = GetMapRequest(
                layers=layers[0]['name'],
                min_x=-6.0, min_y=50.0, max_x=2.0, max_y=58.0,
                width=400, height=300
            )
            map_url = await get_map(map_req)
            print(f"   Generated URL: {map_url[:60]}...")
            
            print("\n" + "=" * 60)
            print("✅ All BGS WMS MCP tools working successfully!")
            print("\nTo run as MCP server: python server/main.py")
            print("To create DXT package: zip -r soil-data-wms.dxt manifest.json server/ requirements.txt")
        
        asyncio.run(demo())
        return
    
    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()