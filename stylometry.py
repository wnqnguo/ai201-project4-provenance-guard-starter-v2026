"""
Signal two: the style signal. ← YOU BUILD THIS IN MILESTONE 4

Signal one reads the text for meaning. This one measures it *as text* — the
shape of it, without understanding a word.

Three measures are stubbed below because the brief names those three. They are
stubs, not implementations: what they compute is yours, and so is how you
combine them.

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how much punctuation, and how varied?

Why these might differ between human and AI writing: generated prose tends
toward even, mid-length sentences and a narrower band of vocabulary, because
that's what "most likely next word" produces on average. Human writing is
lumpier — a three-word sentence next to a forty-word one.

⚠️ **The blind spot, which you have to name in Milestone 1.**

This signal cannot read. It has no idea what the text says. Anything that
changes the shape without changing the substance moves it — adding typos,
breaking up sentences, pasting in a quotation. That is a very cheap thing for
someone to do on purpose, and unit 8's attack set will do it to you.

Build each function on its own and call it from a terminal before you wire
anything together:

    python stylometry.py "some text to look at"
"""

import re
import statistics


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


# Calibration constants for style_signal. A raw value at or above its cap counts
# as fully human-looking (0 for that measure); a raw value of 0 counts as fully
# AI-looking (1). Adjust after looking at real numbers.
SPREAD_FULLY_HUMAN = 0.8
TTR_FULLY_HUMAN = 1.0
PUNCT_FULLY_HUMAN = 0.15
NEUTRAL_SPREAD = 0.4   # returned for one-sentence text; sits mid-range


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


# ── The three measures — YOU BUILD THESE ─────────────────────────────────────

def sentence_length_spread(text: str) -> float:
    """
    How much sentence length varies. ← TODO

    Returns:
        A float. Decide yourself what scale it's on and which direction means
        "more human" — then write that down, because your combining rule
        depends on knowing it.

    A hint on what you're reaching for: the standard deviation of sentence
    lengths, probably divided by the mean so a long text and a short one are
    comparable. `statistics.stdev` is imported for you.

    Watch the edge case: a one-sentence submission has no spread at all, and
    `stdev` raises on fewer than two values. Decide what that should return
    before the attack set decides for you.
    """
    # Raw scale: standard deviation / mean of sentence lengths in words.
    # Roughly 0.2 for very even prose and 0.8 or more for lumpy prose.
    # HIGHER raw value = more human. Needs flipping in style_signal.
    lengths = [len(words(sentence)) for sentence in sentences(text)]
    lengths = [n for n in lengths if n > 0]
    if len(lengths) < 2:
        return NEUTRAL_SPREAD  # one sentence has no spread: say nothing either way
    mean = statistics.mean(lengths)
    return statistics.stdev(lengths) / mean


def type_token_ratio(text: str) -> float:
    """
    Unique words over total words. ← TODO

    Returns:
        A float between 0 and 1. Higher means more varied vocabulary.

    Worth knowing before you rely on it: this measure falls as text gets
    longer, because common words repeat. Two texts of different lengths aren't
    directly comparable on it, and if your test inputs vary a lot in length,
    that alone can look like a signal.
    """
    # Raw scale: 0 to 1. HIGHER raw value = more human. Needs flipping.
    tokens = words(text)
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)


def punctuation_density(text: str) -> float:
    """
    How much punctuation, relative to length. ← TODO

    Returns:
        A float. Whether you count all punctuation or only some kinds — commas,
        semicolons, dashes — is a real choice. Semicolons and em dashes are
        more interesting than full stops, because they vary more between
        writers.
    """
    # Raw scale: counted marks per word. Only ; : , and dashes count, because
    # they vary more between writers than full stops do.
    # Roughly 0.05 for sparse punctuation and 0.2 or more for heavy punctuation.
    # HIGHER raw value = more human. Needs flipping.
    tokens = words(text)
    if not tokens:
        return 0.0
    marks = len(re.findall(r"[;:,\u2014\u2013]|--", text))
    return marks / len(tokens)


# ── Combining them ───────────────────────────────────────────────────────────

def style_signal(text: str) -> float:
    """
    The style signal as a 0–1 score. **Higher means more likely AI.** ← TODO

    Combine your three measures into one number. Same direction as
    `detector.model_signal`, so that `scoring.combine_signals` can treat them
    the same way — if one of your signals runs backwards, everything above it
    is wrong in a way that's hard to see.

    Two things to decide and write down:

      1. Which direction each measure points. Low spread means more AI-ish, so
         it needs flipping. Work out which of your three need that.
      2. How to get each onto a comparable scale. A raw type-token ratio sits
         between 0 and 1; a raw punctuation count doesn't. Adding them
         unscaled means whichever has the bigger numbers wins by default.

    Test it on the four calibration inputs from Milestone 4 — clearly AI,
    clearly human, plain conventional human writing, lightly-edited AI — before
    you trust it. Plain and ordinary, not formal: formal prose reads as *human*
    to signal one, and it is plain writing that gets accused.
    """
    # Each raw measure points toward HUMAN when it is high, so each one is
    # flipped: AI-likeness = 1 - (raw / the value where I call it fully human).
    # The cap values below are my own rough calibration, not a standard.
    spread_ai = 1 - _clamp01(sentence_length_spread(text) / SPREAD_FULLY_HUMAN)
    ttr_ai = 1 - _clamp01(type_token_ratio(text) / TTR_FULLY_HUMAN)
    punct_ai = 1 - _clamp01(punctuation_density(text) / PUNCT_FULLY_HUMAN)
    return round((spread_ai + ttr_ai + punct_ai) / 3, 4)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text)}")
    print(f"type_token_ratio         {type_token_ratio(text)}")
    print(f"punctuation_density      {punctuation_density(text)}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI)")
    print("\nAll zeros? These are stubs — Milestone 4 is where you build them.")
