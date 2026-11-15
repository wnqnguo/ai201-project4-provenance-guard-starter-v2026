# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---
## 1.

Of 10 pieces I wrote myself (varied styles), at most 1 is labeled high-confidence AI.

**Why this target:**

A wrongly accused writer loses trust in the service, and an appeal only fixes it after the damage is done. On a writing site, accusing a real writer costs more than missing some AI text.


---

## 2.

The average combined score of my 5 AI-written texts is at least 0.3 higher than the average of my 5 human-written texts.

**Why this target:**

If scores bunch in the middle, nearly everything is labeled "unsure" and the service tells readers nothing. A gap of 0.3 on a 0-to-1 scale is wide enough to separate the two groups.


---

## 3.

Across 15 test texts (a mix of mine and AI-written), each of the three labels appears at least twice.

**Why this target:**

If a label never fires, writers can never get that answer, even when it is the right one.


---

## 4.

I send 3 appeals for real content IDs and 2 for IDs that don't exist. All 3 real ones return status `under_review` and are recorded in the audit log next to the original decision. All 2 fake ones return a clear error and don't crash the service.

**Why this target:**

An appeal that is silently dropped leaves a wrongly labeled writer with no recourse, so every real appeal has to change status and be recorded.


---

## 5.

I send 5 bad inputs to `/submit` (empty `text`, missing `text`, whitespace-only `text`, missing `creator_id`, and enormous `text`). All 5 return a clear error message and none crash the service.

**Why this target:**

A service that crashes on bad input is unusable for everyone, not just the person who sent it, and a clear error tells the sender what to fix.


---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Capstone criteria (Unit 9)

*Drafted with Claude from what I found and decided while testing the guard by hand (the 9 of 10 foreign-language target and the French result were mine); I read them and approved them before any results existed.*

**1. Bad input is refused.** Of 12 bad inputs, 12 get an HTTP 400 with an `error` and a `message`, and none crashes the service. The 12 are the 8 malformed inputs from the Unit 8 attack set (whitespace only, one character, control characters, punctuation only, one very long word, emoji only, right-to-left script, 60,000 characters) plus a missing `text` field, a number as `text`, broken JSON, and a 9-word sentence.
**Why this target:** each of these either crashed the service or got a made-up label last unit, and a refusal is cheap, so there is no reason to accept a miss.

**2. Foreign-language text is refused.** Of 10 French and Spanish sentences of at least 10 words each (5 of each), 9 get an HTTP 400.
**Why this target:** the detector learned English, so it gave a French sentence a confident "written by a person" label, which is false assurance for anyone submitting AI-written text in another language. I allow one miss for a sentence that is mostly English names.

**3. Every refusal is logged.** After the 12 bad inputs and the 10 foreign-language sentences, 22 of 22 refusals have an entry in `logs/audit.jsonl` with `input` and `duration_ms` filled in.
**Why this target:** the one-character crash last unit left no log entry at all, and an input that leaves no trace is one I can never diagnose.

**4. Normal writing still works.** Of 10 paragraphs of my own writing, each at least 10 words, 9 get a score and a label (HTTP 200) and are not refused.
**Why this target:** wrongly refusing a real writer is the mistake this service exists to avoid, so almost none should be refused, but one slip on a short or odd paragraph is tolerable.

**5. A warm request is quick.** After the model has loaded (the first scored request is not counted), 9 of 10 scored requests finish in under 3 seconds, measured by `duration_ms` in the log.
**Why this target:** the first scored request took 26 seconds while the model loaded, and I care about the ordinary case a writer sees. 3 seconds is about what a person will wait without thinking it broke.
