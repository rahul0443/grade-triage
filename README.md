# Grade Triage

A Cubbie Skill that does the grade math students guess at. Text Cubbie:

- "what do I need on the final to get an A?"
- "what happens if I skip HW 5?"
- "my week is chaos, what do I do tonight?"

Cubbie pulls grades, weights and due dates from Canvas, a bundled Python script does the math, and Cubbie texts back a short answer. Nothing leaves the student's account.

## Why it isn't just a prompt

Language models are unreliable at weighted grade arithmetic. This Skill puts the math in `scripts/gradecalc.py` (standard library only, tested), so "you need 81.7% on the rest" is a computed number. It also tells you plainly when a grade is out of reach.

## Try it without Canvas

```bash
python3 scripts/gradecalc.py need --sample
python3 scripts/gradecalc.py what-if --sample --skip "HW 5"
python3 scripts/gradecalc.py triage --sample --hours 4
python3 -m unittest discover -s tests
```

## Install on Cubbie

Text Cubbie the link to this repo (use the commit-pinned link), then reply yes to the summary.

## Layout

- `SKILL.md` instructions for Cubbie, including iMessage reply style
- `scripts/gradecalc.py` need / what-if / triage commands, each with `--sample`
- `assets/` sample course and task files
- `tests/` unit tests
