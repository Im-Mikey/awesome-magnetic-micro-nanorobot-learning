# New Papers Awaiting Review

Candidates that the [daily update](.github/workflows/daily-update.yml) found but did not add to the list by itself. When a language model judges the papers, only the ones it is unsure about wait here. With keyword rules alone, every candidate waits here.

- **To accept a paper,** move its entry line (the one starting with `- [`) into the suggested section of [README.md](README.md), leave the indented "Found …" note behind, then run `python scripts/update_stats.py`.
- **To reject a paper,** delete it.

Either way the paper will not come back, because every paper the bot has looked at is logged in [scripts/processed_ids.txt](scripts/processed_ids.txt).

### Foundation Models and LLMs

- [MicroVLA: A Vision-Language-Action Framework for Microrobotic Navigation Considering Inter-Particle Micro-Force Fields](https://doi.org/10.1109/iros61738.2026.11777580) - IROS 2026.
  - Found 2026-11-25 in OpenAlex. Suggested: Foundation Models and LLMs. Why: Magnetic actuation not specified; unclear if scope applies (openai/gpt-oss-120b via api.groq.com)
