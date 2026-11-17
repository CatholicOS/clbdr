# Missal Survey Import Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Import the *Roman Missals* survey into CLBDR as books anchored to CESIDR, distinct Missal editions, issuing authorities, and a territorial usage table, all checked by a validator.

**Architecture:** Hand-curated JSON in `data/`. A stdlib Python validator (`scripts/validate.py`) checks the cross-file references and key formats. A unittest suite feeds it broken fixtures to show it catches each kind of error. The survey is read from the scratchpad copy with an isolated script and is never committed.

**Tech Stack:** JSON; Python 3 stdlib (`json`, `re`, `unittest`).

**Spec:** `docs/superpowers/specs/2026-11-17-missal-survey-import-design.md`

## Global Constraints

- Current spellings stay (`book:` prefix, underscore edition keys); no #4 rename.
- Vernacular Missal key: `<book_slug>_<year>_<lang>_<authority>`, where the year is the title-page year.
- No Drive links, no "Ingest Status"/"Post-Ingest Splice" data in the repo; the `.xlsx` is not committed.
- No `short_form` on new editions; existing `short_form` untouched (clbdr#6).
- `martyrologium_romanum_2004_it_IT` and the `_unofficial` keys are not re-keyed.
- Unverified facts carry `verification: "pending"`.

## Review Focus

1. A usage row pointing at an edition key with a typo: the validator must report it. (Task 1 test `test_usage_unknown_edition`.)
2. Two `in_force` rows overlapping for the same territory, language and church: reported. (Task 1 `test_overlapping_in_force`.)
3. An alias equal to a live id, or the same alias on two editions: reported. (Task 1 `test_alias_collisions`.)
4. A predecessor without the matching successor: reported. (Task 1 `test_asymmetric_chain`.)
5. A `trad:`/`esi:` key that doesn't exist in CESIDR (e.g. `esi:armenian-catholic`): reported. (Task 1 `test_unknown_cesidr_key`.)

---

### Task 1: Validator

**Files:**
- Create: `scripts/validate.py`, `tests/test_validate.py`

**Interfaces:**
- Produces: `validate(data_dir: pathlib.Path, cesidr_dir: pathlib.Path | None = None) -> list[str]` (returns error messages; empty = valid); CLI `python3 scripts/validate.py [--cesidr PATH]` exits 1 on errors and prints them. Loads `books.json`, `editions.json`, `rites.json`, `authorities.json`, `usage.json` (the last three optional, so it runs on today's data).
- CESIDR keys: read from `<cesidr_dir>/data/{tradition,churches}.json` when that directory exists (default `../cesidr` relative to the repo); otherwise from `PINNED_TRAD` / `PINNED_ESI` constants in the script (the 6 `trad:` and 24 `esi:` keys as of CESIDR main e6f8af3).

Checks: unique ids per file; edition `book`, `translation_of`, `predecessor`, `successor`, `issuing_authority` and usage `edition` resolve; chains are symmetric; book `rite`/`tradition`/`churches` resolve; usage `in_force` ranges don't overlap per (territory, language, church); aliases are unique and not live ids; editions with `issuing_authority` match `^[a-z0-9_]+_\d{4}_[a-z]{2,3}(-[a-z0-9]+)*_[a-z0-9-]+$` and end in `_<issuing_authority>` (authority slug with `-` → `_`); territory matches `^[A-Z]{2}(-[A-Z0-9]{1,3})?$`.

- [ ] **Step 1: Write failing tests**: one per Review Focus item, plus `test_current_data_valid` (validate(repo/data) == []). Each builds a minimal fixture dir in a `tempfile.TemporaryDirectory` and asserts a message containing the offending key.
- [ ] **Step 2:** `python3 -m unittest discover -s tests -v` → FAIL (module missing).
- [ ] **Step 3:** Implement `scripts/validate.py`.
- [ ] **Step 4:** Rerun → PASS.
- [ ] **Step 5:** Commit.

### Task 2: Books anchored to CESIDR, rites vocabulary

**Files:** Create `data/rites.json`; modify `data/books.json`.

- `rites.json` entries: `rite:roman`, `rite:ambrosian`, `rite:hispano-mozarabic`, `rite:bragan` (all `trad:latin`), `rite:armenian` (`trad:armenian`), `rite:geez` (`trad:alexandrian`), each with `name_la`, `name_en`, `tradition`.
- All existing books: `"tradition": "trad:latin", "churches": ["esi:latin"], "rite": "rite:roman"`.
- New books: `book:missale-ambrosianum` (missal, rite:ambrosian); `book:khorhrdatetr` (title `Խորհրդատետր`, translit, missal, trad:armenian, [esi:armenian], rite:armenian); `book:metshafe-qeddase` (title `መጽሐፈ ቅዳሴ`, missal, trad:alexandrian, [esi:ethiopian, esi:eritrean], rite:geez).
- [ ] Edit; run the validator and tests → pass; commit.

### Task 3: Authorities and Missal editions

**Files:** Create `data/authorities.json`; modify `data/editions.json`.

- Extract survey rows (isolated script in the scratchpad) and group them into distinct editions by (language, publisher/authority, year).
- One edition entry per distinct edition, with the spec's fields; `verification` from column N (`confirmed_title_page` when N says title page/colophon, `confirmed_secondary` when confirmed by other means, else `pending`).
- Re-key `missale_romanum_2011_en_US` → `missale_romanum_2011_en_usccb`, alias `{"key": "missale_romanum_2011_en_US", "system": "clbdr"}`.
- Liturgical Calendar API aliases (`system: "litcal-api"`): EDITIO_TYPICA_1970/1971/1975/2002/2008 on the Latin editions; US_2011, IT_1983, IT_2020, NL_1978, CA_2011, CA_2016.
- Previous official editions from column J become entries with chains; Armenian and Ge'ez editions per the spec.
- [ ] Edit; validator + tests pass; commit.

### Task 4: Usage table

**Files:** Create `data/usage.json`.

- One row per survey row (split bundled territories/editions), as in the spec; `church` for the Armenian/Ge'ez rows; `edition: null, status: "unknown"` where none is named.
- [ ] Generate a draft with a scratchpad script from the survey, hand-review it, write; validator + tests pass; commit.

### Task 5: Docs

**Files:** Modify `docs/schema.md`, `README.md`, `docs/missale-romanum.md`.

- schema.md: book fields `tradition`/`churches`/`rite`, non-Latin book-id rule, `rites.json`, `authorities.json`, vernacular key and year rule, `scope` only on Latin, `aliases`, `usage.json` and the in-force rule, validator usage.
- README: scope beyond the Roman Rite, new files, vernacular example `missale_romanum_2011_en_usccb`, `python3 scripts/validate.py`.
- missale-romanum.md: vernacular section: key pattern and the answer to the CELAM questions from the survey.
- [ ] Edit; commit.

### Task 6: Verify and open the PR

- [ ] Run the validator and tests; push; `gh pr create` referencing #4 and #6.
