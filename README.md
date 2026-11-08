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

<!-- python run_attacks.py --flood 15 -->

```

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

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



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
