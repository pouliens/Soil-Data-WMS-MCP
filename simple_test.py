"""Simple test without external dependencies"""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET


def test_bgs_wms():
    """Test BGS WMS service directly"""
    print("Testing BGS WMS service...")
    
    # Test GetCapabilities
    base_url = "https://map.bgs.ac.uk/arcgis/services/UKSO/UKSO_BGS/MapServer/WMSServer"
    params = {
        "service": "WMS",
        "request": "GetCapabilities",
        "version": "1.3.0"
    }
    
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    print(f"URL: {url}")
    
    try:
        with urllib.request.urlopen(url) as response:
            content = response.read()
            print(f"✓ Response received: {len(content)} bytes")
            
            # Parse XML
            root = ET.fromstring(content)
            print(f"✓ XML parsed successfully")
            
            # Find layers
            layers = root.findall('.//{http://www.opengis.net/wms}Layer')
            print(f"✓ Found {len(layers)} layers")
            
            # Show first few layers
            for i, layer in enumerate(layers[:5]):
                name_elem = layer.find('{http://www.opengis.net/wms}Name')
                title_elem = layer.find('{http://www.opengis.net/wms}Title')
                if name_elem is not None and title_elem is not None:
                    print(f"  {i+1}. {name_elem.text}: {title_elem.text}")
                    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
        
    print("\n✓ BGS WMS service is accessible!")
    return True


if __name__ == "__main__":
    test_bgs_wms()