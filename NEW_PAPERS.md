# New Papers Awaiting Review

Candidates that the [daily update](.github/workflows/daily-update.yml) found but did not add to the list by itself. When a language model judges the papers, only the ones it is unsure about wait here. With keyword rules alone, every candidate waits here.

- **To accept a paper,** move its entry line (the one starting with `- [`) into the suggested section of [README.md](README.md), leave the indented "Found …" note behind, then run `python scripts/update_stats.py`.
- **To reject a paper,** delete it.

Either way the paper will not come back, because every paper the bot has looked at is logged in [scripts/processed_ids.txt](scripts/processed_ids.txt).

### Swarms and Multi-Robot Control

- [ST-GRL: Spatiotemporal Cognitive Graph Reinforcement Learning for Scalable Multi-Robot Collaborative Exploration](https://doi.org/10.1109/iros61738.2026.11776410) - IROS 2026.
  - Found 2026-11-26 in OpenAlex. Suggested: Swarms and Multi-Robot Control. Why: RL for micro-robot swarm exploration; actuation unspecified but fits generic microrobot scope. (openai/gpt-oss-120b via api.groq.com)

### Perception: Detection, Tracking and Localization

- [Engineered E. coli Nissle 1917 as H2S intelligent microbots for precise NIR-II bioimaging and synergistic anticancer therapy](https://doi.org/10.1016/j.cclet.2026.113704) - Chinese Chemical Letters 2026.11.
  - Found 2026-11-26 in OpenAlex. Suggested: Perception: Detection, Tracking and Localization. Why: No abstract; unclear if learning or magnetic actuation present (openai/gpt-oss-120b via api.groq.com)
