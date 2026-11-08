# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

Provenance Guard is a small backend service a writing site could plug into. A writer submits a piece of text, and the service answers with a guess about whether a person or an AI wrote it, a confidence score, and a plain-English label the reader would see. If the writer thinks the label is wrong, they can appeal.

The path a submission takes:

1. A client sends `POST /submit` with JSON containing `text` and `creator_id`.
2. `app.py::submit` checks the input. Missing, empty or enormous text is rejected with a clear error instead of crashing.
3. **Signal one** (`detector.py::model_signal`) runs a small language model (GPT-2) on my own machine and scores how predictable the words are, from 0 to 1. Higher means more AI-like.
4. **Signal two** (`stylometry.py::style_signal`) measures the shape of the text, without reading it: how much sentence length varies, how much vocabulary repeats, how much punctuation there is. Also 0 to 1, higher means more AI-like.
5. `scoring.py::combine_signals` turns the two scores into one confidence number.
6. `scoring.py::score_to_label` maps that number to one of three labels: high-confidence AI, high-confidence human, or unsure.
7. `audit.py` writes a record to `logs/audit.jsonl` (content ID, creator ID, both signal scores, the combined score, the guess and the status), and the response goes back to the client.

If the writer disagrees, `POST /appeal` takes the `content_id` and their reasoning, records it next to the original decision, and moves the item to `under_review`.

---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:** How predictable the text is to a language model (GPT-2 running on my own laptop), measured as perplexity, then squashed onto a 0 to 1 score where higher means more likely AI.

**Why that might differ between human and AI writing:** A language model writes by repeatedly picking a likely next word, so text it wrote tends to be easy for another model to predict. Human writing wanders more: odd word choices, abrupt turns, specific details.

**What it can't see:** Who wrote the text. It only sees how predictable the words are, and predictable is not the same as machine-written. Plain writing with common words in short sentences, like a second-language writer sticking to words they are sure of, scores about as machine-like as AI text. Dense, ornate prose full of rare words often scores as human.

### Signal two — the style signal

**What it measures:** The shape of the text as text, without understanding it: how much sentence length varies, how much of the vocabulary repeats, and how much punctuation there is. Exactly: the standard deviation of sentence length divided by the mean, the share of words that are unique, and the number of semicolons, colons, commas and dashes per word. Each is flipped so that low means more AI-like, scaled to 0 to 1 against a cap I set by hand, and the three are averaged with equal weight (`stylometry.py::style_signal`). A one-sentence text has no sentence spread, so that measure returns a neutral value.

**Why that might differ between human and AI writing:** Generated prose tends toward even, mid-length sentences and a narrower band of vocabulary, because that is what "most likely next word" produces on average. Human writing is lumpier, such as a three-word sentence next to a forty-word one.

**What it can't see:** What the text says. It cannot read, so anything that changes the shape without changing the meaning moves it: adding typos, breaking up sentences, or pasting in a quotation. That is cheap for someone to do on purpose.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:** The combined score is a plain average of the two signals, counted equally. If the signals disagree, the average lands near the middle, which means "unsure", and I treat that as the right answer: two methods disagreeing is uncertainty. To reach the high-confidence AI label, a piece needs a high average, so one strongly AI signal alone is not enough unless the other agrees at least partly.

**The numbers:** Model signal weight 0.5, style signal weight 0.5 (`WEIGHT_MODEL_SIGNAL` and `WEIGHT_STYLE_SIGNAL` in `config.py`). Below 0.35 is high-confidence human, above 0.65 is high-confidence AI, and anything between is unsure (`HUMAN_THRESHOLD` and `AI_THRESHOLD` in `config.py`). The unsure band is wide on purpose, because wrongly accusing a writer costs more than missing some AI text.

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:**

A short paragraph I wrote myself, about an old woman at a funeral, scored 0.74 on the model signal because the wording is plain and predictable, above the AI line on its own. The style signal scored it 0.39, because my sentences vary in length, including a three-word one. The average is 0.56, so the label is unsure instead of high-confidence AI. Without the second signal, my own writing would have been called AI.


---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | below 0.35 | This looks like it was written by a person. |
| unsure | 0.35 to 0.65 | We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work. |
| high-confidence AI | above 0.65 | This looks like it may have been written with AI. Our tools can be wrong, especially on plain or simple writing. If this is your own work, you can appeal and a person will take a look. |

**Why I worded the "unsure" one this way:**

Most of my own test pieces landed in this band, including writing I did myself, so the person reading it may have written every word. It says what the tools don't know instead of guessing, and it says the result isn't a judgment about the writer, so it can't be read as an accusation.



---

## Sample Run

**A submission**

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "Technology has transformed the way people communicate in modern society. It offers many benefits, including faster access to information and improved connectivity. Social media platforms allow individuals to share ideas with a global audience. However, it also presents challenges, such as privacy concerns and misinformation. Overall, it is important to use technology responsibly and thoughtfully.", "creator_id": "faye"}'
```

```json
{
  "confidence": 0.6776,
  "content_id": "b7a06def-a9c8-4129-ad9d-d2d69e1ee447",
  "guess": "ai",
  "label": "This looks like it may have been written with AI. Our tools can be wrong, especially on plain or simple writing. If this is your own work, you can appeal and a person will take a look.",
  "model_score": 0.8456,
  "style_score": 0.5096
}
```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "b7a06def-a9c8-4129-ad9d-d2d69e1ee447", "reasoning": "I wrote this myself as a writing exercise."}'
```

```json
{
  "content_id": "b7a06def-a9c8-4129-ad9d-d2d69e1ee447",
  "message": "Your appeal has been recorded and a person will take a look.",
  "status": "under_review"
}
```

**What the log shows afterwards**

The first entry is the submission above, the next two are other submissions I made in between, and the last is the appeal. The original decision stays where it was, and the appeal sits after it.

```bash
$ curl "http://127.0.0.1:5000/log?limit=4"
```

```json
{
  "count": 4,
  "entries": [
    {
      "timestamp": "2026-10-31T17:30:52+00:00",
      "content_id": "b7a06def-a9c8-4129-ad9d-d2d69e1ee447",
      "creator_id": "faye",
      "guess": "ai",
      "model_score": 0.8456,
      "style_score": 0.5096,
      "combined_score": 0.6776,
      "label": "This looks like it may have been written with AI. Our tools can be wrong, especially on plain or simple writing. If this is your own work, you can appeal and a person will take a look.",
      "status": "decided"
    },
    {
      "timestamp": "2026-10-31T17:30:56+00:00",
      "content_id": "0fb45421-d203-4f77-8dca-4442fefedc22",
      "creator_id": "faye",
      "guess": "human",
      "model_score": 0.201,
      "style_score": 0.4464,
      "combined_score": 0.3237,
      "label": "This looks like it was written by a person.",
      "status": "decided"
    },
    {
      "timestamp": "2026-10-31T17:31:05+00:00",
      "content_id": "d8905dc5-4724-4704-801a-92a3437eba16",
      "creator_id": "faye",
      "guess": "ai",
      "model_score": 0.6534,
      "style_score": 0.5017,
      "combined_score": 0.5776,
      "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
      "status": "decided"
    },
    {
      "timestamp": "2026-10-31T17:31:37+00:00",
      "content_id": "b7a06def-a9c8-4129-ad9d-d2d69e1ee447",
      "creator_id": "faye",
      "event": "appeal",
      "status": "under_review",
      "reasoning": "I wrote this myself as a writing exercise."
    }
  ]
}
```

---

## How I Used AI

**Moment 1: building the style signal**

- *What I asked for:* Help building the three measures in `stylometry.py` (sentence length spread, unique-word ratio, punctuation density) and turning them into one 0 to 1 score.
- *What came back:* Three working functions and a `style_signal` that flips each measure so that high means more AI-like, then averages them.
- *What I changed:* I decided which punctuation counts (semicolons, colons, commas and dashes, not full stops) and what a one-sentence text returns (a neutral value). When I tested it, a chatbot paragraph full of long comma lists scored 0.32, which reads as human. I kept the signal as it was and wrote that up as a blind spot instead of tuning it to fit two examples.

**Moment 2: choosing the combining rule**

- *What I asked for:* Which rule to use to combine the two signals.
- *What came back:* Two options, a plain 50/50 average or an average with a rule for when the signals disagree, and a recommendation for the average.
- *What I changed:* I went with the plain average, because it already put my own funeral paragraph in "unsure" and my criteria are written against the combined score. I also corrected my README after the service returned 0.74 for the model signal on that paragraph, not the 0.65 from my terminal test, which had stray quote marks in the text.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** 5 per minute, 50 per day (`RATE_LIMIT_PER_MINUTE` and `RATE_LIMIT_PER_DAY` in `config.py`), on `POST /submit`.

**Why those numbers and not others:**

A real writer submitting their own work, tweaking it and resubmitting, rarely sends more than a few in a minute or more than about twenty in a day, so 5 and 50 are liveable for them. A script trying to map my thresholds needs hundreds of small variations of one text. At 5 a minute it is slowed to a crawl, and at 50 a day it is cut off long before it has a useful picture of where the 0.35 and 0.65 lines sit. The starter's defaults (10 and 200) would have let that script send 200 probes a day. I did not go lower than 5 because each submission loads a model and takes a second or two, so a writer legitimately fixing a typo and resubmitting three times in a row should not be refused.

**What a caller counts as:** The `creator_id` in the request body, falling back to the caller's address when the body has no usable `creator_id` (`rate_limit_key` in `app.py`). That makes the limit per writer, not per household. Its weakness is that a script can send a fresh `creator_id` with every request and never hit the limit, because I trust the ID the caller supplies. I did not fix that in this unit.

**The run of status codes when I pushed past it:**

`python run_attacks.py --flood 15`, 15 submissions from one `creator_id`, written to `results/flood_2026-11-08_1528.md`:

```
200 200 200 200 200 429 429 429 429 429 429 429 429 429 429
```

Five went through and ten were refused, which is the limit of 5 per minute. The ten refusals are in `logs/audit.jsonl`, for example:

```json
{"timestamp": "2026-11-08T23:28:04+00:00", "creator_id": "flood_tester", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute"}
```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

Run on 2026-11-08 with the service from the previous unit plus the rate limiter, `python run_eval.py --label before` (criteria 1, 2, 3, 5) and `python appeal_check.py --label before` (criterion 4). Every trial of every criterion came out identical to the other two, which is expected because neither signal is random. Files: `results/run_2026-11-08_1528_before.md` and `results/appeal_2026-11-08_1535_before.md`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. My own writing flagged as AI | at most 1 of 10 labeled high-confidence AI | 0 of 11 | 0 of 11 | 0 of 11 | MET |
| 2. Score spread | average combined score of 5 AI texts at least 0.3 above 5 of mine | 0.204 (0.685 vs 0.481) | 0.204 | 0.204 | MISSED |
| 3. Label coverage | across 15 texts, each of the 3 labels at least twice | AI 5, unsure 9, human 1 | AI 5, unsure 9, human 1 | AI 5, unsure 9, human 1 | MISSED |
| 4. Appeal path | 3 real appeals return `under_review` and are logged, 2 fake IDs return an error | 3/3 and 2/2 | 3/3 and 2/2 | 3/3 and 2/2 | MET |
| 5. Bad input | 5 of 5 bad inputs get a 400 and the service keeps running | 5/5 | 5/5 | 5/5 | MET |

How I decided each verdict:

- **1 is MET, narrowly.** No piece got the high-confidence AI label in any trial. But four of my first five pieces landed in "unsure", three of them at a combined 0.54 to 0.58 (the funeral paragraph, the cover letter and the three-sentence Etsy text), and the funeral paragraph's model signal alone was 0.74, above the 0.65 AI line. Five of the 11 are short chat lines that score very human on signal one, and one is a long casual paragraph that also scores very human, so the first five are the real test.
- **2 is MISSED.** The gap is 0.204 against a target of 0.3, in every trial. (If I averaged over all 11 of my pieces the gap would look bigger, 0.349, because the short chat lines score very human. I am not using that. The criterion says 5 and 5, and I do not want to pick the set that passes.)
- **3 is MISSED.** The human label appeared once in 15 (the one-sentence Etsy text) and the target was twice.
- **5 is MET.** All five bad inputs (empty text, no text field, whitespace only, no `creator_id`, 25000 characters) returned 400 in all three trials. Each also left a rejection entry in `logs/audit.jsonl`.

**Real output from one trial** (trial 1 of each; the full three trials are in the files named above).

Criterion 1, produced by `run_eval.py::main` calling `app.py::submit`:

```json
[
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.5647,
    "model_score": 0.7372,
    "style_score": 0.3922,
    "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
    "sent": "At a funeral, an old woman is wearing all black elegant dress and stan"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.6037,
    "model_score": 0.4299,
    "style_score": 0.3627,
    "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
    "sent": "I spilled coffee on my keyboard this morning and spent twenty minutes "
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.5776,
    "model_score": 0.6534,
    "style_score": 0.5017,
    "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
    "sent": "My experience from SolarCity has prepared me to take on bigger challen"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.6763,
    "model_score": 0.201,
    "style_score": 0.4464,
    "label": "This looks like it was written by a person.",
    "sent": "Etsy is a great platform for people who wants to test out starting the"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.541,
    "model_score": 0.4501,
    "style_score": 0.6319,
    "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
    "sent": "Etsy is a great platform for people who wants to test out starting the"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.7514,
    "model_score": 0.0985,
    "style_score": 0.3988,
    "label": "This looks like it was written by a person.",
    "sent": "So ngl I\u2019m not new to online business I had quite few Etsy stores..pen"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.9044,
    "model_score": 0.0246,
    "style_score": 0.1667,
    "label": "This looks like it was written by a person.",
    "sent": "Soft life: slow mornings, coffee, home, golden hour, trees around my c"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.8625,
    "model_score": 0.0527,
    "style_score": 0.2222,
    "label": "This looks like it was written by a person.",
    "sent": "Day in my life: \u201810am on a Wednesday\u2019 style, ex-tech girl running her "
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.7494,
    "model_score": 0.0012,
    "style_score": 0.5,
    "label": "This looks like it was written by a person.",
    "sent": "ok which one we r posting later today tho"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.7002,
    "model_score": 0.0692,
    "style_score": 0.5303,
    "label": "This looks like it was written by a person.",
    "sent": "These videos r great thanks. Let\u2019s see how they perform. I\u2019m excited"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.7385,
    "model_score": 0.0229,
    "style_score": 0.5,
    "label": "This looks like it was written by a person.",
    "sent": "No I\u2019m asking u which one to get from looking at the research Jesus."
  }
]
```

Criterion 2, the five AI-written texts (`spread ai`), same function:

```json
[
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.6776,
    "model_score": 0.8456,
    "style_score": 0.5096,
    "label": "This looks like it may have been written with AI. Our tools can be wrong, especially on plain or simple writing. If this is your own work, you can appeal and a person will take a look.",
    "sent": "Technology has transformed the way people communicate in modern societ"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.6502,
    "model_score": 0.875,
    "style_score": 0.4254,
    "label": "This looks like it may have been written with AI. Our tools can be wrong, especially on plain or simple writing. If this is your own work, you can appeal and a person will take a look.",
    "sent": "Regular exercise is an important part of maintaining a healthy lifesty"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.6902,
    "model_score": 0.7948,
    "style_score": 0.5856,
    "label": "This looks like it may have been written with AI. Our tools can be wrong, especially on plain or simple writing. If this is your own work, you can appeal and a person will take a look.",
    "sent": "Remote work has become increasingly common in recent years. It provide"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.6457,
    "model_score": 0.8064,
    "style_score": 0.4849,
    "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
    "sent": "Reading is a valuable habit that offers numerous benefits for people o"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.7589,
    "model_score": 0.9343,
    "style_score": 0.5834,
    "label": "This looks like it may have been written with AI. Our tools can be wrong, especially on plain or simple writing. If this is your own work, you can appeal and a person will take a look.",
    "sent": "Climate change is one of the most pressing challenges facing the world"
  }
]
```

Criterion 2, the five human texts (`spread human`) are the first five entries of the criterion 1 output above (the funeral, coffee, cover letter and two Etsy texts).

Criterion 3, fifteen texts (`label coverage`), same function:

```json
[
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.5647,
    "model_score": 0.7372,
    "style_score": 0.3922,
    "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
    "sent": "At a funeral, an old woman is wearing all black elegant dress and stan"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.6037,
    "model_score": 0.4299,
    "style_score": 0.3627,
    "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
    "sent": "I spilled coffee on my keyboard this morning and spent twenty minutes "
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.5776,
    "model_score": 0.6534,
    "style_score": 0.5017,
    "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
    "sent": "My experience from SolarCity has prepared me to take on bigger challen"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.6763,
    "model_score": 0.201,
    "style_score": 0.4464,
    "label": "This looks like it was written by a person.",
    "sent": "Etsy is a great platform for people who wants to test out starting the"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.541,
    "model_score": 0.4501,
    "style_score": 0.6319,
    "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
    "sent": "Etsy is a great platform for people who wants to test out starting the"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.6776,
    "model_score": 0.8456,
    "style_score": 0.5096,
    "label": "This looks like it may have been written with AI. Our tools can be wrong, especially on plain or simple writing. If this is your own work, you can appeal and a person will take a look.",
    "sent": "Technology has transformed the way people communicate in modern societ"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.6502,
    "model_score": 0.875,
    "style_score": 0.4254,
    "label": "This looks like it may have been written with AI. Our tools can be wrong, especially on plain or simple writing. If this is your own work, you can appeal and a person will take a look.",
    "sent": "Regular exercise is an important part of maintaining a healthy lifesty"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.6902,
    "model_score": 0.7948,
    "style_score": 0.5856,
    "label": "This looks like it may have been written with AI. Our tools can be wrong, especially on plain or simple writing. If this is your own work, you can appeal and a person will take a look.",
    "sent": "Remote work has become increasingly common in recent years. It provide"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.6457,
    "model_score": 0.8064,
    "style_score": 0.4849,
    "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
    "sent": "Reading is a valuable habit that offers numerous benefits for people o"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.7589,
    "model_score": 0.9343,
    "style_score": 0.5834,
    "label": "This looks like it may have been written with AI. Our tools can be wrong, especially on plain or simple writing. If this is your own work, you can appeal and a person will take a look.",
    "sent": "Climate change is one of the most pressing challenges facing the world"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.5163,
    "model_score": 0.5969,
    "style_score": 0.4357,
    "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
    "sent": "Technology has changed how people communicate these days. It gives us "
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.6447,
    "model_score": 0.8569,
    "style_score": 0.4325,
    "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
    "sent": "Working out is a big part of staying healthy. It's good for your heart"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.6198,
    "model_score": 0.3479,
    "style_score": 0.4125,
    "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
    "sent": "Remote work is everywhere now. You get more flexibility and no commute"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.5899,
    "model_score": 0.7369,
    "style_score": 0.4429,
    "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
    "sent": "Reading every day is a great habit. It builds vocabulary, helps you fo"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.635,
    "model_score": 0.7639,
    "style_score": 0.506,
    "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
    "sent": "Climate change is a huge problem right now. Temperatures keep rising a"
  }
]
```

Criterion 4, produced by `appeal_check.py::main` calling `app.py::submit` and `app.py::appeal`:

```json
{
  "real": [
    {
      "submit_status": 200,
      "content_id": "153d4538-b74a-4aa1-a880-bb42cf22524e",
      "appeal_status": 200,
      "appeal_response": {
        "content_id": "153d4538-b74a-4aa1-a880-bb42cf22524e",
        "message": "Your appeal has been recorded and a person will take a look.",
        "status": "under_review"
      },
      "in_audit_log": true
    },
    {
      "submit_status": 200,
      "content_id": "4787107e-bba4-4c95-8cb5-c52c012a69c7",
      "appeal_status": 200,
      "appeal_response": {
        "content_id": "4787107e-bba4-4c95-8cb5-c52c012a69c7",
        "message": "Your appeal has been recorded and a person will take a look.",
        "status": "under_review"
      },
      "in_audit_log": true
    },
    {
      "submit_status": 200,
      "content_id": "f6b528a8-23b7-4fd2-b814-b39767d4f367",
      "appeal_status": 200,
      "appeal_response": {
        "content_id": "f6b528a8-23b7-4fd2-b814-b39767d4f367",
        "message": "Your appeal has been recorded and a person will take a look.",
        "status": "under_review"
      },
      "in_audit_log": true
    }
  ],
  "fake": [
    {
      "content_id": "does-not-exist-1",
      "appeal_status": 404,
      "appeal_response": {
        "error": "unknown_content_id",
        "message": "No submission found with that content_id."
      }
    },
    {
      "content_id": "00000000-0000-0000-0000-000000000000",
      "appeal_status": 404,
      "appeal_response": {
        "error": "unknown_content_id",
        "message": "No submission found with that content_id."
      }
    }
  ]
}
```

Criterion 5, produced by `run_eval.py::main` calling `app.py::submit` (the `_refuse` helper in `app.py` logs each refusal):

```json
[
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "(empty text)"
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "{\"creator_id\": \"eval_bad_missing\"}"
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "   \n  "
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "{\"text\": \"A normal sentence with no creator id.\"}"
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "word word word word word word word word word word word word word word "
  }
]
```

**Diagnoses**

*Criterion 2 (MISSED).* The stage is signal two, and the combining rule turns that into a miss. Across the five AI texts and five of my texts, signal one averages 0.851 for AI and 0.494 for mine, a gap of 0.357. Signal two averages 0.518 for AI and 0.467 for mine, a gap of only 0.051. With both weighted 0.5, the combined gap is the average of the two gaps, (0.357 + 0.051) / 2 = 0.204, so it cannot reach 0.3 unless signal two starts separating or the weights favor signal one. The mechanism in signal two is that my three measures barely react to these texts: all ten score between 0.36 and 0.63. My own Etsy text scored 0.63, higher than the AI average, because it is three long comma-spliced sentences of similar length, which the sentence-length-spread measure reads as even and AI-like. Signal one is also pulled down by plain writing: my funeral paragraph scored 0.74 and my cover letter 0.65 because their wording is simple and predictable.

*Criterion 3 (MISSED).* The stage is signal two compressing the range, with the 0.35 human threshold sitting below where combined scores can reach. To get "human" the combined score must be under 0.35. Across the 15 texts, signal two never went below 0.36, so signal one would have to score below about 0.34. Only one text did (the one-sentence Etsy text, signal one 0.20), and the closest other, a casual rewrite of an AI paragraph, scored 0.35 on signal one with 0.41 on signal two, for a combined 0.38. This is the exact trap the comment in `config.py` warns about: a style signal that barely varies shrinks the reachable range.

*The pattern.* Both misses trace back to signal two. It separates AI from human by 0.05 and it varies only from 0.36 to 0.63, which both compresses scores away from the human label and drags the 50/50 average toward the middle. That is one problem, not two. Signal one separates well on typical AI text (0.85 vs 0.49) but has its own known weakness on plain human writing, which is why my closest call on criterion 1 was signal one alone scoring my funeral paragraph at 0.74.

Criterion 4 and 5 were met in all three trials and need no diagnosis. I did not revise any criterion.

---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
