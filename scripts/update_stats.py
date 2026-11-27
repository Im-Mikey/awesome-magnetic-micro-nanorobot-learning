"""Refresh the paper counts, the charts and the numbers table from README.md.

Run from the repository root after adding papers:

    python scripts/update_stats.py

It counts every list entry in README.md (lines such as "- [Title](link) - Venue YYYY.MM. ...",
with 🌟 at the end when the code is public), splits them into core sections and "Related:" sections, then rewrites:
- the "> N core papers + ..." line and the per-section counts in Contents;
- assets/paper_growth*.svg, papers per year;
- assets/learning_methods*.svg, papers per year by learning method;
- the table between the <!-- stats-table:start --> and <!-- stats-table:end --> markers.

Learning methods come from assets/methods.json, which the daily update fills in from titles and
abstracts. A paper with no entry there is classified from its title alone.
The "last checked" badge (assets/last_checked.svg) is not touched here: the daily update redraws it on
every run with write_checked_badge().
Only the Python standard library is needed.
"""
import datetime
import json
import math
import pathlib
import re
from collections import Counter, defaultdict
from xml.sax.saxutils import escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
ASSETS = ROOT / "assets"
METHODS_FILE = ASSETS / "methods.json"

ENTRY = re.compile(r"^- \[[^\]]+\]\(\S+?\) - .+? (\d{4})(?:\.\d{2})?\.( .*)?$")
STATS = re.compile(r"^> \d+ core papers \+ \d+ related papers, \d+ with open-source code(?: \(\d+%\))?\. "
                   r"Last updated: .*$")
TOC = re.compile(r"^(?P<head>- \[(?P<name>[^\]]+)\]\(#[^)]+\) )\(\d+\)$")
# The "last checked" badge next to the title, in the flat shields.io style (shields.io is CC0). It is
# drawn here and kept in assets/ because GitHub's image proxy often fails to fetch new images from
# badge services. Verdana digits all have the same width, so every date fits this layout.
CHECKED_BADGE = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="154" height="20" role="img" aria-label="last checked: {date}">'
    '<title>last checked: {date}</title><filter id="blur"><feGaussianBlur stdDeviation="16"/></filter>'
    '<linearGradient id="s" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/>'
    '<stop offset="1" stop-opacity=".1"/></linearGradient><clipPath id="r">'
    '<rect width="154" height="20" rx="3"/></clipPath><g clip-path="url(#r)">'
    '<rect width="79" height="20" fill="#555"/><rect x="79" width="75" height="20" fill="#007ec6"/>'
    '<rect width="154" height="20" fill="url(#s)"/></g>'
    '<g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" '
    'text-rendering="geometricPrecision" font-size="110">'
    '<g transform="scale(.1)"><g aria-hidden="true" fill="#010101">'
    '<text x="405" y="150" fill-opacity=".8" filter="url(#blur)" textLength="690">last checked</text>'
    '<text x="405" y="150" fill-opacity=".3" textLength="690">last checked</text></g>'
    '<text x="405" y="140" textLength="690">last checked</text></g><g transform="scale(.1)">'
    '<g aria-hidden="true" fill="#010101">'
    '<text x="1155" y="150" fill-opacity=".8" filter="url(#blur)" textLength="650">{date}</text>'
    '<text x="1155" y="150" fill-opacity=".3" textLength="650">{date}</text></g>'
    '<text x="1155" y="140" textLength="650">{date}</text></g></g></svg>\n'
)
TABLE_START, TABLE_END = "<!-- stats-table:start -->", "<!-- stats-table:end -->"
ID_RE = re.compile(r"doi\.org/(10\.\d{4,9}/\S+?)(?=\)(?:[,\s]|$)|[\s\]]|$)|arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})", re.I)
TITLE_RE = re.compile(r"^- \[([^\]]+)\]\(")  # the title is the link text

THEMES = {
    "light": dict(surface="#fcfcfb", primary="#0b0b0b", secondary="#52514e", muted="#898781",
                  grid="#e1e0d9", baseline="#c3c2b7", s1="#2a78d6", s2="#eb6834", s3="#1baf7a", s4="#eda100"),
    "dark": dict(surface="#1a1a19", primary="#f0efec", secondary="#c3c2b7", muted="#898781",
                 grid="#2c2c2a", baseline="#383835", s1="#3987e5", s2="#d95926", s3="#199e70", s4="#c98500"),
}
FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"


# --------------------------------------------------------------------------- learning methods

def rx(pattern):
    return re.compile(pattern, re.I)


# checked in this order, first match wins; the title is tried before title + abstract
METHODS = (
    ("fm", rx(r"language models?|\bllms?\b|\bgpt|vision[- ]language|\bvlms?\b|\bvlas?\b|foundation models?|chatgpt"
              r"|natural language|multimodal large")),
    ("rl", rx(r"reinforcement|\b(?:drl|marl)\b|\brl\b|q-learning|deep q|\b(?:dqn|ddpg|ppo|sac|td3|maddpg|mappo|a2c|a3c)\b"
              r"|actor-critic|policy (?:gradient|learning|optimi[sz])|imitation learning|behaviou?r(?:al)? cloning"
              r"|from demonstrations?|(?:adaptive|approximate) dynamic programming|\breward")),
    ("dl", rx(r"deep (?:learning|neural|networks?|convolution\w*|energy)|neural (?:networks?|nets?|operators?|control)"
              r"|\bcnns?\b|convolutional|\byolo|u-?net\b|transformer|graph neural|\bgnns?\b|graph attention|\blstm"
              r"|recurrent neural|autoencoder|diffusion (?:models?|polic\w*)|\bpinns?\b|physics-informed neural"
              r"|\bgans?\b|generative adversarial")),
)
STACK = ("rl", "dl", "fm", "other")  # drawing and legend order, which is also colour slot order
SHORT_LABEL = {"rl": "RL & imitation", "dl": "Deep learning", "fm": "Foundation models", "other": "Other ML"}
LONG_LABEL = {"rl": "RL & imitation learning", "dl": "Deep learning", "fm": "Language & foundation models",
              "other": "Other ML & optimisation"}


def classify_method(title, abstract=""):
    """Main learning method of a paper: 'fm', 'rl', 'dl' or 'other'. Keyword rules, so approximate."""
    for text in (title, f"{title} {abstract}" if abstract else ""):
        for key, pattern in METHODS:
            if text and pattern.search(text):
                return key
    return "other"


def load_methods():
    try:
        return json.loads(METHODS_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_methods(methods):
    ASSETS.mkdir(exist_ok=True)
    METHODS_FILE.write_text(json.dumps(dict(sorted(methods.items())), indent=0) + "\n", encoding="utf-8",
                            newline="\n")


def entry_keys(line):
    return ["doi:" + d.lower() if d else "arxiv:" + a for d, a in ID_RE.findall(line)]


# --------------------------------------------------------------------------- counting

def parse(lines, methods=None):
    """Per-year counts of core and related papers and of learning methods, plus the number with code."""
    methods = methods or {}
    core, rel, by_method, n_code = Counter(), Counter(), defaultdict(Counter), 0
    related = False
    for line in lines:
        if line.startswith("## "):
            related = line[3:].startswith("Related")
            continue
        m = ENTRY.match(line)
        if not m:
            continue
        year = int(m.group(1))
        (rel if related else core)[year] += 1
        n_code += (m.group(2) or "").rstrip().endswith("🌟")
        method = next((methods[k] for k in entry_keys(line) if methods.get(k) in SHORT_LABEL), None)
        if method is None:
            t = TITLE_RE.match(line)
            method = classify_method(t.group(1) if t else line)
        by_method[year][method] += 1
    return core, rel, by_method, n_code


def section_counts(lines):
    counts, current = {}, None
    for line in lines:
        if line.startswith("## "):
            current = line[3:].strip()
            counts.setdefault(current, 0)
        elif current and ENTRY.match(line):
            counts[current] += 1
    return counts


# --------------------------------------------------------------------------- charts

def nice_step(maxv):
    for step in (1, 2, 5, 10, 20, 25, 50, 100):
        if maxv / step <= 6:
            return step
    return 200


def col_path(x, y_top, w, h, r, round_top):
    if h <= 0:
        return ""
    r = min(r, h, w / 2) if round_top else 0
    x2, yb = x + w, y_top + h
    if r == 0:
        return f"M{x:.1f},{yb:.1f}V{y_top:.1f}H{x2:.1f}V{yb:.1f}Z"
    return (f"M{x:.1f},{yb:.1f}V{y_top + r:.1f}Q{x:.1f},{y_top:.1f} {x + r:.1f},{y_top:.1f}"
            f"H{x2 - r:.1f}Q{x2:.1f},{y_top:.1f} {x2:.1f},{y_top + r:.1f}V{yb:.1f}Z")


def stacked_chart(series, years, theme, title, aria, note, footnote="", right=16, direct_labels=False):
    """Stacked columns per year. series: [(label, colour slot, {year: count})] bottom to top."""
    t = THEMES[theme]
    W, H = 720, 316 if footnote else 300
    left, top, bottom = 44, 64, 50 if footnote else 36
    pw, ph = W - left - right, H - top - bottom
    totals = [sum(s[2].get(y, 0) for s in series) for y in years]
    step = nice_step(max(totals))
    ymax = step * math.ceil(max(totals) / step)
    slot = pw / len(years)
    bw = min(24.0, slot * 0.6)

    def sy(v):
        return top + ph - v / ymax * ph

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'role="img" aria-label="{escape(aria)}">',
         f'<rect width="{W}" height="{H}" rx="8" fill="{t["surface"]}"/>',
         f'<text x="{left}" y="26" font-family="{FONT}" font-size="15" font-weight="600" '
         f'fill="{t["primary"]}">{escape(title)}</text>']
    lx = left
    for label, colour, counts in series:
        text = f"{label} ({sum(counts.values())})"
        o.append(f'<rect x="{lx}" y="38" width="10" height="10" rx="2" fill="{t[colour]}"/>')
        o.append(f'<text x="{lx + 16}" y="47" font-family="{FONT}" font-size="12" '
                 f'fill="{t["secondary"]}">{escape(text)}</text>')
        lx += 16 + len(text) * 6.2 + 18
    v = 0
    while v <= ymax:
        y = sy(v)
        if v > 0:
            o.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + pw}" y2="{y:.1f}" '
                     f'stroke="{t["grid"]}" stroke-width="1"/>')
        o.append(f'<text x="{left - 8}" y="{y + 4:.1f}" text-anchor="end" font-family="{FONT}" '
                 f'font-size="11" fill="{t["muted"]}">{v}</text>')
        v += step
    peak = max(range(len(years)), key=lambda i: (totals[i], years[i]))
    last_segments = []
    for i, yr in enumerate(years):
        cx = left + slot * i + slot / 2
        x = cx - bw / 2
        nonzero = [(label, colour, counts.get(yr, 0)) for label, colour, counts in series if counts.get(yr, 0)]
        base = 0
        for j, (label, colour, c) in enumerate(nonzero):
            gap = 2 if j else 0  # 2px surface gap between stacked segments
            h = max(c / ymax * ph - gap, 1.0)
            o.append(f'<path d="{col_path(x, sy(base + c), bw, h, 4, j == len(nonzero) - 1)}" fill="{t[colour]}"/>')
            if i == len(years) - 1:
                last_segments.append((label, colour, c, (sy(base) + sy(base + c)) / 2))
            base += c
        label = f"{yr}*" if (note and yr == years[-1]) else str(yr)
        o.append(f'<text x="{cx:.1f}" y="{top + ph + 18}" text-anchor="middle" font-family="{FONT}" '
                 f'font-size="11" fill="{t["muted"]}">{label}</text>')
        if i in (peak, len(years) - 1) and totals[i]:
            o.append(f'<text x="{cx:.1f}" y="{sy(totals[i]) - 6:.1f}" text-anchor="middle" '
                     f'font-family="{FONT}" font-size="11" font-weight="600" '
                     f'fill="{t["primary"]}">{totals[i]}</text>')
    if direct_labels and last_segments:
        # name each segment of the newest column at its right, nudged apart so labels never overlap
        ys = [s[3] for s in last_segments]
        for k in range(1, len(ys)):
            ys[k] = min(ys[k], ys[k - 1] - 14)
        shift = max(0.0, top + 8 - min(ys))
        ys = [y + shift for y in ys]
        lx = left + slot * (len(years) - 1) + slot / 2 + bw / 2 + 10
        for (label, colour, c, _), y in zip(last_segments, ys):
            o.append(f'<rect x="{lx:.1f}" y="{y - 4:.1f}" width="8" height="8" rx="2" fill="{t[colour]}"/>')
            o.append(f'<text x="{lx + 12:.1f}" y="{y + 4:.1f}" font-family="{FONT}" font-size="11" '
                     f'fill="{t["secondary"]}">{escape(label)} {c}</text>')
    o.append(f'<line x1="{left}" y1="{top + ph}" x2="{left + pw}" y2="{top + ph}" '
             f'stroke="{t["baseline"]}" stroke-width="1"/>')
    if note:
        o.append(f'<text x="{W - 16}" y="26" text-anchor="end" font-family="{FONT}" font-size="11" '
                 f'fill="{t["muted"]}">* {note}</text>')
    if footnote:
        o.append(f'<text x="{left}" y="{H - 10}" font-family="{FONT}" font-size="10.5" '
                 f'fill="{t["muted"]}">{escape(footnote)}</text>')
    o.append("</svg>")
    return "\n".join(o) + "\n"


def stats_table(core, rel, by_method, years, note):
    header = ["Year", "Core", "Related"] + [LONG_LABEL[k] for k in STACK]
    body = [[f"{y}{'*' if note and y == years[-1] else ''}", str(core[y]), str(rel[y])]
            + [str(by_method[y][k]) for k in STACK] for y in reversed(years)]
    body.append(["**Total**", f"**{sum(core.values())}**", f"**{sum(rel.values())}**"]
                + [f"**{sum(by_method[y][k] for y in years)}**" for k in STACK])
    # pad every cell so the pipes line up, as remark-lint (used by awesome-lint) requires
    widths = [max(len(row[i]) for row in [header] + body) for i in range(len(header))]

    def fmt(row):
        return "| " + " | ".join(cell.ljust(w) if i == 0 else cell.rjust(w)
                                 for i, (cell, w) in enumerate(zip(row, widths))) + " |"

    rule = "| " + " | ".join("-" * w if i == 0 else "-" * (w - 1) + ":" for i, w in enumerate(widths)) + " |"
    head = [fmt(header), rule]
    rows = [fmt(r) for r in body[:-1]]
    total = fmt(body[-1])
    foot = ((f"\\* {note}. " if note else "")
            + "Learning methods are assigned from titles and abstracts by keyword rules, so treat them as approximate.")
    return [""] + head + rows + [total, "", foot, ""]


def write_checked_badge(day):
    """Redraw assets/last_checked.svg with the day of the last search for new papers. The daily update calls
    this on every run, also when it finds nothing new, so the README shows that the bot is still running."""
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "last_checked.svg").write_text(CHECKED_BADGE.replace("{date}", f"{day:%Y-%m-%d}"),
                                             encoding="utf-8", newline="\n")


def main():
    lines = README.read_text(encoding="utf-8").splitlines()
    core, rel, by_method, n_code = parse(lines, load_methods())
    today = datetime.date.today()
    years = list(range(min(core | rel), max(core | rel) + 1))
    note = f"{today.year} counts run to {today:%B}" if years[-1] == today.year else ""

    ASSETS.mkdir(exist_ok=True)
    for theme, suffix in (("light", ""), ("dark", "_dark")):
        growth = stacked_chart(
            [("Magnetic micro/nanorobot learning", "s1", core), ("Related work", "s2", rel)], years, theme,
            "Papers in this list by publication year",
            "Papers in the list per publication year, core versus related", note)
        (ASSETS / f"paper_growth{suffix}.svg").write_text(growth, encoding="utf-8", newline="\n")
        methods = stacked_chart(
            [(SHORT_LABEL[k], f"s{i}", {y: by_method[y][k] for y in years}) for i, k in enumerate(STACK, 1)],
            years, theme, "Papers by learning method",
            "Papers in the list per publication year, split by main learning method", note,
            footnote="Methods are assigned from titles and abstracts by keyword rules, so counts are approximate.",
            right=150, direct_labels=True)
        (ASSETS / f"learning_methods{suffix}.svg").write_text(methods, encoding="utf-8", newline="\n")

    total = sum(core.values()) + sum(rel.values())
    stats = (f"> {sum(core.values())} core papers + {sum(rel.values())} related papers, {n_code} with "
             f"open-source code ({round(100 * n_code / total) if total else 0}%). Last updated: {today:%Y-%m-%d}.")
    counts = section_counts(lines)

    def refresh(line):
        if STATS.match(line):
            return stats
        m = TOC.match(line)
        return f"{m['head']}({counts[m['name']]})" if m and m["name"] in counts else line

    out = [refresh(line) for line in lines]
    if TABLE_START in out and TABLE_END in out and out.index(TABLE_START) < out.index(TABLE_END):
        s, e = out.index(TABLE_START), out.index(TABLE_END)
        out[s + 1:e] = stats_table(core, rel, by_method, years, note)
    README.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print(stats)


if __name__ == "__main__":
    main()
