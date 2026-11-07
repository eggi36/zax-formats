# zax-formats

The format library for "Zax: The Alien Hunter" (Reflexive Entertainment / JoWooD, 2001).

- **zaxtools** – every file format of the game read and written byte for byte (levels, way points, images, models, sequences, fonts, dialogue scripts, the data archive), a renderer that draws levels as the game does, the level check.
- **tools/** – `selftest.py` (regression test against the real game data), `render_level.py` (a level as PNG), `export_model.py` (a model as a sprite sheet), `check_levels.py` (the level check over all levels), `png_to_frm.py` (own images through the game's encoder).
- `docs/FORMATS.md` – the formats with evidence levels; `docs/LEVEL_BUGS.md` (bugs in the original level data), `docs/OPEN_ISSUES.md`.

Related repositories, next to this one in the same folder: **zax-editor** (the level editor built on zaxtools), **zax-decomp** (the decompilation of Zax.exe; its docs explain the engine behind the formats), **zax-redone** (the port), **zax-launcher** (a launcher for the original Zax.exe). Until 2026-11-07 the format library and the editor were one repository, zax-toolbox.

## Setup

1. Python 3.10 or newer: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
2. Point `ZAX_DATA` to the game data (the `Data.dat` of an installed game, or an unpacked `Data` folder).
3. Check: `python tools/selftest.py` – expected: 0 failures (it compares the exe's field lists with zax-decomp's `docs/fields.csv` when zax-decomp lies next to this repository).
4. `git config core.hooksPath tools/git-hooks` (the pre-push hook: no game data, no private names or paths).

The game data is not included and must never go into the repository: every player brings the original assets from their own copy. Images generated from the game data are excluded from version control.
