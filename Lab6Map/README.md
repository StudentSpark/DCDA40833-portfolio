# Interactive Folium Map with Mapbox

This Python script creates an interactive map using Folium with Mapbox styling and geocoding.

## Features

- 🗺️ **Custom Mapbox Styles**: Use any Mapbox style including custom styles
- 📍 **Automatic Geocoding**: Converts addresses to coordinates using Mapbox Geocoding API
- 🎨 **Type-based Styling**: Different colors and icons for different location types
- 🖼️ **Rich Popups**: Click markers to see name, description, and embedded images
- 💾 **HTML Export**: Save map as a standalone HTML file

## Setup

### 1. Install Required Packages

```bash
pip install -r requirements.txt
```

### 2. Get Mapbox API Token

1. Go to [Mapbox Account](https://account.mapbox.com/access-tokens/)
2. Sign up or log in
3. Create a new public token or use your default public token
4. Copy the token (starts with `pk.`)

### 3. Configure API Key

Create a `.env` file in this directory and add your token:

```
MAPBOX_PUBLIC_TOKEN=pk.your_actual_token_here
```

You can copy from `.env.example`.

## Usage

### Basic Usage

Simply run the script:

```bash
python lab06.py
```

This will:
1. Read locations from `datasource/hometown_locations.csv - Sheet1.csv`
2. Geocode all addresses using Mapbox API
3. Create an interactive map
4. Save it as `fort_worth_map.html`

### Customization

Edit the `main()` function in `lab06.py` to customize:

```python
# Change the output file name
OUTPUT_FILE = 'my_map.html'

# Use a different Mapbox style
MAPBOX_STYLE = 'mapbox/satellite-streets-v12'

# Adjust zoom level
map_obj = mapper.create_map(csv_file=CSV_FILE, zoom_start=12)
```

### Available Mapbox Styles

- `mapbox/streets-v12` - Default streets (recommended)
- `mapbox/outdoors-v12` - Outdoor/terrain view
- `mapbox/light-v11` - Light theme
- `mapbox/dark-v11` - Dark theme
- `mapbox/satellite-v9` - Satellite imagery
- `mapbox/satellite-streets-v12` - Satellite with street labels
- `your-username/your-style-id` - Custom Mapbox Studio styles

## CSV Format

Your CSV file should have these columns:

| Column | Description | Example |
|--------|-------------|---------|
| name | Location name | "Texas Christian University" |
| address | Full address | "2800 S University Dr, Fort Worth, TX 76129" |
| type | Location type | School, Museum, Restaurant, etc. |
| description | Text description | "A private research university..." |
| image URL | URL to image | https://example.com/image.jpg |

## Supported Location Types

The script automatically assigns colors and icons based on type:

| Type | Color | Icon |
|------|-------|------|
| School | Blue | 🎓 Graduation cap |
| Museum | Purple | 🏛️ University building |
| Restaurant | Red | 🍴 Cutlery |
| Park | Green | 🌲 Tree |
| Industry | Gray | 🏭 Factory |
| Airport | Light Blue | ✈️ Plane |
| Residential | Orange | 🏠 Home |
| Commercial | Beige | 🛒 Shopping cart |
| Recreation | Pink | 🎮 Gamepad |

To add more types, edit the `type_styles` dictionary in the `__init__` method.

## Programmatic Usage

You can also use the script as a module:

```python
from lab06 import MapboxFoliumMap

# Create mapper instance
mapper = MapboxFoliumMap(
    api_key='pk.your_actual_token_here',
    mapbox_style='mapbox/dark-v11'
)

# Create map
map_obj = mapper.create_map(
    csv_file='path/to/your/data.csv',
    center=(32.7555, -97.3308),  # Optional: Fort Worth coordinates
    zoom_start=12
)

# Save to HTML
mapper.save_map(map_obj, 'output.html')
```

## Troubleshooting

### "MAPBOX_PUBLIC_TOKEN not found"
- Make sure `.env` exists in the same directory as `lab06.py`
- Verify it contains `MAPBOX_PUBLIC_TOKEN=pk...`

### "No locations were successfully geocoded"
- Check your internet connection
- Verify your Mapbox token is valid and has geocoding permissions
- Check that addresses in your CSV are properly formatted

### Images not showing in popups
- Verify image URLs are accessible and publicly available
- Check browser console for CORS or loading errors
- Image URLs should start with `http://` or `https://`

### Rate limiting
- The script includes a 0.2-second delay between geocoding requests
- For large datasets, consider geocoding in batches or caching results

## Notes

- Geocoding results are cached during script execution to avoid redundant API calls
- The script handles common typos in location types (e.g., "Musuem" vs "Museum")
- Popups have a maximum width of 320px for better mobile display
- The map uses tooltips (hover) to show location names quickly

## License

MIT License - feel free to modify and use as needed!
