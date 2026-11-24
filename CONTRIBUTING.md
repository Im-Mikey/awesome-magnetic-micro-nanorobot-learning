# Contributing

Thanks for helping grow this list! Pull requests and issues are both welcome.

## What belongs here

The full rules are in [scripts/curation_guide.md](scripts/curation_guide.md). The daily bot's language model judges papers against the same file.

In short, a paper fits when **both** of these hold:

1. **Small magnetic robots.** The paper is about one of these:
   - magnetically actuated micro- or nanorobots;
   - magnetic microswimmers;
   - microrobot swarms or magnetic nanoparticle collectives;
   - soft magnetic millirobots up to a few millimetres.

   Simulation papers about generic microrobots whose actuation is not stated also count.
2. **A real learning component.** For example:
   - reinforcement or imitation learning;
   - deep learning;
   - Bayesian optimisation or Gaussian processes;
   - evolutionary optimisation;
   - learned or data-driven models, or learning-based control;
   - language models and other foundation models.

Closely related work goes in the two **Related** sections at the end:

- learning for micro/nanorobots driven by light, sound, chemistry or living cells, and for simulated microswimmers and active matter;
- learning for magnetic continuum robots, catheters, guidewires, needles, tentacles and capsule robots.

Papers with physical (real robot) experiments are preferred, but simulation-only work is welcome.

## Entry format

Add one line per paper under the best-fitting section. Keep each section ordered **newest first**.

```markdown
- [Paper Title](https://doi.org/xx.xxxx/xxxxx) - Venue YYYY.MM. [arXiv](https://arxiv.org/abs/xxxx.xxxxx), [website](https://...), [code](https://github.com/...) 🌟
```

This is the style [awesome-lint](https://github.com/sindresorhus/awesome-lint) checks. Run `npx awesome-lint README.md` to test a change.

- **Link** the paper title to its DOI if the paper is published.
  - For preprints, link the arXiv page and use the label `arXiv YYYY.MM`.
  - If a paper is accepted at a venue but only the preprint is online, link the arXiv page and use the venue label, for example `- [Paper Title](https://arxiv.org/abs/...) - IROS 2025.`
- **Venue and date** follow the title after ` - ` and end with a full stop.
- **Date** depends on the kind of paper:
  - Journals: `YYYY.MM` of first online publication, such as early access or "available online". If that date is unknown, use the issue month.
  - Conferences: the year only.
  - Preprints: the month of the first version.
- **Extra links** come after that full stop, separated by commas. Use labels from this set: `[arXiv]`, `[bioRxiv]`, `[website]`, `[dataset]` and `[code]`.
- **Code**: when the official code is public, add a `[code]` link and end the line with 🌟.
- **Venue names**: use the short forms already in the list, such as `IEEE RA-L`, `IEEE T-RO`, `ICRA`, `IROS`, `Science Robotics` or `Nature Machine Intelligence`.
- **Duplicates**: list each paper only once, in the section that matches its main contribution.

## Before you open a PR

- Check that every link opens and points to the right paper.
- Use the paper's exact title.
- Use one PR per topic or batch of related papers, so review stays easy.

## For maintainers

After adding entries by hand, refresh the paper counts, the numbers in Contents, the two charts, the numbers table and the date on the "last updated" badge:

```bash
python scripts/update_stats.py
```

This script, and the daily update script described below, need only the Python standard library.

After changing either script, run the tests. They work offline on a temporary copy of the repository, so they never change your files. Add `-v` to list every check.

```bash
python scripts/test_scripts.py
```

### Daily updates

[`.github/workflows/daily-update.yml`](.github/workflows/daily-update.yml) runs [`scripts/daily_update.py`](scripts/daily_update.py) every day at 23:17 UTC. Each run does the following:

1. **Search.** It looks for recent papers in arXiv, OpenAlex, Crossref, PubMed and Semantic Scholar. The default look-back is 10 days. It is longer for indexes that pick up papers late: 45 days for OpenAlex, and 240 days for conference papers, whose DOIs appear months after the meeting. OpenAlex and Crossref index journals and conferences from all major publishers, so no publisher needs a search of its own.
2. **Filter.** It drops papers that are already listed, queued or judged. It also drops papers that fail a keyword filter, which needs both a small robot or magnetic actuation system and a learning method. On the papers already in this list, the filter keeps about 92%. The filter is looser when a working language model is set up, because the model weeds out the extra noise.
3. **Judge.** It judges the rest against [`scripts/curation_guide.md`](scripts/curation_guide.md), one paper per request.
   - A paper goes straight into README only if the model accepts it and the strict keyword filter agrees. Otherwise it waits in NEW_PAPERS.md.
   - After any change, the counts, the two charts and the numbers table are refreshed.
4. **Update preprints.** When a listed arXiv or bioRxiv preprint gets a journal or conference version with the same title, the entry is switched to that version. A close match that is not identical waits in NEW_PAPERS.md instead.
5. **Check, log and push.** Before it commits, `python scripts/daily_update.py check` confirms that every entry:
   - can be read;
   - is in newest-first order;
   - is listed only once;
   - is not dated in the future.

   If the check fails, the run stops without committing. Otherwise every judged paper is logged in [`scripts/processed_ids.txt`](scripts/processed_ids.txt) and the result is pushed.

It costs nothing. GitHub Actions is free for public repositories, and every data source is free.

**Setup.** The workflow runs without any setup. Two optional repository secrets make it work better. Add them under Settings → Secrets and variables → Actions.

| Secret | What it does | Where to get it |
| --- | --- | --- |
| `OPENALEX_API_KEY` | Gives OpenAlex a free daily budget of its own. Without a key, the budget is shared with everyone on the same IP address, which includes other GitHub runners. Recommended. | Free at [openalex.org/settings/api](https://openalex.org/settings/api) |
| `LLM_API_KEY` | Lets a language model judge each candidate, so clear matches go straight into the list. Without it, keyword rules pick the candidates and all of them wait in [NEW_PAPERS.md](NEW_PAPERS.md). | A free key from [Groq](https://console.groq.com/keys) or [Google AI Studio](https://aistudio.google.com/apikey). OpenRouter keys work too, and only its `:free` models are used. |

The provider is detected from the key, and a model is picked automatically. To use another OpenAI-compatible API or a specific model, set the repository variables `LLM_BASE_URL` and `LLM_MODEL`.

`S2_API_KEY` (Semantic Scholar) and `NCBI_API_KEY` (PubMed) are optional as well.

Free tiers change over time. If the model calls fail, the run still finishes, the papers wait in NEW_PAPERS.md, and the run page explains what went wrong.

**Reviewing.** Check [NEW_PAPERS.md](NEW_PAPERS.md) now and then.

- To accept a paper, move its line into the matching section of README.md and run `python scripts/update_stats.py`.
- To reject a paper, delete its line.
- To block a paper for good, add it to `scripts/processed_ids.txt`. The header at the top of that file shows the format.

**Running by hand.** On GitHub, open Actions → Daily paper update → Run workflow. Enter a larger "days" value to look further back, for example after a break. Locally:

```bash
python scripts/daily_update.py run --dry-run    # print the report, change nothing
python scripts/daily_update.py run --days 60
```

GitHub pauses scheduled workflows in a public repository that has had no activity for 60 days. If that happens, re-enable the workflow in the Actions tab.
