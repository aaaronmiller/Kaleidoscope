<script lang="ts">
  import { onMount, tick } from 'svelte';

  // Runes for reactivity in Svelte 5
  let hueShift = $state(0);
  let saturationShift = $state(100);
  let lightnessShift = $state(100);
  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D | null = null;
  let originalImageData: ImageData | null = null;
  let isImageLoaded = $state(false);
  let imgElement = new Image();

  onMount(() => {
    if (canvas) {
      ctx = canvas.getContext('2d', { willReadFrequently: true });
    }
  });

  function handleImageUpload(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      const reader = new FileReader();
      
      reader.onload = (e) => {
        if (e.target?.result) {
          imgElement.onload = async () => {
            if (canvas && ctx) {
              // Resize canvas to max 1024x1024 for performance during live editing
              // Full 4k export could be done in a background worker
              const maxDim = 1024;
              let width = imgElement.width;
              let height = imgElement.height;
              
              if (width > maxDim || height > maxDim) {
                const ratio = Math.min(maxDim / width, maxDim / height);
                width = Math.floor(width * ratio);
                height = Math.floor(height * ratio);
              }
              
              canvas.width = width;
              canvas.height = height;
              
              ctx.drawImage(imgElement, 0, 0, width, height);
              originalImageData = ctx.getImageData(0, 0, width, height);
              isImageLoaded = true;
              
              // Ensure canvas updates before applying filters
              await tick();
              applyFilters();
            }
          };
          imgElement.src = e.target.result as string;
        }
      };
      reader.readAsDataURL(input.files[0]);
    }
  }

  // RGB <-> HSL conversions
  function rgbToHsl(r: number, g: number, b: number): [number, number, number] {
    r /= 255; g /= 255; b /= 255;
    const max = Math.max(r, g, b), min = Math.min(r, g, b);
    let h = 0, s = 0, l = (max + min) / 2;

    if (max !== min) {
      const d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      switch (max) {
        case r: h = (g - b) / d + (g < b ? 6 : 0); break;
        case g: h = (b - r) / d + 2; break;
        case b: h = (r - g) / d + 4; break;
      }
      h /= 6;
    }
    return [h * 360, s * 100, l * 100];
  }

  function hslToRgb(h: number, s: number, l: number): [number, number, number] {
    s /= 100; l /= 100;
    const k = (n: number) => (n + h / 30) % 12;
    const a = s * Math.min(l, 1 - l);
    const f = (n: number) => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));
    return [Math.round(255 * f(0)), Math.round(255 * f(8)), Math.round(255 * f(4))];
  }

  function applyFilters() {
    if (!ctx || !originalImageData || !canvas || !isImageLoaded) return;

    const currentImageData = ctx.createImageData(originalImageData);
    const data = originalImageData.data;
    const currentData = currentImageData.data;

    for (let i = 0; i < data.length; i += 4) {
      // Ignore fully transparent pixels
      if (data[i + 3] === 0) continue;

      const r = data[i];
      const g = data[i + 1];
      const b = data[i + 2];

      let [h, s, l] = rgbToHsl(r, g, b);

      // Apply Shifts
      h = (h + hueShift) % 360;
      if (h < 0) h += 360;
      
      s = Math.max(0, Math.min(100, s * (saturationShift / 100)));
      l = Math.max(0, Math.min(100, l * (lightnessShift / 100)));

      const [newR, newG, newB] = hslToRgb(h, s, l);

      currentData[i] = newR;
      currentData[i + 1] = newG;
      currentData[i + 2] = newB;
      currentData[i + 3] = data[i + 3]; // Preserve alpha
    }

    ctx.putImageData(currentImageData, 0, 0);
  }

  // Effect to trigger updates when sliders change
  $effect(() => {
    // Explicit dependencies for effect checking
    const _h = hueShift; 
    const _s = saturationShift; 
    const _l = lightnessShift;
    if (isImageLoaded) {
      applyFilters();
    }
  });

  function downloadImage() {
    if (!canvas || !isImageLoaded) return;
    const link = document.createElement('a');
    link.download = 'kaleidoscope_recolored.png';
    link.href = canvas.toDataURL('image/png');
    link.click();
  }

  function resetFilters() {
    hueShift = 0;
    saturationShift = 100;
    lightnessShift = 100;
  }
</script>

<main class="min-h-screen bg-neutral-900 text-white p-8 grid grid-cols-1 md:grid-cols-3 gap-8 font-sans">
  <!-- Controls Panel -->
  <div class="col-span-1 bg-neutral-800 p-6 rounded-2xl shadow-xl flex flex-col gap-6 border border-neutral-700">
    <div>
      <h1 class="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent mb-2">
        Kaleidoscope
      </h1>
      <p class="text-neutral-400 text-sm">Interactive Palette Control</p>
    </div>

    <!-- Upload -->
    <div class="border-2 border-dashed border-neutral-600 rounded-xl p-4 text-center hover:bg-neutral-700/50 transition-colors cursor-pointer relative">
      <input 
        type="file" 
        accept="image/png, image/jpeg" 
        onchange={handleImageUpload}
        class="absolute inset-0 opacity-0 cursor-pointer"
      />
      <span class="text-neutral-300 font-medium">+ Load Seamless Pattern</span>
    </div>

    <!-- Sliders -->
    <div class="flex flex-col gap-5 mt-4" style="opacity: {isImageLoaded ? 1 : 0.5}; pointer-events: {isImageLoaded ? 'auto' : 'none'}">
      
      <!-- Hue -->
      <div class="flex flex-col gap-2">
        <div class="flex justify-between">
          <label for="hue" class="text-sm font-medium">Hue Shift</label>
          <span class="text-xs text-neutral-400">{Math.round(hueShift)}°</span>
        </div>
        <input 
          id="hue" 
          type="range" 
          min="-180" 
          max="180" 
          bind:value={hueShift} 
          class="w-full accent-purple-500 h-2 bg-neutral-700 rounded-lg appearance-none cursor-pointer"
        />
        <!-- Visual Hue Bar -->
        <div class="h-2 rounded-full w-full mt-1 bg-gradient-to-r from-red-500 via-yellow-500 via-green-500 via-blue-500 via-purple-500 to-red-500"></div>
      </div>

      <!-- Saturation -->
      <div class="flex flex-col gap-2">
        <div class="flex justify-between">
          <label for="sat" class="text-sm font-medium">Saturation</label>
          <span class="text-xs text-neutral-400">{Math.round(saturationShift)}%</span>
        </div>
        <input 
          id="sat" 
          type="range" 
          min="0" 
          max="200" 
          bind:value={saturationShift} 
          class="w-full accent-pink-500 h-2 bg-neutral-700 rounded-lg appearance-none cursor-pointer"
        />
      </div>

      <!-- Lightness -->
      <div class="flex flex-col gap-2">
        <div class="flex justify-between">
          <label for="lit" class="text-sm font-medium">Lightness</label>
          <span class="text-xs text-neutral-400">{Math.round(lightnessShift)}%</span>
        </div>
        <input 
          id="lit" 
          type="range" 
          min="0" 
          max="200" 
          bind:value={lightnessShift} 
          class="w-full accent-blue-500 h-2 bg-neutral-700 rounded-lg appearance-none cursor-pointer"
        />
      </div>
      
      <div class="flex gap-3 mt-6">
        <button 
          onclick={resetFilters} 
          class="flex-1 py-2 px-4 bg-neutral-700 hover:bg-neutral-600 rounded-lg font-medium transition-colors"
        >
          Reset
        </button>
        <button 
          onclick={downloadImage} 
          class="flex-1 py-2 px-4 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-400 hover:to-pink-400 rounded-lg font-medium shadow-lg shadow-purple-500/20 transition-all"
        >
          Export
        </button>
      </div>

    </div>
  </div>

  <!-- Canvas Display -->
  <div class="col-span-1 md:col-span-2 bg-neutral-950 rounded-2xl border border-neutral-800 flex items-center justify-center p-4 overflow-hidden shadow-2xl relative shadow-inner">
    {#if !isImageLoaded}
      <div class="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
        <svg class="w-16 h-16 text-neutral-700" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
      </div>
    {/if}
    <div class="relative w-full h-full flex items-center justify-center checkered-bg rounded-lg overflow-hidden">
        <canvas 
          bind:this={canvas} 
          class="max-w-full max-h-full object-contain shadow-2xl transition-opacity duration-300"
          style="opacity: {isImageLoaded ? 1 : 0};"
        ></canvas>
    </div>
  </div>
</main>

<style>
  /* Standard transparent checkered background */
  :global(.checkered-bg) {
    background-color: #1a1a1a;
    background-image: 
      linear-gradient(45deg, #242424 25%, transparent 25%), 
      linear-gradient(-45deg, #242424 25%, transparent 25%), 
      linear-gradient(45deg, transparent 75%, #242424 75%), 
      linear-gradient(-45deg, transparent 75%, #242424 75%);
    background-size: 20px 20px;
    background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
  }
</style>
