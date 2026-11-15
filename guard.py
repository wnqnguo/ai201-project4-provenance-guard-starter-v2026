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

# Very common English function words. Ordinary English prose is mostly made of
# these (about a third of the words); French and Spanish text almost never is.
ENGLISH_COMMON = frozenset(
    "the a an and or but of to in on at for with by from as is are was were be been "
    "it its this that these those i me my we our you your he she they them his her "
    "their not no so if then than there here what which who when where how all any "
    "some can could would should will do does did have has had just about into out "
    "up over also very".split()
)


def check_text(text: str):
    """Return None if the text can be scored, else (error_code, message)."""
    n_words = len(stylometry.words(text))
    if n_words < config.MIN_WORDS:
        return (
            "too_few_words",
            f"text needs at least {config.MIN_WORDS} words written in Latin letters "
            f"to be scored (found {n_words}).",
        )

    share = sum(w in ENGLISH_COMMON for w in stylometry.words(text)) / n_words
    if share < config.ENGLISH_COMMON_MIN_SHARE:
        return (
            "not_english",
            "this tool only reads English. The text looks like it is written in "
            "another language, so it was not scored.",
        )
    return None
