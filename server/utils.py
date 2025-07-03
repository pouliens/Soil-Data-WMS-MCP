"""WMS client utilities for BGS soil data service"""

import asyncio
import logging
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)


class BoundingBox:
    """Bounding box for WMS requests"""
    def __init__(self, min_x: float, min_y: float, max_x: float, max_y: float, crs: str = "EPSG:4326"):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
        self.crs = crs


class WMSClient:
    """Simple WMS client for BGS soil data service"""
    
    def __init__(self, base_url: str = "https://map.bgs.ac.uk/arcgis/services/UKSO/UKSO_BGS/MapServer/WMSServer"):
        self.base_url = base_url
        self._capabilities_cache = None
        self._cache_timestamp = None
        self._cache_duration = timedelta(hours=1)
        
    async def get_capabilities(self, version: str = "1.3.0", force_refresh: bool = False) -> dict:
        """Get WMS service capabilities"""
        if (not force_refresh and 
            self._capabilities_cache and 
            self._cache_timestamp and
            datetime.now() - self._cache_timestamp < self._cache_duration):
            return self._capabilities_cache
            
        params = {
            "service": "WMS",
            "request": "GetCapabilities",
            "version": version
        }
        
        url = f"{self.base_url}?{urllib.parse.urlencode(params)}"
        
        try:
            with urllib.request.urlopen(url) as response:
                content = response.read()
                
            capabilities = self._parse_capabilities(content, version)
            self._capabilities_cache = capabilities
            self._cache_timestamp = datetime.now()
            return capabilities
            
        except Exception as e:
            logger.error(f"Error getting capabilities: {e}")
            raise
        
    def _parse_capabilities(self, xml_content: bytes, version: str) -> dict:
        """Parse WMS capabilities XML"""
        try:
            root = ET.fromstring(xml_content)
            
            # Handle namespaces
            namespaces = {
                'wms': 'http://www.opengis.net/wms',
                'xlink': 'http://www.w3.org/1999/xlink'
            }
            
            # Service information
            service_elem = root.find('.//wms:Service', namespaces)
            title = "BGS Soil Data WMS"
            abstract = None
            
            if service_elem is not None:
                title_elem = service_elem.find('wms:Title', namespaces)
                if title_elem is not None:
                    title = title_elem.text
                    
                abstract_elem = service_elem.find('wms:Abstract', namespaces)
                if abstract_elem is not None:
                    abstract = abstract_elem.text
            
            # Supported formats
            formats = []
            format_elems = root.findall('.//wms:GetMap/wms:Format', namespaces)
            for fmt in format_elems:
                if fmt.text:
                    formats.append(fmt.text)
                    
            info_formats = []
            info_format_elems = root.findall('.//wms:GetFeatureInfo/wms:Format', namespaces)
            for fmt in info_format_elems:
                if fmt.text:
                    info_formats.append(fmt.text)
                    
            # Layers
            layers = []
            layer_elems = root.findall('.//wms:Layer', namespaces)
            for layer_elem in layer_elems:
                name_elem = layer_elem.find('wms:Name', namespaces)
                if name_elem is not None and name_elem.text:
                    layer = self._parse_layer(layer_elem, namespaces)
                    layers.append(layer)
                    
            return {
                "title": title,
                "abstract": abstract,
                "version": version,
                "layers": layers,
                "formats": formats,
                "info_formats": info_formats,
                "cached_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing capabilities: {e}")
            raise
        
    def _parse_layer(self, layer_elem, namespaces: Dict[str, str]) -> dict:
        """Parse a single layer from capabilities XML"""
        name_elem = layer_elem.find('wms:Name', namespaces)
        name = name_elem.text if name_elem is not None else ""
        
        title_elem = layer_elem.find('wms:Title', namespaces)
        title = title_elem.text if title_elem is not None else name
        
        abstract_elem = layer_elem.find('wms:Abstract', namespaces)
        abstract = abstract_elem.text if abstract_elem is not None else None
        
        # CRS support
        crs_list = []
        crs_elems = layer_elem.findall('wms:CRS', namespaces)
        for crs_elem in crs_elems:
            if crs_elem.text:
                crs_list.append(crs_elem.text)
                
        # Queryable attribute
        queryable = layer_elem.get('queryable', '0') == '1'
        
        return {
            "name": name,
            "title": title,
            "abstract": abstract,
            "crs_list": crs_list,
            "queryable": queryable
        }
        
    async def get_map(
        self,
        layers: Union[str, List[str]],
        bbox: BoundingBox,
        width: int = 800,
        height: int = 600,
        format: str = "image/png",
        version: str = "1.3.0",
        crs: Optional[str] = None,
        transparent: bool = True,
        bgcolor: str = "0xFFFFFF"
    ) -> str:
        """Generate a map image URL"""
        if isinstance(layers, list):
            layers = ",".join(layers)
            
        if crs is None:
            crs = bbox.crs
            
        params = {
            "service": "WMS",
            "request": "GetMap",
            "version": version,
            "layers": layers,
            "width": width,
            "height": height,
            "format": format,
            "transparent": str(transparent).lower(),
            "bgcolor": bgcolor
        }
        
        # Handle different parameter names for different versions
        if version == "1.3.0":
            params["crs"] = crs
            params["bbox"] = f"{bbox.min_x},{bbox.min_y},{bbox.max_x},{bbox.max_y}"
        else:
            params["srs"] = crs
            params["bbox"] = f"{bbox.min_x},{bbox.min_y},{bbox.max_x},{bbox.max_y}"
            
        return f"{self.base_url}?{urllib.parse.urlencode(params)}"
        
    async def get_feature_info(
        self,
        layers: Union[str, List[str]],
        bbox: BoundingBox,
        x: int,
        y: int,
        width: int = 800,
        height: int = 600,
        info_format: str = "text/plain",
        version: str = "1.3.0",
        crs: Optional[str] = None,
        feature_count: int = 10
    ) -> str:
        """Get feature information at specific coordinates"""
        if isinstance(layers, list):
            layers = ",".join(layers)
            
        if crs is None:
            crs = bbox.crs
            
        params = {
            "service": "WMS",
            "request": "GetFeatureInfo",
            "version": version,
            "layers": layers,
            "query_layers": layers,
            "width": width,
            "height": height,
            "info_format": info_format,
            "feature_count": feature_count,
            "x": x,
            "y": y
        }
        
        # Handle different parameter names for different versions
        if version == "1.3.0":
            params["crs"] = crs
            params["bbox"] = f"{bbox.min_x},{bbox.min_y},{bbox.max_x},{bbox.max_y}"
        else:
            params["srs"] = crs
            params["bbox"] = f"{bbox.min_x},{bbox.min_y},{bbox.max_x},{bbox.max_y}"
            
        url = f"{self.base_url}?{urllib.parse.urlencode(params)}"
        
        try:
            with urllib.request.urlopen(url) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            logger.error(f"Error getting feature info: {e}")
            raise
        
    async def convert_coordinates(
        self, 
        x: float, 
        y: float, 
        source_crs: str, 
        target_crs: str
    ) -> Tuple[float, float]:
        """Simple coordinate conversion (basic implementation)"""
        # This is a simplified implementation
        # For production use, consider using pyproj or similar library
        if source_crs == target_crs:
            return x, y
            
        # Basic conversion between common CRS
        if source_crs == "EPSG:4326" and target_crs == "EPSG:27700":
            # Very rough WGS84 to BNG conversion (for demo purposes only)
            # In production, use proper transformation libraries
            return x * 111319.9, y * 111319.9
        elif source_crs == "EPSG:27700" and target_crs == "EPSG:4326":
            # Very rough BNG to WGS84 conversion (for demo purposes only)
            return x / 111319.9, y / 111319.9
        else:
            # Return as-is for other CRS combinations
            logger.warning(f"No conversion available from {source_crs} to {target_crs}")
            return x, y
        
    async def get_layer_by_name(self, name: str) -> Optional[dict]:
        """Get layer information by name"""
        capabilities = await self.get_capabilities()
        for layer in capabilities.get('layers', []):
            if layer.get('name') == name:
                return layer
        return None
        
    async def search_layers(self, query: str) -> List[dict]:
        """Search for layers by name or title"""
        capabilities = await self.get_capabilities()
        query_lower = query.lower()
        
        matching_layers = []
        for layer in capabilities.get('layers', []):
            name = layer.get('name', '').lower()
            title = layer.get('title', '').lower()
            abstract = layer.get('abstract', '').lower() if layer.get('abstract') else ''
            
            if (query_lower in name or 
                query_lower in title or
                query_lower in abstract):
                matching_layers.append(layer)
                
        return matching_layers