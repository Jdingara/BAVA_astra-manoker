# CONVENTIONS.md (Aider and other tools)

See **AGENTS.md** for the full conventions and **PROJECT_HISTORY.md** for history.

- Python 3.12 scripts. Each output generator is a standalone script next to its outputs.
- Units are millimetres. Cut sizes are whole mm (`math.floor`); max piece 2400 (8x4 sheet 2440 x 1220).
- Edge band: carcass 0.5 mm front edge; shutters 2 mm on 4 sides; side cover / strip 2 mm front only; skirting 0.5 mm top.
- Files are saved with lock-fallback names (`(updated)` / `(HHMMSS)`).
- Verify wardrobe changes with `2-Designs/Owner Drawings/check_all.py`.
