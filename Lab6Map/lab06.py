"""
Interactive Folium Map with Mapbox Integration
Reads locations from CSV, geocodes them using Mapbox API, and displays on an interactive map
"""

import folium
import pandas as pd
import requests
import time
import argparse
import os
from pathlib import Path
from dotenv import load_dotenv


class MapboxFoliumMap:
    """Class to create interactive maps with Mapbox styling and geocoding"""
    
    """Initializes the map defines the rules. Stores the API key and defines a style dictionary. """
    def __init__(self, api_key, mapbox_style='mapbox/streets-v12'):
        """
        Initialize the map creator
        
        Parameters:
        -----------
        api_key : str
            Mapbox public API key
        mapbox_style : str
            Mapbox style identifier (e.g., 'mapbox/streets-v12', 'mapbox/satellite-streets-v12')
        """
        if not api_key:
            raise ValueError("Mapbox API key is missing")
        self.api_key = api_key
        self.mapbox_style = mapbox_style
        self.geocode_cache = {}  # Cache to avoid redundant API calls
        
        # Define color and icon scheme for different types
        self.type_styles = {
            'School': {'color': 'blue', 'icon': 'graduation-cap', 'prefix': 'fa'},
            'Museum': {'color': 'purple', 'icon': 'university', 'prefix': 'fa'},
            'Musuem': {'color': 'purple', 'icon': 'university', 'prefix': 'fa'},  # Handle typo
            'Musueum': {'color': 'purple', 'icon': 'university', 'prefix': 'fa'},  # Handle typo
            'Restaurant': {'color': 'red', 'icon': 'cutlery', 'prefix': 'fa'},
            'Park': {'color': 'green', 'icon': 'tree', 'prefix': 'fa'},
            'Industry': {'color': 'gray', 'icon': 'industry', 'prefix': 'fa'},
            'Airport': {'color': 'lightblue', 'icon': 'plane', 'prefix': 'fa'},
            'Residential': {'color': 'orange', 'icon': 'home', 'prefix': 'fa'},
            'Commercial': {'color': 'beige', 'icon': 'shopping-cart', 'prefix': 'fa'},
            'Recreation': {'color': 'pink', 'icon': 'gamepad', 'prefix': 'fa'},
        }

    def _get_style_path(self):
        """Normalize a Mapbox style into the path expected by the styles API."""
        if self.mapbox_style.startswith('mapbox://styles/'):
            return self.mapbox_style.replace('mapbox://styles/', '')
        return self.mapbox_style

    def _get_tile_url(self, tile_url_template=None):
        """Return either a direct Mapbox tile URL or a proxy tile URL template."""
        if tile_url_template:
            return tile_url_template

        style_path = self._get_style_path()
        return (
            f"https://api.mapbox.com/styles/v1/{style_path}/tiles/512/"
            "{z}/{x}/{y}@2x?access_token=" + self.api_key
        )
    
    """ Uses Mapbox's Geocoding API to convert addresses to latitude and longitude coordinates. Caches results to reduce API calls."""
    def geocode_address(self, address):
        """
        Geocode an address using Mapbox Geocoding API
        
        Parameters:
        -----------
        address : str
            Address to geocode
            
        Returns:
        --------
        tuple : (latitude, longitude) or None if geocoding fails
        """
        # Check cache first
        if address in self.geocode_cache:
            return self.geocode_cache[address]
        
        # Mapbox Geocoding API endpoint
        base_url = "https://api.mapbox.com/geocoding/v5/mapbox.places"
        url = f"{base_url}/{requests.utils.quote(address)}.json"
        
        params = {
            'access_token': self.api_key,
            'limit': 1
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['features']:
                coordinates = data['features'][0]['geometry']['coordinates']
                # Mapbox returns [longitude, latitude], we need [latitude, longitude]
                lat_lon = (coordinates[1], coordinates[0])
                self.geocode_cache[address] = lat_lon
                
                # Be respectful of API rate limits
                time.sleep(0.2)
                
                return lat_lon
            else:
                print(f"Warning: No geocoding result for '{address}'")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error geocoding '{address}': {e}")
            return None
    
    """ Creates HTML content for marker popups. Sets color and symbol based on the location type, and pops up a box with further information."""
    def create_popup_html(self, name, description, image_url):
        """
        Create HTML content for marker popup
        
        Parameters:
        -----------
        name : str
            Location name
        description : str
            Location description
        image_url : str
            URL to image
            
        Returns:
        --------
        str : HTML content for popup
        """
        html = f"""
        <div style="width: 300px; font-family: Arial, sans-serif;">
            <h4 style="margin: 0 0 10px 0; color: #333;">{name}</h4>
            <img src="{image_url}" 
                 style="width: 100%; height: auto; margin-bottom: 10px; border-radius: 5px;"
                 onerror="this.style.display='none'">
            <p style="margin: 0; font-size: 12px; color: #666; line-height: 1.4;">
                {description}
            </p>
        </div>
        """
        return html
    
    def get_marker_style(self, location_type):
        """
        Get marker style (color and icon) for a given location type
        
        Parameters:
        -----------
        location_type : str
            Type of location
            
        Returns:
        --------
        dict : Style parameters for marker
        """
        # Default style if type not found
        default_style = {'color': 'darkblue', 'icon': 'info-sign', 'prefix': 'glyphicon'}
        return self.type_styles.get(location_type, default_style)
    
""" Reads the CSV file, geocodes the address, averages the point locations ot make a center point to base the camera on, and then builds the folium map."""

def create_map(self, csv_file, center=None, zoom_start=11, tile_url_template=None):
        """
        Create the interactive map from CSV data
        
        Parameters:
        -----------
        csv_file : str
            Path to CSV file with columns: name, address, type, description, image URL
        center : tuple
            (latitude, longitude) for map center. If None, will calculate from data
        zoom_start : int
            Initial zoom level
        tile_url_template : str | None
            Optional tile URL template. Use this to generate publish-safe HTML
            that points at a local tile proxy instead of embedding the token.
            
        Returns:
        --------
        folium.Map : The created map object
        """
        expected_columns = ['name', 'address', 'type', 'description', 'image URL']

        # Read CSV file. If it has no header row, reload it with the expected columns
        df = pd.read_csv(csv_file)
        df.columns = df.columns.str.strip().str.strip('"')
        if not {'name', 'address', 'type', 'description'}.issubset(set(df.columns)):
            df = pd.read_csv(csv_file, header=None, names=expected_columns)
            df.columns = expected_columns
        
        # Clean data (remove quotes from string values)
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].str.strip().str.strip('"')
        
        print(f"Loaded {len(df)} locations from {csv_file}")
        print(f"Columns: {list(df.columns)}")
        
        # Geocode all addresses
        print("\nGeocoding addresses...")
        coordinates = []
        for idx, row in df.iterrows():
            address = row['address']
            print(f"  {idx+1}/{len(df)}: {address[:50]}...")
            coords = self.geocode_address(address)
            coordinates.append(coords)
        
        df['coordinates'] = coordinates
        
        # Remove rows where geocoding failed
        df_valid = df[df['coordinates'].notna()].copy()
        print(f"\nSuccessfully geocoded {len(df_valid)}/{len(df)} locations")
        
        if len(df_valid) == 0:
            raise ValueError("No locations were successfully geocoded")
        
        # Calculate center if not provided
        if center is None:
            lats = [coord[0] for coord in df_valid['coordinates']]
            lons = [coord[1] for coord in df_valid['coordinates']]
            center = (sum(lats) / len(lats), sum(lons) / len(lons))
        
        print(f"\nMap center: {center}")
        
        mapbox_url = self._get_tile_url(tile_url_template)
        
        # Create the map with Mapbox tiles
        m = folium.Map(
            location=center,
            zoom_start=zoom_start,
            tiles=mapbox_url,
            attr='© <a href="https://www.mapbox.com/about/maps/">Mapbox</a> © <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        )
        
        # Add markers for each location
        print("\nAdding markers to map...")
        for idx, row in df_valid.iterrows():
            name = row['name']
            location_type = row['type']
            description = row['description']
            image_url = row['image URL']
            coords = row['coordinates']
            
            # Get style for this location type
            style = self.get_marker_style(location_type)
            
            # Create popup HTML
            popup_html = self.create_popup_html(name, description, image_url)
            popup = folium.Popup(popup_html, max_width=320)
            
            # Create marker
            folium.Marker(
                location=coords,
                popup=popup,
                tooltip=name,
                icon=folium.Icon(
                    color=style['color'],
                    icon=style['icon'],
                    prefix=style['prefix']
                )
            ).add_to(m)
            
            print(f"  Added: {name} ({location_type})")
        
        print("\nMap created successfully!")
        return m
    
def save_map(self, map_obj, output_file='map.html'):
        """
        Save the map to an HTML file
        
        Parameters:
        -----------
        map_obj : folium.Map
            Map object to save
        output_file : str
            Output file path
        """
        map_obj.save(output_file)
        print(f"\nMap saved to: {output_file}")
        return output_file


def load_mapbox_api_key(env_file='.env'):
    """Load Mapbox API key from .env file via MAPBOX_PUBLIC_TOKEN."""
    load_dotenv(dotenv_path=env_file)
    api_key = os.getenv('MAPBOX_PUBLIC_TOKEN', '').strip()
    if not api_key:
        raise ValueError(
            f"MAPBOX_PUBLIC_TOKEN not found in {env_file}. "
            "Add your public token to the .env file."
        )
    return api_key

"""Create a small Flask app that serves the HTML and proxies Mapbox tiles. This allows you to share the map without exposing your API key in the HTML. AI designed this one based on my request to hide the API key. Did not end up using this, instead made a restricted public key on Mapbox thats is read only."""
def create_publish_app(html_file, api_key, mapbox_style='mapbox/streets-v12'):
    """Create a small Flask app that serves the HTML and proxies Mapbox tiles."""
    from flask import Flask, Response, abort, send_from_directory

    mapper = MapboxFoliumMap(api_key=api_key, mapbox_style=mapbox_style)
    style_path = mapper._get_style_path()
    app = Flask(__name__, static_folder='.')
    html_path = Path(html_file).resolve()

    @app.route('/')
    def index():
        return send_from_directory(html_path.parent, html_path.name)

    @app.route('/<path:filename>')
    def static_files(filename):
        target = html_path.parent / filename
        if target.exists() and target.is_file():
            return send_from_directory(html_path.parent, filename)
        abort(404)

    @app.route('/tiles/<int:z>/<int:x>/<int:y>')
    def tile_proxy(z, x, y):
        tile_url = (
            f"https://api.mapbox.com/styles/v1/{style_path}/tiles/512/"
            f"{z}/{x}/{y}@2x"
        )
        response = requests.get(
            tile_url,
            params={'access_token': mapper.api_key},
            timeout=30
        )
        response.raise_for_status()
        return Response(
            response.content,
            status=response.status_code,
            content_type=response.headers.get('Content-Type', 'image/png')
        )

    return app


def main():
    """Main function to demonstrate usage"""
    parser = argparse.ArgumentParser(description='Create a Folium map with Mapbox tiles.')
    parser.add_argument('--serve', action='store_true', help='Serve the map through a local tile proxy.')
    parser.add_argument('--host', default='127.0.0.1', help='Host for --serve mode.')
    parser.add_argument('--port', type=int, default=8000, help='Port for --serve mode.')
    parser.add_argument('--env-file', default='.env', help='Path to .env file containing MAPBOX_PUBLIC_TOKEN.')
    parser.add_argument(
        '--proxy-tiles',
        action='store_true',
        help='Use a local tile proxy instead of embedding the Mapbox token in the HTML.'
    )
    args = parser.parse_args()
    
    # Configuration
    CSV_FILE = 'datasource/hometown_locations.csv - Sheet1.csv'
    OUTPUT_FILE = 'fort_worth_map.html'
    
    # You can use different Mapbox styles:
    # Built-in Mapbox styles (use as-is):
    # 'mapbox/streets-v12' - default streets
    # 'mapbox/outdoors-v12' - outdoor/terrain
    # 'mapbox/light-v11' - light theme
    # 'mapbox/dark-v11' - dark theme
    # 'mapbox/satellite-v9' - satellite imagery
    # 'mapbox/satellite-streets-v12' - satellite with streets
    # 
    # Custom Mapbox Studio styles (full URL):
    # 'mapbox://styles/your-username/your-style-id'
    # Example: 'mapbox://styles/thegreatscienceman42/cmmidngy8000m01qp5nlghh7r'
    
    MAPBOX_STYLE = 'mapbox://styles/thegreatscienceman42/cmmidngy8000m01qp5nlghh7r'
    PROXY_TILE_TEMPLATE = '/tiles/{z}/{x}/{y}'
    
    try:
        api_key = load_mapbox_api_key(args.env_file)

        # Create map instance
        mapper = MapboxFoliumMap(
            api_key=api_key,
            mapbox_style=MAPBOX_STYLE
        )
        
        # Create the map
        map_obj = mapper.create_map(
            csv_file=CSV_FILE,
            zoom_start=11,
            tile_url_template=PROXY_TILE_TEMPLATE if args.proxy_tiles else None
        )
        
        # Save to HTML
        mapper.save_map(map_obj, OUTPUT_FILE)

        if args.proxy_tiles:
            print('\nPublish-safe mode enabled: the HTML does not contain your Mapbox token.')
            print('Serve it through the built-in proxy so tiles can load securely.')
        
        print("\n" + "="*60)
        print("SUCCESS! Open the HTML file in your browser to view the map.")
        print("="*60)

        if args.serve:
            app = create_publish_app(
                html_file=OUTPUT_FILE,
                api_key=api_key,
                mapbox_style=MAPBOX_STYLE
            )
            print(f"\nServing map at http://{args.host}:{args.port}")
            app.run(host=args.host, port=args.port, debug=False)
        
    except ValueError as e:
        print(f"\nError: {e}")
        print("\nTo fix this issue:")
        print(f"1. Create a file named '{args.env_file}' in this directory")
        print("2. Add MAPBOX_PUBLIC_TOKEN=your_mapbox_public_token")
        print("3. Get a token at: https://account.mapbox.com/access-tokens/")
        
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
