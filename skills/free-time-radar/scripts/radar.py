#!/usr/bin/env python3
"""Free Time Radar: match campus events to a student's free time for one day.

Reads a CampusGroups / iCalendar events feed (ASU's Sun Devil Central by default), keeps the events that happen on
the given day and fit the student's free windows, ranks them by the student's interests, and prints a short list.

Cubbie fetches the student's calendar first and passes busy blocks in; this script never touches the calendar.
Standard library only (Python 3.9+).

Exit codes:
  0  ok (events found)
  2  bad arguments
  3  the feed could not be downloaded or read
  5  no free time left in the day
  6  free time exists but no events fit it
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone

ASU_FEED = "https://sundevilcentral.eoss.asu.edu/ical/arizonau/ical_arizonau.ics"
HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE_FEED = os.path.join(HERE, "..", "assets", "sample_feed.ics")
CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "free-time-radar")
CACHE_TTL = 3600  # the feed says it refreshes hourly
MAX_EVENT_HOURS = 12  # longer "events" are multi-week listings, not something to drop into
HIDDEN_LOCATION = "sign in to download the location"

FOOD_RE = re.compile(
    r"\b(free (food|pizza|lunch|dinner|breakfast|snacks?|boba|tacos?|donuts?|coffee|drinks?|meal)|"
    r"food (will be |is )?(provided|served)|refreshments|snacks (will be )?provided|pizza|boba|bbq|barbecue|"
    r"potluck|tacos?|donuts?|catered|cookies)\b", re.I)


class RadarError(Exception):
    def __init__(self, msg, code):
        super().__init__(msg)
        self.code = code


# ---------- feed ----------

def fetch_feed(url, refresh=False):
    os.makedirs(CACHE_DIR, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9]+", "_", url)[-120:]
    path = os.path.join(CACHE_DIR, safe + ".ics")
    if not refresh and os.path.exists(path) and time.time() - os.path.getmtime(path) < CACHE_TTL:
        return path
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "free-time-radar/1.0 (Cubbie Skill)"})
        with urllib.request.urlopen(req, timeout=45) as r:
            data = r.read()
    except Exception as e:  # network, HTTP, TLS
        if os.path.exists(path):
            return path  # stale cache beats nothing
        raise RadarError(f"Couldn't download the events feed: {e}", 3)
    if b"BEGIN:VCALENDAR" not in data[:2000]:
        raise RadarError("The events link didn't return a calendar feed (it may need a sign-in now).", 3)
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)
    return path


def unescape(s):
    s = s.replace("\\n", "\n").replace("\\N", "\n").replace("\\,", ",").replace("\\;", ";").replace("\\\\", "\\")
    return s.replace("ﾠ", " ").strip()


def parse_dt(value):
    value = value.strip()
    if re.fullmatch(r"\d{8}T\d{6}Z", value):
        return datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    if re.fullmatch(r"\d{8}T\d{6}", value):  # floating time: treat as UTC-less local, handled by caller
        return datetime.strptime(value, "%Y%m%dT%H%M%S")
    if re.fullmatch(r"\d{8}", value):
        return datetime.strptime(value, "%Y%m%d")
    return None


def parse_ics(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        raw = f.read().replace("\r\n", "\n").replace("\r", "\n")
    raw = re.sub(r"\n[ \t]", "", raw)  # unfold
    events = []
    for block in raw.split("BEGIN:VEVENT")[1:]:
        block = block.split("END:VEVENT")[0]
        ev = {"tags": [], "type": "", "club": ""}
        for line in block.split("\n"):
            if ":" not in line:
                continue
            key, val = line.split(":", 1)
            name = key.split(";")[0].upper()
            if name == "SUMMARY":
                ev["title"] = unescape(val)
            elif name == "DTSTART":
                ev["start"] = parse_dt(val)
            elif name == "DTEND":
                ev["end"] = parse_dt(val)
            elif name == "LOCATION":
                loc = unescape(val)
                ev["location"] = "" if loc.lower().startswith(HIDDEN_LOCATION) else loc
            elif name == "URL":
                ev["url"] = val.strip()
            elif name == "DESCRIPTION":
                ev["description"] = unescape(val)
            elif name == "ORGANIZER":
                m = re.search(r'CN="?([^":;]+)', key)
                ev["host"] = m.group(1).strip() if m else ""
            elif name == "CATEGORIES":
                m = re.search(r"X-CG-CATEGORY=([a-z_]+)", key, re.I)
                kind = m.group(1).lower() if m else "tags"
                if kind == "event_type":
                    ev["type"] = unescape(val)
                elif kind == "club_acronym":
                    ev["club"] = unescape(val)
                else:
                    ev["tags"] += [t.strip() for t in unescape(val).split(",") if t.strip()]
        if ev.get("start") and ev.get("title"):
            ev.setdefault("end", ev["start"] + timedelta(hours=1))
            ev["tags"] = list(dict.fromkeys(ev["tags"]))
            events.append(ev)
    return events


# ---------- time ----------

def parse_hhmm(s, day, tz):
    m = re.fullmatch(r"\s*(\d{1,2}):?(\d{2})?\s*(am|pm)?\s*", s, re.I)
    if not m:
        raise RadarError(f"Can't read the time '{s}'. Use 24-hour HH:MM, like 14:30.", 2)
    h, mi, ap = int(m.group(1)), int(m.group(2) or 0), (m.group(3) or "").lower()
    if ap == "pm" and h < 12:
        h += 12
    if ap == "am" and h == 12:
        h = 0
    if h == 24 and mi == 0:
        return datetime(day.year, day.month, day.day, tzinfo=tz) + timedelta(days=1)
    if not (0 <= h < 24 and 0 <= mi < 60):
        raise RadarError(f"Time out of range: '{s}'.", 2)
    return datetime(day.year, day.month, day.day, h, mi, tzinfo=tz)


def parse_busy(items, day, tz):
    blocks = []
    for item in items:
        if "-" not in item:
            raise RadarError(f"Busy block '{item}' needs START-END, like 09:00-10:15.", 2)
        a, b = item.split("-", 1)
        s, e = parse_hhmm(a, day, tz), parse_hhmm(b, day, tz)
        if e <= s:
            raise RadarError(f"Busy block '{item}' ends before it starts.", 2)
        blocks.append((s, e))
    return sorted(blocks)


def free_windows(day_start, day_end, busy, buffer_min, min_gap):
    buf = timedelta(minutes=buffer_min)
    padded = sorted((s - buf, e + buf) for s, e in busy)
    windows, cur = [], day_start
    for s, e in padded:
        if s > cur:
            windows.append((cur, min(s, day_end)))
        cur = max(cur, e)
        if cur >= day_end:
            break
    if cur < day_end:
        windows.append((cur, day_end))
    return [(s, e) for s, e in windows if e > s and (e - s) >= timedelta(minutes=min_gap)]


def fmt_time(dt):
    return dt.strftime("%I:%M %p").lstrip("0").replace(":00 ", " ").lower()


# ---------- matching ----------

def campus_of(ev):
    camps = [t.replace(" Campus", "") for t in ev["tags"] if t.endswith("Campus")]
    online = any(t in ("Online Event",) for t in ev["tags"]) or ev.get("location", "").lower() == "online event"
    return camps, online


def score(ev, interests, campus):
    text = " ".join([ev["title"], ev.get("description", ""), ev["type"], ev.get("host", ""), " ".join(ev["tags"])]).lower()
    s, why = 0.0, []
    for kw in interests:
        k = kw.strip().lower()
        if not k:
            continue
        if k in ("free food", "food"):
            continue
        rx = re.compile(r"\b" + re.escape(k) + r"s?\b", re.I)
        if rx.search(ev["title"]) or rx.search(ev["type"]) or any(rx.search(t) for t in ev["tags"]):
            s += 3; why.append(kw.strip())
        elif rx.search(text):
            s += 1.5; why.append(kw.strip())
    if ev["food"]:
        s += 2.5 if any(k.strip().lower() in ("free food", "food") for k in interests) else 1.0
    camps, online = campus_of(ev)
    if campus and campus.lower() in [c.lower() for c in camps]:
        s += 1
    elif campus and not camps and not online:
        s -= 0.5  # campus not listed; could be anywhere
    if ev["type"] in ("Meeting",) and "Club Meetings" in ev["tags"] and not why:
        s -= 1  # routine meetings of clubs the student didn't ask about
    return s, why


def matches(events, day_start, day_end, windows, campus, include_online, interests, exclude, min_attend):
    out = []
    for ev in events:
        st, en = ev["start"], ev["end"]
        if st.tzinfo is None:  # floating time: assume the student's zone
            st = st.replace(tzinfo=day_start.tzinfo); en = en.replace(tzinfo=day_start.tzinfo)
        st, en = st.astimezone(day_start.tzinfo), en.astimezone(day_start.tzinfo)
        if en <= day_start or st >= day_end:
            continue
        if (en - st) > timedelta(hours=MAX_EVENT_HOURS):
            continue
        camps, online = campus_of(ev)
        here = bool(campus) and campus.lower() in [c.lower() for c in camps]
        if online and not camps and not include_online:
            continue  # online-only event, student didn't ask for online
        if campus and camps and not here and not (online and include_online):
            continue  # tagged for other campuses only
        blob = " ".join([ev["title"], ev["type"], ev.get("host", ""), " ".join(ev["tags"])]).lower()
        if any(x.strip().lower() and x.strip().lower() in blob for x in exclude):
            continue
        best = None
        for ws, we in windows:
            o_s, o_e = max(st, ws), min(en, we)
            if o_e <= o_s:
                continue
            overlap = o_e - o_s
            need = min(timedelta(minutes=min_attend), en - st)
            if overlap >= need and (best is None or overlap > best[0]):
                best = (overlap, o_s, o_e)
        if not best:
            continue
        ev = dict(ev)
        ev["food"] = bool(FOOD_RE.search(ev["title"] + " " + ev.get("description", "")))
        s, why = score(ev, interests, campus)
        full = best[1] <= st and best[2] >= en
        if full:
            s += 0.5
        ev.update(local_start=st, local_end=en, fits_fully=full, attend_from=best[1], attend_to=best[2],
                  score=s, why=why, campuses=camps, online=online)
        out.append(ev)
    out.sort(key=lambda e: (-e["score"], e["local_start"]))
    return out


# ---------- output ----------

def line_for(ev):
    when = f"{fmt_time(ev['local_start'])}-{fmt_time(ev['local_end'])}"
    where = ev.get("location") or ("online" if ev["online"] and not ev["campuses"] else
                                   (", ".join(ev["campuses"]) + " campus" if ev["campuses"] else "location on RSVP page"))
    extras = []
    if ev["food"]:
        extras.append("food mentioned")
    if not ev["fits_fully"]:
        extras.append(f"you can catch {fmt_time(ev['attend_from'])}-{fmt_time(ev['attend_to'])}")
    host = f" ({ev['host']})" if ev.get("host") else ""
    tail = f" [{'; '.join(extras)}]" if extras else ""
    return f"- {when}: {ev['title']}{host}, {where}{tail}\n  {ev.get('url', '')}"


def main(argv=None):
    p = argparse.ArgumentParser(description="Match campus events to free time for one day.")
    src = p.add_mutually_exclusive_group()
    src.add_argument("--feed", default=ASU_FEED, help="iCalendar feed URL (default: ASU Sun Devil Central)")
    src.add_argument("--ics-file", help="Read a local .ics file instead of downloading")
    src.add_argument("--sample", action="store_true", help="Use the bundled sample feed (no network, nothing saved)")
    p.add_argument("--now", required=True,
                   help="Student's local date-time with UTC offset, ISO format, e.g. 2026-10-27T07:30-07:00")
    p.add_argument("--date", help="Day to plan, YYYY-MM-DD (default: the date in --now)")
    p.add_argument("--busy", action="append", default=[], help="Busy block in local time, HH:MM-HH:MM; repeatable")
    p.add_argument("--day-start", default="08:00", help="Earliest time to suggest (default 08:00)")
    p.add_argument("--day-end", default="22:00", help="Latest time to suggest (default 22:00)")
    p.add_argument("--buffer", type=int, default=15, help="Minutes to keep free around each busy block (default 15)")
    p.add_argument("--min-gap", type=int, default=30, help="Ignore free windows shorter than this many minutes (default 30)")
    p.add_argument("--min-attend", type=int, default=30, help="Minutes of an event the student must be able to attend (default 30)")
    p.add_argument("--campus", help="Student's campus, e.g. Tempe, Downtown Phoenix, Polytechnic, West Valley")
    p.add_argument("--include-online", action="store_true", help="Also suggest online events")
    p.add_argument("--interests", default="", help="Comma-separated interests, e.g. 'ai,career,free food,cricket'")
    p.add_argument("--exclude", default="", help="Comma-separated words to skip, e.g. 'spiritual,housing'")
    p.add_argument("--top", type=int, default=3, help="How many events to list (default 3)")
    p.add_argument("--refresh", action="store_true", help="Ignore the one-hour cache and download again")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    try:
        try:
            now = datetime.fromisoformat(args.now)
        except ValueError:
            raise RadarError("--now must look like 2026-10-27T07:30-07:00", 2)
        if now.tzinfo is None:
            raise RadarError("--now needs the UTC offset, like 2026-10-27T07:30-07:00", 2)
        tz = now.tzinfo
        day = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else now.date()
        day_start = parse_hhmm(args.day_start, day, tz)
        day_end = parse_hhmm(args.day_end, day, tz)
        if day == now.date() and now > day_start:
            day_start = now  # don't suggest things that already started... unless still attendable (handled by overlap)
        busy = parse_busy(args.busy, day, tz)
        windows = free_windows(day_start, day_end, busy, args.buffer, args.min_gap)

        path = SAMPLE_FEED if args.sample else (args.ics_file or fetch_feed(args.feed, args.refresh))
        try:
            events = parse_ics(path)
        except OSError as e:
            raise RadarError(f"Couldn't read the events file: {e}", 3)

        interests = [x for x in args.interests.split(",") if x.strip()]
        exclude = [x for x in args.exclude.split(",") if x.strip()]
        found = matches(events, day_start, day_end, windows, args.campus, args.include_online,
                        interests, exclude, args.min_attend)
    except RadarError as e:
        print(f"error: {e}")
        return e.code

    label = day.strftime("%a %b %d").replace(" 0", " ")
    if args.json:
        print(json.dumps({
            "date": day.isoformat(),
            "free_windows": [[fmt_time(s), fmt_time(e)] for s, e in windows],
            "matches_total": len(found),
            "events": [{
                "title": e["title"], "host": e.get("host"), "start": e["local_start"].isoformat(),
                "end": e["local_end"].isoformat(), "fits_fully": e["fits_fully"], "type": e["type"],
                "tags": e["tags"], "campuses": e["campuses"], "online": e["online"],
                "location": e.get("location") or None, "food_mentioned": e["food"],
                "matched_interests": e["why"], "url": e.get("url"), "score": round(e["score"], 2),
            } for e in found[: args.top]],
        }, indent=2))
    else:
        if day_start >= day_end:
            print(f"{label}: it's already past {fmt_time(day_end)}. Plan tomorrow with --date.")
        elif not windows:
            print(f"{label}: no free time between {fmt_time(day_start)} and {fmt_time(day_end)}.")
        else:
            print(f"{label} free: " + ", ".join(f"{fmt_time(s)}-{fmt_time(e)}" for s, e in windows))
            if found:
                print(f"{len(found)} events fit. Top {min(args.top, len(found))}:")
                for e in found[: args.top]:
                    print(line_for(e))
            else:
                print("No events fit your free time.")
    if not windows:
        return 5
    return 0 if found else 6


if __name__ == "__main__":
    sys.exit(main())
