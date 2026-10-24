#!/usr/bin/env python3
"""Grade math for the Grade Triage skill. Standard library only.

Usage:
  gradecalc.py need   FILE.json [--target 90]      (any command takes --sample instead of FILE.json)
  gradecalc.py what-if FILE.json --skip "HW 5" [--score "HW 4=70"] [--assume 85]
  gradecalc.py triage TASKS.json [--now 2026-10-24T20:00] [--hours 4]

FILE.json (one course):
  {"course": "CSE 310", "categories": [
     {"name": "Homework", "weight": 30,
      "graded": [[90, 100], [80, 100]],        # [earned, possible]
      "upcoming": [{"name": "HW 5", "possible": 100}]},
     {"name": "Final", "weight": 40, "graded": [],
      "upcoming": [{"name": "Final", "possible": 100}]}]}

TASKS.json:
  {"tasks": [{"course": "CSE 310", "name": "HW 5", "due": "2026-10-25T23:59",
              "pct_of_grade": 3.0, "hours": 2.5, "done": false}]}
"""
import argparse
import json
import os
import sys
from datetime import datetime

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")


def load(path):
    if path == "--sample":
        path = os.path.join(ASSETS, "course.json")
    with open(path) as f:
        return json.load(f)


def category_state(cat):
    """Return (earned_weight, graded_weight, upcoming_weight) in percent of course grade."""
    graded = cat.get("graded", [])
    upcoming = cat.get("upcoming", [])
    g_earn = sum(e for e, _ in graded)
    g_poss = sum(p for _, p in graded)
    u_poss = sum(u["possible"] for u in upcoming)
    total = g_poss + u_poss
    if total == 0:
        return 0.0, 0.0, 0.0
    w = cat["weight"]
    return w * g_earn / total, w * g_poss / total, w * u_poss / total


def course_state(course):
    earned = graded = upcoming = 0.0
    for cat in course["categories"]:
        e, g, u = category_state(cat)
        earned += e
        graded += g
        upcoming += u
    return earned, graded, upcoming


def letter(pct):
    for cut, name in ((90, "A"), (80, "B"), (70, "C"), (60, "D")):
        if pct >= cut:
            return name
    return "E"


def cmd_need(args):
    course = load(args.file)
    earned, graded, upcoming = course_state(course)
    targets = [args.target] if args.target else [90, 80, 70, 60]
    now = 100 * earned / graded if graded else None
    out = [f"{course.get('course', 'Course')}: "
           + (f"{now:.1f}% on {graded:.0f}% of the grade graded so far "
              f"({letter(now)})." if now is not None else "nothing graded yet.")]
    out.append(f"{upcoming:.1f}% of the grade is still ahead.")
    for t in targets:
        if upcoming <= 0:
            out.append(f"Target {t}%: no work left, final is {earned:.1f}%.")
            continue
        need = (t - earned) / upcoming * 100
        if need > 100:
            out.append(f"Target {t}% ({letter(t)}): not reachable, "
                       f"even 100% on everything left gives {earned + upcoming:.1f}%.")
        elif need <= 0:
            out.append(f"Target {t}% ({letter(t)}): already locked in.")
        else:
            out.append(f"Target {t}% ({letter(t)}): average {need:.1f}% on the remaining work.")
    print("\n".join(out))


def final_pct(course, assume=85.0, skip=(), scores=None):
    """Projected final %: upcoming work scores `scores[name]`, else `assume`; skipped counts as 0."""
    scores = scores or {}
    earned = weight = 0.0
    for cat in course["categories"]:
        e = sum(x for x, _ in cat.get("graded", []))
        poss = sum(p for _, p in cat.get("graded", []))
        for u in cat.get("upcoming", []):
            poss += u["possible"]
            if u["name"] not in skip:
                e += scores.get(u["name"], assume) / 100 * u["possible"]
        if poss == 0:
            continue
        earned += cat["weight"] * e / poss
        weight += cat["weight"]
    return 100 * earned / weight if weight else 0.0


def cmd_what_if(args):
    course = load(args.file)
    scores = {}
    for s in args.score or []:
        name, val = s.rsplit("=", 1)
        scores[name.strip()] = float(val)
    skip = set(args.skip or [])
    base = final_pct(course, args.assume, scores=scores)
    alt = final_pct(course, args.assume, skip=skip, scores=scores)
    print(f"Assuming {args.assume:g}% on work you haven't done: {base:.1f}% ({letter(base)}). "
          f"Skipping {', '.join(sorted(skip)) or 'nothing'} (counts as 0): {alt:.1f}% ({letter(alt)}). "
          f"Skipping costs {base - alt:.1f} points.")


def cmd_triage(args):
    if args.file == "--sample":
        args.file = os.path.join(ASSETS, "tasks.json")
        args.now = args.now or "2026-10-24T20:00"
    data = load(args.file)
    now = datetime.fromisoformat(args.now) if args.now else datetime.now()
    rows = []
    for t in data["tasks"]:
        if t.get("done"):
            continue
        due = datetime.fromisoformat(t["due"])
        left = (due - now).total_seconds() / 3600
        if left < 0:
            continue
        hours = max(t.get("hours", 1.0), 0.25)
        value = t["pct_of_grade"] / hours
        urgency = 1 + 2 / (1 + left / 24)  # 3x if due now, ~1.5x at 24h, fades after
        rows.append((value * urgency, value, left, hours, t))
    rows.sort(key=lambda r: -r[0])
    if not rows:
        print("Nothing due. You're clear.")
        return
    budget = args.hours
    print(f"Plan for the next {budget:g}h (best grade return per hour first):")
    used = 0.0
    later = []
    for i, (_, value, left, hours, t) in enumerate(rows, 1):
        line = (f"{t['course']}: {t['name']}  ~{hours:g}h, worth {t['pct_of_grade']:.1f}% "
                f"of the grade, due in {left:.0f}h  ({value:.2f} pts/hr)")
        if used + hours <= budget:
            used += hours
            print(f" {i}. DO NOW  {line}")
        else:
            later.append(line)
    for line in later:
        print(f"    LATER   {line}")
    skippable = [r for r in rows if r[1] < 0.15]
    if skippable:
        print("Low-value (under 0.15 pts/hr), first to drop if you're swamped: "
              + ", ".join(f"{r[4]['name']}" for r in skippable))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("need")
    n.add_argument("file", nargs="?")
    n.add_argument("--target", type=float)
    n.add_argument("--sample", action="store_true", help="use bundled sample data")
    n.set_defaults(fn=cmd_need)
    w = sub.add_parser("what-if")
    w.add_argument("file", nargs="?")
    w.add_argument("--skip", action="append")
    w.add_argument("--score", action="append")
    w.add_argument("--assume", type=float, default=85.0)
    w.add_argument("--sample", action="store_true", help="use bundled sample data")
    w.set_defaults(fn=cmd_what_if)
    t = sub.add_parser("triage")
    t.add_argument("file", nargs="?")
    t.add_argument("--now")
    t.add_argument("--hours", type=float, default=4.0)
    t.add_argument("--sample", action="store_true", help="use bundled sample data")
    t.set_defaults(fn=cmd_triage)
    args = p.parse_args(argv)
    if args.sample or not args.file:
        args.file = "--sample"
    try:
        args.fn(args)
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as e:
        print(f"Bad input: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
