# GapQuest

**Every morning Cubbie checks your calendar and Canvas, then texts what's due plus the events, workshops and free food that fit your gaps.**

A [Cubbie](https://hackathon.cubbie.ai) Skill for ASU students. Built for the Cubbie Hackathon, **Track 1**.

> ### Vote for GapQuest
> **https://hackathon.cubbie.ai** (voting needs a `.edu` email; it takes 10 seconds)

---

## The problem

ASU's Sun Devil Central lists thousands of events a semester: club meetings, career workshops, company info sessions,
movie nights, and a lot of free food. Almost nobody checks it. You find out about the AI club's buildathon or the
free pizza at 5 pm the next day, from someone's Instagram story.

Meanwhile you have a 2-hour gap between classes every Tuesday and spend it scrolling. **The events and the free time
both exist. Nothing connects them.**

## What it does

GapQuest lives in iMessage. It looks at your day, finds the real gaps, and picks the two or three things on campus
worth walking to.

| Step | What happens |
|---|---|
| **Read your day** | Cubbie reads today's Google Calendar and what's due on Canvas. |
| **Find the gaps** | It works out your free windows, with walking time around each class. |
| **Match events** | It pulls today's events from Sun Devil Central and keeps only the ones you can actually make. |
| **Rank for you** | It ranks them by your interests (AI, career, cricket, movies...) and your campus. |
| **Free food** | "Where's the free food today?" lists only events whose description says food is provided, and names it: pizza, Panda Express, donuts. |
| **Morning brief** | Opt in once and get it every weekday at 7:30 am. Or an 11 am free-food alert that only texts when there's food in your gaps. |
| **Add it** | "Add the 6 pm one" puts it on your calendar. You tap Register yourself. |

### And it handles the rest of your week

| Mode | You text | GapQuest does |
|---|---|---|
| **Grade Rescue** | "What do I need on the ECON final to keep a B?" | Reads your Canvas grades and category weights, does the exact math (drops, extra credit, what-ifs), shows which assignments move your grade most, and checks in weekly only when the numbers change. |
| **Career Fair Follow-Up** | "Met 4 recruiters today" + business-card photos | Turns notes, voice memos and cards into personal follow-up emails saved as Gmail drafts (never sent for you), and nudges you a week later about anyone who didn't reply. |
| **Deal Finder** | "Where can I get AirPods Pro cheapest?" | Compares retailers, education pricing, student discounts, refurbished, textbook rentals and local listings by the real total after shipping and Tempe sales tax. Opens the cart; you pay. |
| **Late-Night Food Run** | "It's 1 am, what's open?" | Three places really open near campus, within your budget and diet, with closing times. |

## See it

Real output from ASU's Sun Devil Central feed:

```text
Cubbie:  Morning! Due today: CSE 310 HW 4, 11:59 pm.
         Free: 10:30-11:45, 1:30-4:15, after 6.

         Worth it today:
         1. 6 pm Lovable Buildathon (AI in Business Club), Tempe
         2. 3 pm AI and Multilingualism Lab, Durham Hall 132
         3. 5 pm Barrett Boy's Night. Free pizza

         Want any on your calendar?

You:     broke till friday, any free food today?

Cubbie:  Free food in your gaps today:
         1. 1:30 SILC Café, Durham Hall. Free food
         2. 5 pm Barrett Boy's Night. Free pizza
         3 more happen while you're in class.
```

## Try it

1. Text Cubbie this link:
   `https://github.com/HarshaKoushikTeja/GapQuest`
2. Reply "yes" when Cubbie asks to install it. No app, no account, no ASU sign-in.
3. Ask: "what's happening on campus today?", "where's the free food?", "what do I need on my final for a B?",
   "where can I get this cheaper?" or send a photo of a recruiter's business card.

## Why it's different

- **It knows your schedule.** Not a list of 60 events. Only the ones that fit between your classes, with walking time.
- **Proactive.** One morning text with what's due and what's worth going to. Silent on days with nothing.
- **Free food you can trust.** It reads each event's description and only says "free" when the event says so. Food drives, potlucks and "percentage nights" never count.
- **No login.** It uses Sun Devil Central's public calendar feed, so there's no ASU password or Duo prompt.
- **One install, your whole week.** Events, free food, grades, networking, deals and late-night food in one Skill. Just text it.
- **Exact where it matters.** Grade math, price totals and free-time matching run in small scripts, so the numbers are right, not guessed.
- **Asks before acting.** It never registers you, sends an email, changes your calendar or pays without a yes.

## How it works

The Skill is a set of instructions plus three small scripts.

```
SKILL.md                     Modes, the events steps, and the rules every mode follows
references/grades.md         Grade Rescue steps          references/course-file.md   its data format
references/networking.md     Career Fair Follow-Up steps
references/deals.md          Deal Finder steps           references/offers-file.md   its data format
references/food-run.md       Late-Night Food Run steps
scripts/radar.py             Events feed -> free windows -> matched, ranked events (and free food)
scripts/grade_math.py        Exact grade math: current grade, range, what you need, biggest swings, what-ifs
scripts/compare.py           Ranks offers by real total: price - discounts + shipping + tax
assets/                      Sample data for each script, so everything runs offline
```

Sun Devil Central's feed is about 5 MB and 5,000 events. `radar.py` downloads it (cached for an hour, since the feed
refreshes hourly), turns your busy blocks into free windows, keeps events that fit at least 30 minutes, skips other
campuses and multi-week listings, classifies food as free / mentioned / paid, and ranks by your interests. It needs
only Python 3. No packages, no keys.

Try it without Cubbie:

```bash
python3 scripts/radar.py --sample --now 2026-10-27T07:30-07:00 --busy 09:00-10:15 --busy 12:00-13:15 --campus Tempe --interests "ai,career,free food"
python3 scripts/radar.py --sample --now 2026-10-27T07:30-07:00 --busy 09:00-10:15 --campus Tempe --food
python3 scripts/grade_math.py --sample --target B --solve-for final
python3 scripts/compare.py --sample --tax-rate 8.1
```

**Other schools.** Sun Devil Central runs on CampusGroups, and other CampusGroups schools have the same Subscribe
link on their events page. Give GapQuest that link and it works there too.

## What it won't do

- Register you for events, send an email or message for you, place an order or pay.
- Do your graded work, or contact anyone but you.
- Promise free food the event didn't mention, or invent an event, grade, price or coupon.
- Show rooms that Sun Devil Central hides behind sign-in. It gives the campus and the event link instead.

## Built for the Cubbie Hackathon

Track 1 asks for a Skill students would miss if it disappeared. GapQuest turns the dead time between classes into
the events, people and free food you would otherwise hear about the next day, and covers the rest of the week too:
the final you're worried about, the recruiters you meant to email, the thing you almost paid full price for.

**If you'd use this, [vote for GapQuest](https://hackathon.cubbie.ai).** `.edu` email needed.
