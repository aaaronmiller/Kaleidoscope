import argparse
import math
import os
import numpy as np
from PIL import Image, ImageDraw

def create_mask_image(size, draw_func, *args, **kwargs):
    """
    Creates a black and white mask image of a given size using a drawing function.
    The shape is white (255) and the background is black (0).
    """
    # Create a new black image (L mode for 8-bit pixels, black and white)
    img = Image.new('L', size, 0)
    draw = ImageDraw.Draw(img)
    draw_func(draw, size, *args, **kwargs)
    return img

def draw_hexagon(draw, size):
    """Draws a regular hexagon centered in the image."""
    w, h = size
    center = (w / 2, h / 2)
    # The radius of the bounding circle
    radius = min(w, h) / 2 * 0.95  # 95% of the max possible radius to leave a small margin
    
    points = []
    # Generate 6 points for the hexagon
    for i in range(6):
        # Start at 30 degrees (pi/6) so the flat sides are horizontal/vertical depending on orientation
        # Here we use flat-topped hexagons (0, 60, 120, 180, 240, 300 degrees)
        angle_deg = 60 * i
        angle_rad = math.radians(angle_deg)
        x = center[0] + radius * math.cos(angle_rad)
        y = center[1] + radius * math.sin(angle_rad)
        points.append((x, y))
        
    draw.polygon(points, fill=255)

def draw_rhombus(draw, size, angle_deg=60):
    """
    Draws a rhombus. 
    angle_deg is the acute angle of the rhombus.
    """
    w, h = size
    center = (w / 2, h / 2)
    
    # Let the longer diagonal be along the x-axis for simplicity (or y-axis)
    # The diagonals of a rhombus bisect each other at 90 degrees.
    # If the acute angle is theta, the diagonals d1 and d2 relate to the side length a:
    # d1 = 2 * a * sin(theta/2)
    # d2 = 2 * a * cos(theta/2)
    
    # Let's define the max diagonal to fit within the image
    max_diag = min(w, h) * 0.95
    
    # Calculate the half-diagonals based on the desired angle
    theta_rad = math.radians(angle_deg)
    
    # We'll set the primary (longer) diagonal to max_diag.
    # Which diagonal is longer depends on if theta < 90.
    # If theta < 90, cos(theta/2) > sin(theta/2), so d2 > d1.
    half_d_long = max_diag / 2
    
    # The ratio of the short diagonal to the long diagonal is tan(theta/2)
    half_d_short = half_d_long * math.tan(theta_rad / 2)
    
    # Define the 4 vertices
    # Top, Right, Bottom, Left
    points = [
        (center[0], center[1] - half_d_short), # Top
        (center[0] + half_d_long, center[1]),  # Right
        (center[0], center[1] + half_d_short), # Bottom
        (center[0] - half_d_long, center[1])   # Left
    ]
    
    draw.polygon(points, fill=255)

def draw_triangle(draw, size):
    """Draws an equilateral triangle."""
    w, h = size
    center = (w / 2, h / 2)
    radius = min(w, h) / 2 * 0.95
    
    points = []
    # 3 points, starting from top (-90 degrees)
    for i in range(3):
        angle_deg = -90 + 120 * i
        angle_rad = math.radians(angle_deg)
        x = center[0] + radius * math.cos(angle_rad)
        y = center[1] + radius * math.sin(angle_rad)
        points.append((x, y))
        
    draw.polygon(points, fill=255)


def generate_fractal_boundary(size, max_iter=100):
    """
    Generates a mask using a Julia set to create an interesting, complex 
    but still mathematical boundary. This is more of a texture/organic shape.
    """
    w, h = size
    # Create abstract organic shape
    # We'll use a specific Julia set parameter
    c = complex(-0.4, 0.6) 
    
    # Create coordinate grid
    y, x = np.ogrid[-1.5:1.5:h*1j, -1.5:1.5:w*1j]
    z = x + y*1j
    
    # Create output array initialized to 0
    img = np.zeros(z.shape, dtype=int)
    
    # Create a mask to track points that haven't escaped
    active = np.ones(z.shape, dtype=bool)
    
    for i in range(max_iter):
        # Only update active points
        z[active] = z[active]**2 + c
        
        # Check which points have escaped
        escaped = np.abs(z) > 2
        
        # Only process points that just escaped
        just_escaped = escaped & active
        
        # We don't need to record iteration count, just if it's in the set
        # img[just_escaped] = i
        
        # Update active mask
        active = active & ~just_escaped
    
    # Points that never escaped (active == True) are inside the set
    # Create a binary mask where inside is 255 and outside is 0
    binary_mask = np.zeros_like(img, dtype=np.uint8)
    binary_mask[active] = 255
    
    # The Julia set might be disconnected depending on C.
    # For a solid mask, we might just want to use the inner points.
    
    return Image.fromarray(binary_mask, mode='L')


def main():
    parser = argparse.ArgumentParser(description="Generate geometric math masks for Kaleidoscope")
    parser.add_argument("--shape", type=str, choices=["hexagon", "rhombus", "triangle", "fractal"], default="hexagon", help="Shape to generate")
    parser.add_argument("--size", type=int, default=1024, help="Size of the square image in pixels")
    parser.add_argument("--angle", type=float, default=60, help="Acute angle for rhombus (e.g., 36 or 72 for Penrose)")
    parser.add_argument("--outdir", type=str, default="data/masks", help="Output directory")
    
    args = parser.parse_args()
    
    os.makedirs(args.outdir, exist_ok=True)
    
    size = (args.size, args.size)
    
    print(f"Generating {args.shape} mask of size {args.size}x{args.size}...")
    
    if args.shape == "hexagon":
        img = create_mask_image(size, draw_hexagon)
        filename = f"hexagon_{args.size}.png"
    elif args.shape == "rhombus":
        img = create_mask_image(size, draw_rhombus, angle_deg=args.angle)
        filename = f"rhombus_{int(args.angle)}deg_{args.size}.png"
    elif args.shape == "triangle":
        img = create_mask_image(size, draw_triangle)
        filename = f"triangle_{args.size}.png"
    elif args.shape == "fractal":
        img = generate_fractal_boundary(size)
        filename = f"julia_fractal_{args.size}.png"
    
    outpath = os.path.join(args.outdir, filename)
    img.save(outpath)
    print(f"Saved mask to {outpath}")

if __name__ == "__main__":
    main()
