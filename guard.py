"""
Input guard (capstone extension).

Decides whether a piece of text can be scored at all, BEFORE either signal runs.
Both signals were built for ordinary prose. Fed one character, emoji or text in
another script, signal one raises an error or returns a number that means
nothing, and the service used to crash (500) or hand out a confident label.

    from guard import check_text
    problem = check_text(text)     # None if fine, else (error_code, message)
"""

import config
import stylometry


def check_text(text: str):
    """Return None if the text can be scored, else (error_code, message)."""
    n_words = len(stylometry.words(text))
    if n_words < config.MIN_WORDS:
        return (
            "too_few_words",
            f"text needs at least {config.MIN_WORDS} words written in Latin letters "
            f"to be scored (found {n_words}).",
        )
    return None
