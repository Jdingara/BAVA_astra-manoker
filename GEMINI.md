# GEMINI.md

Gemini CLI: read **AGENTS.md** (rules, pipeline, decisions, pending items) and **PROJECT_HISTORY.md** (what happened and why) before doing anything.

Most important rules:
- Reply to the owner in simple English with tables. He writes Tanglish. Ask when a request is ambiguous.
- Never modify the owner's AutoCAD drawing (read only, or a copy).
- After any wardrobe change: `owner_cutlist.py` → `check_all.py` (FAILED 0) → regenerate the outputs. Tell the user which file is newest.
- Cut sizes are whole mm (floor), pieces ≤ 2400. Never invent laminate codes or shades.
- Keep the repo private. No catalogues in git.
