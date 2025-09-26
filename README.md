# BGS Soil Data WMS MCP Server

A FastMCP 2.0 server providing access to British Geological Survey soil property data via WMS.

## Overview

This MCP server enables AI assistants to query comprehensive UK soil data including topsoil properties, profile soil data, soil texture, soil depth, and parent material characteristics. Data is sourced from the BGS under the Open Government Licence.

## One-Click Installer for VS Code

1. Click to Install to VS Code

[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_BGS_Soil_Data_WMS_--_MCP_Server-0098FF?style=flat-square&logo=visualstudiocode&logoColor=ffffff)](vscode:mcp/install?%7B%22name%22%3A%22BGS%20Soil%20Data%20WMS%22%2C%22type%22%3A%22http%22%2C%22url%22%3A%22https%3A%2F%2Fbgs-soil-data-wms.fastmcp.app%2Fmcp%22%7D)

2. Open VS Code and toggle Co-Pilot on
3. Switch to Agent Mode
4. (optional) Check if you're connected to the MCP
5. Start asking questions about UK soil data! If you want the data to be visualised or captured somewhere ask AI to create an HTML file, jupyter notebook, or store the data in CSV file.

## Features

- **Point-specific soil data queries** at any UK coordinate
- **Multiple soil data types**: topsoil, profile soil, soil texture, soil depth, parent material
- **High-resolution data**: Detailed soil property measurements from BGS surveys
- **Multiple coordinate systems**: WGS84 (CRS:84) and British National Grid
- **3 output formats**: HTML, XML, and plain text
- **Map visualization**: Generate WMS GetMap URLs for GIS applications

## Available Soil Data Types

| Data Type | Description |
|-----------|-------------|
| `topsoil` | Top soil sample data and properties |
| `profile_soil` | Profile soil sample data from different depths |
| `soil_texture` | Soil texture classification and properties |
| `soil_depth` | Soil depth measurements from boreholes |
| `parent_material` | Soil parent material grain size and composition |

## Installation

```bash
# Install dependencies
pip install fastmcp pydantic
# or using uv:
uv sync

# Run the server
python server/main.py
```

## Example Queries

### 🗺️ **Soil Data Visualization**

**London area soil data:**
```python
get_soil_map_url("topsoil_layer", 51.45, -0.15, 51.55, -0.05, 450, 450, "image/png")
```

**Midlands agricultural area:**
```python
get_soil_map_url("soil_texture", 52.4, -1.9, 52.5, -1.8)
```

**Scottish highlands soil depth:**
```python
get_soil_map_url("soil_depth", 57.0, -4.5, 57.1, -4.4)
```

### 🔍 **Point-Specific Soil Data Queries**

**London soil analysis:**
```python
get_soil_data_at_location(51.5074, -0.1278, "topsoil", "text/html")
get_soil_data_at_location(51.5074, -0.1278, "soil_texture", "text/xml")
get_soil_data_at_location(51.5074, -0.1278, "soil_depth", "text/plain")
```

**Agricultural planning - East Anglia:**
```python
get_soil_data_at_location(52.2, 0.1, "topsoil", "text/html")
get_soil_data_at_location(52.2, 0.1, "soil_texture", "text/plain")
get_soil_data_at_location(52.2, 0.1, "parent_material", "text/html")
```

**Welsh valleys soil analysis:**
```python
get_soil_data_at_location(51.75, -3.25, "profile_soil")
get_soil_data_at_location(51.75, -3.25, "soil_depth")
```

### 🏗️ **Construction & Engineering Queries**

**Foundation analysis:**
```python
get_soil_data_at_location(53.4808, -2.2426, "soil_depth", "text/plain")    # Manchester
get_soil_data_at_location(52.4862, -1.8904, "parent_material", "text/plain") # Birmingham
get_soil_data_at_location(51.4816, -3.1791, "soil_texture", "text/plain")   # Cardiff
```

**Infrastructure planning:**
```python
get_soil_data_at_location(54.9783, -1.6178, "topsoil", "text/html")     # Newcastle
get_soil_data_at_location(55.8642, -4.2518, "soil_depth", "text/html")  # Glasgow
get_soil_data_at_location(53.7967, -1.5492, "profile_soil", "text/html") # Leeds
```

### 🌱 **Agricultural & Environmental Queries**

**Crop suitability analysis:**
```python
get_soil_data_at_location(52.5, -0.5, "topsoil")          # Cambridgeshire
get_soil_data_at_location(52.8, -1.0, "soil_texture")     # Nottinghamshire
get_soil_data_at_location(53.2, -0.5, "parent_material")  # Lincolnshire
```

**Environmental monitoring:**
```python
get_soil_data_at_location(50.8, -4.1, "topsoil")       # Devon coast
get_soil_data_at_location(54.4, -3.2, "soil_depth")    # Lake District
get_soil_data_at_location(53.3, -1.8, "profile_soil")  # Peak District
```

### 📊 **Multi-layer Soil Profiling**

**Complete soil profile at one location:**
```python
# Complete soil analysis at specific coordinates
lat, lon = 53.2058, -0.5417  # Lincoln area
get_soil_data_at_location(lat, lon, "topsoil")
get_soil_data_at_location(lat, lon, "profile_soil") 
get_soil_data_at_location(lat, lon, "soil_texture")
get_soil_data_at_location(lat, lon, "soil_depth")
get_soil_data_at_location(lat, lon, "parent_material")
```

### 🎯 **Regional Soil Mapping**

**Southern England chalk soils:**
```python
get_soil_map_url("topsoil", 50.8, -0.3, 50.9, -0.2)      # South Downs
get_soil_map_url("soil_texture", 51.2, -1.8, 51.3, -1.7) # North Wessex Downs
```

**Scottish soil mapping:**
```python
get_soil_map_url("parent_material", 56.8, -5.2, 56.9, -5.1)  # Isle of Skye
get_soil_map_url("soil_depth", 57.6, -4.0, 57.7, -3.9)       # Moray Firth
```

**Welsh valley soils:**
```python
get_soil_map_url("topsoil", 53.1, -4.1, 53.2, -4.0)     # Snowdonia
get_soil_map_url("profile_soil", 51.6, -3.4, 51.7, -3.3) # Rhondda Valley
```

### 📊 **Service Discovery**

**Discover soil data layers:**
```python
get_available_soil_layers()
```

**Search for specific soil types:**
```python
get_available_soil_layers("texture")
get_available_soil_layers("depth")
```

**Get service capabilities:**
```python
get_capabilities()
```

**Service information:**
```python
get_soil_data_summary()
```

### 💡 **Data Usage Tips**

1. **Use specific coordinates** for point data queries (latitude/longitude in decimal degrees)
2. **Small areas work best** for map visualization (0.05-0.15° boxes)
3. **HTML format** provides richest information display
4. **XML format** good for structured data processing
5. **Plain text format** for simple information extraction
6. **Try different soil data types** - coverage varies by location

## API Reference

### Tools

#### `get_soil_data_at_location(latitude, longitude, data_type, format_type)`
Get soil information at a specific geographic location.

**Parameters:**
- `latitude` (float): Latitude in decimal degrees (WGS84)
- `longitude` (float): Longitude in decimal degrees (WGS84)
- `data_type` (str): Soil data type - topsoil, profile_soil, soil_texture, soil_depth, parent_material
- `format_type` (str): Response format - text/html, text/xml, or text/plain

#### `get_available_soil_layers(search_query)`
Get available soil data layers from the BGS WMS service.

**Parameters:**
- `search_query` (str, optional): Filter layers by search term

#### `get_capabilities()`
Get WMS capabilities document showing all available soil layers and metadata.

#### `get_soil_map_url(layer, min_lat, min_lon, max_lat, max_lon, width, height, format_type)`
Generate WMS GetMap URL for soil data visualization.

**Parameters:**
- `layer` (str): Layer name (use get_available_soil_layers() to see options)
- `min_lat` (float): Minimum latitude (south boundary)
- `min_lon` (float): Minimum longitude (west boundary)
- `max_lat` (float): Maximum latitude (north boundary)
- `max_lon` (float): Maximum longitude (east boundary)
- `width` (int): Image width in pixels
- `height` (int): Image height in pixels
- `format_type` (str): Image format (image/png, image/gif, image/jpeg)

#### `get_soil_layer_info(layer_name)`
Get detailed information about a specific soil data layer.

**Parameters:**
- `layer_name` (str): Name of the soil layer to describe

#### `convert_coordinates(x, y, source_crs, target_crs)`
Convert coordinates between different coordinate reference systems.

**Parameters:**
- `x` (float): X coordinate
- `y` (float): Y coordinate
- `source_crs` (str): Source coordinate reference system
- `target_crs` (str): Target coordinate reference system

#### `get_soil_data_summary()`
Get summary of available soil data types and their descriptions.

## Data Source

- **Provider**: British Geological Survey (BGS) / UK Research and Innovation (UKRI)
- **License**: Open Government Licence
- **Attribution**: "Contains British Geological Survey materials © UKRI [year]"
- **Service URL**: https://map.bgs.ac.uk/arcgis/services/UKSO/UKSO_BGS/MapServer/WMSServer

## Technical Details

- **WMS Version**: 1.3.0
- **Coordinate System**: WGS84 (CRS:84), British National Grid (EPSG:27700)
- **Coverage**: Great Britain (England, Wales, Scotland)
- **Data Types**: Topsoil, profile soil, texture, depth, parent material
- **Built with**: FastMCP 2.0, Pydantic

## Use Cases

- **Agricultural planning**: Understand soil properties for crop selection and farming practices
- **Construction projects**: Foundation analysis and site investigation
- **Environmental assessment**: Soil contamination and remediation planning
- **Education**: Explore UK soil diversity and characteristics
- **Research**: Soil science and environmental studies
- **GIS applications**: Generate soil maps for spatial analysis
- **Land use planning**: Inform development and conservation decisions