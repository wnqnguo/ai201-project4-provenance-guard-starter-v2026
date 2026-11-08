"""
What your test runs. ← UNIT 8, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
false positives needs your own writing. One about label coverage needs inputs
across the score range. One about the appeal path needs a real content_id.

Working that out is Milestone 3's first step, and this file is where you write
it down. `run_eval.py` runs everything here three times.

Two are filled in as examples. Replace them with what your criteria actually
need — these are a shape, not a set.

A scenario carries **either** of these:

    "texts"   a list of strings. Each is sent as {"text": ..., "creator_id": ...}
              with a creator_id made up for you. Use this for most criteria.

    "bodies"  a list of whole request bodies, sent exactly as written. Use this
              when the malformed request IS the point — empty text, no `text`
              field at all, something enormous. A bad-input criterion needs it,
              because you cannot express "the field is missing" as a string.
"""

# ── Texts used by more than one criterion ────────────────────────────────────

# Things Faye actually wrote herself. Do not add anything here that she did not write.
MINE = [
    # funeral paragraph
    "At a funeral, an old woman is wearing all black elegant dress and standing far away from the rest of the people. Lots of people are crying at the funeral. But not the old woman. She looks peaceful, even though there is an deep sadness in her eyes.",
    # coffee-on-keyboard
    "I spilled coffee on my keyboard this morning and spent twenty minutes drying it with a hairdryer while my cat watched from the couch like I was an idiot. The N key still sticks.",
    # cover letter paragraph
    "My experience from SolarCity has prepared me to take on bigger challenges. During my time there, I was able to pick up a in-house client side framework and PolymerJS, which I had no prior experience with and deliver production code with them. I picked up Android during a company hackathon and was given an android project to work on soon after. I learned about the importance of single responsibility and separation of concerns in software. In addition, I worked on apis in ASP.NET MVC and unit testing. I use Git as a version control system. I am confident that my experience makes me a great fit for Shift.",
    # Etsy, one sentence
    "Etsy is a great platform for people who wants to test out starting their own business, it has a lot less learning curve n upfront cost compare to Amazon.",
    # Etsy, three sentences
    "Etsy is a great platform for people who wants to test out starting their own business, it has a lot less learning curve n upfront cost compare to Amazon. It cost only $20 cents to post a listing on Etsy, where as on Amazon there is a monthly amazon fulfillment fee, and you have to pay for storage of your stock at Amazon warehouse. And due to way more sellers on amazon a lot from oversee factories who can offer very competitive price, it is much harder for individuals to start with a small amount of money.",
]

# Written by Claude (an AI), asked for typical plain AI prose on everyday topics.
AI_WRITTEN = [
    "Technology has transformed the way people communicate in modern society. It offers many benefits, including faster access to information and improved connectivity. Social media platforms allow individuals to share ideas with a global audience. However, it also presents challenges, such as privacy concerns and misinformation. Overall, it is important to use technology responsibly and thoughtfully.",
    "Regular exercise is an important part of maintaining a healthy lifestyle. It helps improve cardiovascular health, strengthen muscles, and boost mental well-being. Many people find it difficult to stay consistent, but setting small goals can make the process easier. Over time, these habits can lead to lasting benefits. Ultimately, finding an activity you enjoy is the key to long-term success.",
    "Remote work has become increasingly common in recent years. It provides employees with greater flexibility and can reduce commuting time. At the same time, it can make communication and collaboration more difficult for teams. Companies must find ways to support their workers and maintain a strong culture. With the right approach, remote work can be effective for everyone involved.",
    "Reading is a valuable habit that offers numerous benefits for people of all ages. It expands vocabulary, improves concentration, and encourages creative thinking. Whether it is fiction or non-fiction, every book offers something new to learn. Making time to read each day can have a positive impact on overall well-being. In conclusion, reading remains one of the most rewarding activities available.",
    "Climate change is one of the most pressing challenges facing the world today. Rising temperatures are causing more extreme weather events and threatening ecosystems. Governments, businesses, and individuals all have a role to play in reducing emissions. By working together, it is possible to create a more sustainable future. Taking action now is essential for protecting the planet for future generations.",
]

# Five more AI-written texts, with the kind of loosening a person might do:
# casual wording, a typo, shorter sentences. Used only for label coverage.
AI_LOOSENED = [
    "Technology has changed how people communicate these days. It gives us lots of benefits, like quicker access to info and better connectivity. Social media lets people share ideas with a global audience. But it also has downsides, such as privacy worries and missinformation. Still, we should use technology carefuly.",
    "Working out is a big part of staying healthy. It's good for your heart, your muscles, and your mood. Lots of people struggle to keep it up, but small goals really help. Pick something you actually like doing, and you'll stick with it.",
    "Remote work is everywhere now. You get more flexibility and no commute, which is great. But teams can struggle to talk to each other, and company culture can slip. Good support from managers makes a big diffrence.",
    "Reading every day is a great habit. It builds vocabulary, helps you focus, and gets your imagination going. Fiction or non-fiction, there's always something to learn. A little time each day goes a long way.",
    "Climate change is a huge problem right now. Temperatures keep rising and storms are getting worse. Governments, companies, and regular people all need to cut emissions. If we work together we can still make a better future.",
]


SCENARIOS = [
    # Criterion 1: of my own writing, at most 1 labeled high-confidence AI.
    # NOTE: the criterion says 10 pieces; only the pieces Faye has actually
    # written are here. Add more of her own before the final run.
    {
        "name": "my own writing",
        "criterion": 1,
        "texts": MINE,
    },
    # Criterion 2: average combined score of AI-written text is at least 0.3
    # higher than the average for my own writing. Compare these two groups.
    {
        "name": "spread ai",
        "criterion": 2,
        "texts": AI_WRITTEN,
    },
    {
        "name": "spread human",
        "criterion": 2,
        "texts": MINE,
    },
    # Criterion 3: across 15 texts, each of the three labels appears at least twice.
    {
        "name": "label coverage",
        "criterion": 3,
        "texts": MINE + AI_WRITTEN + AI_LOOSENED,
    },
    # Criterion 4 (appeals) cannot be run here: it needs a submission first and
    # then an appeal against the content_id that came back. Tested by hand with
    # curl, and the commands and output are in the README.

    # Criterion 5: five bad inputs to /submit, each should get a clear error
    # (HTTP 400 with an `error` field) and the service must keep running.
    {
        "name": "bad input",
        "criterion": 5,
        "bodies": [
            {"text": "", "creator_id": "eval_bad_empty"},
            {"creator_id": "eval_bad_missing"},                  # no text field at all
            {"text": "   \n  ", "creator_id": "eval_bad_blank"},  # whitespace only
            {"text": "A normal sentence with no creator id."},    # no creator_id
            {"text": "word " * 5000, "creator_id": "eval_bad_huge"},  # 25000 characters
        ],
    },
]


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems
