# Course file format

`scripts/grade_math.py` reads one JSON file per course. Build it from Canvas (or from a grades screenshot or the
syllabus) and save it to `~/.config/grade-rescue/<course-code>.json`.

```json
{
  "course": "ECON 201",
  "weighted": true,
  "cutoffs": {"A": 90, "B": 80, "C": 70, "D": 60},
  "groups": [
    {
      "name": "Homework",
      "weight": 20,
      "drop_lowest": 1,
      "assignments": [
        {"name": "HW 1", "points": 10, "score": 9},
        {"name": "HW 5", "points": 10, "score": null, "due": "Thu Nov 5"},
        {"name": "HW 2", "points": 10, "score": null, "excused": true}
      ]
    },
    {
      "name": "Final Exam",
      "weight": 30,
      "assignments": [{"name": "Final Exam", "points": 150, "score": null, "due": "Tue Dec 8"}]
    }
  ]
}
```

Fields:

- `course`: name to show in replies.
- `weighted`: `true` when the course weights assignment groups (each group has a `weight`, in percent; they don't
  need to add up to 100, the script normalizes). `false` when the grade is total points earned over total points
  possible; then `weight` is ignored.
- `cutoffs`: the course's letter scale, highest first is not required. Include plus/minus letters if the syllabus
  uses them, for example `{"A": 93, "A-": 90, "B+": 87, ...}`. Leave it out to use 90/80/70/60.
- `groups[].drop_lowest`: how many of the lowest graded scores in that group are dropped (0 if none).
- `assignments[].points`: points possible. Use 0 for extra credit that is graded on top.
- `assignments[].score`: points earned, or `null` when it is not graded yet.
- `assignments[].excused`: `true` to leave it out completely.
- `assignments[].due`: optional, shown next to the biggest-swing items. Use the student's local date, short form.

Leave out assignments that don't count toward the grade (practice quizzes, surveys with 0 points and no score).
