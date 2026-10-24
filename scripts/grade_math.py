#!/usr/bin/env python3
"""Grade Rescue: exact grade math for one course.

Reads a course file (JSON) that Cubbie builds from Canvas, a grades screenshot or the syllabus, and prints:
- the current grade on graded work,
- the best and worst possible final grade,
- the average needed on everything left for each letter,
- optionally, the score needed on one assignment (usually the final),
- which remaining assignments can move the grade the most.

Standard library only. Exit codes:
  0  ok
  2  input file missing or not valid
  3  nothing left to grade (current grade is printed anyway)
  4  the assignment named in --solve-for was not found among ungraded work
"""

import argparse
import json
import os
import sys

DEFAULT_CUTOFFS = {"A": 90.0, "B": 80.0, "C": 70.0, "D": 60.0}
HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE = os.path.join(HERE, "..", "assets", "sample_course.json")


class InputError(Exception):
    pass


def load_course(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise InputError(f"Course file not found: {path}")
    except json.JSONDecodeError as e:
        raise InputError(f"Course file is not valid JSON: {e}")

    groups = data.get("groups")
    if not isinstance(groups, list) or not groups:
        raise InputError("Course file needs a non-empty 'groups' list.")
    weighted = bool(data.get("weighted", all(isinstance(g, dict) and "weight" in g for g in groups)))
    for g in groups:
        if "name" not in g or not isinstance(g.get("assignments"), list):
            raise InputError("Each group needs a 'name' and an 'assignments' list.")
        if weighted:
            try:
                g["weight"] = float(g["weight"])
            except (KeyError, TypeError, ValueError):
                raise InputError(f"Group '{g['name']}' needs a numeric 'weight' (the course is weighted).")
        g["drop_lowest"] = int(g.get("drop_lowest", 0) or 0)
        for a in g["assignments"]:
            if "name" not in a:
                raise InputError(f"An assignment in '{g['name']}' has no name.")
            try:
                a["points"] = float(a.get("points", 0) or 0)
            except (TypeError, ValueError):
                raise InputError(f"'{a['name']}' has a non-numeric 'points'.")
            s = a.get("score")
            if s is not None:
                try:
                    a["score"] = float(s)
                except (TypeError, ValueError):
                    raise InputError(f"'{a['name']}' has a non-numeric 'score'.")
            a["excused"] = bool(a.get("excused", False))

    cutoffs = data.get("cutoffs") or DEFAULT_CUTOFFS
    try:
        cutoffs = {str(k): float(v) for k, v in cutoffs.items()}
    except (AttributeError, TypeError, ValueError):
        raise InputError("'cutoffs' must map letters to percentages, like {\"A\": 90}.")
    return {
        "course": data.get("course", "This course"),
        "weighted": weighted,
        "cutoffs": dict(sorted(cutoffs.items(), key=lambda kv: -kv[1])),
        "groups": groups,
    }


def letter_for(pct, cutoffs):
    for letter, cut in cutoffs.items():
        if pct >= cut - 1e-9:
            return letter
    return "F" if "F" not in cutoffs else min(cutoffs, key=cutoffs.get)


def counted(a):
    """Assignments that count: not excused, and either worth points or carrying extra credit."""
    return not a["excused"] and (a["points"] > 0 or (a["score"] or 0) > 0)


def graded_after_drops(g):
    graded = [a for a in g["assignments"] if counted(a) and a["score"] is not None]
    n = g["drop_lowest"]
    real = [a for a in graded if a["points"] > 0]
    if n > 0 and len(real) > n:
        real.sort(key=lambda a: a["score"] / a["points"])
        dropped = set(id(a) for a in real[:n])
        graded = [a for a in graded if id(a) not in dropped]
    return graded


def remaining(g):
    return [a for a in g["assignments"] if counted(a) and a["score"] is None and a["points"] > 0]


def grade_with(course, fill):
    """Final percentage when each remaining assignment gets fill(a) as a fraction (0..1).

    fill returning None leaves that assignment out (used for the current grade on graded work only).
    """
    num = 0.0
    den = 0.0
    for g in course["groups"]:
        earned = sum(a["score"] for a in graded_after_drops(g))
        possible = sum(a["points"] for a in graded_after_drops(g))
        for a in remaining(g):
            f = fill(a)
            if f is None:
                continue
            earned += f * a["points"]
            possible += a["points"]
        if possible <= 0:
            continue
        if course["weighted"]:
            num += g["weight"] * earned / possible
            den += g["weight"]
        else:
            num += earned
            den += possible
    if den <= 0:
        return None
    return 100.0 * num / den


def group_average(course, g):
    graded = [a for a in graded_after_drops(g) if a["points"] > 0]
    pts = sum(a["points"] for a in graded)
    if pts > 0:
        return sum(a["score"] for a in graded) / pts
    return None


def weight_done(course):
    """Share of the course (0..100) that is already graded."""
    total = 0.0
    done = 0.0
    for g in course["groups"]:
        all_pts = sum(a["points"] for a in g["assignments"] if counted(a) and a["points"] > 0)
        graded_pts = sum(a["points"] for a in graded_after_drops(g) if a["points"] > 0)
        if all_pts <= 0:
            continue
        w = g["weight"] if course["weighted"] else all_pts
        total += w
        done += w * graded_pts / all_pts
    return 100.0 * done / total if total else 0.0


def fmt(x):
    return f"{x:.1f}%"


def parse_what_if(items):
    out = {}
    for item in items or []:
        if "=" not in item:
            raise InputError(f"--what-if needs NAME=PERCENT, got: {item}")
        name, val = item.rsplit("=", 1)
        try:
            out[name.strip().lower()] = float(val.strip().rstrip("%")) / 100.0
        except ValueError:
            raise InputError(f"--what-if percent is not a number: {item}")
    return out


def find_assignment(course, name):
    name = name.strip().lower()
    matches = []
    for g in course["groups"]:
        for a in remaining(g):
            if a["name"].lower() == name:
                return a, g
            if name in a["name"].lower():
                matches.append((a, g))
    if len(matches) == 1:
        return matches[0]
    return None, None


def analyze(course, target=None, solve_for=None, assume=None, what_if=None):
    cut = course["cutoffs"]
    what_if = what_if or {}
    lines = []
    result = {"course": course["course"]}

    # Apply what-ifs as if those scores were already in.
    for g in course["groups"]:
        for a in remaining(g):
            for key, frac in what_if.items():
                if key == a["name"].lower() or key in a["name"].lower():
                    a["score"] = round(frac * a["points"], 4)
                    a["what_if"] = True
                    break

    current = grade_with(course, lambda a: None)
    result["current"] = current
    done = weight_done(course)
    result["percent_of_course_graded"] = done
    if current is None:
        lines.append(f"{course['course']}: nothing has been graded yet.")
    else:
        lines.append(f"{course['course']}: {fmt(current)} right now ({letter_for(current, cut)}), "
                     f"with {done:.0f}% of the course graded.")

    left = [(a, g) for g in course["groups"] for a in remaining(g)]
    result["remaining_count"] = len(left)
    if not left:
        lines.append("Nothing left to grade, so this is the final grade unless something changes.")
        return result, lines, 3

    worst = grade_with(course, lambda a: 0.0)
    best = grade_with(course, lambda a: 1.0)
    result["worst"], result["best"] = worst, best
    lines.append(f"Range from here: {fmt(worst)} if you get 0 on everything left, {fmt(best)} if you ace it all.")

    # Uniform average needed on all remaining work.
    span = best - worst
    needs = {}
    letters = [target] if target else list(cut.keys())
    lines.append("To finish with:")
    for letter in letters:
        if letter not in cut:
            raise InputError(f"Unknown letter '{letter}'. This course uses: {', '.join(cut)}")
        t = cut[letter]
        if worst >= t - 1e-9:
            needs[letter] = 0.0
            lines.append(f"- {letter} ({t:g}%): already locked in")
        elif span <= 0 or best < t - 1e-9:
            x = 100.0 * (t - worst) / span if span > 0 else float("inf")
            needs[letter] = x
            lines.append(f"- {letter} ({t:g}%): out of reach (would need {x:.0f}% average)" if span > 0
                         else f"- {letter} ({t:g}%): out of reach")
        else:
            x = 100.0 * (t - worst) / span
            needs[letter] = x
            lines.append(f"- {letter} ({t:g}%): average {fmt(x)} on what's left")
    result["average_needed"] = needs

    # Assumed score on the other remaining work.
    def assumed(a, g):
        if assume is not None:
            return assume / 100.0
        avg = group_average(course, g)
        if avg is None:
            avg = (current / 100.0) if current is not None else 0.85
        return min(max(avg, 0.0), 1.0)

    code = 0
    if solve_for:
        fa, fg = find_assignment(course, solve_for)
        if fa is None:
            lines.append(f"Couldn't find one ungraded assignment matching '{solve_for}'.")
            code = 4
        else:
            others = {id(a): assumed(a, g) for a, g in left if a is not fa}
            g0 = grade_with(course, lambda a: 0.0 if a is fa else others[id(a)])
            g1 = grade_with(course, lambda a: 1.0 if a is fa else others[id(a)])
            basis = (f"{assume:g}%" if assume is not None else "your current average in each category")
            lines.append(f"On {fa['name']} (other remaining work at {basis}):")
            solved = {}
            for letter in letters:
                t = cut[letter]
                if g0 >= t - 1e-9:
                    solved[letter] = 0.0
                    lines.append(f"- {letter}: locked in even with a 0")
                elif g1 < t - 1e-9:
                    x = 100.0 * (t - g0) / (g1 - g0) if g1 > g0 else float("inf")
                    solved[letter] = x
                    lines.append(f"- {letter}: not possible on this alone (would need {x:.0f}%)")
                else:
                    x = 100.0 * (t - g0) / (g1 - g0)
                    solved[letter] = x
                    lines.append(f"- {letter}: {fmt(x)}")
            result["solve_for"] = {"assignment": fa["name"], "needed": solved}

    # Which remaining items move the grade most (percentage points between 0 and 100 on that item).
    swings = []
    base = {id(a): assumed(a, g) for a, g in left}
    for a, g in left:
        hi = grade_with(course, lambda b: 1.0 if b is a else base[id(b)])
        lo = grade_with(course, lambda b: 0.0 if b is a else base[id(b)])
        swings.append((hi - lo, a))
    swings.sort(key=lambda s: -s[0])
    result["biggest_swings"] = [{"assignment": a["name"], "points": round(s, 2), "due": a.get("due")}
                                for s, a in swings[:5]]
    lines.append("Biggest swing left:")
    for s, a in swings[:3]:
        due = f", due {a['due']}" if a.get("due") else ""
        lines.append(f"- {a['name']}: worth up to {s:.1f} pts of your grade{due}")

    if any(g["drop_lowest"] for g in course["groups"]):
        lines.append("Note: dropped scores are applied to graded work only.")
    if what_if:
        lines.append("Includes the what-if scores you gave.")
    return result, lines, code


def main(argv=None):
    p = argparse.ArgumentParser(description="Exact grade math for one course.")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--input", help="Path to the course JSON file")
    src.add_argument("--sample", action="store_true", help="Use the bundled sample course")
    p.add_argument("--target", help="Only show this letter (for example B)")
    p.add_argument("--solve-for", help="Name (or part of it) of one ungraded assignment, such as 'Final'")
    p.add_argument("--assume", type=float, help="Percent to assume on other remaining work (default: current average per category)")
    p.add_argument("--what-if", action="append", metavar="NAME=PERCENT", help="Pretend an ungraded item got this score; repeatable")
    p.add_argument("--json", action="store_true", help="Print JSON instead of text")
    args = p.parse_args(argv)

    try:
        course = load_course(SAMPLE if args.sample else args.input)
        result, lines, code = analyze(course, target=args.target, solve_for=args.solve_for,
                                      assume=args.assume, what_if=parse_what_if(args.what_if))
    except InputError as e:
        print(f"error: {e}")
        return 2

    if args.json:
        def clean(o):
            if isinstance(o, float):
                return None if o != o or o in (float("inf"), float("-inf")) else round(o, 2)
            if isinstance(o, dict):
                return {k: clean(v) for k, v in o.items()}
            if isinstance(o, list):
                return [clean(v) for v in o]
            return o
        print(json.dumps(clean(result), indent=2))
    else:
        print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main())
