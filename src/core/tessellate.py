import math
import os
import argparse
from PIL import Image

def tile_hexagon(tile_img, out_w, out_h):
    """
    Tessellates a regular hexagon tile to fill an output image of size out_w x out_h.
    Uses a standard flat-topped hexagon grid layout.
    """
    tile_w, tile_h = tile_img.size
    
    # We generated the hexagon with a radius = min(w,h)/2 * 0.95
    # The true width of a flat-topped hex is 2*radius
    # The horizontal distance between adjacent centers is 1.5 * radius
    # The vertical distance is sqrt(3) * radius
    radius = (min(tile_w, tile_h) / 2) * 0.95
    
    horizontal_spacing = 1.5 * radius
    vertical_spacing = math.sqrt(3) * radius
    
    # Create a blank output image (transparent)
    output = Image.new('RGBA', (out_w, out_h), (0,0,0,0))
    
    # We want to place tiles such that they cover the output bounds
    # Find how many columns and rows we need
    cols = int((out_w / horizontal_spacing) + 2)
    rows = int((out_h / vertical_spacing) + 2)
    
    # Render loop
    for col in range(-1, cols):
        for row in range(-1, rows):
            # Calculate center position
            x = col * horizontal_spacing
            
            # Every other column is offset vertically by half the vertical spacing
            y_offset = (vertical_spacing / 2) * (col % 2)
            y = (row * vertical_spacing) + y_offset
            
            # The exact paste coordinates (top-left of the tile)
            paste_x = int(x - tile_w/2)
            paste_y = int(y - tile_h/2)
            
            # PIL paste with an alpha mask uses the third argument as the mask
            output.paste(tile_img, (paste_x, paste_y), tile_img)
            
    return output

def tile_triangle(tile_img, out_w, out_h):
    """
    Tessellates equilateral triangles to fill the output.
    This creates a hexagonal lattice out of 6 triangles meeting at a point.
    """
    tile_w, tile_h = tile_img.size
    radius = (min(tile_w, tile_h) / 2) * 0.95
    
    # Side length 'a' of equilateral triangle
    # Distance from center to vertex = a / sqrt(3) -> a = radius * sqrt(3)
    a = radius * math.sqrt(3)
    height = a * math.sqrt(3) / 2
    
    # Create the output
    output = Image.new('RGBA', (out_w, out_h), (0,0,0,0))
    
    # We need an "up" pointing triangle and a "down" pointing triangle.
    # We generated an "up" pointing triangle originally
    tile_up = tile_img
    tile_down = tile_img.rotate(180, expand=False)
    
    # Grid spacing
    cols = int((out_w / (a / 2)) + 2)
    rows = int((out_h / height) + 2)
    
    for row in range(-1, rows):
        for col in range(-1, cols):
            # Triangle grid logic
            # A row alternates up/down pointing triangles
            points_up = (col + row) % 2 == 0
            
            x = int((col * a / 2) - tile_w/2)
            y = int((row * height) - tile_h/2)
            
            # The centers of down-pointing triangles are slightly offset relative to their bounding box
            # If generated cleanly, simple rotation is fine
            if points_up:
                output.paste(tile_up, (x, y), tile_up)
            else:
                output.paste(tile_down, (x, y), tile_down)
                
    return output

def tile_p1_wallpaper(tile_img, out_w, out_h):
    """
    The simplest wallpaper group. Standard translation. p1.
    Just blindly stamps it in a grid without any interlocking logic.
    Provides a fallback/baseline for arbitrary non-locking shapes.
    """
    w, h = tile_img.size
    output = Image.new('RGBA', (out_w, out_h), (0,0,0,0))
    
    cols = (out_w // w) + 2
    rows = (out_h // h) + 2
    
    for c in range(cols):
        for r in range(rows):
            x = c * w
            y = r * h
            output.paste(tile_img, (x, y), tile_img)
            
    return output

def main():
    parser = argparse.ArgumentParser(description="Tessellate exactly-masked geometric tiles")
    parser.add_argument("--tile", type=str, required=True, help="Path to transparent styled tile")
    parser.add_argument("--pattern", type=str, default="hexagon", choices=["hexagon", "triangle", "p1"], help="Tessellation lattice logic")
    parser.add_argument("--width", type=int, default=4096, help="Output width in pixels")
    parser.add_argument("--height", type=int, default=4096, help="Output height in pixels")
    parser.add_argument("--out", type=str, default="output/final_pattern.png", help="Output path")
    
    args = parser.parse_args()
    
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    
    print(f"Loading styled tile: {args.tile}")
    tile = Image.open(args.tile).convert("RGBA")
    
    print(f"Tessellating using {args.pattern} lattice to {args.width}x{args.height}...")
    
    if args.pattern == "hexagon":
        output = tile_hexagon(tile, args.width, args.height)
    elif args.pattern == "triangle":
        output = tile_triangle(tile, args.width, args.height)
    elif args.pattern == "p1":
        output = tile_p1_wallpaper(tile, args.width, args.height)
        
    output.save(args.out, "PNG")
    print(f"Saved massive seamless pattern to {args.out}")

if __name__ == "__main__":
    main()
