# GapQuest

You have 2 hours between classes and no plan. GapQuest is a Cubbie Skill that checks your calendar and ASU's Sun Devil Central, then texts you the club events, workshops and free food that fit your free time. Ask "where’s the free food today?" and it lists only events that say food is provided. Built for the Cubbie Hackathon (Track 1).

**Install:** text Cubbie this link and reply "yes":

```text
https://github.com/HarshaKoushikTeja/GapQuest/tree/main/skills/gapquest
```

Then ask: "what's happening on campus today?" or "send me a morning brief every weekday at 7:30".

## More Skills in this repo

Install any of them the same way, with its folder link.

| Skill | The moment | What Cubbie does |
| --- | --- | --- |
| [grade-rescue](skills/grade-rescue) | "What do I need on the final to keep a B?" | Reads your Canvas grades and weights, does the exact math, shows which assignments move your grade most, and checks in weekly only when the numbers change |
| [career-fair-followup](skills/career-fair-followup) | "Met 5 recruiters, emailed none." | Turns notes, voice memos or business-card photos into personal follow-up emails (Gmail drafts, never sent without your yes) and nudges you a week later |
| [gapquest](skills/gapquest) | "I have 3 hours free and no idea what is on campus." | Matches Sun Devil Central events to the gaps in your calendar and your interests; optional 7:30 am brief |
| [student-deal-finder](skills/student-deal-finder) | "About to pay full price for this." | Finds the cheapest real total (shipping, tax, student discounts, used and local pickup) and hands you the checkout |
| [late-night-food-run](skills/late-night-food-run) | "It's 1 AM. What's actually open?" | Three places really open near campus, within your budget and diet; hands you the checkout |

## Install on Cubbie

Text Cubbie the link to a Skill's folder, for example:

```text
https://github.com/HarshaKoushikTeja/GapQuest/tree/main/skills/grade-rescue
```

Reply "yes" when Cubbie asks before fetching. Then ask it the way you normally would: "what do I need on my econ final for a B?"

## Try the scripts without Cubbie

```bash
python3 skills/gapquest/scripts/radar.py --sample --now 2026-10-27T07:30-07:00 --busy 09:00-10:15 --campus Tempe --interests "ai,career,free food"
```

Grade math:

```bash
cd skills/grade-rescue
python3 scripts/grade_math.py --sample --target B --solve-for final
```

Standard library only (Python 3.9+). Your grades stay on your own Cubbie drive; nothing is sent to any server.
