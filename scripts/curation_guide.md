# Curation guide

These rules decide whether a paper belongs in the list and where it goes. The daily update sends this file to the language model that judges new papers, so keep it short and exact.

## In scope: both must hold

1. **Small magnetic robots.** Magnetically actuated micro- or nanorobots, magnetic microswimmers, microrobot swarms, magnetic nanoparticle collectives, or soft magnetic millirobots up to a few millimetres.
2. **A real learning component** that carries the contribution. This includes:
   - reinforcement learning and imitation learning;
   - deep learning and other machine learning;
   - Bayesian optimisation and Gaussian processes;
   - evolutionary or genetic optimisation of designs or controllers;
   - learned or data-driven models, and learning-based control;
   - language, vision-language and other foundation models.

Simulation-only work counts. So do simulation papers about generic microrobots whose actuation is not stated; they go in the core sections.

## Related sections

These are in scope too, but they are listed at the end of the README.

- **Related: Learning for Other Microswimmers and Active Matter** covers learning for micro/nanorobots driven by light or optical tweezers, sound, chemistry or living cells (biohybrid), and for simulated microswimmers and active matter. Pick the matching subgroup.
- **Related: Magnetic Continuum Robots, Catheters and Capsules** covers learning for magnetically steered catheters, guidewires, continuum robots, needles, tentacles and capsule endoscopes. The learning has to serve the robot itself: control, planning, localisation, sensing, modelling or design.

## Out of scope

- Machine learning that appears only as motivation or future work.
- Magnetic nanoparticles used for imaging, hyperthermia or drug release with no robotic motion control.
- Learning for a downstream task in which the robot plays no part, such as spotting lesions in capsule endoscopy images.
- Catheters, continuum robots and surgical robots that are not magnetic.
- Magnetic robots of centimetre scale or larger, apart from the continuum and capsule robots above.
- Corrections, errata, retraction notices, editorials, cover images, and dataset or software records with no paper.
- Retracted papers.

## Decision

- **include**: the paper clearly meets the rules above.
- **maybe**: the paper might be in scope, but the title and abstract are not enough to decide. Typical cases are a missing abstract, unclear actuation, or an unclear role for learning. A maintainer reviews these papers.
- **exclude**: the paper is out of scope.

## Section

Choose the one section that matches the paper's main contribution. Two sections have their own rules:

- **Surveys and Perspectives** takes reviews whose main subject is learning, AI or autonomy for micro/nanorobots or microswimmers, magnetic or not. A broad review that mentions AI only in passing is out of scope.
- **Hardware and Software Platforms** takes open magnetic actuation setups built to collect data or run learning experiments. Such a setup may be listed even when its paper has no learning component.
