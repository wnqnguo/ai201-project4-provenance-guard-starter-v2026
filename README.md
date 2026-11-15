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

**The numbers:** Model signal weight 0.5, style signal weight 0.5 (`WEIGHT_MODEL_SIGNAL` and `WEIGHT_STYLE_SIGNAL` in `config.py`). Below 0.35 is high-confidence human, above 0.75 is high-confidence AI (it was 0.65 until the Unit 8 improvement, see The Improvement), and anything between is unsure (`HUMAN_THRESHOLD` and `AI_THRESHOLD` in `config.py`). The unsure band is wide on purpose, because wrongly accusing a writer costs more than missing some AI text.

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
| unsure | 0.35 to 0.75 (0.35 to 0.65 before Unit 8) | We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work. |
| high-confidence AI | above 0.75 (above 0.65 before Unit 8) | This looks like it may have been written with AI. Our tools can be wrong, especially on plain or simple writing. If this is your own work, you can appeal and a person will take a look. |

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

**Moment 3: checking my work against the grading**

- *What I asked for:* I asked Claude to check my project against the grading.
- *What came back:* A comparison of what I had against what the grading asks for, and what was still missing.
- *What I changed:* I filled in what was missing before moving on. 

**Moment 4: finding my own writing for the tests**

- *What I asked for:* In a separate chat, I asked Claude to pull five examples of my own writing from my past chats, as paragraphs, to use as the human-written texts in my tests.
- *What came back:* Five pieces taken from my chats. 
- *What I changed:* One of the pieces was too personal, so I asked for it to be replaced with a paragraph about my more generic stuff. I then gave the pieces to this session to use as the human side of the tests.

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

`python run_attacks.py --set attack_set` against the service as it stood after Milestone 1 (rate limiter on at 5 per minute and 50 per day, refusals logged, nothing else changed). 56 attacks, written to `results/attack_run_2026-11-08_1552.md`. The run itself auto-marked one attack BROKE (the 500 on MF02). I marked the rest myself. "Label" is which of the three labels came back, shown as AI, HUMAN or UNSURE.

How I decided HELD or BROKE, by what each family is going for:

- **evasion (EV):** these are AI-written texts changed to avoid detection. BROKE if the text did not get the AI label, since the attacker's goal was to avoid it. Most got "unsure", so they were not vouched for as human, but they were still not caught.
- **false_positive (FP):** these are genuine human writing. BROKE if the writer got the AI label, because that is a real writer accused.
- **prompt_injection (PI):** PI01, PI02, PI03 and PI05 are an AI-style essay with an instruction attached, going for a HUMAN label or a forged log entry. BROKE only if the HUMAN label came back. PI04 and PI06 are going for a hostile label or a pass for real human text.
- **malformed (MF, RQ):** BROKE if the service crashed, or gave a confident label to something that is not writing. HELD if it refused or said "unsure".
- **flood_same_creator (FL):** HELD if the limiter stopped it.

**Result: 21 BROKE, 35 HELD out of 56.** By family: evasion 9 of 10 broke, false_positive 6 of 8, prompt_injection 1 of 6, malformed 5 of 20, flood 0 of 12.

| ID | Targeting | Status | Label | Combined | Mark | Why |
|---|---|---|---|---|---|---|
| EV01 | signal two: typos raise word variety | 200 | UNSURE | 0.364 | **BROKE** | typos made signal one score it 0.16 (human-like); got 'unsure' |
| EV02 | signal two: broken-up sentences raise length spread | 200 | UNSURE | 0.457 | **BROKE** | broken-up sentences pulled signal two to 0.32; got 'unsure' |
| EV03 | signal two: a pasted quotation changes the shape | 200 | UNSURE | 0.559 | **BROKE** | pasted quotation; both signals mid, got 'unsure' |
| EV04 | signal one: unusual words raise perplexity | 200 | UNSURE | 0.585 | **BROKE** | unusual words; signals mid, got 'unsure' |
| EV05 | both signals: heavy human editing pass | 200 | HUMAN | 0.324 | **BROKE** | heavy editing pass fooled both signals; got the HUMAN label |
| EV06 | signal two: one very long sentence and one very short | 200 | UNSURE | 0.459 | **BROKE** | one very long and one very short sentence pulled signal two to 0.34; 'unsure' |
| EV07 | signal two: padding with punctuation | 200 | UNSURE | 0.414 | **BROKE** | punctuation padding pulled signal two to 0.24; 'unsure' |
| EV08 | signal one: text below the token window | 200 | UNSURE | 0.397 | **BROKE** | short text, signal one 0.25; 'unsure' |
| EV09 | both: AI text with a human opening paragraph bolted on | 200 | UNSURE | 0.564 | **BROKE** | human opening dragged the average; 'unsure' |
| EV10 | signal two: repeated stanza structure | 200 | AI | 0.854 | **HELD** | both signals high; kept the AI label |
| FP01 | plain, clear human writing with no flourishes | 200 | UNSURE | 0.574 | **HELD** | real human writing, not accused ('unsure') |
| FP02 | human writing in a formal register | 200 | AI | 0.686 | **BROKE** | real human writing got the AI label |
| FP03 | a non-native English speaker writing carefully | 200 | AI | 0.714 | **BROKE** | real human writing got the AI label |
| FP04 | a student essay written to a rubric | 200 | AI | 0.689 | **BROKE** | real human writing got the AI label |
| FP05 | technical documentation written by a person | 200 | AI | 0.713 | **BROKE** | real human writing got the AI label |
| FP06 | a person imitating a formal template | 200 | AI | 0.693 | **BROKE** | real human writing got the AI label |
| FP07 | human writing that repeats a phrase deliberately | 200 | AI | 0.675 | **BROKE** | real human writing got the AI label |
| FP08 | very short genuine human submission | 200 | UNSURE | 0.404 | **HELD** | real human writing, not accused ('unsure') |
| PI01 | instruction to ignore the check | 200 | UNSURE | 0.438 | **HELD** | instruction ignored; no HUMAN label (got 'unsure') |
| PI02 | instruction disguised as a system message | 200 | HUMAN | 0.258 | **BROKE** | got the HUMAN label, but through the odd prefix lowering signal one, not by obeying it |
| PI03 | instruction wrapped in the writer's voice | 200 | UNSURE | 0.554 | **HELD** | instruction ignored; no HUMAN label (got 'unsure') |
| PI04 | attempt to make the label text hostile | 200 | UNSURE | 0.480 | **HELD** | label text unchanged; markup never reaches the label |
| PI05 | attempt to inject into the audit log | 200 | UNSURE | 0.394 | **HELD** | entry in the log is a normal one; the text is never written to the log |
| PI06 | instruction plus real human text | 200 | UNSURE | 0.549 | **HELD** | instruction ignored; human text got 'unsure' |
| MF01 | text is only whitespace | 400 | — | — | **HELD** | 400, refused and logged |
| MF02 | text is a single character | 500 | — | — | **BROKE** | 500: signal one raised ValueError (too short), uncaught, no log entry |
| MF03 | text is control characters | 200 | HUMAN | 0.250 | **BROKE** | control characters were scored and labeled HUMAN |
| MF04 | text is only punctuation | 200 | UNSURE | 0.422 | **HELD** | punctuation only, labeled 'unsure' |
| MF05 | text is a very long single word | 200 | AI | 0.749 | **BROKE** | a very long single word was scored 0.75 and labeled AI |
| MF06 | text is emoji only | 200 | AI | 0.915 | **BROKE** | emoji only was scored 0.92 and labeled AI |
| MF07 | text is right-to-left script | 200 | AI | 0.870 | **BROKE** | right-to-left script was scored 0.87 and labeled AI |
| MF08 | text is 60,000 characters | 400 | — | — | **HELD** | 400 text_too_long, logged |
| RQ01 | no text field at all | 400 | — | — | **HELD** | 400, refused and logged |
| RQ02 | no creator_id | 400 | — | — | **HELD** | 400, refused and logged |
| RQ03 | text is a number | 400 | — | — | **HELD** | 400, refused and logged |
| RQ04 | text is a list | 400 | — | — | **HELD** | 400, refused and logged |
| RQ05 | text is null | 400 | — | — | **HELD** | 400, refused and logged |
| RQ06 | creator_id is an object | 400 | — | — | **HELD** | 400, refused and logged |
| RQ07 | body is a JSON array, not an object | 400 | — | — | **HELD** | 400, refused and logged |
| RQ08 | body is unparseable JSON | 400 | — | — | **HELD** | 400, refused and logged |
| RQ09 | body is empty | 400 | — | — | **HELD** | 400, refused and logged |
| RQ10 | body is form-encoded, not JSON | 429 | — | — | **HELD** | 429 from the limiter before the route (no creator_id), logged |
| RQ11 | body is JSON claiming to be plain text | 429 | — | — | **HELD** | 429 from the limiter before the route (no creator_id), logged |
| RQ12 | deeply nested JSON | 400 | — | — | **HELD** | 400, refused and logged |
| FL01_01 | 20 rapid submissions from one creator | 200 | HUMAN | — | **HELD** | limiter allowed 5, refused the rest |
| FL01_02 | 20 rapid submissions from one creator | 200 | HUMAN | — | **HELD** | limiter allowed 5, refused the rest |
| FL01_03 | 20 rapid submissions from one creator | 200 | HUMAN | — | **HELD** | limiter allowed 5, refused the rest |
| FL01_04 | 20 rapid submissions from one creator | 200 | HUMAN | — | **HELD** | limiter allowed 5, refused the rest |
| FL01_05 | 20 rapid submissions from one creator | 200 | HUMAN | — | **HELD** | limiter allowed 5, refused the rest |
| FL01_06 | 20 rapid submissions from one creator | 429 | — | — | **HELD** | limiter allowed 5, refused the rest |
| FL01_07 | 20 rapid submissions from one creator | 429 | — | — | **HELD** | limiter allowed 5, refused the rest |
| FL01_08 | 20 rapid submissions from one creator | 429 | — | — | **HELD** | limiter allowed 5, refused the rest |
| FL01_09 | 20 rapid submissions from one creator | 429 | — | — | **HELD** | limiter allowed 5, refused the rest |
| FL01_10 | 20 rapid submissions from one creator | 429 | — | — | **HELD** | limiter allowed 5, refused the rest |
| FL01_11 | 20 rapid submissions from one creator | 429 | — | — | **HELD** | limiter allowed 5, refused the rest |
| FL01_12 | 20 rapid submissions from one creator | 429 | — | — | **HELD** | limiter allowed 5, refused the rest |

**Ten audit log entries from the run** (from `logs/audit.jsonl`, the full 55 entries for the run are in `results/audit_extract.json`). They are, in order: six false positives or misses (FP03, FP05, EV05, PI02, MF03, MF06), a right-to-left text called AI (MF07), a held evasion (EV10), a rate-limit rejection from the flood rows, and a 400 rejection for a missing `creator_id`:

```json
{"timestamp": "2026-11-08T23:52:08+00:00", "content_id": "ee8a99fe-2bff-4645-8a1c-8724e203ab97", "creator_id": "attacker_FP03", "guess": "ai", "model_score": 0.8051, "style_score": 0.6223, "combined_score": 0.7137, "label": "This looks like it may have been written with AI. Our tools can be wrong, especially on plain or simple writing. If this is your own work, you can appeal and a person will take a look.", "status": "decided"}
{"timestamp": "2026-11-08T23:52:08+00:00", "content_id": "31ee40eb-e426-4b8b-9575-6abc3c73a873", "creator_id": "attacker_FP05", "guess": "ai", "model_score": 0.8005, "style_score": 0.6259, "combined_score": 0.7132, "label": "This looks like it may have been written with AI. Our tools can be wrong, especially on plain or simple writing. If this is your own work, you can appeal and a person will take a look.", "status": "decided"}
{"timestamp": "2026-11-08T23:52:06+00:00", "content_id": "1d8c7ff4-1aa0-4261-9840-eefdf4868230", "creator_id": "attacker_EV05", "guess": "human", "model_score": 0.3212, "style_score": 0.327, "combined_score": 0.3241, "label": "This looks like it was written by a person.", "status": "decided"}
{"timestamp": "2026-11-08T23:52:09+00:00", "content_id": "afa38c58-f237-4c17-9348-93ac0362e351", "creator_id": "attacker_PI02", "guess": "human", "model_score": 0.2044, "style_score": 0.3111, "combined_score": 0.2577, "label": "This looks like it was written by a person.", "status": "decided"}
{"timestamp": "2026-11-08T23:52:10+00:00", "content_id": "33131674-02f7-4ddf-b040-9ebcf7f05aee", "creator_id": "attacker_MF03", "guess": "human", "model_score": 0.0, "style_score": 0.5, "combined_score": 0.25, "label": "This looks like it was written by a person.", "status": "decided"}
{"timestamp": "2026-11-08T23:52:12+00:00", "content_id": "d3115739-0409-4188-98e6-1d2bc99ae9e6", "creator_id": "attacker_MF06", "guess": "ai", "model_score": 0.9969, "style_score": 0.8333, "combined_score": 0.9151, "label": "This looks like it may have been written with AI. Our tools can be wrong, especially on plain or simple writing. If this is your own work, you can appeal and a person will take a look.", "status": "decided"}
{"timestamp": "2026-11-08T23:52:12+00:00", "content_id": "bee9fee8-bb97-475a-a5e5-e1a2186d6e18", "creator_id": "attacker_MF07", "guess": "ai", "model_score": 0.9064, "style_score": 0.8333, "combined_score": 0.8699, "label": "This looks like it may have been written with AI. Our tools can be wrong, especially on plain or simple writing. If this is your own work, you can appeal and a person will take a look.", "status": "decided"}
{"timestamp": "2026-11-08T23:52:07+00:00", "content_id": "15a396dc-1fa7-42f5-8e4d-780ebbd5ab99", "creator_id": "attacker_EV10", "guess": "ai", "model_score": 0.9792, "style_score": 0.729, "combined_score": 0.8541, "label": "This looks like it may have been written with AI. Our tools can be wrong, especially on plain or simple writing. If this is your own work, you can appeal and a person will take a look.", "status": "decided"}
{"timestamp": "2026-11-08T23:52:13+00:00", "creator_id": "attacker_flood", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute"}
{"timestamp": "2026-11-08T23:52:12+00:00", "creator_id": "unknown", "event": "rejected", "status": "rejected", "reason": "invalid_creator_id", "route": "/submit", "status_code": 400}
```

MF02 (the one-character text) is not among them because it left no entry at all. The route crashed with a 500 before it reached `audit.log_decision`, so the request that broke the service is the one request in the run with no trace in the log.

**The single worst outcome** — the one I'd least want to explain to a writer whose work got caught by it:

FP03, a non-native English speaker writing carefully about their first month in a new country (a 418-character piece in short, simple, correct sentences about arriving in a new country). It came back with a model score of 0.805, a style score of 0.622 and a combined 0.714, so the service said: "This looks like it may have been written with AI. Our tools can be wrong, especially on plain or simple writing. If this is your own work, you can appeal and a person will take a look." That is the writer my label text warns about, and it is exactly the person least likely to feel able to appeal. Both signals agreed, so the second signal did not rescue it the way it did for my own funeral paragraph.

---

## Run Log and Verdicts

Run on 2026-11-08 with the service from the previous unit plus the rate limiter, `python run_eval.py --label before` (criteria 1, 2, 3, 5) and `python appeal_check.py --label before` (criterion 4). Every trial of every criterion came out identical to the other two, which is expected because neither signal is random. Files: `results/run_2026-11-08_1528_before.md` and `results/appeal_2026-11-08_1535_before.md`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. My own writing flagged as AI | at most 1 of 10 labeled high-confidence AI | 0 of 11 | 0 of 11 | 0 of 11 | MET |
| 2. Score spread | average combined score of 5 AI texts at least 0.3 above 5 of mine | 0.204 (0.685 vs 0.481) | 0.204 | 0.204 | MISSED |
| 3. Label coverage | across 15 texts, each of the 3 labels at least twice | AI 5, unsure 9, human 1 | AI 5, unsure 9, human 1 | AI 5, unsure 9, human 1 | MISSED |
| 4. Appeal path | 3 real appeals return `under_review` and are logged, 2 fake IDs return an error | 3/3 and 2/2 | 3/3 and 2/2 | 3/3 and 2/2 | MET |
| 5. Bad input | 5 of 5 bad inputs return a clear error message and none crash the service | 5/5 | 5/5 | 5/5 | MET |

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


*Attack run: the 9 evasion attacks that got through (EV01 to EV09).* The stage differs by attack, which is the useful finding. Signal one is the weak stage for EV01 (typos: model score 0.16) and EV08 (very short text: 0.25), because rare or broken words and short inputs raise perplexity and look human. Signal two is the weak stage for EV02, EV06 and EV07, where broken-up sentences, one very long plus one very short sentence, and punctuation padding pulled the style score to 0.32, 0.34 and 0.24 while signal one stayed above 0.57. Note that this contradicts my first guess for typos: I expected typos to fool the style signal, but EV01's style score was 0.56 (still AI-like) and it was the model signal that moved. EV03, EV04 and EV09 left both signals in the middle (0.42 to 0.70) and averaged to about 0.56 to 0.59. EV05, the heavy editing pass, pulled both signals down and was the only one to get the HUMAN label (combined 0.324). Only EV10, a repeated stanza structure, scored high on both and kept the AI label (0.854).

*The pattern behind all nine.* My combining rule is a 50/50 average and the AI line is 0.65. For the average to exceed 0.65, both signals have to be high: if either signal is 0.30 or below, even a perfect 1.0 from the other gives only 0.65. So the AI label works like an AND, and defeating either one signal is enough to escape it. That is one problem across nine attacks, at the combining rule, not nine separate ones.

*Attack run: the 6 false positives (FP02 to FP07).* The stage is both signals, and the second one does not help. These are genuine human texts: a formal register, a non-native speaker, a student essay, technical documentation, a formal template and a deliberate repetition. Signal one scored them 0.74 to 0.88 because plain, conventional or repeated wording is very predictable to GPT-2. Signal two scored them 0.47 to 0.63, because even-length sentences and little punctuation variety are exactly what it reads as machine-like. Both fail in the same direction, so averaging cannot rescue them the way it rescued my own funeral paragraph (model 0.74, style 0.39). This also exposes a gap in my own testing: criterion 1 was MET only because my test pieces are casual, typo-filled and comma-spliced, which both signals read as human. The attack set's plain and formal writers are the ones my criterion did not cover.

*Attack run: the 5 malformed inputs that got a confident label (MF02, MF03, MF05, MF06, MF07).* MF02 (one character) is a crash at the route: signal one raised `ValueError: Text is too short to score` and `app.py::submit` does not catch it, so Flask returned a 500 and, because the exception happened before `audit.log_decision`, no log entry was written. The other four are scored and labeled when they should have been refused. The route checks that `text` is a non-empty string and under 20000 characters, but not that it contains any writing. Control characters scored 0.0 on signal one (HUMAN label), and a very long single word, emoji only and right-to-left script scored 0.998, 0.997 and 0.906. For the last two, signal two's `words()` only matches Latin letters and digits, so non-Latin text has zero words and `style_signal` returns 0.83 (AI-like) for them.

*Attack run: the 1 prompt injection that got through (PI02).* The stage is signal one, and the mechanism is not that the service obeyed the instruction. Neither signal can read an instruction: signal one measures predictability and signal two measures shape. The AI-style essay body appears to be the same in PI01, PI02, PI03 and PI05, and only the prefix differs. PI02 added an odd, system-style prefix and its model score was 0.204, against 0.463 for the plain-English "ignore previous instructions" (PI01) and 0.594 for the polite note (PI03). So the unusual wording of the prefix raised perplexity, which is the same mechanism as the typo and unusual-word evasions, and the injection worked by accident. PI04 and PI05 were held for structural reasons: the label text is fixed in `scoring.py::score_to_label` and never built from user text, and the text is never written to the audit log.

Criterion 4 and 5 were met in all three trials and need no diagnosis. I did not revise any criterion.

---

## The Improvement

**What I changed:** One number in `config.py`: `AI_THRESHOLD` from 0.65 to 0.75. Nothing else moved: the weights are still 0.5 and 0.5, `HUMAN_THRESHOLD` is still 0.35, and the signals, the labels and the route are untouched. The "unsure" band is now 0.35 to 0.75 instead of 0.35 to 0.65.

**Which diagnosis pointed at it:** The worst outcome of the attack run was a false positive: FP03, a non-native English speaker writing carefully, labeled as possibly AI at a combined 0.714. Six of the eight staff false-positive cases were accused (FP02 to FP07, combined 0.675 to 0.714), and both of my signals failed in the same direction on them, so no combining rule could have rescued them. The cheapest honest fix at the stage where the accusation is made (the label mapping) is to require stronger evidence before saying it. I chose this over input validation, which would fix the five malformed inputs, because a wrongly accused writer is the mistake my own Milestone 1 reasoning says is the expensive one.

**What I predicted before running it again** (written before the after runs, from the combined scores in the before runs):

- All six accused writers (FP02 to FP07) move to "unsure", so false positives that broke go from 6 to 0.
- MF05 (the very long single word, combined 0.749) also drops to "unsure". MF06 and MF07 stay labeled AI (0.915 and 0.870).
- The evasion attacks do not change: nine already got a non-AI label, and EV10 (0.854) keeps the AI label.
- The cost: of my 15 label-coverage texts, only one has a combined score above 0.75, so the AI label appears once instead of four times. Criterion 3 stays MISSED and the AI side of it gets worse. Criterion 1 stays MET. Criterion 2 does not change because it compares scores, not labels.
- Overall I expect BROKE to fall from 21 to 14 of 56.

### Attack Run — After

`python run_attacks.py --set attack_set --label after` after the change, written to `results/attack_run_2026-11-08_1601_after.md`. Same 56 attacks, same marking rules as Attack Run — Before. Every score (model, style and combined) is identical to the before run, as expected, because the only thing that changed is where the AI line sits. The changes are all in the label column:

| ID | Label before | Label after | Mark before | Mark after |
|---|---|---|---|---|
| FP02 | AI | UNSURE | BROKE | HELD |
| FP03 | AI | UNSURE | BROKE | HELD |
| FP04 | AI | UNSURE | BROKE | HELD |
| FP05 | AI | UNSURE | BROKE | HELD |
| FP06 | AI | UNSURE | BROKE | HELD |
| FP07 | AI | UNSURE | BROKE | HELD |
| MF05 | AI | UNSURE | BROKE | HELD |

Everything else, including the 500 on MF02, came back the same. Totals:

| Family | Attacks | BROKE before | BROKE after |
|---|---|---|---|
| evasion | 10 | 9 | 9 |
| false_positive | 8 | 6 | 0 |
| prompt_injection | 6 | 1 | 1 |
| malformed (MF) | 8 | 5 | 4 |
| malformed (RQ) | 12 | 0 | 0 |
| flood_same_creator | 12 | 0 | 0 |
| **Total** | **56** | **21** | **14** |

**Run Log — After** (`python run_eval.py --label after`, `results/run_2026-11-08_1601_after.md`, and `python appeal_check.py --label after`, `results/appeal_2026-11-08_1601_after.md`). All three trials of every criterion were identical again.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. My own writing flagged as AI | at most 1 of 10 labeled high-confidence AI | 0 of 11 | 0 of 11 | 0 of 11 | MET |
| 2. Score spread | average combined score of 5 AI texts at least 0.3 above 5 of mine | 0.204 | 0.204 | 0.204 | MISSED |
| 3. Label coverage | across 15 texts, each of the 3 labels at least twice | AI 1, unsure 13, human 1 | AI 1, unsure 13, human 1 | AI 1, unsure 13, human 1 | MISSED |
| 4. Appeal path | 3 real appeals return `under_review` and are logged, 2 fake IDs return an error | 3/3 and 2/2 | 3/3 and 2/2 | 3/3 and 2/2 | MET |
| 5. Bad input | 5 of 5 bad inputs return a clear error message and none crash the service | 5/5 (4 got a 400, 1 got a 429) | 5/5 (same) | 5/5 (same) | MET |

Criterion 3 got worse on its AI side (the AI label went from 4 of 15 texts to 1, so now two of the three labels are under the target of 2, where before only the human label was). Criterion 5 changed shape without changing verdict: the request with no `creator_id` came back as a 429 instead of a 400 in all three trials. That is not an effect of the threshold. The attack run had just sent a burst of requests with no usable `creator_id`, and all of those share one rate-limit bucket (keyed by address, 5 per minute), so the eval's one such request was refused by the limiter before it reached the route. It still returned a clear error message and did not crash, so it meets the criterion as written.

Real output, criterion 3 after (trial 1, produced by `run_eval.py::main` calling `app.py::submit`), the one that changed:

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
    "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
    "sent": "Technology has transformed the way people communicate in modern societ"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.6502,
    "model_score": 0.875,
    "style_score": 0.4254,
    "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
    "sent": "Regular exercise is an important part of maintaining a healthy lifesty"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.6902,
    "model_score": 0.7948,
    "style_score": 0.5856,
    "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
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

**Did it help, and how do I know:**

Yes on the target, and at a cost. My prediction was that false positives broken would fall from 6 to 0, MF05 would also move to "unsure", the evasion attacks would not change, the AI label would shrink to one text in my coverage set, and BROKE would fall from 21 to 14 of 56. The after run matches all of that: exactly the seven attacks I named changed (FP02 to FP07 and MF05), BROKE is 14 of 56, and the label coverage set has one AI label. I know it helped because the same 56 inputs and identical scores produced fewer accusations, so the difference can only come from the threshold. None of the staff's eight false-positive cases now gets the AI label, including the non-native speaker (FP03, combined 0.714).

What it cost, which I also predicted: real AI text now needs a combined score above 0.75 to be called AI. Of my 15 coverage texts only one clears it, and three AI paragraphs (combined 0.65 to 0.69) that used to be called AI are now "unsure". So fewer writers are wrongly accused and more AI text goes unlabeled, and that is the trade I said in Milestone 1 I would choose. It did not touch the nine evasions or the four malformed inputs that still get confident labels, and it does not make signal two separate better (criterion 2 is still 0.204), so it fixes the symptom of the worst outcome and not its cause.

---

## What's Still Broken

- **Evasion, 9 of 10 attacks still get a non-AI label (EV01 to EV09).** Diagnosis in Run Log and Verdicts: the combining rule is a 50/50 average, so the AI label needs both signals high and escaping either one is enough. What I would do: a rule that lets one very strong signal count on its own, or a third signal that is hard to move by rewording. I stopped because that is a redesign of `combine_signals` and a new signal, not one measurable change, and it would also bring back false positives.
- **Confident labels on junk and non-Latin text (MF03, MF04 human; MF06, MF07 AI).** The stylometry `words()` helper only matches Latin letters and digits, so text in other scripts has zero words and scores as if it were empty. What I would do: validate input (minimum number of real words, supported script) and return a 400. I stopped because I chose the threshold fix over input validation; this is the next thing I would do.
- **MF02 returns a 500 and leaves no audit log entry.** A one-character text makes `detector.model_signal` raise a ValueError that nothing catches. What I would do: a minimum length check in `/submit` that goes through `_refuse`, so it is a 400 and a logged rejection. I stopped because it is a different stage from the one I improved and I wanted the before/after to change one thing.
- **Prompt injection, 1 of 6 still breaks (PI02).** The service did not obey the instruction; the odd prefix text happened to pull signal one down far enough for a HUMAN label. I would strip or score only the body after any leading system-style line, but a rule like that is easy to get around and I stopped there.
- **The rate limiter can be bypassed by changing `creator_id`.** It is keyed by creator, so a script that rotates ids gets a fresh 5 a minute each time. The 50 a day cap has the same hole. What I would do: also key on the address, or require a real account. I stopped because there is no account system in this project.
- **Criterion 2 MISSED (gap 0.204 against 0.3).** Signal two barely separates AI from human text (gap 0.051, scores only 0.36 to 0.63). Changing weights toward signal one would reach the target on my ten texts, but I would be fitting to ten samples, so I did not.
- **Criterion 3 MISSED (AI 1, unsure 13, human 1).** The improvement made the AI side worse on purpose. The human side was already short because the style signal compresses scores toward the middle.

**The trade I'd make if this ran for real:** I would keep the higher AI line (0.75), because a wrongly accused writer loses trust and work while a missed AI text is only a missed flag. The people who pay are the platform's reviewers and the honest writers whose work competes with undetected AI text, and I would say that openly in the label rather than hide it.

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

---

## Capstone

**What This Extends**

Provenance Guard, the same repository as Units 7 and 8. What's new is an input guard on `POST /submit`: text that can't be scored gets a clear, logged 400 instead of crashing the service or getting a confident label. It also adds a catch-all so an unexpected failure while scoring returns a logged error instead of an HTML crash page, and the audit log now records how long each request took and what text came in.

**The Shape**

B, harden against failure. The Unit 8 attack run left a list of bad-input failures: a one-character text crashed the service with a 500 and left no log entry (MF02), and control characters, one very long word, emoji and right-to-left script all got scored and labeled as if they were writing (MF03, MF05, MF06, MF07). This unit's extension makes the service refuse those inputs honestly.

Out of scope, on purpose:
- The `creator_id` rotation that gets around the rate limiter. It needs an account system this project doesn't have.
- Any change to the two signals, the weights or the thresholds. That is a different problem (the evasion attacks) and would mix two changes together.
- A hosted deploy. The detector loads GPT-2 locally, which doesn't fit a free 512 MB host, so this runs locally with logs (Path B).

**Running It**

Path B, local with logs. The service runs on my laptop with `python app.py`, and RUNNING.md holds the start command, the Python version (3.12), the pinned dependencies and the one model file (GPT-2, about 550 MB). I took Path B from the start because GPT-2 does not fit a free 512 MB host. Both the before and after runs below were produced this way, and their results and the audit log are committed in `results/` and `logs/audit.jsonl`. One honest gap: I have not yet followed RUNNING.md from a fresh clone in a new folder, so a missing step there would not have been caught.

**Instrumentation**

Every request to `/submit`, accepted or refused, appends one JSON line to `logs/audit.jsonl` (written by `audit.py`, called from `app.py::submit` and `app.py::_refuse`). A scored request records: `timestamp`, `content_id`, `creator_id`, `guess`, `model_score`, `style_score`, `combined_score`, `label`, `status`, plus the capstone additions `duration_ms` (time from the start of the request to the log write) and `input` (the first 200 characters of the text) with `input_chars` (its full length). A refused request records `timestamp`, `creator_id`, `event: rejected`, `status`, `reason`, `route`, `status_code`, `duration_ms`, `input` and `input_chars`. The last four of the entries below are failed runs (rejected inputs). Real entries, from trial 1 of the after run (`capstone_run.py`, read back through `GET /log`); labels and long inputs are cut for width, nothing else is changed:

```
{"combined_score": 0.4284, "content_id": "f30b9f08-af17-4639-b7d1-28a645bb6753", "creator_id": "cap_t1_ES2", "duration_ms": 122.1, "guess": "human", "input": "Mi hermana vive en Madrid desde hace tres años y trabaja en ...", "input_chars": 102, "label": "We can't tell for certain how this was w...", "model_score": 0.3133, "status": "decided", "style_score": 0.5435, "timestamp": "2026-11-15T22:48:32+00:00"}
{"combined_score": 0.3876, "content_id": "6274a190-7875-49f9-b1db-846b5b7a3124", "creator_id": "cap_t1_ES4", "duration_ms": 75.7, "guess": "human", "input": "Por la mañana me gusta tomar un café caliente mientras leo l...", "input_chars": 95, "label": "We can't tell for certain how this was w...", "model_score": 0.2752, "status": "decided", "style_score": 0.5, "timestamp": "2026-11-15T22:48:32+00:00"}
{"combined_score": 0.5647, "content_id": "590efbe0-677f-4a7e-bba0-1111b0272365", "creator_id": "cap_t1_N1", "duration_ms": 107.4, "guess": "ai", "input": "At a funeral, an old woman is wearing all black elegant dres...", "input_chars": 247, "label": "We can't tell for certain how this was w...", "model_score": 0.7372, "status": "decided", "style_score": 0.3922, "timestamp": "2026-11-15T22:48:32+00:00"}
{"combined_score": 0.3963, "content_id": "476300b7-ade0-4832-9fc8-dae37ccdea34", "creator_id": "cap_t1_N2", "duration_ms": 83.1, "guess": "human", "input": "I spilled coffee on my keyboard this morning and spent twent...", "input_chars": 177, "label": "We can't tell for certain how this was w...", "model_score": 0.4299, "status": "decided", "style_score": 0.3627, "timestamp": "2026-11-15T22:48:33+00:00"}
{"combined_score": 0.5776, "content_id": "a8783aef-6f26-4a17-a16f-d68fb32c35fe", "creator_id": "cap_t1_N3", "duration_ms": 195.4, "guess": "ai", "input": "My experience from SolarCity has prepared me to take on bigg...", "input_chars": 609, "label": "We can't tell for certain how this was w...", "model_score": 0.6534, "status": "decided", "style_score": 0.5017, "timestamp": "2026-11-15T22:48:33+00:00"}
{"combined_score": 0.3237, "content_id": "2f0a897c-f411-475e-906f-073fb9a47ae7", "creator_id": "cap_t1_N4", "duration_ms": 83.0, "guess": "human", "input": "Etsy is a great platform for people who wants to test out st...", "input_chars": 153, "label": "This looks like it was written by a pers...", "model_score": 0.201, "status": "decided", "style_score": 0.4464, "timestamp": "2026-11-15T22:48:33+00:00"}
{"combined_score": 0.541, "content_id": "5bfb005e-c341-4d91-97a5-35306c13ba4d", "creator_id": "cap_t1_N5", "duration_ms": 230.9, "guess": "ai", "input": "Etsy is a great platform for people who wants to test out st...", "input_chars": 510, "label": "We can't tell for certain how this was w...", "model_score": 0.4501, "status": "decided", "style_score": 0.6319, "timestamp": "2026-11-15T22:48:33+00:00"}
{"combined_score": 0.2486, "content_id": "2ba900ac-187b-4dd2-a87d-e22f0d797a55", "creator_id": "cap_t1_N6", "duration_ms": 370.7, "guess": "human", "input": "So ngl I’m not new to online business I had quite few Etsy s...", "input_chars": 941, "label": "This looks like it was written by a pers...", "model_score": 0.0985, "status": "decided", "style_score": 0.3988, "timestamp": "2026-11-15T22:48:33+00:00"}
{"creator_id": "cap_t1_MF03", "duration_ms": 0.4, "event": "rejected", "input": "\u0001\u0002 test \u001b[31mred\u001b[0m", "input_chars": 20, "reason": "too_few_words", "route": "/submit", "status": "rejected", "status_code": 400, "timestamp": "2026-11-15T22:48:32+00:00"}
{"creator_id": "cap_t1_NEW1", "duration_ms": 0.4, "event": "rejected", "input": null, "input_chars": null, "reason": "invalid_text", "route": "/submit", "status": "rejected", "status_code": 400, "timestamp": "2026-11-15T22:48:32+00:00"}
{"creator_id": "unknown", "duration_ms": 0.5, "event": "rejected", "input": null, "input_chars": null, "reason": "invalid_json", "route": "/submit", "status": "rejected", "status_code": 400, "timestamp": "2026-11-15T22:48:32+00:00"}
{"creator_id": "cap_t1_FR1", "duration_ms": 0.4, "event": "rejected", "input": "Hier soir, nous avons préparé un grand dîner pour toute la f...", "input_chars": 102, "reason": "not_english", "route": "/submit", "status": "rejected", "status_code": 400, "timestamp": "2026-11-15T22:48:32+00:00"}
```

**What It Costs**

There is no API spend: signal one runs GPT-2 on my own laptop. The cost I measured is seconds of compute for one scored request, read from `duration_ms` in the service's own log. Across the 57 warm scored requests in the before and after runs (30 and 27; criterion 5's measurements), the mean was 132 ms (range 66 to 390 ms). The one-off cost is the model load: the first scored request after starting the app took 26.6 s. Refused requests cost about 1 ms.

For a hundred people a day, one scored submission each: 100 x 0.13 s = about 13 s of compute a day, plus one 27 s model load per start if the service restarts daily, so roughly 40 s a day in total on this laptop. That is a measurement on my Mac, not a hosting quote.

**Run Log and Verdicts**

Produced by `capstone_run.py::main` and `capstone_run.py::run_trial` (inputs in `capstone_inputs.json`), service running as in RUNNING.md. Raw results: `results/capstone_2026-11-15_1436_before.json` and `.md`. Every request used its own `creator_id`, so the rate limiter was not what was measured.

**Before the improvement**

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Bad input refused with a 400 and a message | 12 of 12 | 12/12 | 12/12 | 12/12 | MET |
| 2. French/Spanish refused with a 400 | 9 of 10 | 0/10 | 0/10 | 0/10 | MISSED |
| 3. Every refusal logged with `input` and `duration_ms` | 22 of 22 | 9/22 | 9/22 | 9/22 | MISSED |
| 4. My own paragraphs scored, not refused | 9 of 10 | 10/10 | 10/10 | 10/10 | MET |
| 5. Warm scored request under 3 s | 9 of 10 | 10/10 | 10/10 | 10/10 | MET |

All three trials came out identical, as expected: nothing here involves randomness, and the model is run the same way each time.

Real output, trial 1 (produced by `capstone_run.py::run_trial`, which calls `app.py::submit`).

Criterion 1, status and error for the 12 bad inputs:

```
MF01  400  invalid_text: text is required and must be a non-empty string.
MF02  400  too_few_words: text needs at least 10 words written in Latin letters to be scored (found 1).
MF03  400  too_few_words: text needs at least 10 words written in Latin letters to be scored (found 3).
MF04  400  too_few_words: text needs at least 10 words written in Latin letters to be scored (found 0).
MF05  400  too_few_words: text needs at least 10 words written in Latin letters to be scored (found 1).
MF06  400  too_few_words: text needs at least 10 words written in Latin letters to be scored (found 0).
MF07  400  too_few_words: text needs at least 10 words written in Latin letters to be scored (found 0).
MF08  400  text_too_long: text must be 20000 characters or fewer.
NEW1  400  invalid_text: text is required and must be a non-empty string.
NEW2  400  invalid_text: text is required and must be a non-empty string.
NEW3  400  invalid_json: Send a JSON object with text and creator_id.
NEW4  400  too_few_words: text needs at least 10 words written in Latin letters to be scored (found 9).
```

Criterion 2, the ten French and Spanish sentences (none refused):

```
FR1  200  confidence 0.6651  model_score 0.2642  This looks like it was written by a person
FR2  200  confidence 0.5752  model_score 0.3328  We can't tell for certain how this was wri
FR3  200  confidence 0.7243  model_score 0.1685  This looks like it was written by a person
FR4  200  confidence 0.6184  model_score 0.4021  We can't tell for certain how this was wri
FR5  200  confidence 0.5789  model_score 0.3237  We can't tell for certain how this was wri
ES1  200  confidence 0.6806  model_score 0.1055  This looks like it was written by a person
ES2  200  confidence 0.5716  model_score 0.3133  We can't tell for certain how this was wri
ES3  200  confidence 0.6962  model_score 0.202  This looks like it was written by a person
ES4  200  confidence 0.6124  model_score 0.2752  We can't tell for certain how this was wri
ES5  200  confidence 0.6186  model_score 0.2277  We can't tell for certain how this was wri
```

Criterion 3, the 12 rejected entries the service wrote to `logs/audit.jsonl` (via `audit.py::log_rejection`, called from `app.py::_refuse`). `input` is null on three of them, and the ten foreign-language sentences have no rejected entry at all because they were scored:

```
{"timestamp": "2026-11-15T22:35:58+00:00", "reason": "invalid_text", "status_code": 400, "input": "     \n\n   \t  ", "input_chars": 13, "duration_ms": 0.7}
{"timestamp": "2026-11-15T22:35:58+00:00", "reason": "too_few_words", "status_code": 400, "input": "a", "input_chars": 1, "duration_ms": 0.3}
{"timestamp": "2026-11-15T22:35:58+00:00", "reason": "too_few_words", "status_code": 400, "input": "\u0001\u0002 test \u001b[31mred\u001b[0m", "input_chars": 20, "duration_ms": 0.3}
{"timestamp": "2026-11-15T22:35:58+00:00", "reason": "too_few_words", "status_code": 400, "input": "!!! ??? ... ,,, ;;; --- ((( )))", "input_chars": 31, "duration_ms": 0.6}
{"timestamp": "2026-11-15T22:35:58+00:00", "reason": "too_few_words", "status_code": 400, "input": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "input_chars": 4000, "duration_ms": 0.4}
{"timestamp": "2026-11-15T22:35:58+00:00", "reason": "too_few_words", "status_code": 400, "input": "🙂🙃😀😃😄😁😆😅😂🤣🙂🙃😀😃😄😁😆😅😂🤣🙂🙃😀😃😄😁😆😅😂🤣🙂🙃😀😃😄😁😆😅😂🤣", "input_chars": 200, "duration_ms": 0.4}
{"timestamp": "2026-11-15T22:35:58+00:00", "reason": "too_few_words", "status_code": 400, "input": "هذا نص باللغة العربية لاختبار كيفية تعام", "input_chars": 105, "duration_ms": 0.7}
{"timestamp": "2026-11-15T22:35:58+00:00", "reason": "text_too_long", "status_code": 400, "input": "We got to the campsite about four. The p", "input_chars": 57640, "duration_ms": 0.5}
{"timestamp": "2026-11-15T22:35:58+00:00", "reason": "invalid_text", "status_code": 400, "input": null, "input_chars": null, "duration_ms": 0.3}
{"timestamp": "2026-11-15T22:35:58+00:00", "reason": "invalid_text", "status_code": 400, "input": null, "input_chars": null, "duration_ms": 0.5}
{"timestamp": "2026-11-15T22:35:58+00:00", "reason": "invalid_json", "status_code": 400, "input": null, "input_chars": null, "duration_ms": 0.3}
{"timestamp": "2026-11-15T22:35:58+00:00", "reason": "too_few_words", "status_code": 400, "input": "I walked to the coffee shop this morning", "input_chars": 47, "duration_ms": 0.6}
```

Criterion 4, my ten paragraphs:

```
N1  200  ai  confidence 0.5647
N2  200  human  confidence 0.6037
N3  200  ai  confidence 0.5776
N4  200  human  confidence 0.6763
N5  200  ai  confidence 0.541
N6  200  human  confidence 0.7514
N7  200  human  confidence 0.9044
N8  200  human  confidence 0.8625
N9  200  human  confidence 0.7002
N10 200  human  confidence 0.7385
```

Criterion 5, `duration_ms` of the same ten scored requests (from `audit.py::log_decision` entries, matched by `content_id`):

```
[107.6, 80.8, 196.2, 75.1, 170.9, 390.2, 69.3, 67.8, 66.2, 67.5]
```

**Diagnosis**

*Criterion 2 (MISSED, 0 of 10).* The stage is the input guard, `guard.py::check_text`, and the signal behind it. The guard counts words with `stylometry.words`, which only keeps the letters a to z, digits and apostrophes, so a French or Spanish sentence of ordinary length still counts as 16 to 23 "words" and passes. Nothing in the guard checks which language the text is in. The text then reaches signal one, GPT-2, which was trained on English: it finds French and Spanish surprising, so `model_score` comes out low (0.11 to 0.40), and a low model score reads as human. Four of the ten were labeled "written by a person" at 0.67 to 0.72 confidence, the other six "unsure". The mechanism is a missing check at the guard, which sends text the detector can't judge to a detector that gives a confident-looking answer anyway.

*Criterion 3 (MISSED, 9 of 22).* Two separate causes.
- Ten of the 13 misses are the French and Spanish sentences. They were never refused, so no rejected entry exists to be logged. This is the same root as criterion 2, not a logging fault.
- Three misses are real logging faults: a missing `text` field (NEW1), `text` sent as a number (NEW2) and broken JSON (NEW3). `app.py::_input_fields` only records `input` when `text` is a string, so these entries exist, with a timestamp, reason and `duration_ms`, but `input` is null. What came in is not recorded for them, which is exactly what the criterion asked for.

*Pattern.* Criterion 2 and ten of the 13 criterion 3 misses are one problem with two symptoms: the guard has no language check. The other three criterion 3 misses are a second, smaller problem in how rejected requests are logged.

*Criteria met.* 1, 4 and 5 were met. Criterion 5 was met with room to spare, which means the target was set too low: the ten warm scored requests took 66 to 390 ms (30 of 30 across the three trials, mean 127 ms), where I allowed 3,000 ms. I would tighten it to 9 of 10 under 500 ms. I set 3 seconds from the 26-second first request, which was the model loading, not the cost of a normal request.

**The Improvement**

*What I changed:* One change in `guard.py::check_text`, with its setting in `config.py`: an English check. The share of a text's words that are very common English words (the, and, to, of, was, and about 50 more, listed in `guard.py::ENGLISH_COMMON`) must be at least 10% (`ENGLISH_COMMON_MIN_SHARE = 0.10`), or the request is refused with a 400 `not_english`. Ordinary English is about a third of these words and French or Spanish is almost none.

*Which diagnosis it follows from:* The criterion 2 diagnosis (no language check at the guard). It should also fix ten of the 13 criterion 3 misses, because refusing the foreign sentences means they get rejected entries. It does nothing about the three `input` null entries (NEW1 to NEW3), so I am leaving those and expect criterion 3 to still miss.

*How I chose 10%:* I measured the share on my own English texts and on five other French and Spanish sentences I wrote separately from the test set (shares of 0 to 4% on those, and 22% to 48% on the English, apart from one list-style line at 8%). 10% sits in the gap.

*What I predicted before running it again* (from those shares, computed before the after run):
- Eight of the ten test sentences are refused. Two slip through, ES2 (13%) and ES4 (11%), so criterion 2 gets 8 of 10 and stays MISSED.
- One of my own paragraphs is refused by mistake: the list-style line "Soft life: slow mornings, coffee, home, ..." (8%, N7). Criterion 4 drops to 9 of 10, which still meets its target.
- Criterion 3 goes from 9 of 22 to 17 of 22 (eight more foreign refusals logged), still MISSED because of NEW1 to NEW3 and the two slips.
- Criteria 1 and 5 do not change.

**After the improvement**

Same `capstone_run.py`, same inputs, three trials. Raw results: `results/capstone_2026-11-15_1448_after.json` and `.md`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Bad input refused with a 400 and a message | 12 of 12 | 12/12 | 12/12 | 12/12 | MET |
| 2. French/Spanish refused with a 400 | 9 of 10 | 8/10 | 8/10 | 8/10 | MISSED |
| 3. Every refusal logged with `input` and `duration_ms` | 22 of 22 | 17/22 | 17/22 | 17/22 | MISSED |
| 4. My own paragraphs scored, not refused | 9 of 10 | 9/10 | 9/10 | 9/10 | MET |
| 5. Warm scored request under 3 s | 9 of 10 | 9/10 | 9/10 | 9/10 | MET |

Real output, trial 1 (produced by `capstone_run.py::run_trial`).

The ten foreign-language sentences, status and error (eight refused, two scored):

```
FR1  400  not_english
FR2  400  not_english
FR3  400  not_english
FR4  400  not_english
FR5  400  not_english
ES1  400  not_english
ES2  200  scored: We can't tell for certain how 
ES3  400  not_english
ES4  200  scored: We can't tell for certain how 
ES5  400  not_english
```

The one of my own paragraphs that was refused by mistake (N7, a short list-style line), as input id, status and error:

```
[('N7', 400, 'not_english')]
```

**Did it help, and how do I know:** Yes, partly. Criterion 2 went from 0 of 10 to 8 of 10 and criterion 3 from 9 of 22 to 17 of 22, so the ten that were never refused are now eight refused and logged. It is still a miss on both because two sentences (ES2 at 13% common English words and ES4 at 11%) are above my 10% line and three log entries still have no `input` (NEW1 to NEW3, which the change was never aimed at). I know the change did it because only the English check changed between the two runs, the inputs were identical, and the trials came out identical three times. The result also matched my prediction exactly (8 of 10, one of my own paragraphs refused, 17 of 22), which tells me I understood the mechanism.

**What it cost elsewhere:** One of my own ten paragraphs, the list-style line N7, is now refused as "not English" (it has few small words, 8%), so criterion 4 fell from 10 of 10 to 9 of 10. It still meets its target of 9 of 10, but that is exactly the slip I said I could tolerate, and it is a real writer wrongly refused. Criterion 5 reads 9 of 10 instead of 10 of 10 only because that refused paragraph is no longer scored, so there are nine timings instead of ten; every one of the nine was still under 400 ms. Criteria 1 and 5 otherwise did not change. I also note the refusal for foreign text is correct only by a rule of thumb (common-word share), not by actually identifying a language.

**What's Still Broken**

- *Criterion 2, 8 of 10 (target 9 of 10).* Two Spanish sentences, ES2 (13%) and ES4 (11%), have enough words that overlap with English function words (such as "a" and "me") to clear my 10% line. I would raise the line to about 15% and, better, replace the word-share rule with a real language detector. I stopped because the brief allows one improvement, and moving the line up would refuse more of my own writing: N7 is already refused at 8%, and my calibration used only five held-out sentences, so I did not trust a second number I could not test.
- *Criterion 3, 17 of 22 (target 22 of 22).* Three of the five misses are NEW1 to NEW3 (missing `text`, `text` as a number, broken JSON): `app.py::_input_fields` only logs `input` when `text` is a string. I would log the first 200 bytes of the raw request body for those. I stopped because that is a second, separate change and the language check covered ten of the 13 misses, so I chose that one. The other two misses are ES2 and ES4, the same as criterion 2.
- *Criterion 4, now 9 of 10, still MET but costing one real writer.* The list-style line N7 is refused as not English. I would fix it with the same language detector as above.
- *Criterion 5 was set too low.* All warm requests took under 400 ms, so a 3 second target tells me nothing. I would tighten it to 9 of 10 under 500 ms.
- *Known from Unit 8, not touched here:* nine of the ten evasion attacks still get a non-AI label, the rate limiter can be bypassed by changing `creator_id`, and prompt injection PI02 still gets a human label. These are out of scope for this extension, as written in The Shape.

If this were real and I had another unit, the first thing I would do is rebuild the test set much larger (50 or more sentences each in French, Spanish and several other languages, and 30 or more of my own English paragraphs, including short and list-style ones) before changing the threshold. Everything I measured about the English check rests on ten sentences, so a bigger set would tell me whether 10% is right before I tune anything.

**How I Used AI**

*Moment 1: writing the criteria.* I did not know how to decide a target, so I asked Claude how to write them. It gave me a fill-in-the-blank sentence for each, with questions to answer, and later example commands for bad inputs I had not tried. Trying those, I found that a French sentence got a confident "written by a person" label, and I wrote the French/Spanish criterion and its 9 of 10 target myself. When I was sick and could not decide the rest, I asked Claude to draft the other four from what I had found, and I approved them as drafted, with no changes. `criteria.md` says this.

*Moment 2: building and testing it.* I asked Claude to recommend the shape ("whatever you recommend") and went along with its pick of Provenance Guard and shape B. It then wrote the guard, the logging changes, the test inputs, the three-trial runner, the diagnoses, the improvement and these README sections. I ran the app and every test command on my machine and pasted back the results, tried the bad inputs by hand, and decided to count the French result as a real failure to test. I did not write the code or the diagnoses myself, and I have not re-checked every number by hand. Claude predicted the after results before the run, and they came out as predicted.
