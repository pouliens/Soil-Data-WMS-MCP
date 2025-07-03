# Soil Data WMS MCP Server

An MCP (Model Context Protocol) server for accessing BGS (British Geological Survey) soil property data through their WMS service.

## Features

- Access to BGS soil property data layers
- Support for WMS GetCapabilities, GetMap, and GetFeatureInfo operations
- Coordinate system conversion between BNG and WGS84
- Layer discovery and metadata retrieval
- Caching for improved performance

## Installation

```bash
pip install -e .
```

## Usage

Start the MCP server:

```bash
soil-wms-mcp
```

Or run in development mode with the MCP Inspector:

```bash
mcp dev soil_wms_mcp/server.py
```

## Available Tools

- `get_capabilities`: Get WMS service capabilities and available layers
- `get_map`: Generate map images for specific layers and bounds
- `get_feature_info`: Get detailed information about features at coordinates
- `list_layers`: List available soil data layers
- `describe_layer`: Get detailed information about a specific layer
- `convert_coordinates`: Convert between coordinate systems

## BGS WMS Service

This server connects to the BGS WMS service at:
`https://map.bgs.ac.uk/arcgis/services/UKSO/UKSO_BGS/MapServer/WMSServer`

Data includes:
- Top soil and profile soil sample data
- Soil texture
- Soil depth
- Soil parent material