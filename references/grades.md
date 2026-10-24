# GapQuest mode: Grade Rescue

Read this when the student's request matches this mode (see the Modes table in SKILL.md). Commands run from the GapQuest folder. The Replies and asking-first rules in SKILL.md apply here too.

The student wants one honest number: what they need from here. Get their real grades and the course's
weighting, let the script do the exact math, and answer in a couple of short texts.

Cubbie's built-in `study-plan-builder` makes study plans; this mode does the grade math and what-ifs, then
points the student at the assignments that matter most. If they then want a study plan, hand off to that.

## When to use

- "What do I need on the ECON final to keep a B?"
- "Can I still get an A in CSE 310?"
- "I got a 62 on the midterm. Am I cooked?"
- "What if I get an 80 on Midterm 2?"
- "How am I doing in my classes?" (run it for each course, see step 6)

Do not use it to change grades, contact the professor about a grade (that is `email-to-professor`), or do graded
work for the student.

## Steps

1. **Pick the course and the goal.** Use the course the student named; if they didn't, ask which one (offer the
   courses from Canvas). Use the letter they named; otherwise use the target letter remembered for that course;
   otherwise show every letter. When the student names a goal, remember it for that course.

2. **Get the grades and weights from Canvas.** With Cubbie's Canvas ability, read for that course:
   - every assignment group with its weight, its drop rules (drop lowest N) and whether the course weights groups
     at all (if not, grades are total points),
   - every assignment with points possible, the student's score (or that it is not graded yet), whether it is
     excused, and its due date,
   - the course's grading scheme (letter cutoffs) if Canvas has one.

   If Canvas is not connected or a weight is missing, ask the student for a screenshot of the course's Grades page
   or a photo of the syllabus grading section and read it with Cubbie's file-reading ability. Ask for any number
   you still can't find. Never guess a weight, a cutoff or a score; a wrong weight gives a confidently wrong answer.
   If nothing gives the cutoffs, use 90/80/70/60 and say so in one short line.

3. **Write the course file** to `~/.config/gapquest/grades/<course-code>.json` (create the folder if needed; lowercase
   course code with dashes, such as `econ-201.json`). The format is in `references/course-file.md`. Overwrite it
   with fresh Canvas data each time so it never goes stale.

4. **Run the math** from this Skill's folder:

   ```bash
   python3 scripts/grade_math.py --input ~/.config/gapquest/grades/<course-code>.json --target <letter> --solve-for "<final exam name>"
   ```

   - Leave out `--target` to show every letter.
   - Add `--solve-for` when the student asks about one assignment (usually the final). Use part of its name as it
     appears in Canvas. Other ungraded work is then assumed at the student's current average in each category;
     if the student says how they expect to do ("assume I get 90s on homework"), pass `--assume 90`.
   - For "what if I get a 70 on Midterm 2", add `--what-if "Midterm 2=70"` (repeatable).
   - Add `--json` only if you need the numbers to build something else, such as the multi-course summary.
   - `--sample` runs on a bundled example course without any student data, for a demo or a quick check.

5. **Reply** (see Replies). Lead with the number they asked for.

6. **"How am I doing in my classes?"** Run steps 2 to 4 for each current course with `--json`. Text one line per
   course (current percent, letter, and the average needed on what's left to keep that letter), and call out the
   course closest to slipping a letter. If there are more than five courses, send a short PDF and text the top three.

7. **Offer one follow-up**, one question at a time, with a default they can accept with "yes":
   - Reminders before the biggest-swing items the script lists ("Want reminders 2 days before Midterm 2 and the
     final?"). Create them with Cubbie's reminders ability only after the student says yes. Each reminder names the
     course, the assignment, its due date and the score the student needs on it.
   - A weekly check-in ("Sunday 7 pm?"). Create it only after a yes. Word it so it works on its own days later:
     "GapQuest grade check for <course>: re-read the Canvas grades, rewrite
     ~/.config/gapquest/grades/<course-code>.json, run scripts/grade_math.py with target <letter>, and text the student
     only if a new grade posted or the score needed on what's left changed by 3 points or more."

## Replies

Short, plain text, no Markdown, a few lines per message. Lead with the answer.

- First message: the one number they asked for, then the current grade. For example:
  "You need an 83% on the ECON 201 final to keep your B.
  You're at 78.8% now, with 38% of the course graded."
- Second message, only if useful: the biggest swing left, or the range ("Worst case 31%, best case 92%").
- If the goal is out of reach, say so plainly and kindly, then give the best letter still possible and what it
  takes. Don't soften the math, and don't lecture.
- If it is already locked in, say that first; it's good news.
- If Canvas shows a current score that differs from the script's, say both in one line and why it can happen
  (Canvas may count missing work as zero or hide some groups), and ask the student which matches their syllabus.
- Round to one decimal. Never show raw JSON or the command.
- Finish with at most one offer from step 7.

## When something fails

| Exit code | Meaning | What to do |
| --- | --- | --- |
| 0 | Done | Reply as above |
| 2 | The course file is missing or malformed (the script prints which field) | Fix the file from the Canvas data and run again once; if a value is truly missing, ask the student for it |
| 3 | Nothing left to grade | Tell them the grade is effectively final and what it is |
| 4 | `--solve-for` matched no ungraded assignment, or several | List the ungraded assignment names and ask which one they mean |

Never make up a number when the script fails.
