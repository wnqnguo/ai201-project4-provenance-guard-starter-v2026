#!/usr/bin/env python3
"""
Capstone test: the five criteria in criteria.md, three trials each.

    python app.py                                  # one terminal
    python capstone_run.py --label before          # another
    python capstone_run.py --label after           # after the improvement

Inputs live in capstone_inputs.json (12 bad inputs, 10 foreign-language
sentences, 10 paragraphs of my own writing). Every request gets its own
creator_id so the rate limiter (5 a minute per creator) is not what is being
measured. The service is left exactly as it runs normally.

Each trial reads the audit log back from the service to check criterion 3 and
to get duration_ms for criterion 5. Nothing is decided by hand.
"""

import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).parent
URL = "http://127.0.0.1:5000"
WARM_UP_TEXT = "I walked to the coffee shop this morning and the barista remembered my order."


def post(item, trial):
    """Send one input. Returns (status, json_or_None). Never raises."""
    cid = f"cap_t{trial}_{item['id']}"
    try:
        if "raw" in item:
            r = requests.post(f"{URL}/submit", data=item["raw"].encode("utf-8"),
                              headers={"Content-Type": "application/json"}, timeout=120)
        else:
            body = dict(item["body"])
            if "creator_id" in body:
                body["creator_id"] = cid
            r = requests.post(f"{URL}/submit", json=body, timeout=120)
    except Exception as exc:  # noqa: BLE001
        return None, {"transport_error": f"{type(exc).__name__}: {exc}"}
    try:
        return r.status_code, r.json()
    except ValueError:
        return r.status_code, None


def log_entries():
    r = requests.get(f"{URL}/log", timeout=60)
    return r.json()["entries"]


def run_trial(trial, inputs):
    """Send all 32 requests in order and score the five criteria for this trial."""
    before_n = len(log_entries())
    sent = []
    for group in ("bad", "foreign", "normal"):
        for item in inputs[group]:
            status, payload = post(item, trial)
            sent.append({"group": group, "id": item["id"], "note": item["note"],
                         "status": status, "payload": payload})
    new = log_entries()[before_n:]

    # Criterion 1: 12 bad inputs -> 400 with error + message
    bad = [s for s in sent if s["group"] == "bad"]
    c1 = [s for s in bad if s["status"] == 400 and isinstance(s["payload"], dict)
          and s["payload"].get("error") and s["payload"].get("message")]
    # Criterion 2: 10 foreign -> 400
    foreign = [s for s in sent if s["group"] == "foreign"]
    c2 = [s for s in foreign if s["status"] == 400]
    # Criterion 3: each of the 22 requests (bad + foreign) left a rejected
    # entry with input and duration_ms filled in. Requests are sent one at a
    # time, so rejected entries line up with refused requests in order.
    refusals = [s for s in bad + foreign if s["status"] in (400, 500)]
    rejected = [e for e in new if e.get("event") == "rejected"]
    logged_ok = []
    for s, e in zip(refusals, rejected):
        same_reason = isinstance(s["payload"], dict) and s["payload"].get("error") == e.get("reason")
        if same_reason and e.get("input") not in (None, "") and e.get("duration_ms") is not None:
            logged_ok.append((s["id"], e))
    c3 = len(logged_ok)
    # Criterion 4: 10 normal paragraphs -> 200
    normal = [s for s in sent if s["group"] == "normal"]
    c4 = [s for s in normal if s["status"] == 200]
    # Criterion 5: duration_ms of the 10 scored normal paragraphs, warm model
    decided = {e.get("content_id"): e for e in new if e.get("event") != "rejected"}
    durations = []
    for s in normal:
        if s["status"] == 200:
            e = decided.get(s["payload"]["content_id"])
            if e and e.get("duration_ms") is not None:
                durations.append(e["duration_ms"])
    c5 = [d for d in durations if d < 3000]
    return {
        "trial": trial,
        "c1": (len(c1), len(bad)), "c2": (len(c2), len(foreign)),
        "c3": (c3, 22), "c4": (len(c4), len(normal)), "c5": (len(c5), len(normal)),
        "durations_ms": durations, "sent": sent, "new_log_entries": new,
        "c1_failures": [s["id"] for s in bad if s not in c1],
        "c2_failures": [s["id"] for s in foreign if s not in c2],
        "c4_failures": [s["id"] for s in normal if s not in c4],
        "c3_missing": [s["id"] for s in refusals if s["id"] not in [i for i, _ in logged_ok]]
                      + [s["id"] for s in bad + foreign if s not in refusals],
    }


def main():
    global URL
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--url", default=URL)
    args = ap.parse_args()
    URL = args.url
    inputs = json.loads((ROOT / "capstone_inputs.json").read_text(encoding="utf-8"))

    try:
        requests.get(f"{URL}/health", timeout=10)
    except Exception as exc:  # noqa: BLE001
        sys.exit(f"Service not reachable at {URL}: {exc}\nStart it with: python app.py")

    print("Warming up the model (this request is not counted)...")
    t0 = time.perf_counter()
    requests.post(f"{URL}/submit", json={"text": WARM_UP_TEXT, "creator_id": "cap_warmup"}, timeout=300)
    print(f"  warm-up took {time.perf_counter() - t0:.1f}s")

    trials = []
    for t in (1, 2, 3):
        print(f"Trial {t}/3 ...")
        r = run_trial(t, inputs)
        trials.append(r)
        print("  c1 {0}/{1}  c2 {2}/{3}  c3 {4}/{5}  c4 {6}/{7}  c5 {8}/{9}".format(
            *r["c1"], *r["c2"], *r["c3"], *r["c4"], *r["c5"]))

    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    out_json = ROOT / "results" / f"capstone_{stamp}_{args.label}.json"
    out_md = ROOT / "results" / f"capstone_{stamp}_{args.label}.md"
    out_json.parent.mkdir(exist_ok=True)
    out_json.write_text(json.dumps(trials, ensure_ascii=False, indent=1), encoding="utf-8")

    names = {
        "c1": "1. 12 bad inputs get a 400 with a message",
        "c2": "2. 10 French/Spanish sentences get a 400",
        "c3": "3. 22 refusals logged with input and duration_ms",
        "c4": "4. 10 of my own paragraphs are scored, not refused",
        "c5": "5. 10 warm scored requests under 3 seconds",
    }
    lines = [f"# Capstone run: {args.label}", "",
             f"Produced by `capstone_run.py::main` on {stamp}. Raw output: `{out_json.name}`.", "",
             "| Criterion | Run 1 | Run 2 | Run 3 |", "|---|---|---|---|"]
    for k, n in names.items():
        lines.append(f"| {n} | " + " | ".join(f"{t[k][0]}/{t[k][1]}" for t in trials) + " |")
    lines += ["", "## Misses by trial (input ids)", ""]
    for t in trials:
        lines.append(f"- Trial {t['trial']}: c1 {t['c1_failures']}, c2 {t['c2_failures']}, "
                     f"c3 not logged {t['c3_missing']}, c4 {t['c4_failures']}, "
                     f"c5 durations_ms {t['durations_ms']}")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote {out_md.relative_to(ROOT)} and {out_json.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
