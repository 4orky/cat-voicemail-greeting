#!/usr/bin/env python3
# Cat-voicemail foundry: drafts a dozen voicemail greetings a cat might
# record, scores each against the judge brief, revises the wording once,
# and writes the strongest single line to /output/entry.txt. The brief:
# one line, 1-120 characters, a voicemail greeting recorded by a cat.
# Five lenses, heaviest first, in the judge's own order: it must read as
# a cat's voicemail greeting and land a laugh; the joke must come from
# something specific to cats; the cat must have a clear voice and
# attitude of its own; it must work spoken aloud, punch arriving quickly;
# and the wording must be fresh, not a tired pun or catchphrase.
# Weights below encode that order. Each entry keeps its first draft, its
# revised final, a note on what the revision fixed, and marks out of ten
# per lens. Selection is deterministic: highest weighted total wins, and
# a tie goes to the shorter line.
from hashlib import md5 as _md5
from hashlib import sha256 as _sha256
from pathlib import Path as _Path
_WEIGHTS = {"voicemail": 3, "cat_specific": 3, "voice": 2, "spoken": 2, "fresh": 1}
_FORBIDDEN = ("hello, this is", "please leave a message after the tone")
_ENTRIES = [
    {"draft": "You've reached the cat. I saw you call. I chose not to answer. Leave a message; I'll knock it off the table later.",
     "final": "You've reached the cat. I saw you call. I chose not to answer. Leave a message \u2014 I'll knock it off the table later.",
     "polish": "Swapped the semicolon for an em dash so the caller waits a beat before the punch, and the punch lands as the last thing heard.",
     "marks": {"voicemail": 10, "cat_specific": 9, "voice": 10, "spoken": 9, "fresh": 9}},
    {"draft": "Hi, it's Biscuit. I knocked the phone off the table, so talk fast. I only listen when the can opener runs.",
     "final": "Hi, it's Biscuit. I knocked the phone off the table, so talk fast. I only listen when the can opener runs.",
     "polish": "No change: the two cat facts already stack, and the can opener is the whole punch.",
     "marks": {"voicemail": 9, "cat_specific": 9, "voice": 9, "spoken": 8, "fresh": 8}},
    {"draft": "Hey, it's Waffles. I knocked the phone into the sink, so make it quick. The beep is me. Meow.",
     "final": "Hey, it's Waffles. I knocked the phone into the sink, so make it quick. The beep is me. Meow.",
     "polish": "No change: the beep being the cat is already the joke, and adding a word would blunt it.",
     "marks": {"voicemail": 9, "cat_specific": 8, "voice": 9, "spoken": 9, "fresh": 9}},
    {"draft": "Hi, it's Miso. I'm busy knocking your glass off the table, so leave a message. I'll ignore it at 4 a.m.",
     "final": "Hi, it's Miso. I'm busy knocking your glass off the table. Leave a message and I'll ignore it at 4 a.m.",
     "polish": "Cut 'so' and let the two sentences stand apart; the 4 a.m. callback now lands on its own.",
     "marks": {"voicemail": 9, "cat_specific": 9, "voice": 8, "spoken": 8, "fresh": 8}},
    {"draft": "Meow. It's 4 a.m. and I'm starving, so leave a message and I'll eat it. The human will call you back. Maybe.",
     "final": "Meow. It's 4 a.m. and I'm starving, so leave a message and I'll eat it. The human will call you back. Maybe.",
     "polish": "No change: 'Maybe.' as its own sentence is already the shrug the line needs.",
     "marks": {"voicemail": 9, "cat_specific": 9, "voice": 8, "spoken": 8, "fresh": 8}},
    {"draft": "You've reached Whiskers. I'm napping in the box your package came in. Leave a message; I'll sit on it later.",
     "final": "You've reached Whiskers. I'm napping in the box your package came in. Leave a message, I'll sit on it later.",
     "polish": "The comma keeps the line rolling like speech; the semicolon made it read like a memo.",
     "marks": {"voicemail": 9, "cat_specific": 9, "voice": 8, "spoken": 8, "fresh": 8}},
    {"draft": "Hi, this is Beans. I'm busy sitting in the empty box you threw away. Leave a message, I'll pretend I didn't hear it.",
     "final": "Hi, this is Beans. I'm busy sitting in the empty box you threw away. Leave a message, I'll pretend I didn't hear it.",
     "polish": "No change: the box the human threw away is the joke, and it is already doing all the work.",
     "marks": {"voicemail": 9, "cat_specific": 9, "voice": 8, "spoken": 8, "fresh": 8}},
    {"draft": "Hey, it's Pickles. The human's out; I'm in charge now. Leave a message after the beep, then go shake the treat bag.",
     "final": "Hey, it's Pickles. The human's out, so I'm in charge now. Leave a message after the beep, then go shake the treat bag.",
     "polish": "Replaced the semicolon with 'so': the takeover now sounds like a decree, not a list.",
     "marks": {"voicemail": 9, "cat_specific": 7, "voice": 9, "spoken": 8, "fresh": 8}},
    {"draft": "You've reached Mochi. I'm asleep on your keyboard. Leave a message, or better, open a can of tuna and we'll talk.",
     "final": "You've reached Mochi. I'm asleep on your keyboard. Leave a message, or better, open a can of tuna and we'll talk.",
     "polish": "No change: the bribe is the punch, and it already arrives in the last clause.",
     "marks": {"voicemail": 9, "cat_specific": 8, "voice": 8, "spoken": 8, "fresh": 7}},
    {"draft": "This is Chairman Meow. I'm unavailable, currently pushing your favourite mug off the shelf. Leave a message. Or don't.",
     "final": "This is Chairman Meow. I'm unavailable, currently pushing your favourite mug off the shelf. Leave a message. Or don't.",
     "polish": "No change: 'Or don't.' already ends the line on the cat's indifference.",
     "marks": {"voicemail": 9, "cat_specific": 8, "voice": 9, "spoken": 7, "fresh": 6}},
    {"draft": "You've reached Sir Pounce. I'm currently ignoring you from the top of the fridge. Leave a message after the beep.",
     "final": "You've reached Sir Pounce. I'm ignoring you from the top of the fridge. Leave a message after the beep.",
     "polish": "Cut 'currently': the ignoring is permanent, and the shorter sentence says so.",
     "marks": {"voicemail": 9, "cat_specific": 7, "voice": 9, "spoken": 8, "fresh": 7}},
    {"draft": "Meow. You've reached the cat. I'm not home, I'm on the counter knocking things off. Leave a message after the beep.",
     "final": "Meow. You've reached the cat. I'm not home, I'm on the counter knocking things off. Leave a message after the beep.",
     "polish": "No change: it says the cat thing plainly, and plain is all this one has.",
     "marks": {"voicemail": 9, "cat_specific": 8, "voice": 8, "spoken": 7, "fresh": 7}},
]  # twelve drafts scored; the first entry wins on weighted total
def _weighted(marks):
    return sum(marks[lens] * _WEIGHTS[lens] for lens in _WEIGHTS)
def _acceptable(line):
    stripped = line.strip()
    if not 1 <= len(stripped) <= 120:
        return False
    if "\n" in stripped or "\r" in stripped:
        return False
    lowered = stripped.lower()
    return not any(phrase in lowered for phrase in _FORBIDDEN)
def _choose(entries):
    ranked = []
    for entry in entries:
        line = entry["final"]
        if not _acceptable(line):
            raise ValueError("entry fails the gate: %r" % line)
        ranked.append((_weighted(entry["marks"]), -len(line), line))
    ranked.sort(reverse=True)
    return ranked[0][2]
def _publish(line):
    target = _Path("/output/entry.txt")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(line, encoding="utf-8")
    target.chmod(0o644)
    raw = target.read_bytes()
    if _sha256(raw).hexdigest() != _sha256(line.encode("utf-8")).hexdigest():
        raise SystemExit("entry.txt bytes differ from the chosen line")
    if _md5(raw).hexdigest() != _md5(line.encode("utf-8")).hexdigest():
        raise SystemExit("entry.txt md5 differs from the chosen line")
    import stat as _stat
    if _stat.S_IMODE(target.stat().st_mode) != 0o644:
        raise SystemExit("entry.txt is not world-readable")
    checked = raw.decode("utf-8")
    if not _acceptable(checked):
        raise SystemExit("entry.txt fails the gate after writing")
    print(line, flush=True)
if __name__ == "__main__": _publish(_choose(_ENTRIES))
