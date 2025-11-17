# Storyteller Highlight Generator

**Goal:** Ingest sports match events and produce a **Story Pack** (a JSON bundle of Pages) plus a **minimal preview** to step through Pages.

A Python implementation of a CLI tool with:
- A **data contract** for events.
- A **JSON Schema** for the output pack.
- A **preview** (`preview/index.html`) that loads a `story.json` via a file picker.

## Deliverables
- `main.py` a script that converts `data/match_events.json` into `out/story.json` following `schema/story.schema.json`.
- The pack(Story Pack/ JSON bundle) includes at least:
  - A **cover** Page.
  - **N highlights** chosen by your heuristic.
  - Stable ordering, no exact duplicates, and required fields present.
  - A sensible fallback: if no highlights, include a "no highlights" Page.
- A minimal preview: open `preview/index.html` and load your `out/story.json` to step through Pages.
- Tunable ranking with `weights.json`.
- Smarter captions (LLM + evaluation script that checks factual fields).

## How to run the preview (no server needed)
1) Build your `out/story.json` using: `uv run main.py --strict -o out/story.json`.
2) Or, `uv run main.py --lenient -o out/story.json` for not validation.
3) Open `preview/index.html` in your browser.
4) Click "Load pack.json" and select the file from `out/`.

## Repository layout
- `data/` —  `match_events.json`  (see `data/events_schema.md`).
- `assets/` — Images used by Pages. A tiny placeholder is included.
- `out/` — Your output pack(s).
- `schema/pack.schema.json` — JSON Schema for validating the output pack.
- `preview/index.html` — Minimal viewer that loads a pack via file picker.
- `tests/invariants.md` — Non‑code test cases and invariants to enforce.
- `templates/DECISIONS.md`, `templates/AI_USAGE.md`, `templates/EVALS.md` — Templates to fill in.
- `weights.example.json` — Optional ranking weights you can adopt.

