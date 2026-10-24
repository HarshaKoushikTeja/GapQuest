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
3. Ask: "what's happening on campus today?" or "where's the free food?"

## Why it's different

- **It knows your schedule.** Not a list of 60 events. Only the ones that fit between your classes, with walking time.
- **Proactive.** One morning text with what's due and what's worth going to. Silent on days with nothing.
- **Free food you can trust.** It reads each event's description and only says "free" when the event says so. Food drives, potlucks and "percentage nights" never count.
- **No login.** It uses Sun Devil Central's public calendar feed, so there's no ASU password or Duo prompt.
- **Asks before acting.** It never registers you or changes your calendar without a yes.

## How it works

The Skill is a set of instructions (`SKILL.md`) plus one small script.

```
SKILL.md                When to use it, and the steps Cubbie follows
scripts/radar.py        Downloads the events feed, finds free windows, matches and ranks events
assets/sample_feed.ics  One real day of ASU events, for trying it offline
```

Sun Devil Central's feed is about 5 MB and 5,000 events. `radar.py` downloads it (cached for an hour, since the feed
refreshes hourly), turns your busy blocks into free windows, keeps events that fit at least 30 minutes, skips other
campuses and multi-week listings, classifies food as free / mentioned / paid, and ranks by your interests. It needs
only Python 3. No packages, no keys.

Try it without Cubbie:

```bash
python3 scripts/radar.py --sample --now 2026-10-27T07:30-07:00 --busy 09:00-10:15 --busy 12:00-13:15 --campus Tempe --interests "ai,career,free food"
python3 scripts/radar.py --sample --now 2026-10-27T07:30-07:00 --busy 09:00-10:15 --campus Tempe --food
```

**Other schools.** Sun Devil Central runs on CampusGroups, and other CampusGroups schools have the same Subscribe
link on their events page. Give GapQuest that link and it works there too.

## What it won't do

- Register you for events or send anything for you.
- Promise free food the event didn't mention, or invent an event, time or room.
- Show rooms that Sun Devil Central hides behind sign-in. It gives the campus and the event link instead.

## Built for the Cubbie Hackathon

Track 1 asks for a Skill students would miss if it disappeared. GapQuest turns the dead time between classes into
the events, people and free food you would otherwise hear about the next day.

**If you'd use this, [vote for GapQuest](https://hackathon.cubbie.ai).** `.edu` email needed.
