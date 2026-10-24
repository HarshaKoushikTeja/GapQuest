# Cubbie Student Skills

Three Cubbie Skills for the moments college students actually text about. Built for the Cubbie Hackathon (Track 1).

| Skill | The moment | What Cubbie does |
| --- | --- | --- |
| [grade-rescue](skills/grade-rescue) | "What do I need on the final to keep a B?" | Reads your Canvas grades and weights, does the exact math, shows which assignments move your grade most, and checks in weekly only when the numbers change |
| [career-fair-followup](skills/career-fair-followup) | "Met 5 recruiters, emailed none." | Turns notes, voice memos or business-card photos into personal follow-up emails (Gmail drafts, never sent without your yes) and nudges you a week later |
| [late-night-food-run](skills/late-night-food-run) | "It's 1 AM. What's actually open?" | Three places really open near campus, within your budget and diet; hands you the checkout |

## Install on Cubbie

Text Cubbie the link to a Skill's folder, for example:

```text
https://github.com/<owner>/cubbie-student-skills/tree/main/skills/grade-rescue
```

Reply "yes" when Cubbie asks before fetching. Then ask it the way you normally would: "what do I need on my econ final for a B?"

## Try the grade math without Cubbie

```bash
cd skills/grade-rescue
python3 scripts/grade_math.py --sample --target B --solve-for final
```

Standard library only (Python 3.9+). Your grades stay on your own Cubbie drive; nothing is sent to any server.
