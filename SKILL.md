---
name: grade-triage
description: Tells a student exactly what grade they need on remaining work and which assignment to do tonight for the biggest grade payoff per hour. Use when a student asks "what do I need on the final to get an A", "what if I skip this", "what should I work on tonight", or says their week is chaos. Does real grade math with a script instead of guessing, using their Canvas grades and due dates, and can set a nightly triage check-in if they say yes.
license: MIT
---

# Grade Triage

Students guess at grades and at what to do first. This skill does the math with a bundled script and answers in a couple of short texts.

## What it answers

1. What do I need on the rest of the course to get an A, B or C?
2. What happens to my grade if I skip or bomb one assignment?
3. What should I do tonight, in what order, with the hours I have?

## Getting the data

Cubbie fetches the data first. The script cannot reach Canvas or any other ability.

1. Read the student's Canvas courses, graded assignments with scores, upcoming assignments with due dates and points, and each course's grading weights (assignment groups). If Canvas is not connected, ask them to connect it. If they would rather not, ask for the weights and scores in a text or a screenshot and read the photo.
2. Build the course file in the shape shown in `assets/course.json`: categories with a weight in percent, graded items as [earned, possible], and upcoming items with their possible points.
3. For triage, build the task file in the shape shown in `assets/tasks.json`. Fill `pct_of_grade` as category weight times the item's points divided by the category's total points. Fill `hours` from what the student says, or guess from the assignment type and say it is a guess. Use the student's local date and time for `--now`.

Write both files under `~/.config/grade-triage/` so a later check-in can reuse them.

## Commands

Run from this skill folder. Python 3 standard library only, nothing to install.

- `python3 scripts/gradecalc.py need ~/.config/grade-triage/course.json --target 90`
  Leave off `--target` to get A, B, C and D at once. It says plainly when a grade is out of reach or already locked in.
- `python3 scripts/gradecalc.py what-if ~/.config/grade-triage/course.json --skip "HW 5" --score "HW 4=70" --assume 85`
  Skipped work counts as zero. Work with no score yet is assumed at `--assume` percent.
- `python3 scripts/gradecalc.py triage ~/.config/grade-triage/tasks.json --now 2026-10-24T20:00 --hours 4`
  Ranks by grade points per hour, weighted up for things due soon.

Every command also takes `--sample` to run on bundled data in `assets/`, which touches no saved state. Use it to show a student what the answer looks like before their data is connected.

## Workflow

1. Work out which of the three questions they are asking. If it is unclear, ask one question and suggest a default they can answer with "yes".
2. Fetch their data, write the files, run the command.
3. Reply with the answer first, then the one thing to do next.
4. For triage, ask before doing anything for them. Offer to set reminders for the order you suggested, and wait for a yes.
5. Offer a nightly 9 pm triage check-in once, in one line. Create it only if they agree on the time. Word it so it makes sense days later, for example "Grade Triage: your top two things to do tonight across all courses".

## Replies

Short plain text, like a friend texting between classes. No headings, tables, bold markers or code blocks.

- Lead with the answer. "To get an A in CSE 310 you need 92 on the rest. It's out of reach if you skip HW 5."
- One idea per message. Send at most three lines of triage in the text. If more than five items are due this week, send the top three and offer the full plan as a PDF or doc.
- Put any link on its own line.
- Never invent a score. If a weight or score is missing, say which one and ask for it.
- Do not promise a grade. Say "if you average 85 on the rest".
- If Canvas is not connected: "Connect Canvas and I can do this for all your classes in one go. Or text me your weights and scores and I'll do one class now."
- If the script fails or the numbers look wrong: say you couldn't work it out, name the class, and ask for the weights again.
- If nothing is due: "You're clear this week. Want me to check again Sunday night?"

## Safety and scope

- Never ask for a Canvas password. Use the connected account or what the student types.
- Do not message teachers or classmates. If the student wants to ask for an extension, offer to draft the email for them to send.
- Do not tell a student to skip graded work as advice. Show the cost in points and let them decide.
- Grades stay with the student. Nothing is sent to any server.
