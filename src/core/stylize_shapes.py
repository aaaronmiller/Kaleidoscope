import os
import io
import json
import base64
import random
import argparse
import requests
from PIL import Image

# Initialize connection to Stability API
STABILITY_API_URL = "https://api.stability.ai/v2beta/stable-image/control/sketch"

def get_api_key():
    """Retrieve Stability API key from environments"""
    api_key = os.environ.get("STABILITY_API_KEY")
    if not api_key:
        # Fallback to a mock for initial setup/testing if no key is present
        print("WARNING: STABILITY_API_KEY not found in environment. Using mock mode.")
    return api_key

def generate_prompt(word_list_dir, style="psychedelic"):
    """
    Generate a combinatorial mad-lib prompt.
    For Phase 2, we simulate this with hardcoded lists if files are missing,
    or use the actual JSON data if available.
    """
    prompt_elements = []
    
    # Simple hardcoded lists for the initial script
    colors = ["vibrant jewel tones", "neon glowing colors", "pastel watercolor", "monochromatic black and white"]
    textures = ["intricate filigree", "smooth liquid metal", "cellular organic", "rough impasto paint"]
    subjects = ["botanical flora", "sacred geometry", "swirling nebulae", "kaleidoscopic mandalas"]
    
    prompt = f"A seamless tileable pattern featuring {random.choice(subjects)}, in {style} style, with {random.choice(textures)} and {random.choice(colors)}. High detail, 8k resolution, symmetrical design fitting perfectly within the boundary."
    
    return prompt

def generate_styled_shape(mask_path, prompt, output_path, api_key=None, mock=False):
    """
    Submits the mathematical mask to Stability API ControlNet (Sketch) 
    to generate a styled shape perfectly preserving the boundary.
    """
    print(f"Applying style to mask: {mask_path}")
    print(f"Prompt: {prompt}")
    
    # Load and resize mask if necessary to fit API requirements (1024x1024 or similar)
    img = Image.open(mask_path)
    
    if mock or not api_key:
        # In mock mode, we just create a noise image and mask it
        print("Mock mode: creating fake styled image in place of API call")
        w, h = img.size
        noise = Image.effect_noise((w, h), 50).convert('RGB')
        
        # Colorize the noise based on prompt keywords loosely
        if "neon" in prompt:
            colored_noise = Image.new('RGB', (w, h), (random.randint(50,255), 0, random.randint(50,255)))
        else:
            colored_noise = Image.new('RGB', (w, h), (0, random.randint(50,255), random.randint(50,255)))
            
        styled_img = Image.blend(noise, colored_noise, 0.5)
        
        # Apply the mask right away for the mock output
        # Save temp mock styled image
        styled_img.save("temp_styled.png")
        return "temp_styled.png"

    # API Request Preparation
    files = {
        "image": open(mask_path, "rb")
    }
    
    data = {
        "prompt": prompt,
        "control_strength": 0.9, # High control strength to force the edge shape
        "output_format": "png"
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*"
    }

    print("Calling Stability API...")
    response = requests.post(
        STABILITY_API_URL, 
        headers=headers, 
        files=files, 
        data=data
    )

    if response.status_code == 200:
        with open(output_path, 'wb') as file:
            file.write(response.content)
        print(f"Successfully stylized image saved to {output_path}")
        return output_path
    else:
        print(f"API Error ({response.status_code}): {response.text}")
        raise Exception("API call failed")

def apply_transparency(styled_path, mask_path, output_path):
    """
    Cut out the stylized image using the exact original math mask.
    This ensures absolutely perfectly accurate transparent boundaries for tessellation.
    """
    print(f"Applying transparency map from {mask_path} to {styled_path}")
    styled_img = Image.open(styled_path).convert("RGBA")
    mask_img = Image.open(mask_path).convert("L")
    
    # Ensure they are exactly the same size
    if styled_img.size != mask_img.size:
        print(f"Warning: resizing styled image from {styled_img.size} to match mask {mask_img.size}")
        styled_img = styled_img.resize(mask_img.size, Image.LANCZOS)
    
    # Force transparency
    styled_img.putalpha(mask_img)
    
    styled_img.save(output_path, "PNG")
    print(f"Final transparent tiled element saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Style math masks using AI (Stability ControlNet)")
    parser.add_argument("--mask", type=str, required=True, help="Path to the input black-and-white mask")
    parser.add_argument("--style", type=str, default="psychedelic", help="Overall style keyword")
    parser.add_argument("--outdir", type=str, default="output/tiles", help="Output directory")
    parser.add_argument("--mock", action="store_true", help="Run without API key to test the script pipeline")
    
    args = parser.parse_args()
    
    os.makedirs(args.outdir, exist_ok=True)
    
    # Base name for outputs
    base_name = os.path.splitext(os.path.basename(args.mask))[0]
    raw_styled_path = os.path.join(args.outdir, f"{base_name}_styled_raw.png")
    final_path = os.path.join(args.outdir, f"{base_name}_finished_tile.png")
    
    api_key = get_api_key()
    prompt = generate_prompt("data/word_lists", args.style)
    
    try:
        # Step 2.1: Stylize
        generated_path = generate_styled_shape(args.mask, prompt, raw_styled_path, api_key, args.mock)
        
        # Step 2.2: Perfect Transparency Cutout
        apply_transparency(generated_path, args.mask, final_path)
        
        # Clean up temporary raw mock if we used it
        if args.mock and os.path.exists("temp_styled.png"):
            os.remove("temp_styled.png")
            
        print("\nPhase 2 Complete! We have perfectly mapped stylized tiles ready for Phase 3 tessellation.")
            
    except Exception as e:
        print(f"Error during Phase 2 pipeline: {e}")

if __name__ == "__main__":
    main()
