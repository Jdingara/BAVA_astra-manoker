# CLAUDE.md

@AGENTS.md
@PROJECT_HISTORY.md

Claude Code: the two files above hold everything (rules, pipeline, decisions, pending items, full history). Read them before acting.

Most important rules:
- Reply to the owner in simple English with tables. He writes Tanglish. Ask when a request is ambiguous, and show a picture before rebuilding cut lists.
- Never modify the owner's AutoCAD drawing. Read it through COM, or work on a copy.
- After any wardrobe change: `owner_cutlist.py` → `check_all.py` (must say FAILED 0) → regenerate the requested files. Tell the user which file is newest (outputs use lock-fallback names).
- Cut sizes are whole mm, rounded down. No piece longer than 2400. Never invent laminate codes or shades.
- Keep the repo private. Don't commit the catalogues. Commit author "Astra Interiors".
