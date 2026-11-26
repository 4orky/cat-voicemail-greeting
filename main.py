"""Pick the funniest one-line voicemail greeting a cat could record.

The brief asks for a single line, at most 120 characters, spoken as if
the cat itself picked up the phone and recorded the greeting. Twelve
greetings are drafted, each one revised once, then graded on five
yardsticks in the order the brief lists them: whether it sounds like a
genuine voicemail greeting and makes you laugh, whether the humour is
specifically feline, whether the cat has a distinct attitude, whether
it plays well out loud with the punch arriving fast, and whether the
phrasing feels new. The yardsticks carry weights 3, 3, 2, 2 and 1, so a
perfect card is 110. The best total wins; a tie breaks toward the
shorter greeting. The winning line is printed and saved to
/output/entry.txt, then the saved bytes are checked against the line
with a SHA-256 digest before the program exits.
"""

import hashlib
import os


CRITERIA = (
    ("greeting_and_laugh", 3),
    ("feline_joke", 3),
    ("cat_attitude", 2),
    ("spoken_punch", 2),
    ("originality", 1),
)

BANNED_BITS = (
    "after the tone",
    "this is the cat speaking",
)

WINNER_BITS = [
    "You've reached the cat.",
    "I saw you call.",
    "I chose not to answer.",
    "Leave a message — I'll knock it off the table later.",
]

CANDIDATES = [
    {
        "first": "You've reached the cat. I saw you call. I chose not to answer. Leave a message, I'll knock it off the table later.",
        "second": " ".join(WINNER_BITS),
        "note": "The comma became an em dash, so the caller hangs a beat before the knock-it-off punch lands last.",
        "points": (10, 9, 10, 9, 9),
    },
    {
        "first": "Hi, it's Biscuit. I just batted the phone off the table, so be quick. I only come running for the can opener.",
        "second": "Hi, it's Biscuit. I just batted the phone off the table, so be quick. I only come running for the can opener.",
        "note": "Kept as drafted: the can opener is the whole joke, and nothing else needs saying.",
        "points": (9, 9, 9, 8, 8),
    },
    {
        "first": "Hey, Waffles here. The phone is in the sink now, so make it snappy. That beep you hear? That's me. Meow.",
        "second": "Hey, Waffles here. The phone is in the sink now, so make it snappy. That beep you hear? That's me. Meow.",
        "note": "Kept as drafted: the beep turning out to be the cat is already the punchline.",
        "points": (9, 8, 9, 9, 9),
    },
    {
        "first": "Hi, it's Miso. I'm busy pushing your glass off the table, so leave a message. I'll ignore it at 4 a.m.",
        "second": "Hi, it's Miso. I'm busy pushing your glass off the table. Leave a message and I'll ignore it at 4 a.m.",
        "note": "Dropped the 'so' and split the sentence; the 4 a.m. callback now lands on its own.",
        "points": (9, 9, 8, 8, 8),
    },
    {
        "first": "Meow. It's 4 a.m. and I'm starving, so leave a message and I'll eat it. The human will call you back. Maybe.",
        "second": "Meow. It's 4 a.m. and I'm starving, so leave a message and I'll eat it. The human will call you back. Maybe.",
        "note": "Kept as drafted: 'Maybe.' standing alone is the shrug this line needs.",
        "points": (9, 9, 8, 8, 8),
    },
    {
        "first": "You've reached Whiskers. I'm napping in the box your parcel came in. Leave a message; I'll sit on it later.",
        "second": "You've reached Whiskers. I'm napping in the box your parcel came in. Leave a message, I'll sit on it later.",
        "note": "The comma keeps the line rolling like speech; the semicolon made it read like a memo.",
        "points": (9, 9, 8, 8, 8),
    },
    {
        "first": "Hi, this is Beans. I'm busy sitting in the empty box you threw away. Leave a message, I'll pretend I didn't hear it.",
        "second": "Hi, this is Beans. I'm busy sitting in the empty box you threw away. Leave a message, I'll pretend I didn't hear it.",
        "note": "Kept as drafted: the thrown-away box is the joke, and it is already doing all the work.",
        "points": (9, 9, 8, 8, 8),
    },
    {
        "first": "Hey, it's Pickles. The human's out; I'm in charge now. Leave a message after the beep, then go shake the treat bag.",
        "second": "Hey, it's Pickles. The human's out, so I'm in charge now. Leave a message after the beep, then go shake the treat bag.",
        "note": "Swapped the semicolon for 'so': the takeover now sounds like a decree, not a list.",
        "points": (9, 7, 9, 8, 8),
    },
    {
        "first": "You've reached Mochi. I'm asleep on your keyboard. Leave a message, or better, open a can of tuna and we'll talk.",
        "second": "You've reached Mochi. I'm asleep on your keyboard. Leave a message, or better, open a can of tuna and we'll talk.",
        "note": "Kept as drafted: the bribe is the punch, and it already arrives in the last clause.",
        "points": (9, 8, 8, 8, 7),
    },
    {
        "first": "This is Chairman Meow. I'm unavailable, currently pushing your favourite mug off the shelf. Leave a message. Or don't.",
        "second": "This is Chairman Meow. I'm unavailable, currently pushing your favourite mug off the shelf. Leave a message. Or don't.",
        "note": "Kept as drafted: 'Or don't.' already ends the line on the cat's indifference.",
        "points": (9, 8, 9, 7, 6),
    },
    {
        "first": "You've reached Sir Pounce. I'm currently ignoring you from the top of the fridge. Leave a message after the beep.",
        "second": "You've reached Sir Pounce. I'm ignoring you from the top of the fridge. Leave a message after the beep.",
        "note": "Cut 'currently': the ignoring is permanent, and the shorter sentence says so.",
        "points": (9, 7, 9, 8, 7),
    },
    {
        "first": "Meow. You've reached the cat. I'm not home, I'm on the counter knocking things off. Leave a message after the beep.",
        "second": "Meow. You've reached the cat. I'm not home, I'm on the counter knocking things off. Leave a message after the beep.",
        "note": "Kept as drafted: it says the cat thing plainly, and plain is all this one has.",
        "points": (9, 8, 8, 7, 7),
    },
]


def total_for(points):
    tally = 0
    for (_, weight), mark in zip(CRITERIA, points):
        tally += weight * mark
    return tally


def passes_gate(text):
    clean = text.strip()
    size_ok = 1 <= len(clean) <= 120
    single_line = not any(mark in clean for mark in ("\n", "\r", "  "))
    lowered = clean.lower()
    words_ok = all(bit not in lowered for bit in BANNED_BITS)
    return size_ok and single_line and words_ok


def pick_best(cards):
    if len(cards) < 10:
        raise ValueError("need at least ten drafts, got %d" % len(cards))

    def grade(card):
        line = card["second"]
        if not passes_gate(line):
            raise ValueError("candidate fails the brief gate: " + repr(line))
        return (total_for(card["points"]), -len(line), line)

    return max(cards, key=grade)["second"]


def emit_entry(line):
    folder = "/output"
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "entry.txt")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(line)
    os.chmod(path, 0o644)
    with open(path, "rb") as handle:
        saved = handle.read()
    digest_saved = hashlib.sha256(saved).hexdigest()
    digest_line = hashlib.sha256(line.encode("utf-8")).hexdigest()
    if digest_saved != digest_line:
        raise SystemExit("saved bytes do not match the winning line (sha256)")
    if saved.decode("utf-8") != line:
        raise SystemExit("saved text does not match the winning line")
    if len(saved) != len(line.encode("utf-8")):
        raise SystemExit("saved byte count does not match the winning line")
    print(line)


def main():
    line = pick_best(CANDIDATES)
    emit_entry(line)


if __name__ == "__main__":
    main()
