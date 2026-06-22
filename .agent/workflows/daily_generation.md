---
description: Automated daily pattern generation pipeline with trend analysis, AI generation, transforms, and deployment
---

# Daily Generation Workflow

This workflow runs automatically at a configured time each day to generate new patterns.

## Prerequisites
- API keys configured in `config/api_keys.yaml`
- Database connection established
- At least one POD platform enabled

## Execution Steps

### 1. Trend Analysis (15 minutes)
```bash
# turbo
python scripts/fetch_trends.py --sources pinterest,twitter --output data/trends/$(date +%Y%m%d).json
```

This fetches current trending keywords and updates the trend cache.

### 2. Generate Prompts (10 minutes)
```bash
python scripts/generate_prompts.py \
  --count 20 \
  --trend-weight 0.3 \
  --output output/prompts/$(date +%Y%m%d)/
```

Creates N prompts using mad-lib selection weighted by trends.

### 3. Generate Base Images (30 minutes)
```bash
python scripts/generate_images.py \
  --prompts output/prompts/$(date +%Y%m%d)/ \
  --provider openai \
  --output output/base_images/$(date +%Y%m%d)/
```

Submits prompts to AI image generator and downloads results.

### 4. Apply Transforms (20 minutes)
```bash
python scripts/apply_transforms.py \
  --input output/base_images/$(date +%Y%m%d)/ \
  --presets random \
  --variants 3 \
  --output output/transformed/$(date +%Y%m%d)/
```

Applies mathematical transformations to each base image.

### 5. Quality Check (10 minutes)
```bash
# turbo
python scripts/quality_check.py \
  --input output/transformed/$(date +%Y%m%d)/ \
  --threshold 0.95 \
  --output output/final/$(date +%Y%m%d)/
```

Runs automated QA and moves passing patterns to final folder.

### 6. Deploy to Platforms (15 minutes)
```bash
python scripts/deploy_patterns.py \
  --input output/final/$(date +%Y%m%d)/ \
  --platforms printful \
  --dry-run false
```

Uploads patterns to enabled POD platforms.

### 7. Generate Provenance (5 minutes)
```bash
# turbo
python scripts/generate_provenance.py \
  --date $(date +%Y%m%d) \
  --output output/provenance/
```

Creates provenance documentation and hash chains.

## Post-Run
- Check logs at `logs/daily_$(date +%Y%m%d).log`
- Review any patterns flagged for manual review
- Monitor platform upload confirmations

## Error Recovery
If any step fails:
1. Check the specific step's log output
2. Fix the issue (usually API rate limits or connection issues)
3. Re-run from the failed step using `--resume-from <step_number>`

## Configuration
Edit `config/schedule.yaml` to modify:
- Run time (default: 01:00 local)
- Pattern count (default: 20)
- Enabled platforms
- Trend sources
