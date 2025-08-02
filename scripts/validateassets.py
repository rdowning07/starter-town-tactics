
import os
import yaml
try:
    from PIL import Image
except ImportError:
    print("⚠️  PIL/Pillow not installed. Install with: pip install Pillow")
    Image = None

def validate_tilesets(yaml_file):
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    print("🧪 Validating tilesets...")
    for tileset in data['tilesets']:
        path = tileset['file']
        if not os.path.exists(path):
            print(f"❌ Missing file: {path}")
            continue

        if Image is None:
            print(f"⚠️  Skipping image validation for {path} (PIL not available)")
            continue

        try:
            with Image.open(path) as img:
                width, height = img.size
                tile_w, tile_h = tileset['tile_size']

                # Calculate how many complete tiles can fit
                tiles_x = width // tile_w
                tiles_y = height // tile_h

                if width % tile_w == 0 and height % tile_h == 0:
                    print(f"✅ {tileset['name']} ({path}) is perfect: {width}x{height} = {tiles_x}x{tiles_y} tiles")
                else:
                    print(f"⚠️  {tileset['name']} ({path}): {width}x{height} = {tiles_x}x{tiles_y} tiles (with {width % tile_w}x{height % tile_h} padding)")

        except (OSError, ValueError) as e:
            print(f"❌ Failed to open image {path}: {e}")

if __name__ == '__main__':
    validate_tilesets('data/tileset_mapping.yaml')
