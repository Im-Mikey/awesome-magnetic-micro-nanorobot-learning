# New Papers Awaiting Review

Candidates that the [daily update](.github/workflows/daily-update.yml) found but did not add to the list by itself. When a language model judges the papers, only the ones it is unsure about wait here. With keyword rules alone, every candidate waits here.

- **To accept a paper,** move its entry line (the one starting with `- [`) into the suggested section of [README.md](README.md), leave the indented "Found …" note behind, then run `python scripts/update_stats.py`.
- **To reject a paper,** delete it.

Either way the paper will not come back, because every paper the bot has looked at is logged in [scripts/processed_ids.txt](scripts/processed_ids.txt).

### Surveys and Perspectives

- [Next-generation medical nanorobotics: biohybrid systems, AI-guided navigation, and clinical translation challenges](https://doi.org/10.1016/j.nxnano.2026.100824) - Next Nanotechnology 2026.12.
  - Found 2026-11-23 in OpenAlex. Suggested: Surveys and Perspectives. Why: broad medical nanorobotics review that covers AI-guided navigation (manual review)
- [Machine learning techniques for understanding pattern formation and self-assembly in active colloidal systems](https://doi.org/10.1088/1361-648x/aec211) - Journal of Physics: Condensed Matter 2026.11.
  - Found 2026-11-23 in PubMed. Suggested: Surveys and Perspectives. Why: review of machine learning for active colloids; could sit in Surveys next to the RL-for-active-matter review (manual review)
- [Swarm Autonomy: From Agent Functionalization to Machine Intelligence](https://doi.org/10.1002/adma.202312956) - Advanced Materials 2024.05.
  - Found 2026-11-23 in review. Suggested: Surveys and Perspectives. Why: swarm autonomy review; machine intelligence may mean emergent swarm behaviour, not machine learning (manual review)

### Control and Navigation

- [AI-driven deformation control of hard-magnetic soft beams](https://doi.org/10.1016/j.ijsolstr.2026.114404) - International Journal of Solids and Structures 2027.01.
  - Found 2026-11-23 in OpenAlex. Suggested: Control and Navigation. Why: AI-driven deformation control of hard-magnetic soft beams; no abstract to confirm the robot scale (manual review)
- [Robust data-driven velocity control of stick–slip planar micro-robots: comparison between three advanced control frameworks](https://doi.org/10.1007/s11012-026-02194-4) - Meccanica 2026.10.
  - Found 2026-11-23 in OpenAlex, Semantic Scholar. Suggested: Control and Navigation. Why: data-driven control of stick-slip micro-robots, which are usually piezo-driven; check the actuation (manual review)
- [Reinforcement Learning-Based Motion Control of Jellyfish Millirobots](https://doi.org/10.1007/978-981-95-4897-2_44) - MLCCIM 2026.
  - Found 2026-11-23 in OpenAlex. Suggested: Control and Navigation. Why: matched learning, millirobots (keyword rules)

### Swarms and Multi-Robot Control

- [Deep Neural Network-Based Control of Microswarms for Long-Term Locomotion](https://doi.org/10.1109/aim65483.2026.11658232) - AIM 2026.
  - Found 2026-11-23 in OpenAlex. Suggested: Swarms and Multi-Robot Control. Why: matched deep neural, microswarms, magnet (keyword rules)
- [Deep Reinforcement Learning-Driven Nanobot Collectives for Micro-Thrombus Localization and Cardiovascular Flow Optimization](https://doi.org/10.1109/gseact68539.2026.11620180) - GSEACT 2026.
  - Found 2026-11-23 in OpenAlex. Suggested: Swarms and Multi-Robot Control. Why: matched learning, nanobot, magnet (keyword rules)
- [Rule-Driven Self-Organized Swarm Delivery to Evolutionary Nanorobots](https://doi.org/10.1109/nsens71111.2026.11663130) - NSENS 2026.
  - Found 2026-11-23 in OpenAlex. Suggested: Swarms and Multi-Robot Control. Why: matched evolutionary, nanorobots (keyword rules)

### Modeling and System Identification

- [A deep energy method for hard-magnetic soft materials](https://doi.org/10.1007/s10409-026-60469-x) - Acta Mechanica Sinica 2026.11.
  - Found 2026-11-23 in OpenAlex. Suggested: Modeling and System Identification. Why: physics-informed deep energy method for hard-magnetic soft materials; materials model rather than a robot (manual review)

### Design and Fabrication

- [Evolving Nanorobots in Nonstationary Biological Landscapes](https://doi.org/10.1109/nsens71111.2026.11663124) - NSENS 2026.
  - Found 2026-11-23 in OpenAlex. Suggested: Design and Fabrication. Why: matched evolutionary, nanorobots (keyword rules)

### Foundation Models and LLMs

- [LLM-Guided Co-Evolution of Nanorobot Morphology and Control for Tumor Targeting](https://doi.org/10.1109/nano67986.2026.11667610) - NANO 2026.
  - Found 2026-11-23 in OpenAlex. Suggested: Foundation Models and LLMs. Why: matched llm, nanorobot (keyword rules)

### Related: Learning for Other Microswimmers and Active Matter

- [Model inference from fluid flow in continuum theories of active matter](https://doi.org/10.1103/st8r-wrrd) - Physical Review E 2026.11. [arXiv](https://arxiv.org/abs/2607.20100)
  - Found 2026-11-23 in OpenAlex. Suggested: Related: Learning for Other Microswimmers and Active Matter › Simulated microswimmers and active matter. Why: learns continuum models of active matter from flow data; tangential to microswimmer control (manual review)

### Related: Magnetic Continuum Robots, Catheters and Capsules

- [Oil-chamber profile optimization design for drag reduction in an underactuated capsule robot with a suspended rotor](https://doi.org/10.1088/1742-6596/3337/1/012034) - Journal of Physics: Conference Series 2026.10.
  - Found 2026-11-23 in OpenAlex. Suggested: Related: Magnetic Continuum Robots, Catheters and Capsules. Why: matched genetic algorithm, capsule robot, magnet (keyword rules)
- [Autonomous Magnetic Control of Capsule Robots with Deep Reinforcement Learning](https://doi.org/10.1109/fasta70174.2026.11548713) - FASTA 2026.
  - Found 2026-11-23 in OpenAlex. Suggested: Related: Magnetic Continuum Robots, Catheters and Capsules. Why: matched learning, capsule robots, magnet (keyword rules)
- [A FEM Framework for Simulating Magnetic Soft Continuum Robots via Consistent Torque-to-Nodal Force Mapping](https://doi.org/10.1109/marss70227.2026.11655676) - MARSS 2026.
  - Found 2026-11-23 in OpenAlex. Suggested: Related: Magnetic Continuum Robots, Catheters and Capsules. Why: matched learning, small-scale robot, magnet (keyword rules)
- [Soft-Magnetic-Elastomer-Based Shape Sensing of Continuum Robots Using Magnetic Imaging and Convolutional Neural Network](https://doi.org/10.1109/icmtim69588.2026.11526223) - ICMTIM 2026.
  - Found 2026-11-23 in OpenAlex. Suggested: Related: Magnetic Continuum Robots, Catheters and Capsules. Why: matched convolutional, continuum robots, magnet (keyword rules)
- [Uncertainty-Resilient Fuzzy Reinforcement Learning for Autonomous Endovascular Navigation of Magnetic Vascular Catheter Robots](https://doi.org/10.1109/cis-ram71614.2026.11668487) - CIS 2026.
  - Found 2026-11-23 in OpenAlex. Suggested: Related: Magnetic Continuum Robots, Catheters and Capsules. Why: matched learning, magnetic actuation, magnet (keyword rules)
- [Enabling the future of colonoscopy with intelligent and autonomous magnetic manipulation](https://doi.org/10.1038/s42256-020-00231-9) - Nature Machine Intelligence 2020.10.
  - Found 2026-11-23 in review. Suggested: Related: Magnetic Continuum Robots, Catheters and Capsules. Why: autonomous magnetic colonoscopy; no abstract available, check whether a learning method is used (manual review)
