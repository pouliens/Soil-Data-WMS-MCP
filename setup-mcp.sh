#!/bin/bash

# Setup BGS WMS MCP Server for Claude Code
export MCP_BGS_SOIL_WMS_COMMAND="python"
export MCP_BGS_SOIL_WMS_ARGS="server/main.py"
export MCP_BGS_SOIL_WMS_CWD="/data/data/com.termux/files/home/my-projects/soil-data-wms-mcp"

echo "BGS Soil WMS MCP server environment configured"
echo "Server location: $MCP_BGS_SOIL_WMS_CWD"
echo "Command: $MCP_BGS_SOIL_WMS_COMMAND $MCP_BGS_SOIL_WMS_ARGS"