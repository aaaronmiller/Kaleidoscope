# Kaleidoscope v1.0: Infinite Pattern Generation System
## Product Requirements Document - IMPLEMENTATION READY

**Document Status:** Implementation-Ready  
**Last Updated:** December 8, 2025  
**Maintainer:** Kaleidoscope Core Team  
**Architecture:** Python-based Agentic Pipeline with Mathematical Transform Engine

---

## Executive Summary

Kaleidoscope v1.0 is an automated pattern generation system that produces infinite unique designs by combining AI image generation with mathematically rigorous transformations. The system creates legally protectable patterns suitable for fabric manufacturers, design studios, and print-on-demand marketplaces.

**Critical Innovation:** Mathematical transformation layer provides human authorship claim for AI-generated base content, enabling trademark protection for distinctive patterns.

---

## Key Features in v1.0

1. **Mad-Lib Prompt Engine:** Combinatorial word selection from 20 thematic lists (50+ words each) producing 10^33+ unique combinations
2. **AI Image Integration:** Multi-provider abstraction (DALL-E 3, Stable Diffusion) with fallback
3. **Mathematical Transform Engine:** All 17 wallpaper groups + N-fold kaleidoscope + fractal overlays
4. **Seamless Tiling:** Automated edge detection and correction
5. **Provenance Tracking:** Complete generation chain for IP documentation
6. **POD Integration:** Automated deployment to Printful via REST API
7. **Trend Intelligence:** Pinterest/X keyword integration for responsive generation
8. **Scheduled Automation:** Cron-based daily generation pipeline

---

## Core Requirements (R1-R14)

### R1: Word List Management and Prompt Generation

**Purpose:** Enable infinite unique prompt creation through combinatorial word selection.

**Acceptance Criteria:**

1. THE System SHALL maintain 20+ thematic word lists in `data/word_lists/` with JSON schema:
```json
{
  "list_id": "string (format: NN_name)",
  "name": "string (display name)",
  "description": "string",
  "words": ["array of 50+ strings"],
  "weight": "float 0.0-1.0 (default 1.0)",
  "category": "enum: color|style|nature|cultural|abstract|technique"
}
```

2. THE System SHALL support weighted random sampling with configurable parameters:
```python
class PromptGenerator:
    def __init__(self, word_lists_path: str):
        self.word_lists = self.load_word_lists(word_lists_path)
        self.trend_keywords = []
    
    def generate_word_selection(
        self,
        min_words: int = 5,
        max_words: int = 25,
        trend_weight: float = 0.3,
        style_bias: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Select words from lists with weighted randomization.
        
        Returns:
            {
                "words": ["list", "of", "selected", "words"],
                "sources": {"list_id": ["words", "from", "that", "list"]},
                "trend_injected": ["trend", "words"],
                "style_bias": "style_name or None",
                "timestamp": "ISO8601",
                "seed": "random seed for reproducibility"
            }
        """
        selected = []
        sources = {}
        
        # Determine words per list (1-5 from each, randomly)
        for wl in self.word_lists:
            k = random.randint(1, 5)
            if style_bias and wl["category"] == "cultural":
                # Bias toward matching cultural styles
                if style_bias.lower() in [w.lower() for w in wl["words"]]:
                    k += 2
            
            sample = random.sample(wl["words"], min(k, len(wl["words"])))
            selected.extend(sample)
            sources[wl["list_id"]] = sample
        
        # Inject trend keywords
        if self.trend_keywords and random.random() < trend_weight:
            trend_sample = random.sample(
                self.trend_keywords, 
                min(3, len(self.trend_keywords))
            )
            selected.extend(trend_sample)
        
        return {
            "words": selected,
            "sources": sources,
            "trend_injected": trend_sample if self.trend_keywords else [],
            "style_bias": style_bias,
            "timestamp": datetime.utcnow().isoformat(),
            "seed": random.getrandbits(64)
        }
```

3. THE System SHALL compose final prompts via LLM with system prompt:
```python
PROMPT_COMPOSER_SYSTEM = """
You are a creative director specializing in surface pattern design.
Given a list of thematic words, compose an evocative prompt for
generating abstract or semi-abstract pattern art suitable for fabric
printing.

Requirements:
- Combine words into a coherent visual description
- Emphasize texture, color, and repeating elements
- Include lighting and mood descriptors
- Specify "seamless pattern" or "tileable design" explicitly
- Output should be 50-150 words

Do NOT include:
- Human figures or faces
- Branded content or logos
- Specific copyrighted characters
- Text or typography
"""

def compose_prompt(words: List[str], style_bias: Optional[str] = None) -> str:
    """Compose final prompt from word selection via LLM."""
    user_message = f"Words: {', '.join(words)}"
    if style_bias:
        user_message += f"\nStyle emphasis: {style_bias}"
    
    response = llm_client.create(
        model="claude-3-5-sonnet-latest",
        system=PROMPT_COMPOSER_SYSTEM,
        messages=[{"role": "user", "content": user_message}],
        temperature=0.8,
        max_tokens=300
    )
    return response.content
```

4. THE System SHALL log all prompt generation to provenance with schema:
```json
{
  "prompt_id": "uuid",
  "timestamp": "ISO8601",
  "word_selection": {
    "words": ["..."],
    "sources": {"list_id": ["..."]},
    "trend_injected": ["..."],
    "style_bias": "string or null",
    "seed": 12345678901234567890
  },
  "composed_prompt": "full text of composed prompt",
  "llm_model": "claude-3-5-sonnet-latest",
  "llm_temperature": 0.8
}
```

5. THE `generate` command SHALL support style bias via flag:
```bash
kaleidoscope generate --style-bias "japanese ukiyo-e" --count 10
kaleidoscope generate --style-bias "psychedelic" --trend-weight 0.5
```

---

### R2: AI Image Generation Layer

**Purpose:** Generate base images from prompts using external AI image APIs.

**Acceptance Criteria:**

1. THE System SHALL implement provider abstraction for multiple AI services:
```python
from abc import ABC, abstractmethod
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class GeneratedImage:
    image_bytes: bytes
    width: int
    height: int
    provider: str
    model: str
    prompt: str
    revised_prompt: Optional[str]
    generation_id: str
    cost_usd: float
    metadata: Dict[str, Any]

class ImageProvider(ABC):
    @abstractmethod
    def generate(
        self,
        prompt: str,
        width: int = 2048,
        height: int = 2048,
        quality: str = "hd",
        style: str = "natural"
    ) -> GeneratedImage:
        """Generate image from prompt."""
        pass
    
    @abstractmethod
    def get_cost_per_image(self, width: int, height: int) -> float:
        """Return cost in USD for single image generation."""
        pass
    
    @abstractmethod
    def check_availability(self) -> bool:
        """Check if provider is available and authenticated."""
        pass

class DallE3Provider(ImageProvider):
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = "dall-e-3"
    
    def generate(
        self,
        prompt: str,
        width: int = 2048,
        height: int = 2048,
        quality: str = "hd",
        style: str = "natural"
    ) -> GeneratedImage:
        # Map dimensions to DALL-E sizes
        size = self._map_size(width, height)
        
        response = self.client.images.generate(
            model=self.model,
            prompt=prompt,
            size=size,
            quality=quality,
            style=style,
            n=1,
            response_format="b64_json"
        )
        
        image_data = base64.b64decode(response.data[0].b64_json)
        
        return GeneratedImage(
            image_bytes=image_data,
            width=width,
            height=height,
            provider="openai",
            model=self.model,
            prompt=prompt,
            revised_prompt=response.data[0].revised_prompt,
            generation_id=str(uuid.uuid4()),
            cost_usd=self.get_cost_per_image(width, height),
            metadata={"style": style, "quality": quality}
        )
    
    def get_cost_per_image(self, width: int, height: int) -> float:
        # DALL-E 3 pricing (as of Dec 2024)
        if width <= 1024 and height <= 1024:
            return 0.040  # Standard
        else:
            return 0.080  # HD
    
    def _map_size(self, width: int, height: int) -> str:
        if width == height:
            return "1024x1024" if width <= 1024 else "1792x1024"
        elif width > height:
            return "1792x1024"
        else:
            return "1024x1792"

class StableDiffusionProvider(ImageProvider):
    def __init__(self, api_key: str, endpoint: str = "https://api.stability.ai"):
        self.api_key = api_key
        self.endpoint = endpoint
    
    def generate(
        self,
        prompt: str,
        width: int = 2048,
        height: int = 2048,
        quality: str = "hd",
        style: str = "natural"
    ) -> GeneratedImage:
        response = requests.post(
            f"{self.endpoint}/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "text_prompts": [{"text": prompt, "weight": 1.0}],
                "height": min(height, 1024),
                "width": min(width, 1024),
                "samples": 1,
                "steps": 50 if quality == "hd" else 30
            }
        )
        
        image_data = base64.b64decode(response.json()["artifacts"][0]["base64"])
        
        return GeneratedImage(
            image_bytes=image_data,
            width=width,
            height=height,
            provider="stability",
            model="sdxl-1.0",
            prompt=prompt,
            revised_prompt=None,
            generation_id=response.json()["artifacts"][0]["seed"],
            cost_usd=self.get_cost_per_image(width, height),
            metadata={"steps": 50 if quality == "hd" else 30}
        )
```

2. THE System SHALL implement automatic fallback between providers:
```python
class ImageGeneratorOrchestrator:
    def __init__(self, providers: List[ImageProvider]):
        self.providers = providers
        self.primary_index = 0
    
    def generate(self, prompt: str, **kwargs) -> GeneratedImage:
        """Try providers in order until one succeeds."""
        errors = []
        
        for i, provider in enumerate(self.providers):
            try:
                if not provider.check_availability():
                    continue
                return provider.generate(prompt, **kwargs)
            except Exception as e:
                errors.append(f"{provider.__class__.__name__}: {e}")
                continue
        
        raise RuntimeError(f"All providers failed: {errors}")
```

3. THE System SHALL enforce minimum output resolution of 2048×2048 pixels.

4. THE System SHALL extract color palette from generated images:
```python
def extract_palette(image: Image.Image, n_colors: int = 5) -> List[str]:
    """Extract dominant colors as hex codes."""
    # Resize for speed
    img = image.copy()
    img.thumbnail((150, 150))
    
    # Get pixels
    pixels = np.array(img).reshape(-1, 3)
    
    # K-means clustering
    kmeans = KMeans(n_clusters=n_colors, random_state=42)
    kmeans.fit(pixels)
    
    # Convert to hex
    colors = []
    for center in kmeans.cluster_centers_:
        hex_color = "#{:02x}{:02x}{:02x}".format(
            int(center[0]), int(center[1]), int(center[2])
        )
        colors.append(hex_color)
    
    return colors
```

5. THE System SHALL implement cost tracking and budget enforcement:
```python
class CostTracker:
    def __init__(self, daily_budget_usd: float = 50.0):
        self.daily_budget = daily_budget_usd
        self.daily_spend = 0.0
        self.reset_date = date.today()
    
    def can_generate(self, estimated_cost: float) -> bool:
        self._check_reset()
        return (self.daily_spend + estimated_cost) <= self.daily_budget
    
    def record_spend(self, amount: float):
        self._check_reset()
        self.daily_spend += amount
    
    def _check_reset(self):
        if date.today() > self.reset_date:
            self.daily_spend = 0.0
            self.reset_date = date.today()
```

---

### R3: Mathematical Transformation Engine

**Purpose:** Apply mathematically rigorous transformations to create seamless, repeating patterns.

**Acceptance Criteria:**

1. THE System SHALL implement all 17 wallpaper symmetry groups:
```python
from enum import Enum
from dataclasses import dataclass
import numpy as np
from PIL import Image

class WallpaperGroup(Enum):
    P1 = "p1"      # Translation only
    P2 = "p2"      # 180° rotation
    PM = "pm"      # Horizontal reflection
    PG = "pg"      # Glide reflection
    CM = "cm"      # Reflection + glide
    PMM = "pmm"    # 180° + 2 perpendicular reflections
    PMG = "pmg"    # 180° + reflection + glide
    PGG = "pgg"    # 180° + perpendicular glides
    CMM = "cmm"    # 180° + 2 reflections (rhombic)
    P4 = "p4"      # 90° rotation
    P4M = "p4m"    # 90° + 2 reflection axes at 45°
    P4G = "p4g"    # 90° + reflection + glide
    P3 = "p3"      # 120° rotation
    P3M1 = "p3m1"  # 120° + reflection ⟂ to sides
    P31M = "p31m"  # 120° + reflection ∥ to sides
    P6 = "p6"      # 60° rotation
    P6M = "p6m"    # 60° + reflections

@dataclass
class TransformSpec:
    wallpaper_group: Optional[WallpaperGroup] = None
    kaleidoscope_folds: Optional[int] = None
    fractal_type: Optional[str] = None
    fractal_blend: float = 0.3
    seamless_correction: bool = True

class WallpaperTransformer:
    """Apply wallpaper group symmetry to create repeating patterns."""
    
    def apply(self, image: Image.Image, group: WallpaperGroup) -> Image.Image:
        """Apply specified wallpaper group transformation."""
        
        # Extract fundamental domain based on group
        fd = self._extract_fundamental_domain(image, group)
        
        # Apply symmetry operations to tile the plane
        match group:
            case WallpaperGroup.P1:
                return self._tile_p1(fd)
            case WallpaperGroup.P2:
                return self._tile_p2(fd)
            case WallpaperGroup.PM:
                return self._tile_pm(fd)
            case WallpaperGroup.P4M:
                return self._tile_p4m(fd)
            case WallpaperGroup.P6M:
                return self._tile_p6m(fd)
            case _:
                return self._tile_generic(fd, group)
    
    def _tile_p4m(self, fd: Image.Image) -> Image.Image:
        """P4M: 90° rotation + mirrors at 45°."""
        w, h = fd.size
        
        # Create unit cell from fundamental domain
        # P4M unit cell = 8 copies of FD arranged with rotations and reflections
        unit = Image.new('RGB', (w * 2, h * 2))
        
        # Original
        unit.paste(fd, (0, 0))
        # Horizontal flip
        unit.paste(fd.transpose(Image.FLIP_LEFT_RIGHT), (w, 0))
        # Vertical flip
        unit.paste(fd.transpose(Image.FLIP_TOP_BOTTOM), (0, h))
        # Both flips
        unit.paste(fd.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM), (w, h))
        
        # Rotate unit 90° and blend
        unit_90 = unit.rotate(90, expand=False)
        unit = Image.blend(unit, unit_90, 0.5)
        
        return self._tile_unit_cell(unit, target_size=2048)
    
    def _rotation_matrix(self, theta: float) -> np.ndarray:
        """2D rotation matrix for angle theta (radians)."""
        return np.array([
            [np.cos(theta), -np.sin(theta)],
            [np.sin(theta), np.cos(theta)]
        ])
    
    def _reflection_matrix(self, alpha: float) -> np.ndarray:
        """2D reflection matrix across line at angle alpha."""
        return np.array([
            [np.cos(2*alpha), np.sin(2*alpha)],
            [np.sin(2*alpha), -np.cos(2*alpha)]
        ])
```

2. THE System SHALL implement N-fold kaleidoscope transformation:
```python
class KaleidoscopeTransformer:
    """Apply N-fold mirror reflections for kaleidoscopic patterns."""
    
    def apply(self, image: Image.Image, folds: int) -> Image.Image:
        """
        Apply N-fold kaleidoscope transformation.
        
        Args:
            image: Source image
            folds: Number of mirror folds (3-12 typical)
        
        Returns:
            Kaleidoscopic pattern with N-fold radial symmetry
        """
        w, h = image.size
        center = (w // 2, h // 2)
        radius = min(w, h) // 2
        
        # Create output image
        result = Image.new('RGB', (w, h), (0, 0, 0))
        result_array = np.array(result)
        source_array = np.array(image)
        
        # Angle of each wedge
        wedge_angle = 2 * np.pi / folds
        
        # For each pixel, determine which wedge it's in and map to base wedge
        for y in range(h):
            for x in range(w):
                # Convert to polar coordinates
                dx = x - center[0]
                dy = y - center[1]
                r = np.sqrt(dx**2 + dy**2)
                theta = np.arctan2(dy, dx)
                
                if theta < 0:
                    theta += 2 * np.pi
                
                # Determine wedge index
                wedge_idx = int(theta / wedge_angle)
                
                # Map to base wedge angle
                base_theta = theta - wedge_idx * wedge_angle
                
                # Mirror odd wedges
                if wedge_idx % 2 == 1:
                    base_theta = wedge_angle - base_theta
                
                # Convert back to cartesian
                src_x = int(center[0] + r * np.cos(base_theta))
                src_y = int(center[1] + r * np.sin(base_theta))
                
                # Bounds check and sample
                if 0 <= src_x < w and 0 <= src_y < h:
                    result_array[y, x] = source_array[src_y, src_x]
        
        return Image.fromarray(result_array)
```

3. THE System SHALL implement fractal overlay generation:
```python
class FractalGenerator:
    """Generate fractal patterns for overlay blending."""
    
    def mandelbrot(
        self,
        width: int,
        height: int,
        x_range: Tuple[float, float] = (-2.5, 1.0),
        y_range: Tuple[float, float] = (-1.25, 1.25),
        max_iter: int = 256
    ) -> np.ndarray:
        """
        Generate Mandelbrot set visualization.
        
        Formula: z_{n+1} = z_n² + c, starting with z_0 = 0
        Point c is in set if |z_n| remains bounded as n → ∞
        """
        x = np.linspace(x_range[0], x_range[1], width)
        y = np.linspace(y_range[0], y_range[1], height)
        X, Y = np.meshgrid(x, y)
        C = X + 1j * Y
        
        Z = np.zeros_like(C)
        M = np.zeros(C.shape)
        
        for i in range(max_iter):
            mask = np.abs(Z) <= 2
            Z[mask] = Z[mask] ** 2 + C[mask]
            M[mask] = i
        
        # Normalize to 0-255
        M = (M / max_iter * 255).astype(np.uint8)
        return M
    
    def julia(
        self,
        width: int,
        height: int,
        c: complex = complex(-0.7, 0.27015),
        x_range: Tuple[float, float] = (-1.5, 1.5),
        y_range: Tuple[float, float] = (-1.5, 1.5),
        max_iter: int = 256
    ) -> np.ndarray:
        """
        Generate Julia set for fixed parameter c.
        
        Formula: z_{n+1} = z_n² + c, starting with z_0 = pixel coordinate
        """
        x = np.linspace(x_range[0], x_range[1], width)
        y = np.linspace(y_range[0], y_range[1], height)
        X, Y = np.meshgrid(x, y)
        Z = X + 1j * Y
        
        M = np.zeros(Z.shape)
        
        for i in range(max_iter):
            mask = np.abs(Z) <= 2
            Z[mask] = Z[mask] ** 2 + c
            M[mask] = i
        
        M = (M / max_iter * 255).astype(np.uint8)
        return M
```

4. THE System SHALL implement seamless tile correction:
```python
class SeamlessCorrector:
    """Ensure patterns tile seamlessly."""
    
    def correct(self, image: Image.Image, blend_width: int = 64) -> Image.Image:
        """
        Apply seamless correction to image edges.
        
        Uses gradient blending to create smooth transitions at edges.
        """
        arr = np.array(image, dtype=np.float32)
        h, w = arr.shape[:2]
        
        # Create horizontal seam correction
        left = arr[:, :blend_width]
        right = arr[:, -blend_width:]
        
        # Gradient weights
        gradient = np.linspace(0, 1, blend_width)
        gradient = gradient.reshape(1, -1, 1)
        
        # Blend left and right edges
        blended = right * gradient + left * (1 - gradient)
        
        # Apply to both edges
        arr[:, :blend_width] = blended
        arr[:, -blend_width:] = blended
        
        # Create vertical seam correction
        top = arr[:blend_width, :]
        bottom = arr[-blend_width:, :]
        
        gradient_v = np.linspace(0, 1, blend_width).reshape(-1, 1, 1)
        blended_v = bottom * gradient_v + top * (1 - gradient_v)
        
        arr[:blend_width, :] = blended_v
        arr[-blend_width:, :] = blended_v
        
        return Image.fromarray(arr.astype(np.uint8))
    
    def verify_seamless(self, image: Image.Image, threshold: float = 5.0) -> bool:
        """
        Verify that image tiles seamlessly.
        
        Returns True if edge discontinuity is below threshold.
        """
        arr = np.array(image, dtype=np.float32)
        
        # Compare left edge to right edge
        left_right_diff = np.mean(np.abs(arr[:, 0] - arr[:, -1]))
        
        # Compare top edge to bottom edge
        top_bottom_diff = np.mean(np.abs(arr[0, :] - arr[-1, :]))
        
        return left_right_diff < threshold and top_bottom_diff < threshold
```

5. THE transform engine SHALL chain multiple transformations:
```python
class TransformPipeline:
    """Chain multiple transformations."""
    
    def __init__(self):
        self.wallpaper = WallpaperTransformer()
        self.kaleidoscope = KaleidoscopeTransformer()
        self.fractal = FractalGenerator()
        self.seamless = SeamlessCorrector()
    
    def apply(self, image: Image.Image, spec: TransformSpec) -> Image.Image:
        """Apply transformation pipeline according to spec."""
        result = image.copy()
        
        # Apply kaleidoscope first (if specified)
        if spec.kaleidoscope_folds:
            result = self.kaleidoscope.apply(result, spec.kaleidoscope_folds)
        
        # Apply wallpaper group (if specified)
        if spec.wallpaper_group:
            result = self.wallpaper.apply(result, spec.wallpaper_group)
        
        # Overlay fractal (if specified)
        if spec.fractal_type:
            fractal_img = self._generate_fractal(result.size, spec.fractal_type)
            result = Image.blend(
                result, 
                fractal_img, 
                alpha=spec.fractal_blend
            )
        
        # Apply seamless correction (if enabled)
        if spec.seamless_correction:
            result = self.seamless.correct(result)
            
            # Verify seamlessness
            if not self.seamless.verify_seamless(result):
                logger.warning("Pattern may not tile perfectly")
        
        return result
```

---

### R4: Provenance and IP Documentation

**Purpose:** Maintain complete generation chain for legal IP protection.

**Acceptance Criteria:**

1. THE System SHALL create provenance record for each pattern with schema:
```json
{
  "pattern_id": "uuid",
  "created_at": "ISO8601",
  "version": "1.0.0",
  
  "generation_chain": {
    "word_selection": {
      "prompt_id": "uuid (reference to prompt provenance)",
      "words": ["array of selected words"],
      "sources": {"list_id": ["words"]},
      "trend_injected": ["trend", "words"],
      "style_bias": "string or null"
    },
    
    "prompt_composition": {
      "composed_prompt": "full prompt text",
      "llm_model": "claude-3-5-sonnet-latest",
      "llm_temperature": 0.8,
      "composition_timestamp": "ISO8601"
    },
    
    "image_generation": {
      "provider": "openai",
      "model": "dall-e-3",
      "prompt_sent": "prompt as sent to API",
      "revised_prompt": "revised prompt from API (if any)",
      "generation_id": "provider-specific ID",
      "original_dimensions": {"width": 2048, "height": 2048},
      "cost_usd": 0.08,
      "generation_timestamp": "ISO8601"
    },
    
    "transformations": [
      {
        "type": "kaleidoscope",
        "parameters": {"folds": 6},
        "formula": "z' = e^(2iθ_k) * z̄, θ_k = πk/N",
        "timestamp": "ISO8601"
      },
      {
        "type": "wallpaper_group",
        "parameters": {"group": "p4m"},
        "formula": "R(90°), M(45°), translations",
        "timestamp": "ISO8601"
      },
      {
        "type": "seamless_correction",
        "parameters": {"blend_width": 64},
        "timestamp": "ISO8601"
      }
    ],
    
    "quality_check": {
      "seamless_verified": true,
      "edge_discontinuity_score": 2.3,
      "complexity_score": 0.67,
      "passed": true,
      "timestamp": "ISO8601"
    }
  },
  
  "output": {
    "final_dimensions": {"width": 2048, "height": 2048},
    "file_hash_sha256": "abc123...",
    "file_path": "output/final/20241208_abc123_p4m_japanese.png",
    "color_palette": ["#1a2b3c", "#4d5e6f", "..."],
    "style_tags": ["japanese", "floral", "geometric"]
  },
  
  "authorship_claim": {
    "human_contributions": [
      "Word list curation and weighting",
      "Transform pipeline design",
      "Mathematical formula specification",
      "Quality threshold settings"
    ],
    "ai_contributions": [
      "Prompt composition from word selection",
      "Base image generation"
    ],
    "legal_basis": "Mathematical transformations constitute sufficient human creative input per USPTO guidance on AI-assisted works"
  },
  
  "provenance_hash": "SHA256 of entire record for integrity verification"
}
```

2. THE System SHALL compute and store cryptographic hash chain:
```python
import hashlib
import json

def compute_provenance_hash(record: Dict) -> str:
    """Compute SHA-256 hash of provenance record."""
    # Remove the hash field itself before computing
    record_copy = {k: v for k, v in record.items() if k != "provenance_hash"}
    
    # Canonical JSON serialization
    canonical = json.dumps(record_copy, sort_keys=True, separators=(',', ':'))
    
    return hashlib.sha256(canonical.encode()).hexdigest()

def verify_provenance(record: Dict) -> bool:
    """Verify provenance record integrity."""
    stored_hash = record.get("provenance_hash")
    computed_hash = compute_provenance_hash(record)
    return stored_hash == computed_hash
```

3. THE System SHALL export provenance as legally-formatted document:
```python
def export_provenance_document(pattern_id: str) -> str:
    """Export provenance as formatted legal document."""
    record = load_provenance(pattern_id)
    
    return f"""
PATTERN PROVENANCE CERTIFICATE
==============================
Pattern ID: {record['pattern_id']}
Created: {record['created_at']}

AUTHORSHIP DECLARATION
This pattern was created through a human-directed process combining:
1. Human-curated word lists and thematic selections
2. Human-designed mathematical transformation algorithms  
3. AI-assisted image generation

TRANSFORMATION CHAIN
{format_transformation_chain(record['generation_chain']['transformations'])}

MATHEMATICAL FORMULAS APPLIED
- Kaleidoscope: z' = e^(2iθ_k) * z̄ where θ_k = πk/N
- Symmetry Group: {record['generation_chain']['transformations'][1]['parameters']['group']}

INTEGRITY VERIFICATION
Hash: {record['provenance_hash']}

This document certifies the complete creation chain of the above pattern.
"""
```

---

### R5: Print-on-Demand Integration

**Purpose:** Automate deployment of patterns to POD platforms.

**Acceptance Criteria:**

1. THE System SHALL implement Printful REST API integration:
```python
import requests
from typing import List, Optional

class PrintfulClient:
    """Printful API client for pattern deployment."""
    
    BASE_URL = "https://api.printful.com"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def upload_file(self, image_path: str) -> Dict:
        """Upload pattern file to Printful."""
        with open(image_path, "rb") as f:
            files = {"file": f}
            response = self.session.post(
                f"{self.BASE_URL}/files",
                files=files
            )
            response.raise_for_status()
            return response.json()["result"]
    
    def create_sync_product(
        self,
        store_id: int,
        pattern_id: str,
        file_id: int,
        product_variants: List[int],
        metadata: Dict
    ) -> Dict:
        """Create product with pattern across variants."""
        
        sync_product = {
            "sync_product": {
                "name": f"Pattern {pattern_id[:8]}",
                "thumbnail": file_id
            },
            "sync_variants": [
                {
                    "variant_id": variant_id,
                    "files": [{
                        "id": file_id,
                        "type": "default"
                    }],
                    "retail_price": self._calculate_price(variant_id)
                }
                for variant_id in product_variants
            ]
        }
        
        response = self.session.post(
            f"{self.BASE_URL}/stores/{store_id}/sync/products",
            json=sync_product
        )
        response.raise_for_status()
        return response.json()["result"]
    
    def get_product_catalog(self) -> List[Dict]:
        """Get available Printful products."""
        response = self.session.get(f"{self.BASE_URL}/products")
        response.raise_for_status()
        return response.json()["result"]
```

2. THE System SHALL generate product mockups:
```python
def generate_mockups(
    self,
    file_id: int,
    product_id: int,
    variant_ids: List[int]
) -> List[str]:
    """Generate product mockups for pattern preview."""
    
    mockup_task = {
        "files": [{"placement": "default", "image_url": f"file://{file_id}"}],
        "format": "jpg",
        "variant_ids": variant_ids
    }
    
    response = self.session.post(
        f"{self.BASE_URL}/mockup-generator/create-task/{product_id}",
        json=mockup_task
    )
    response.raise_for_status()
    task_key = response.json()["result"]["task_key"]
    
    # Poll for completion
    while True:
        status = self.session.get(
            f"{self.BASE_URL}/mockup-generator/task?task_key={task_key}"
        ).json()
        
        if status["result"]["status"] == "completed":
            return [m["mockup_url"] for m in status["result"]["mockups"]]
        elif status["result"]["status"] == "failed":
            raise RuntimeError("Mockup generation failed")
        
        time.sleep(2)
```

3. THE System SHALL track deployment status:
```json
{
  "deployment_id": "uuid",
  "pattern_id": "uuid",
  "platform": "printful",
  "status": "deployed|pending|failed",
  "deployed_at": "ISO8601",
  "products_created": [
    {
      "product_type": "all-over-print-tee",
      "variant_count": 12,
      "listing_url": "https://...",
      "retail_price_range": {"min": 29.99, "max": 45.99}
    }
  ],
  "mockup_urls": ["https://..."],
  "error": null
}
```

---

### R6: Trend Intelligence Integration

**Purpose:** Incorporate trending keywords for market-responsive generation.

**Acceptance Criteria:**

1. THE System SHALL poll Pinterest Trends API:
```python
class PinterestTrendsClient:
    """Pinterest Trends API integration."""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.pinterest.com/v5"
    
    def get_trending_keywords(
        self,
        interests: List[str] = ["womens_fashion", "design", "home_decor"]
    ) -> List[Dict]:
        """
        Fetch trending keywords from Pinterest.
        
        Returns list of:
        {
            "keyword": "bohemian patterns",
            "score": 0.87,
            "growth_rate": 0.15,
            "category": "design"
        }
        """
        keywords = []
        
        for interest in interests:
            response = requests.get(
                f"{self.base_url}/trends/keywords",
                headers={"Authorization": f"Bearer {self.access_token}"},
                params={"interest_id": interest, "limit": 20}
            )
            
            if response.ok:
                for kw in response.json().get("items", []):
                    keywords.append({
                        "keyword": kw["keyword"],
                        "score": kw.get("score", 0.5),
                        "growth_rate": kw.get("growth_rate", 0),
                        "category": interest,
                        "source": "pinterest"
                    })
        
        return sorted(keywords, key=lambda x: x["score"], reverse=True)
```

2. THE System SHALL poll Twitter/X trending topics:
```python
class TwitterTrendsClient:
    """Twitter/X Trends API integration."""
    
    def get_trending_hashtags(
        self,
        woeid: int = 1  # Worldwide
    ) -> List[Dict]:
        """Fetch trending hashtags relevant to design/fashion."""
        
        # Filter for design-relevant hashtags
        design_keywords = [
            "pattern", "fabric", "design", "textile", "print",
            "fashion", "interior", "wallpaper", "art"
        ]
        
        response = self.client.get_trends_place(woeid)
        
        relevant = []
        for trend in response[0]["trends"]:
            name = trend["name"].lower().replace("#", "")
            if any(kw in name for kw in design_keywords):
                relevant.append({
                    "keyword": name,
                    "score": trend.get("tweet_volume", 0) / 100000,
                    "growth_rate": 0,
                    "source": "twitter"
                })
        
        return relevant
```

3. THE System SHALL cache trends with TTL:
```python
class TrendCache:
    """Cache for trend data with TTL."""
    
    def __init__(self, ttl_hours: int = 6):
        self.ttl = timedelta(hours=ttl_hours)
        self.cache: Dict[str, Tuple[datetime, List[Dict]]] = {}
    
    def get(self, source: str) -> Optional[List[Dict]]:
        if source not in self.cache:
            return None
        
        timestamp, data = self.cache[source]
        if datetime.utcnow() - timestamp > self.ttl:
            del self.cache[source]
            return None
        
        return data
    
    def set(self, source: str, data: List[Dict]):
        self.cache[source] = (datetime.utcnow(), data)
    
    def get_merged_trends(self) -> List[Dict]:
        """Get merged trends from all sources."""
        all_trends = []
        for source in self.cache:
            cached = self.get(source)
            if cached:
                all_trends.extend(cached)
        
        # Deduplicate and sort by score
        seen = set()
        unique = []
        for t in sorted(all_trends, key=lambda x: x["score"], reverse=True):
            if t["keyword"] not in seen:
                seen.add(t["keyword"])
                unique.append(t)
        
        return unique
```

---

### R7: Automated Scheduling

**Purpose:** Enable daily automated pattern generation.

**Acceptance Criteria:**

1. THE System SHALL support cron-based scheduling:
```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

class GenerationScheduler:
    """Automated generation scheduler."""
    
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.scheduler = BackgroundScheduler()
    
    def start(self):
        """Start the scheduler with configured jobs."""
        
        # Daily generation job
        self.scheduler.add_job(
            self.daily_generation_job,
            CronTrigger.from_crontab(self.config["schedule"]["cron"]),
            id="daily_generation",
            name="Daily Pattern Generation"
        )
        
        # Trend update job (more frequent)
        self.scheduler.add_job(
            self.trend_update_job,
            CronTrigger(hour="*/6"),  # Every 6 hours
            id="trend_update",
            name="Trend Data Update"
        )
        
        self.scheduler.start()
    
    def daily_generation_job(self):
        """Execute daily generation pipeline."""
        logger.info("Starting daily generation pipeline")
        
        try:
            # 1. Fetch latest trends
            trends = self.trend_client.fetch_all()
            self.prompt_generator.update_trends(trends)
            
            # 2. Generate patterns
            for i in range(self.config["daily_count"]):
                pattern = self.generate_single_pattern()
                
                # 3. Quality check
                if self.quality_check(pattern):
                    # 4. Deploy to platforms
                    self.deploy_pattern(pattern)
            
            logger.info(f"Daily generation complete: {self.config['daily_count']} patterns")
            
        except Exception as e:
            logger.error(f"Daily generation failed: {e}")
            self.alert_failure(e)
```

2. THE System SHALL provide CLI for manual triggering:
```bash
# Full pipeline
kaleidoscope generate --count 20 --deploy

# Individual steps
kaleidoscope trends --update
kaleidoscope generate --count 10 --no-deploy
kaleidoscope deploy --pattern-ids abc123,def456

# Status
kaleidoscope status
kaleidoscope list-patterns --date today
kaleidoscope list-deployments --status pending
```

---

### R8-R14: Additional Requirements

**R8: Quality Assurance**
- Automated seamless verification (edge discontinuity < 5.0)
- Complexity scoring (reject < 0.2 or > 0.9)
- Color balance checks
- Human review queue for edge cases

**R9: Storage and Catalog**
- PostgreSQL database for pattern catalog
- S3/GCS for image storage
- Full-text search on tags and metadata

**R10: Cultural Sensitivity**
- Human review required for cultural style patterns
- "Inspired by" labeling (not claiming authenticity)
- Excluded patterns: sacred/ceremonial imagery

**R11: Cost Management**
- Daily budget caps (default: $50)
- Per-pattern cost tracking
- Alert on budget thresholds

**R12: Logging and Monitoring**
- Structured JSON logging
- Error alerting via Slack/email
- Performance metrics dashboard

**R13: Testing Requirements**
- Unit tests for all transform functions
- Integration tests for API providers
- Visual regression tests for pattern quality

**R14: Security**
- API key encryption at rest
- No PII in patterns or metadata
- Rate limiting on internal APIs

---

## CLI Command Reference

```bash
# Initialize project
kaleidoscope init --config ./config.yaml

# Generate patterns
kaleidoscope generate --count 20 --style-bias "japanese" --trend-weight 0.3
kaleidoscope generate --count 5 --kaleidoscope-folds 6 --wallpaper-group p4m

# Manage trends
kaleidoscope trends --update
kaleidoscope trends --list
kaleidoscope trends --add "custom keyword"

# Deploy patterns
kaleidoscope deploy --pattern-id abc123 --platform printful
kaleidoscope deploy --all-pending

# View status
kaleidoscope status
kaleidoscope list --date 2024-12-08
kaleidoscope show --pattern-id abc123

# Scheduler
kaleidoscope scheduler start
kaleidoscope scheduler stop
kaleidoscope scheduler status

# Provenance
kaleidoscope provenance --export abc123 --format pdf
kaleidoscope provenance --verify abc123

# Development
kaleidoscope validate-transforms
kaleidoscope test-provider openai
kaleidoscope benchmark --count 10
```

---

## File Tree

```
kaleidoscope/
├── src/
│   ├── __init__.py
│   ├── cli.py                      # CLI entry point (Click-based)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── prompt_engine.py        # R1: Word list + prompt generation
│   │   ├── image_generator.py      # R2: AI provider abstraction
│   │   ├── transform_engine.py     # R3: Transform pipeline
│   │   └── provenance.py           # R4: Provenance tracking
│   ├── math/
│   │   ├── __init__.py
│   │   ├── symmetry_groups.py      # 17 wallpaper groups
│   │   ├── kaleidoscope.py         # N-fold mirrors
│   │   ├── fractals.py             # Mandelbrot/Julia/L-systems
│   │   └── tiling.py               # Seamless correction
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── printful.py             # R5: Printful API
│   │   ├── pinterest_trends.py     # R6: Pinterest trends
│   │   └── twitter_trends.py       # R6: Twitter trends
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── orchestrator.py         # Pipeline coordination
│   │   ├── scheduler.py            # R7: Cron scheduling
│   │   ├── quality_check.py        # R8: QA automation
│   │   └── deployer.py             # Deployment orchestration
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── catalog.py              # R9: Pattern catalog
│   │   ├── models.py               # SQLAlchemy models
│   │   └── file_storage.py         # S3/local file storage
│   └── utils/
│       ├── __init__.py
│       ├── image_utils.py
│       ├── color_utils.py
│       └── logging.py
├── data/
│   └── word_lists/
│       ├── 01_colors.json
│       ├── 04_cultural_styles.json
│       ├── 05_nature_elements.json
│       ├── 12_flora_botanical.json
│       ├── 13_fauna_naturalist.json
│       └── 21_counterculture_psychedelic.json
├── config/
│   ├── default.yaml
│   ├── schedule.yaml
│   └── api_keys.yaml.example
├── tests/
│   ├── test_prompt_engine.py
│   ├── test_transforms.py
│   ├── test_seamless.py
│   └── test_integrations.py
├── scripts/
│   └── run_daily_generation.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Daily generation capacity | 100+ patterns/day | Automated count |
| Seamless tile pass rate | > 95% | QA automation |
| API cost per pattern | < $0.50 | Cost tracking |
| Time to first sale | < 30 days | Platform analytics |
| Trend keyword incorporation | > 70% | Provenance analysis |
| Provenance completeness | 100% | Validation script |

---

## Risk Register

| Risk ID | Description | Probability | Impact | Mitigation |
|---------|-------------|-------------|--------|------------|
| RISK-001 | AI provider API changes | Medium | High | Multi-provider abstraction |
| RISK-002 | IP legal challenge | Medium | High | Strong provenance documentation |
| RISK-003 | POD platform policy change | Low | Medium | Diversified channels |
| RISK-004 | Cultural sensitivity violation | Medium | High | Human review for cultural styles |
| RISK-005 | Cost overrun | Medium | Medium | Daily budget caps, alerts |

---

## Implementation Roadmap

**MVP (8 weeks)**
- Core prompt engine with 6 word lists
- DALL-E 3 provider integration
- P4M + 6-fold kaleidoscope transforms
- Seamless correction
- Provenance tracking
- Printful API integration

**v1.5 (4 weeks)**
- Full 17 wallpaper groups
- Stable Diffusion provider
- Pinterest/Twitter trend integration
- Scheduled automation
- Quality automation

**v2.0 (6 weeks)**
- Additional POD platforms
- Self-improvement feedback loop
- B2B licensing portal
- API for developers

---

## Authority Statement

This document represents the FINAL v1.0 specification and is AUTHORITATIVE.

**Key Architectural Decisions Finalized:**
1. Python-based implementation with Click CLI
2. Multi-provider abstraction for AI image generation
3. Mathematical transform engine with all 17 wallpaper groups
4. Provenance-first IP documentation
5. Printful as primary POD integration

**No further architectural changes are authorized. Implement exactly as specified.**

---

**Document End - Total Lines: ~1,400**
