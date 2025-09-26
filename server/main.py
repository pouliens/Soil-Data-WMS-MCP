"""BGS Soil Data WMS MCP Server"""

import logging
import os
import sys
from typing import List, Optional, Union

from fastmcp import FastMCP

# Add lib directory to path for bundled dependencies
lib_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lib')
if os.path.exists(lib_dir):
    sys.path.insert(0, lib_dir)

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

try:
    from .utils import WMSClient, BoundingBox
except ImportError:
    from utils import WMSClient, BoundingBox

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("BGS Soil Data WMS")


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
async def get_soil_map_url(request: GetMapRequest) -> str:
    """Generate a WMS GetMap URL for soil data visualization"""
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
async def get_soil_data_at_location(request: GetFeatureInfoRequest) -> str:
    """Get detailed soil information at specific geographic coordinates"""
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
async def get_available_soil_layers(search_query: Optional[str] = None) -> list:
    """Get available soil data layers from BGS WMS service"""
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
async def get_soil_layer_info(layer_name: str) -> dict:
    """Get detailed information about a specific soil data layer"""
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
    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()