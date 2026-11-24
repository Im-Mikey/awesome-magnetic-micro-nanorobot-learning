# New Papers Awaiting Review

Candidates that the [daily update](.github/workflows/daily-update.yml) found but did not add to the list by itself. When a language model judges the papers, only the ones it is unsure about wait here. With keyword rules alone, every candidate waits here.

- **To accept a paper,** move its entry line (the one starting with `- [`) into the suggested section of [README.md](README.md), leave the indented "Found …" note behind, then run `python scripts/update_stats.py`.
- **To reject a paper,** delete it.

Either way the paper will not come back, because every paper the bot has looked at is logged in [scripts/processed_ids.txt](scripts/processed_ids.txt).

### Perception: Detection, Tracking and Localization

- [Metal–Organic-Framework-Encoded Magnetic Soft Robot for Untethered Multimodal Hazard Mapping and Autonomous Source Localization in Confined Spaces](https://doi.org/10.1021/acssensors.6c03254) - ACS Sensors 2026.11.
  - Found 2026-11-24 in Crossref. Suggested: Perception: Detection, Tracking and Localization. Why: Abstract lacks clear learning component; unclear if ML used for localization (openai/gpt-oss-120b via api.groq.com)
