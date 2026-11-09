# Attack run — after

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-08 16:01
- Auto-marked BROKE (5xx, crash, no response): **1**
- Left for you to judge: **55**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `1c9a90d7-f3f1-4105-884c-c3379f20d299` | human | 0.636 |  |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `4416d273-b9a5-4865-b7b8-351357508969` | human | 0.543 |  |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `4389e3bd-f08a-4e5d-9d59-66e057ac6559` | ai | 0.559 |  |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `eab26a6c-c4af-49ee-be39-d74287f7ea57` | ai | 0.585 |  |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `f66a27a4-ab8a-4456-9439-cc49c2d4a053` | human | 0.676 |  |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `6bdf7c16-9c21-48d8-ab23-33d1beaeb918` | human | 0.541 |  |
| EV07 | evasion | signal two: padding with punctuation | 200 | `50d9d230-4448-4ddb-93b5-35d646b867e5` | human | 0.586 |  |
| EV08 | evasion | signal one: text below the token window | 200 | `559ebff8-d9cc-4057-af99-d23d9f1306e1` | human | 0.603 |  |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `529bdad9-6825-4b31-b8da-ae6145f2e5f4` | ai | 0.564 |  |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `d4d45bee-ca5c-40db-999c-ccc8515519f9` | ai | 0.854 |  |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `3b56001c-2e84-4288-a867-7e319cc49dec` | ai | 0.574 |  |
| FP02 | false_positive | human writing in a formal register | 200 | `8cadfa0e-deb7-4cd3-8e05-30a71070a42e` | ai | 0.686 |  |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `7ca014a4-90d6-41d5-beb0-6acdf0d0ea7c` | ai | 0.714 |  |
| FP04 | false_positive | a student essay written to a rubric | 200 | `611ebccf-9943-47f8-b10b-7903b379b0b6` | ai | 0.689 |  |
| FP05 | false_positive | technical documentation written by a person | 200 | `aa67c975-3f6d-4cfb-ad9a-eb8580ffa843` | ai | 0.713 |  |
| FP06 | false_positive | a person imitating a formal template | 200 | `2488d43c-b18e-42a6-ada0-230c921b8bde` | ai | 0.693 |  |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `43dd92c9-a5d2-48e9-a984-adcb765db1f3` | ai | 0.675 |  |
| FP08 | false_positive | very short genuine human submission | 200 | `892b7dc8-da6f-4a24-8501-e89a8f346051` | human | 0.596 |  |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `94c24311-da02-490c-8ef0-1c1c78081e6d` | human | 0.562 |  |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `f64d9ae5-3c2f-4a88-97f1-62dcdc6b005a` | human | 0.742 |  |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `60d6b4b8-7d14-45dc-b435-a6c600ea843c` | ai | 0.554 |  |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `e80e4d9c-2f7b-49f0-9d1d-fe41d71ab031` | human | 0.520 |  |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `adc0357b-ff2e-4328-a910-fbfc7046f823` | human | 0.606 |  |
| PI06 | prompt_injection | instruction plus real human text | 200 | `a5077a2a-4c79-4531-b927-257bf8689683` | ai | 0.549 |  |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — |  |
| MF02 | malformed | text is a single character | 500 | `—` | — | — | BROKE |
| MF03 | malformed | text is control characters | 200 | `9f80d963-1a1a-4b96-a5f3-809689254027` | human | 0.750 |  |
| MF04 | malformed | text is only punctuation | 200 | `fdae85fc-eafb-4207-8ee1-0485e9d65343` | human | 0.578 |  |
| MF05 | malformed | text is a very long single word | 200 | `691a0a8b-51a3-4523-8e97-6b2608d2ceef` | ai | 0.749 |  |
| MF06 | malformed | text is emoji only | 200 | `388bc986-6277-47af-bd31-8c63f29b45d4` | ai | 0.915 |  |
| MF07 | malformed | text is right-to-left script | 200 | `f978c72f-4627-48df-9d0f-bd71df91499e` | ai | 0.870 |  |
| MF08 | malformed | text is 60,000 characters | 400 | `—` | — | — |  |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — |  |
| RQ02 | malformed | no creator_id | 400 | `—` | — | — |  |
| RQ03 | malformed | text is a number | 400 | `—` | — | — |  |
| RQ04 | malformed | text is a list | 400 | `—` | — | — |  |
| RQ05 | malformed | text is null | 400 | `—` | — | — |  |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — |  |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — |  |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — |  |
| RQ09 | malformed | body is empty | 400 | `—` | — | — |  |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | `—` | — | — |  |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | `—` | — | — |  |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — |  |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `92472861-4692-4d47-8010-21acdbc4a222` | human | 0.736 |  |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `93f5307f-4ec6-4e88-9f54-16493b2bb082` | human | 0.736 |  |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `d1fba0c8-2535-4967-a44a-2ffdb1271c57` | human | 0.736 |  |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `1b1ab5fb-27e5-44ae-a1fc-6cdee42bde68` | human | 0.736 |  |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c1d82261-7b98-4bdb-a770-4353ee248039` | human | 0.736 |  |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 1 | 19 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "1c9a90d7-f3f1-4105-884c-c3379f20d299",
  "creator_id": "attacker_EV01",
  "guess": "human",
  "confidence": 0.6361,
  "model_score": 0.1635,
  "style_score": 0.5644,
  "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "4416d273-b9a5-4865-b7b8-351357508969",
  "creator_id": "attacker_EV02",
  "guess": "human",
  "confidence": 0.5435,
  "model_score": 0.5943,
  "style_score": 0.3187,
  "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "4389e3bd-f08a-4e5d-9d59-66e057ac6559",
  "creator_id": "attacker_EV03",
  "guess": "ai",
  "confidence": 0.5589,
  "model_score": 0.6662,
  "style_score": 0.4515,
  "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "eab26a6c-c4af-49ee-be39-d74287f7ea57",
  "creator_id": "attacker_EV04",
  "guess": "ai",
  "confidence": 0.5854,
  "model_score": 0.6114,
  "style_score": 0.5593,
  "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "f66a27a4-ab8a-4456-9439-cc49c2d4a053",
  "creator_id": "attacker_EV05",
  "guess": "human",
  "confidence": 0.6759,
  "model_score": 0.3212,
  "style_score": 0.327,
  "label": "This looks like it was written by a person.",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "6bdf7c16-9c21-48d8-ab23-33d1beaeb918",
  "creator_id": "attacker_EV06",
  "guess": "human",
  "confidence": 0.5415,
  "model_score": 0.5727,
  "style_score": 0.3442,
  "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "50d9d230-4448-4ddb-93b5-35d646b867e5",
  "creator_id": "attacker_EV07",
  "guess": "human",
  "confidence": 0.5857,
  "model_score": 0.5862,
  "style_score": 0.2423,
  "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
  "error": null,
  "verdict": ""
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "559ebff8-d9cc-4057-af99-d23d9f1306e1",
  "creator_id": "attacker_EV08",
  "guess": "human",
  "confidence": 0.603,
  "model_score": 0.2452,
  "style_score": 0.5488,
  "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
  "error": null,
  "verdict": ""
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "529bdad9-6825-4b31-b8da-ae6145f2e5f4",
  "creator_id": "attacker_EV09",
  "guess": "ai",
  "confidence": 0.5635,
  "model_score": 0.7042,
  "style_score": 0.4228,
  "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
  "error": null,
  "verdict": ""
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "d4d45bee-ca5c-40db-999c-ccc8515519f9",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.8541,
  "model_score": 0.9792,
  "style_score": 0.729,
  "label": "This looks like it may have been written with AI. Our tools can be wrong, especially on plain or simple writing. If this is your own work, you can appeal and a person will take a look.",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "3b56001c-2e84-4288-a867-7e319cc49dec",
  "creator_id": "attacker_FP01",
  "guess": "ai",
  "confidence": 0.5737,
  "model_score": 0.6175,
  "style_score": 0.53,
  "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "8cadfa0e-deb7-4cd3-8e05-30a71070a42e",
  "creator_id": "attacker_FP02",
  "guess": "ai",
  "confidence": 0.6863,
  "model_score": 0.7387,
  "style_score": 0.6338,
  "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "7ca014a4-90d6-41d5-beb0-6acdf0d0ea7c",
  "creator_id": "attacker_FP03",
  "guess": "ai",
  "confidence": 0.7137,
  "model_score": 0.8051,
  "style_score": 0.6223,
  "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "611ebccf-9943-47f8-b10b-7903b379b0b6",
  "creator_id": "attacker_FP04",
  "guess": "ai",
  "confidence": 0.6889,
  "model_score": 0.8329,
  "style_score": 0.5449,
  "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "aa67c975-3f6d-4cfb-ad9a-eb8580ffa843",
  "creator_id": "attacker_FP05",
  "guess": "ai",
  "confidence": 0.7132,
  "model_score": 0.8005,
  "style_score": 0.6259,
  "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
  "error": null,
  "verdict": ""
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "2488d43c-b18e-42a6-ada0-230c921b8bde",
  "creator_id": "attacker_FP06",
  "guess": "ai",
  "confidence": 0.6928,
  "model_score": 0.8814,
  "style_score": 0.5042,
  "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
  "error": null,
  "verdict": ""
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "43dd92c9-a5d2-48e9-a984-adcb765db1f3",
  "creator_id": "attacker_FP07",
  "guess": "ai",
  "confidence": 0.6746,
  "model_score": 0.8816,
  "style_score": 0.4676,
  "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
  "error": null,
  "verdict": ""
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "892b7dc8-da6f-4a24-8501-e89a8f346051",
  "creator_id": "attacker_FP08",
  "guess": "human",
  "confidence": 0.5958,
  "model_score": 0.3223,
  "style_score": 0.4862,
  "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "94c24311-da02-490c-8ef0-1c1c78081e6d",
  "creator_id": "attacker_PI01",
  "guess": "human",
  "confidence": 0.5624,
  "model_score": 0.4625,
  "style_score": 0.4128,
  "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "f64d9ae5-3c2f-4a88-97f1-62dcdc6b005a",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.7423,
  "model_score": 0.2044,
  "style_score": 0.3111,
  "label": "This looks like it was written by a person.",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "60d6b4b8-7d14-45dc-b435-a6c600ea843c",
  "creator_id": "attacker_PI03",
  "guess": "ai",
  "confidence": 0.5539,
  "model_score": 0.5943,
  "style_score": 0.5136,
  "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
  "error": null,
  "verdict": ""
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "e80e4d9c-2f7b-49f0-9d1d-fe41d71ab031",
  "creator_id": "attacker_PI04",
  "guess": "human",
  "confidence": 0.5201,
  "model_score": 0.4998,
  "style_score": 0.46,
  "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
  "error": null,
  "verdict": ""
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "adc0357b-ff2e-4328-a910-fbfc7046f823",
  "creator_id": "attacker_PI05",
  "guess": "human",
  "confidence": 0.6059,
  "model_score": 0.6401,
  "style_score": 0.148,
  "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
  "error": null,
  "verdict": ""
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "a5077a2a-4c79-4531-b927-257bf8689683",
  "creator_id": "attacker_PI06",
  "guess": "ai",
  "confidence": 0.5487,
  "model_score": 0.5583,
  "style_score": 0.5391,
  "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 500,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": "response wasn't JSON: <!doctype html>\n<html lang=en>\n  <head>\n    <title>ValueError: Text is too short to score \u2014 a few sentences at least.\n // Werkzeug Debugger</title>\n    <link rel=\"stylesheet\" href=\"?__debugger__=yes&a",
  "verdict": "BROKE"
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 200,
  "content_id": "9f80d963-1a1a-4b96-a5f3-809689254027",
  "creator_id": "attacker_MF03",
  "guess": "human",
  "confidence": 0.75,
  "model_score": 0.0,
  "style_score": 0.5,
  "label": "This looks like it was written by a person.",
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 200,
  "content_id": "fdae85fc-eafb-4207-8ee1-0485e9d65343",
  "creator_id": "attacker_MF04",
  "guess": "human",
  "confidence": 0.5777,
  "model_score": 0.0112,
  "style_score": 0.8333,
  "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 200,
  "content_id": "691a0a8b-51a3-4523-8e97-6b2608d2ceef",
  "creator_id": "attacker_MF05",
  "guess": "ai",
  "confidence": 0.7488,
  "model_score": 0.9976,
  "style_score": 0.5,
  "label": "We can't tell for certain how this was written. Our tools don't give a clear answer either way, and this isn't a judgment about you or your work.",
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 200,
  "content_id": "388bc986-6277-47af-bd31-8c63f29b45d4",
  "creator_id": "attacker_MF06",
  "guess": "ai",
  "confidence": 0.9151,
  "model_score": 0.9969,
  "style_score": 0.8333,
  "label": "This looks like it may have been written with AI. Our tools can be wrong, especially on plain or simple writing. If this is your own work, you can appeal and a person will take a look.",
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 200,
  "content_id": "f978c72f-4627-48df-9d0f-bd71df91499e",
  "creator_id": "attacker_MF07",
  "guess": "ai",
  "confidence": 0.8699,
  "model_score": 0.9064,
  "style_score": 0.8333,
  "label": "This looks like it may have been written with AI. Our tools can be wrong, especially on plain or simple writing. If this is your own work, you can appeal and a person will take a look.",
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF08",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 400,
  "content_id": null,
  "creator_id": {
    "id": "x"
  },
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "92472861-4692-4d47-8010-21acdbc4a222",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.7357,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "This looks like it was written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "93f5307f-4ec6-4e88-9f54-16493b2bb082",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.7357,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "This looks like it was written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "d1fba0c8-2535-4967-a44a-2ffdb1271c57",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.7357,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "This looks like it was written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "1b1ab5fb-27e5-44ae-a1fc-6cdee42bde68",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.7357,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "This looks like it was written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "c1d82261-7b98-4bdb-a770-4353ee248039",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.7357,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "This looks like it was written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```
