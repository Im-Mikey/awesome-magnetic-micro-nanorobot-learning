"""Offline tests for the two update scripts, daily_update.py and update_stats.py.

Run them after changing either script:

    python scripts/test_scripts.py

The tests work on a temporary copy of the repository, so README.md and the other files here are never
changed. They need only the Python standard library and no network: a small local server stands in
for the language model, and any other web request fails the run. Add -v to list every check.
"""
import contextlib
import importlib.util
import io
import json
import pathlib
import shutil
import sys
import tempfile
import threading
import time
import traceback
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

REPO = pathlib.Path(__file__).resolve().parent.parent
# A made-up preprint. The tests list it first, then upgrade it to a published version.
FIX_ARXIV = "2601.99999"
FIX_TITLE = "Learning to Steer Magnetic Microrobots Through a Test Channel"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cand(**fields):
    """A candidate paper shaped like the ones the fetch step builds."""
    paper = dict(title="", abstract="", doi="", arxiv="", pmid="", venue="", venue_type="journal", date="2026-11-01",
                 event="", code="", website="", sources=["test"])
    paper.update(fields)
    return paper


class FakeModel:
    """A local stand-in for an OpenAI-compatible API. Chat requests always get the same status and results."""

    def __init__(self, status, results=()):
        self.calls = 0
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):  # list models
                self.reply(200, {"data": [{"id": "m"}]})

            def do_POST(self):  # chat completion
                fake.calls += 1
                self.reply(status, {"choices": [{"message": {"content": json.dumps({"results": list(results)})}}]})

            def reply(self, code, body):
                data = json.dumps(body).encode()
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *args):
                pass

        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}/v1"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.server.shutdown()
        self.server.server_close()


def run_checks(check):
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="awesome-list-tests-"))
    try:
        copy = tmp / "repo"
        shutil.copytree(REPO, copy, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        du = load("daily_update", copy / "scripts" / "daily_update.py")
        us = load("update_stats", copy / "scripts" / "update_stats.py")
        checks(du, us, copy, check)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def checks(du, us, copy, check):
    # --- a new preprint is listed in its section; later checks upgrade this entry
    fixture = cand(title=FIX_TITLE, arxiv=FIX_ARXIV, venue="arXiv", venue_type="preprint", date="2026-01-15",
                   kind="new", decision="include", section="Control and Navigation")
    done = du.insert({"candidates": [fixture]})
    listed = next((e for e in du.list_entries(du.README) if FIX_ARXIV in e["url"]), None)
    check("insert: a new preprint is listed in its section", len(done["added"]) == 1 and listed is not None)
    if listed is None:
        return  # every later check builds on this entry
    arx, ltitle = FIX_ARXIV, FIX_TITLE
    methods_file = copy / "assets" / "methods.json"
    log0, readme0, queue0, methods0 = (p.read_text(encoding="utf-8")
                                       for p in (du.PROCESSED, du.README, du.QUEUE, methods_file))

    def reset():
        for path, text in ((du.PROCESSED, log0), (du.README, readme0), (du.QUEUE, queue0), (methods_file, methods0)):
            path.write_text(text, encoding="utf-8")

    # --- dates: first online, never in the future
    future = [du.TODAY.year + 1, 1, 1]
    check("date: created beats a later issue date",
          du.crossref_date({"created": {"date-parts": [[2023, 3, 27]]}, "issued": {"date-parts": [[2024, 4]]}})
          == "2023-03-27")
    check("date: published-online is used when present",
          du.crossref_date({"published-online": {"date-parts": [[2025, 4, 25]]},
                            "created": {"date-parts": [[2025, 4, 1]]}}) == "2025-04-25")
    check("date: a future issue date falls back to created",
          du.crossref_date({"issued": {"date-parts": [future[:2]]}, "created": {"date-parts": [[2026, 10, 20]]}})
          == "2026-10-20")

    # --- upgrades need agreeing titles; near misses are queued
    c = cand(title="Thermal Conductivity of Ferrofluids in Rotating Magnetic Fields", doi="10.1016/j.jmmm.2026.1",
             arxiv=arx, venue="Journal of Magnetism and Magnetic Materials")
    fresh, ups, poss = du.split_known([c])
    check("upgrade: a shared arXiv ID with an unrelated title is only a possible upgrade", not ups and poss == [c])
    c = cand(title=ltitle, doi="10.1103/test.123", arxiv=arx, venue="Physical Review E")
    fresh, ups, poss = du.split_known([c])
    check("upgrade: a shared arXiv ID with the same title upgrades", ups == [c])
    du.PROCESSED.write_text(log0 + f"2026-11-01\tinclude\tarxiv:{arx}\tx\n", encoding="utf-8")
    fresh, ups, poss = du.split_known([dict(c)])
    check("upgrade: still found after the arXiv ID was logged again", len(ups) == 1)
    reset()
    c = cand(title=ltitle + ": Part II", doi="10.1109/test.77",
             abstract="We use deep reinforcement learning to steer magnetic microrobots.")
    fresh, ups, poss = du.split_known([c])
    check("upgrade: a near-identical title is queued, not applied", not ups and poss == [c])

    # --- the possible-upgrade path ends in the queue
    done = du.insert(du.judge({"candidates": [dict(c, kind="possible", maybe_upgrade_of=listed["line"])]}))
    check("upgrade: a possible upgrade is queued for a person", len(done["queued"]) == 1
          and "may be the published version" in du.QUEUE.read_text(encoding="utf-8"))
    reset()

    # --- an upgrade switches the link, keeps the arXiv link and keeps the learning-method tag
    want = next(t for t in ("fm", "rl", "dl", "other") if t != us.classify_method(ltitle))
    tags = json.loads(methods0)
    tags[f"arxiv:{arx}"] = want
    methods_file.write_text(json.dumps(tags), encoding="utf-8")
    c = cand(title=ltitle, doi="10.1109/test.4242", arxiv=arx, venue_type="conference", date="2026-10-01",
             venue="2026 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)")
    fresh, ups, poss = du.split_known([c])
    done = du.insert(du.judge({"candidates": [dict(u, kind="upgrade") for u in ups]}))
    new = next((e["line"] for e in du.list_entries(du.README) if "10.1109/test.4242" in e["url"]), "")
    check("upgrade: the published version replaces the preprint, arXiv link kept", len(done["upgraded"]) == 1
          and new.startswith(f"- [{ltitle}](https://doi.org/10.1109/test.4242) - IROS 2026.")
          and f"[arXiv](https://arxiv.org/abs/{arx})" in new and listed["line"] not in du.README.read_text(encoding="utf-8"))
    tags = json.loads(methods_file.read_text(encoding="utf-8"))
    check("upgrade: the preprint's learning-method tag is kept",
          tags.get("doi:10.1109/test.4242") == want and tags.get(f"arxiv:{arx}") == want)
    check("upgrade: README is still consistent", du.check_readme() == [])
    reset()

    # --- upgrading a bioRxiv entry keeps the preprint as an extra link
    lines = ["## Control and Navigation", "", "*d*", "",
             "- [Photoacoustic control](https://doi.org/10.1101/2025.08.13.670011) - bioRxiv 2025.08. "
             "[Code](https://github.com/x/y) 🌟", ""]
    c = cand(title="Photoacoustic control", doi="10.1109/MARSS.2024.1", venue="2024 International Conference on "
             "Manipulation, Automation and Robotics at Small Scales (MARSS)", venue_type="conference", date="2024-07-01",
             upgrade_of=lines[4])
    ok = du.upgrade_entry(lines, c)
    new = next(x for x in lines if x.startswith("- "))
    check("upgrade: bioRxiv entry gets the published link first, keeps bioRxiv, code and star", ok
          and new.startswith("- [Photoacoustic control](https://doi.org/10.1109/MARSS.2024.1) - MARSS 2024.")
          and new.endswith("🌟") and "[bioRxiv](https://doi.org/10.1101/2025.08.13.670011)" in new
          and "[Code](https://github.com/x/y)" in new)

    # --- keyword filter: electric motors are not micromotors, deep-learning words are not motors
    for text, hit in (("a convolutional encoder-decoder network", False), ("an autoencoder", False),
                      ("cargo-bearing micromotors", False), ("rotor unbalance of the micromotor", True),
                      ("incremental encoders on the motor shaft", True)):
        check(f"filter: electric-motor rule {'matches' if hit else 'ignores'} '{text}'",
              bool(du.ELECTRIC_MOTOR.search(text)) == hit)
    check("filter: keeps micromotors steered by an encoder-decoder network", du.passes_gate(
        {"title": "Catalytic micromotors navigated by a convolutional encoder-decoder network", "abstract": ""}))
    check("filter: knows microswarms", du.passes_gate(
        {"title": "A Deep Learning-Based Framework for Environment-Adaptive Navigation of Size-Adaptable Microswarms",
         "abstract": ""}))

    # --- hand-written lines in the processed log
    du.PROCESSED.write_text(log0 + "2026-11-24  exclude  10.1234/ABCD.5678  Some blocked paper\n"
                            "2026-11-24 exclude 2601.12345v2 Another blocked paper\n", encoding="utf-8")
    ids, titles = du.load_processed()
    check("log: spaces and an uppercase DOI are accepted", "doi:10.1234/abcd.5678" in ids)
    check("log: a bare arXiv ID with a version is accepted", "arxiv:2601.12345" in ids)
    check("log: a single-space line keeps its full title", du.norm_title("Another blocked paper") in titles)
    reset()

    # --- duplicates found in several sources keep the journal DOI over a preprint DOI
    a = cand(title="Learning magnetic microrobot control in flow", doi="10.21203/rs.3.rs-1", venue_type="preprint",
             venue="Research Square")
    b = cand(title="Learning magnetic microrobot control in flow", doi="10.1038/s41467-026-1",
             venue="Nature Communications")
    merged = du.merge([a, b])
    check("merge: the journal DOI is kept", len(merged) == 1 and merged[0]["doi"] == "10.1038/s41467-026-1")

    # --- entry format, links and code detection
    line = ("- [A Title Here](https://doi.org/10.1109/LRA.2025.1) - IEEE RA-L 2025.01. "
            "[Project Page](https://a.github.io/p), [Code](https://github.com/a/b) 🌟")
    m = du.ENTRY_RE.match(line)
    check("format: title, label and extra links parse", m and m["title"] == "A Title Here"
          and m["label"] == "IEEE RA-L 2025.01"
          and [x["kind"] for x in du.LINK_RE.finditer(m["rest"])] == ["Project Page", "Code"])
    line = "- [Some Title](https://doi.org/10.1016/S0140-6736(20)30183-5) - Lancet 2020.02. [code](https://github.com/a/b) 🌟"
    m = du.ENTRY_RE.match(line)
    check("format: a DOI with parentheses parses", m and m["url"].endswith("30183-5")
          and du.DOI_RE.findall(line) == ["10.1016/S0140-6736(20)30183-5"] and du.date_key(line) == (2020, 2))
    c = cand(title="Deep RL for magnetic microrobots", doi="10.1109/LRA.2026.9", venue="IEEE Robotics and Automation Letters",
             date="2026-03-02", arxiv="2601.00001", code="https://github.com/a/b")
    check("format: make_line writes the awesome-lint style", du.make_line(c) ==
          "- [Deep RL for magnetic microrobots](https://doi.org/10.1109/LRA.2026.9) - IEEE RA-L 2026.03. "
          "[arXiv](https://arxiv.org/abs/2601.00001), [code](https://github.com/a/b) 🌟")
    check("code: a cited library without a cue is ignored",
          du.code_link("We train with stable-baselines3 (https://github.com/DLR-RM/stable-baselines3).") == "")
    check("code: 'code is available at' counts",
          du.code_link("Code is available at https://github.com/lab/magbot.") == "https://github.com/lab/magbot")
    check("website: link shorteners are refused", du.website_link("Project page: https://bit.ly/abc", author_text=True) == "")

    # --- rewriting the queue keeps a maintainer's own notes
    du.QUEUE.write_text(queue0.rstrip() + "\n\n### Control and Navigation\n\nNote to self: ask the authors about code.\n",
                        encoding="utf-8")
    du.write_queue([], du.readme_structure(readme0.splitlines()))
    check("queue: unrecognised lines are kept", "Note to self: ask the authors about code."
          in du.QUEUE.read_text(encoding="utf-8"))
    reset()

    # --- README check
    check("check: the README passes", du.check_readme() == [])
    label = du.ENTRY_RE.match(listed["line"])["label"]
    bad_line = listed["line"].replace(label, label.split()[0] + " 2099.01", 1)
    du.README.write_text(readme0.replace(listed["line"], bad_line), encoding="utf-8")
    check("check: a future date is caught", any("future" in p for p in du.check_readme()))
    reset()

    # --- language model: a failing API is asked once only, and auto-include needs the strict filter
    papers = [cand(title=f"Deep reinforcement learning for magnetic microrobots {i}", arxiv=f"2611.0000{i}")
              for i in range(4)]
    with FakeModel(500) as fake:
        data = du.judge({"candidates": papers}, du.LLM("k", fake.url, "m"))
    check("model failure: asked once (two tries), then stopped", fake.calls == 2)
    check("model failure: the papers fall back to the queue", all(p["decision"] == "maybe" for p in data["candidates"]))
    loose = cand(title="Smart nanorobots for precise therapy", arxiv="2611.11111",
                 abstract="An overview of intelligent nanorobots.")
    strict = cand(title="Deep reinforcement learning for magnetic microrobot navigation", arxiv="2611.22222")
    accept = [{"id": "c1", "decision": "include", "section": "Control and Navigation", "subgroup": "", "reason": "ok"}]
    with FakeModel(200, accept) as fake:
        du.judge({"candidates": [loose, strict]}, du.LLM("k", fake.url, "m"))
    check("model include: a loose keyword match still waits for review", loose["decision"] == "maybe")
    check("model include: a strict keyword match goes straight in", strict["decision"] == "include")

    # --- adding a paper records its learning method and redraws the charts
    done = du.insert({"candidates": [dict(strict, section="Control and Navigation")]})
    tags = json.loads(methods_file.read_text(encoding="utf-8"))
    check("insert: the learning-method tag is recorded", len(done["added"]) == 1 and tags.get("arxiv:2611.22222") == "rl")
    check("insert: charts and numbers table are redrawn", (copy / "assets" / "learning_methods.svg").exists()
          and "| **Total** |" in du.README.read_text(encoding="utf-8"))
    check("insert: README is still consistent", du.check_readme() == [])
    reset()

    # --- learning-method classifier
    for title, method in (("Training microrobots to swim by a large language model", "fm"),
                          ("Lyapunov-Constrained DRL for Robust Path Following", "rl"),
                          ("Deep Learning-based 3D Magnetic Microrobot Tracking", "dl"),
                          ("Bayesian optimisation of helical swimmer shape", "other")):
        check(f"method: '{title[:45]}' is {method}", us.classify_method(title) == method)


def main():
    verbose = "-v" in sys.argv[1:]
    out = sys.stdout
    with contextlib.suppress(AttributeError):
        out.reconfigure(encoding="utf-8", errors="replace")
    results = []

    def check(name, ok):
        results.append(bool(ok))
        if verbose or not ok:
            print(("PASS  " if ok else "FAIL  ") + name, file=out)

    blocked = []
    real_urlopen, real_sleep = urllib.request.urlopen, time.sleep

    def local_only(req, *args, **kwargs):
        url = req.full_url if isinstance(req, urllib.request.Request) else str(req)
        if urllib.parse.urlsplit(url).hostname not in ("127.0.0.1", "localhost"):
            blocked.append(url)
            raise OSError(f"the tests must not use the network: {url}")
        return real_urlopen(req, *args, **kwargs)

    urllib.request.urlopen, time.sleep = local_only, (lambda seconds: None)  # no network, no back-off waits
    try:
        # the scripts print their own progress; keep it out of the test report
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            run_checks(check)
    except Exception:
        traceback.print_exc()
        print("\nThe tests stopped with an error (see above).", file=out)
        return 2
    finally:
        urllib.request.urlopen, time.sleep = real_urlopen, real_sleep
    check("no request left this computer", not blocked)
    failed = results.count(False)
    print(f"{len(results) - failed} passed, {failed} failed", file=out)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
