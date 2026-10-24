---
name: gapquest
description: Finds campus events, club meetings, workshops and free food that fit inside the gaps in a student's day, using their calendar and ASU's Sun Devil Central events feed, and sends a short morning brief. Use whenever a student asks "what's happening on campus today", "anything to do between classes", "where's the free food", "any free pizza today", "I'm broke and hungry", "what should I go to tonight", "any AI or career events this week", says they're bored or want to meet people, or wants a daily morning summary of their day, even if they don't say "events". Works for any school whose events site offers an iCal subscribe link.
---

# GapQuest

Students miss most of what happens on campus because nobody checks Sun Devil Central between classes. This Skill
looks at the student's day, finds the real gaps, and picks the two or three events worth walking to, every
morning if they want.

It is different from Cubbie's built-in `study-plan-builder`: this finds things to attend, not study time.

## When to use

- "What's happening on campus today?"
- "I have a 2 hour gap after my 12:00, anything going on?"
- "Any free food events tonight?" / "where's the free pizza at" / "broke till Friday, any free food?" (step 5)
- "Send me a morning summary of my day with events I can go to."
- "Any AI or career events this week?" (run it for each day of the week, step 6)

Do not use it to register for events on the student's behalf, or for events off campus.

## Settings (first use, then remembered)

Use what Cubbie remembers about the student. Ask only for what is missing, one question at a time, each with a
default they can accept with "yes", and remember every answer:

1. Campus: Tempe, Downtown Phoenix, Polytechnic or West Valley. ("Tempe?")
2. Interests, a few words: for example "ai, career, free food, cricket, movies".
3. Anything to skip: for example "spiritual, housing". Default: nothing.
4. Online events too? Default: no.
5. Hours to suggest events in. Default 8 am to 10 pm. Minutes to walk between places. Default 15.
6. The events feed. Default: ASU's Sun Devil Central,
   https://sundevilcentral.eoss.asu.edu/ical/arizonau/ical_arizonau.ics
   For another school, ask the student to open their events site, tap Subscribe (or "Add to calendar"), and send
   the iCal link. Pass it with `--feed`.

When the student later says "not into X" or "more like that", update the interests or the skip list.

## Steps

1. **Local time.** Take the student's current local date and time with its UTC offset, for example
   `2026-10-27T07:30-07:00` (Arizona is always -07:00). Never use the computer's clock or time zone.

2. **Busy times.** With Cubbie's Google ability, read the student's Google Calendar for the day. Every timed event is
   a busy block; skip all-day events and events marked free. If Google isn't connected, ask once for their weekly
   class schedule, remember it, and use it as the busy blocks (offer to connect Google for meetings too).

3. **What's due** (for the morning brief only). With Cubbie's Canvas ability, read what is due today. If Canvas isn't
   connected, skip this line.

4. **Run the matcher** from this Skill's folder:

   ```bash
   python3 scripts/radar.py --now "<local ISO time>" --busy "09:00-10:15" --busy "12:00-13:15" --campus "<campus>" --interests "<interests>" --exclude "<skip list>" --top 3
   ```

   - One `--busy` per busy block, in 24-hour local time.
   - Add `--include-online` if the student wants online events, `--day-start`/`--day-end`/`--buffer` if they set
     their own hours or walking time, and `--feed "<link>"` for a school other than ASU.
   - For another day, add `--date YYYY-MM-DD` and use that day's calendar.
   - Add `--json` when you need to combine several days.
   - The script downloads the feed (about 5 MB) and keeps it for an hour, so repeat runs are fast.
   - `--sample --now 2026-10-27T07:30-07:00` runs on a bundled one-day copy of ASU's real feed, with no network and
     nothing saved, for a demo.

5. **Free food.** When the student asks about free food (or is hungry and broke), run step 4 with `--food --top 5`.
   It keeps only events whose description says food is provided or free, names the food ("free pizza, panda
   express"), puts events that fully fit first, then the soonest, and says how many more happen while the student is
   busy. Add `--food-maybe` if nothing comes back, to include events that only mention food; say those are unconfirmed.
   Food drives, potlucks, "percentage nights" and food for purchase are never counted as free. For "right now",
   pass the current time in `--now`; events already underway still count if enough of them is left.

6. **Reply** (see Replies).

7. **"This week" questions.** Run step 4 for each of the next 7 days with `--date` and `--json`, using each day's
   calendar, and send the best five overall as a short list. More than that goes in a one-page document.

8. **When the student picks one.** Offer "Add it to your calendar?" and add it with Cubbie's Google ability only after
   they say yes, with the event link in the notes. Registration needs their own Sun Devil Central sign-in, so send the
   event link and let them tap Register. Never register for them.

9. **Offer the morning brief once.** "Want this every weekday at 7:30 am?" Create the daily check-in with Cubbie's
   reminders ability only after a yes, at the time and days they choose. Word it so it works on its own:
   "GapQuest morning brief: get the student's local time, read today's Google Calendar and today's Canvas due
   dates, run scripts/radar.py with the student's saved campus, interests and skip list, and text the brief. If no
   event fits, send only the due-today line."
   After a free-food question, offer the food alert instead: "Want a heads-up at 11 am on days there's free food in
   your gaps?" Word that check-in: "GapQuest free-food alert: get the student's local time and today's Google
   Calendar, run scripts/radar.py with --food and the saved campus, and text the top two only if any fit; otherwise
   send nothing."

## Replies

Short, plain text, no Markdown. Lead with the best pick. A morning brief looks like:

"Morning! Due today: CSE 310 HW 4, 11:59 pm.
Free: 10:30-11:45, 1:30-4:15, after 6.

Worth it today:
1. 6 pm Lovable Buildathon (AI in Business Club), Tempe
2. 3 pm AI and Multilingualism Lab, Durham Hall 132
3. 5 pm Barrett Boy's Night. Free pizza

Want any on your calendar?"

A free-food reply looks like:

"Free food in your gaps today:
1. 1:30 SILC Café, Durham Hall. Free food
2. 5 pm Barrett Boy's Night. Free pizza
3 more happen while you're in class."

- One line per event: time, short title, host if useful, place. Put a link on its own line only when the student
  asks about a specific event, so the brief stays short.
- "Free pizza" means the event's own description says food is provided; say it that way, and add "while it lasts"
  if the student asks. "Food mentioned" means it only talks about food; don't call that free.
- Most Sun Devil Central events hide the room until the student signs in. Say the campus, and that the room is on
  the event page.
- If an event only partly fits ("you can catch 1:30-3"), say so.
- If nothing fits, say so in one line and mention the next free window.

## When something fails

| Exit code | Meaning | What to do |
| --- | --- | --- |
| 0 | Events found | Reply as above |
| 2 | A time or option was malformed (the script says which) | Fix the arguments and run once more |
| 3 | The feed couldn't be downloaded or isn't a calendar anymore | Say Sun Devil Central isn't reachable right now and send only the due-today line; for another school, ask for a fresh iCal link |
| 5 | No free time in the day | "Your day is packed. Nothing fits until tonight." Offer tomorrow |
| 6 | Free time, but no events fit | Say so and offer to include online events or widen the hours |

Never invent an event, a time or a room.
