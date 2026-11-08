#!/usr/bin/env python3
"""
Check criterion 4: the appeal path.  <- UNIT 8, MILESTONE 3

    python app.py                          # in one terminal
    python appeal_check.py --label before  # in another

run_eval.py cannot do this one, because an appeal needs a content_id from an
earlier submission. This script, three times over:

  1. submits 3 texts and appeals each real content_id        (expect 200, under_review)
  2. appeals 2 content_ids that do not exist                 (expect 404 with an error field)
  3. reads GET /log and checks each real appeal was recorded (expect an appeal entry)

Writes results/appeal_<date>_<label>.md.
"""

import argparse
import datetime as dt
import json
import urllib.error
import urllib.request

import config

URL = f"http://{config.HOST}:{config.PORT}"

TEXTS = [
    "I spilled coffee on my keyboard this morning and spent twenty minutes drying it with a hairdryer while my cat watched from the couch like I was an idiot. The N key still sticks.",
    "At a funeral, an old woman is wearing all black elegant dress and standing far away from the rest of the people. Lots of people are crying at the funeral. But not the old woman. She looks peaceful, even though there is an deep sadness in her eyes.",
    "Technology has transformed the way people communicate in modern society. It offers many benefits, including faster access to information and improved connectivity. Social media platforms allow individuals to share ideas with a global audience.",
]
FAKE_IDS = ["does-not-exist-1", "00000000-0000-0000-0000-000000000000"]


def post(path, body):
    req = urllib.request.Request(
        URL + path, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, None
    except Exception as e:  # service down, not JSON, ...
        return None, {"exception": repr(e)}


def get_log():
    with urllib.request.urlopen(URL + "/log", timeout=60) as r:
        return json.loads(r.read())["entries"]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--label", default="")
    args = ap.parse_args()
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    lines = []
    rows = []
    for trial in (1, 2, 3):
        trial_out = {"real": [], "fake": []}
        real_ok = fake_ok = 0
        for i, text in enumerate(TEXTS, 1):
            cid_status, sub = post("/submit", {"text": text, "creator_id": f"appeal_check_{stamp}_{trial}_{i}"})
            cid = (sub or {}).get("content_id")
            a_status, appeal = post("/appeal", {"content_id": cid, "reasoning": "I wrote this myself."})
            logged = any(e.get("event") == "appeal" and e.get("content_id") == cid for e in get_log())
            ok = a_status == 200 and (appeal or {}).get("status") == "under_review" and logged
            real_ok += ok
            trial_out["real"].append({"submit_status": cid_status, "content_id": cid,
                                      "appeal_status": a_status, "appeal_response": appeal,
                                      "in_audit_log": logged})
        for fake in FAKE_IDS:
            a_status, appeal = post("/appeal", {"content_id": fake, "reasoning": "I wrote this myself."})
            ok = a_status == 404 and isinstance(appeal, dict) and "error" in appeal
            fake_ok += ok
            trial_out["fake"].append({"content_id": fake, "appeal_status": a_status, "appeal_response": appeal})
        rows.append((trial, real_ok, fake_ok))
        lines.append(f"**Trial {trial}**\n\n```json\n{json.dumps(trial_out, indent=2)}\n```\n")
        print(f"trial {trial}: real appeals ok {real_ok}/3, fake ids ok {fake_ok}/2")

    path = config.RESULTS_DIR / f"appeal_{stamp}{'_' + args.label if args.label else ''}.md"
    config.RESULTS_DIR.mkdir(exist_ok=True)
    head = [
        f"# Appeal check{' - ' + args.label if args.label else ''}",
        "",
        f"- Produced by: `appeal_check.py::main` against `app.py::appeal` · {stamp}",
        "",
        "| Trial | Real appeals ok (want 3/3) | Fake ids refused with 404 + error (want 2/2) |",
        "|---|---|---|",
    ] + [f"| {t} | {r}/3 | {f}/2 |" for t, r, f in rows] + ["", ""]
    path.write_text("\n".join(head) + "\n".join(lines), encoding="utf-8")
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
