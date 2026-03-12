# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## Wolfram Alpha

**App ID:** `LHQJ395EVU`

**Usage:**
```bash
python3 /home/james/.openclaw/workspace/wolfram_query.py "your query"
```

**Examples:**
```bash
python3 wolfram_query.py "integrate x^2 dx"
python3 wolfram_query.py "thermal conductivity of steel"
python3 wolfram_query.py "convert 500 W/cm2 to W/m2"
python3 wolfram_query.py "solve x^2 + 3x - 7 = 0"
```

**Quota:** 2,000 non-commercial queries/month (free tier)

---

Add whatever helps you do your job. This is your cheat sheet.
