# Kaleidoscope: Project Structure & Directory Schema

---

## Root Directory Layout

```
Kaleidoscope/
├── .agent/                     # Agent configuration and workflows
│   └── workflows/              # Automation workflow definitions
│       ├── daily_generation.md
│       ├── trend_analysis.md
│       └── deploy_patterns.md
│
├── docs/                       # Project documentation
│   ├── 00_executive_summary.md
│   ├── 01_prd.md
│   ├── 02_mathematical_foundations.md
│   ├── 03_project_structure.md
│   ├── 04_agent_architecture.md
│   ├── 05_adversarial_validation.md
│   ├── 06_monetization_strategy.md
│   └── 07_cultural_styles_reference.md
│
├── src/                        # Source code
│   ├── core/                   # Core engine components
│   │   ├── __init__.py
│   │   ├── prompt_engine.py    # Mad-lib prompt generation
│   │   ├── image_generator.py  # AI image API wrappers
│   │   ├── transform_engine.py # Mathematical transformations
│   │   └── tile_engine.py      # Seamless tiling logic
│   │
│   ├── math/                   # Mathematical modules
│   │   ├── __init__.py
│   │   ├── symmetry_groups.py  # 17 wallpaper groups
│   │   ├── kaleidoscope.py     # N-fold mirror math
│   │   ├── fractals.py         # Mandelbrot, Julia, L-systems
│   │   └── tiling.py           # Penrose, Wang tiles
│   │
│   ├── integrations/           # External service integrations
│   │   ├── __init__.py
│   │   ├── printful.py         # Printful API client
│   │   ├── spoonflower.py      # Spoonflower automation
│   │   ├── redbubble.py        # Redbubble selenium automation
│   │   ├── pinterest_trends.py # Pinterest Trends API
│   │   └── twitter_trends.py   # X/Twitter Trends API
│   │
│   ├── pipeline/               # Generation pipeline
│   │   ├── __init__.py
│   │   ├── scheduler.py        # Cron-based scheduling
│   │   ├── orchestrator.py     # Pipeline coordination
│   │   ├── quality_check.py    # Automated QA
│   │   └── deployer.py         # Platform deployment
│   │
│   ├── storage/                # Data persistence
│   │   ├── __init__.py
│   │   ├── catalog.py          # Pattern catalog management
│   │   ├── provenance.py       # IP provenance tracking
│   │   └── models.py           # Database models
│   │
│   └── utils/                  # Utilities
│       ├── __init__.py
│       ├── image_utils.py
│       ├── color_utils.py
│       └── logging_utils.py
│
├── data/                       # Static data files
│   ├── word_lists/             # Prompt generation word lists
│   │   ├── 01_colors.json
│   │   ├── 02_textures.json
│   │   ├── 03_emotions.json
│   │   ├── 04_cultural_styles.json
│   │   ├── 05_nature_elements.json
│   │   ├── 06_geometric_forms.json
│   │   ├── 07_art_movements.json
│   │   ├── 08_materials.json
│   │   ├── 09_atmospheres.json
│   │   ├── 10_time_periods.json
│   │   ├── 11_natural_patterns.json
│   │   ├── 12_flora_botanical.json
│   │   ├── 13_fauna_naturalist.json
│   │   ├── 14_celestial.json
│   │   ├── 15_water_elements.json
│   │   ├── 16_abstract_concepts.json
│   │   ├── 17_architectural.json
│   │   ├── 18_textile_techniques.json
│   │   ├── 19_light_effects.json
│   │   └── 20_seasonal_themes.json
│   │
│   ├── style_prompts/          # Style-specific prompt templates
│   │   ├── japanese.json
│   │   ├── islamic_geometric.json
│   │   ├── celtic.json
│   │   ├── naturalist_audubon.json
│   │   └── ...
│   │
│   └── transform_presets/      # Pre-configured transform chains
│       ├── kaleidoscope_6fold.json
│       ├── wallpaper_p4m.json
│       ├── fractal_overlay.json
│       └── ...
│
├── output/                     # Generated outputs
│   ├── base_images/            # Raw AI-generated images
│   ├── transformed/            # Post-transformation patterns
│   ├── final/                  # Production-ready exports
│   ├── mockups/                # Product mockups
│   └── provenance/             # Generation logs and hashes
│
├── config/                     # Configuration files
│   ├── settings.yaml           # Main configuration
│   ├── api_keys.yaml.example   # API key template
│   ├── schedule.yaml           # Automation schedule
│   └── platforms.yaml          # POD platform configs
│
├── tests/                      # Test suite
│   ├── test_prompt_engine.py
│   ├── test_transforms.py
│   ├── test_integrations.py
│   └── fixtures/
│
├── scripts/                    # Utility scripts
│   ├── setup_env.sh
│   ├── run_daily_generation.py
│   └── export_catalog.py
│
├── requirements.txt            # Python dependencies
├── pyproject.toml              # Project metadata
├── README.md                   # Project overview
└── LICENSE                     # License file
```

---

## Key Directory Descriptions

### `/src/core/`
Core pattern generation logic. The **prompt_engine** generates creative prompts via mad-lib word selection + LLM composition. The **transform_engine** applies mathematical operations from the `/src/math/` modules.

### `/src/math/`
Pure mathematical implementations. These modules encode the formulas from `02_mathematical_foundations.md` as reusable transformation functions.

### `/src/integrations/`
External API wrappers. Each POD platform and trend source has its own module with standardized interfaces.

### `/data/word_lists/`
The 20 thematic word lists (50+ words each) that power the mad-lib prompt generation. Categories span colors, textures, cultural styles, natural elements, and more.

### `/output/`
Ephemeral storage for generated content. `provenance/` maintains the hash chains required for IP documentation.

---

## Database Schema (PostgreSQL)

```sql
-- Patterns catalog
CREATE TABLE patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Generation metadata
    word_seeds TEXT[],
    prompt_text TEXT,
    ai_model VARCHAR(50),
    ai_model_version VARCHAR(20),
    
    -- Transformation chain
    transforms JSONB,
    symmetry_group VARCHAR(10),
    
    -- Files
    base_image_path VARCHAR(500),
    final_pattern_path VARCHAR(500),
    mockup_paths TEXT[],
    
    -- Provenance
    provenance_hash VARCHAR(64),
    
    -- Catalog
    style_tags TEXT[],
    color_palette TEXT[],
    collection_id UUID REFERENCES collections(id),
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending',
    quality_score FLOAT,
    deployed_platforms TEXT[]
);

-- Collections/series grouping
CREATE TABLE collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200),
    description TEXT,
    style_theme VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Platform deployments
CREATE TABLE deployments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_id UUID REFERENCES patterns(id),
    platform VARCHAR(50),
    platform_product_id VARCHAR(200),
    deployed_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20),
    listing_url VARCHAR(500)
);

-- Trend keywords cache
CREATE TABLE trend_keywords (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(200),
    source VARCHAR(50),
    score FLOAT,
    fetched_at TIMESTAMP DEFAULT NOW()
);
```

---

## File Naming Conventions

### Patterns
```
{timestamp}_{hash8}_{symmetry}_{style}.png
Example: 20241207_a3f8b2c1_p4m_japanese.png
```

### Word Lists
```
{number}_{category}.json
Example: 12_flora_botanical.json
```

### Provenance Logs
```
{pattern_id}_provenance.json
```

---

*Project Structure v1.0*
