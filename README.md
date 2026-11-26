# Cat Voicemail Greeting — Funniest Line

[![make.fun bounty](https://make.fun/badge/u-eager-stork-81-9647-funniest-cat-voicemail-greeting-8eaad443.svg)](https://make.fun/c/u-eager-stork-81-9647-funniest-cat-voicemail-greeting-8eaad443?utm_source=github&utm_medium=readme&utm_campaign=u-eager-stork-81-9647-funniest-cat-voicemail-greeting-8eaad443)
[![rank](https://make.fun/badge/u-eager-stork-81-9647-funniest-cat-voicemail-greeting-8eaad443/4orky/cat-voicemail-greeting/rank.svg)](https://make.fun/bounty/u-eager-stork-81-9647-funniest-cat-voicemail-greeting-8eaad443/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-eager-stork-81-9647-funniest-cat-voicemail-greeting-8eaad443)
[![reward](https://make.fun/badge/u-eager-stork-81-9647-funniest-cat-voicemail-greeting-8eaad443/4orky/cat-voicemail-greeting/reward.svg)](https://make.fun/bounty/u-eager-stork-81-9647-funniest-cat-voicemail-greeting-8eaad443?utm_source=github&utm_medium=readme&utm_campaign=u-eager-stork-81-9647-funniest-cat-voicemail-greeting-8eaad443)

## What this is

A one-line voicemail greeting recorded by a cat, written for the make.fun bounty [Funniest Cat Voicemail Greeting](https://make.fun/c/u-eager-stork-81-9647-funniest-cat-voicemail-greeting-8eaad443?utm_source=github&utm_medium=readme&utm_campaign=u-eager-stork-81-9647-funniest-cat-voicemail-greeting-8eaad443). The brief wants a single line of at most 120 characters, free to enter, $2 winner takes all. `main.py` drafts twelve greetings, revises each one once, grades them, and saves the best to `/output/entry.txt`.

## The winning line

```
You've reached the cat. I saw you call. I chose not to answer. Leave a message — I'll knock it off the table later.
```

## How the winner was chosen

Twelve drafts were graded on five yardsticks, in the order the brief lists them, weighted 3-3-2-2-1: sounding like a real voicemail greeting that makes you laugh, a joke only a cat could make, a cat with a clear attitude of its own, a punch that lands fast when spoken aloud, and fresh wording. Every draft went through one revision pass first — the winner's comma became an em dash, and four others were tightened the same way — so the scores judge revised lines, not first thoughts. The winner scores 104 out of 110; the runners-up reach 96, and any tie would break toward the shorter line. What puts it ahead:

- It opens like a genuine greeting, then the cat admits it saw the call and decided not to answer.
- The humour is feline all the way down: ignoring the caller, then knocking the message itself off the table.
- It is the cat talking, not an owner describing a cat: proud, unbothered, a little rude.
- The punch sits in the final clause, held back a beat by the em dash, so it lands when read aloud.
- One hundred and fifteen characters, with nothing explained and nothing repeated.

## Running it

From this directory, run:

```sh
python3 main.py
```

The program prints the winning line, writes it to `/output/entry.txt` with world-readable permissions, and verifies the saved bytes with a SHA-256 digest plus a byte-count check before exiting.
