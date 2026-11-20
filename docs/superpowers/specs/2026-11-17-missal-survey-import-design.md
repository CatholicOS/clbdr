# Design: importing the Roman Missal survey, with ecclesial anchoring and territorial usage

Date: 2026-11-17 · Branch: `feat/missale-romanum-vernacular-editions`

## Intent

A survey spreadsheet, *Roman Missals* (exported from Google Sheets, 245 rows: one per
territory × language), records which Missal each territory uses: the edition and its
year, publisher, bishops' conference, rite, a Drive scan, historical editions, and
verification notes. Many rows have decree protocol numbers and in-force dates taken from
title pages. CLBDR has one vernacular Missal (`missale_romanum_2011_en_US`). The survey
contains about 45–50 distinct vernacular editions.

The goal is to turn the survey into registry data that consumers can resolve against:
the martyrology-api, the Liturgical Calendar API (which has its own `missal_id` keys), and
the CLEDR. That takes three things:

1. **Distinct editions**: each vernacular Missal edition as an entry in `data/editions.json`.
2. **Territorial usage**: which edition each territory/language actually uses, and with
   what status. Many editions are shared across countries, so this can't be one `scope`
   per edition (decision B: a separate usage table).
3. **Ecclesial anchoring**: books aren't only Roman. Every book refers to CESIDR for the
   liturgical tradition and the Church(es) *sui iuris* it belongs to. A rite level within a
   tradition is also needed (Roman vs Ambrosian; the Zaire Use as a use of the Roman Rite).

## Goals

- Every distinct Missal edition in the survey, Latin or vernacular, Roman Rite or not, as
  an edition entry, carrying the survey's verified facts (decree/prot., approval date,
  in-force date, publisher, title) with honest verification flags.
- `data/usage.json`: one row per (territory, language) from the survey, pointing to an
  edition (or null where the survey names none), with a status.
- Books carry `tradition` (CESIDR `trad:`), `churches` (CESIDR `esi:` list) and `rite`.
- Vernacular edition keys follow the agreed structure (book, year, language, issuing
  authority), spelled for now in the current underscore form:
  `missale_romanum_2011_en_usccb`.
- An `aliases` field on editions, carrying former CLBDR keys (`missale_romanum_2011_en_US`)
  and the Liturgical Calendar API's `missal_id` keys (`US_2011`, `IT_1983`, `IT_2020`,
  `NL_1978`, `CA_2011`, `CA_2016`, `EDITIO_TYPICA_1970` …).
- A small validator (`scripts/validate.py`) checking referential integrity, so the import
  can be verified.

## Non-goals

- **The issue #4 rename** (`book:` → `ll:`/`liber-liturgicus:`, hyphens, `/`). Held for
  committee decision. This import uses the current spellings, so the rename later converts
  everything in one pass.
- **The `short_form` fix** (clbdr#6). Untouched here; new editions get no `short_form`.
- **Drive links.** They point into a private Drive and many are scans of copyrighted
  books; publishing them in a public repo would distribute them. The spreadsheet's
  "Ingest Status" and "Post-Ingest Splice" columns are internal workflow and are also
  left out.
- **Hand missals and private compilations** (*Volksmisboek* 1939, Schaller 1931, Urbaniana
  hand missals, app-derived text compilations, EF Ordo booklets). They aren't editions of
  the Missal. They may appear in an edition's `note` as sources, but not as entries.
- **Moving `rite` into CESIDR.** Proposed as follow-up only.

## Anti-goals

- Presenting unverified facts as verified. The survey separates "Confirmed from title
  page" from "Needs local verification". That distinction must survive the import.
- Inventing editions to fill rows that say only "local use" or "resources".

## Approaches considered (usage)

- **A: territory list on each edition.** Simple, but it can't hold status ("1992 in force,
  2022 being adopted") or dates, and the martyrology-api's (date, territory, locale)
  lookup would have to scan every edition.
- **B: separate usage table (chosen).** Mirrors the survey's grain (territory ×
  language), holds status and dates, and is the lookup the API needs.

## Approaches considered (edition keys)

- **(1) Readable path, book/year/language/authority (chosen)**, with `aliases`, so moving
  later to opaque canonical IDs (PR #1) stays cheap.
- **(2) Opaque minted IDs.** This would decide PR #1, which is still before the committee.

## Data model changes

### `data/books.json`

New fields on every book:

- `tradition`: a CESIDR `trad:` key. All current books are `trad:latin`.
- `churches`: a list of CESIDR `esi:` keys. Current books: `["esi:latin"]`.
- `rite`: a key into the new `data/rites.json` (`rite:roman`, `rite:ambrosian`, …).
  Current books: `rite:roman`. Eastern books carry the rite of their tradition
  (`rite:armenian`, `rite:geez`).

New books from the survey:

- `book:missale-ambrosianum`: Ambrosian Missal (`rite:ambrosian`, `trad:latin`,
  `esi:latin`; Archdiocese of Milan).
- The Armenian Catholic Divine Liturgy book (survey: *Khorhrdatetr Surb Pataragi*):
  `trad:armenian`, `["esi:armenian"]`.
- The Ge'ez *Metshafe Qeddase*: `trad:alexandrian`, `["esi:ethiopian", "esi:eritrean"]`.

The book `id` rule extends: `book:` + the Latin title, or, for books with no Latin title,
the standard transliteration of the native title, ASCII-folded, lowercase and hyphenated.
`title_la` is optional, and `title` (native script) plus `title_translit` are added where
the book isn't Latin. `category: missal` is defined as "the book for the celebration of
the Eucharist" in any tradition.

### `data/rites.json` (new)

A local vocabulary: `rite:roman`, `rite:ambrosian`, `rite:hispano-mozarabic`,
`rite:bragan`, `rite:armenian`, `rite:geez`, …, each with `name_la`, `name_en` and
`tradition` (CESIDR `trad:` key). The `$comment` notes this belongs in CESIDR eventually
(CESIDR identifies Churches and traditions, not rites).

A *use* within a rite (the Zaire Use, the Anglican-patrimony *Divine Worship*) is not a
rite. It is an edition-level `use` attribute (`"use": "zairean"`).

### `data/authorities.json` (new)

Issuing authorities for vernacular editions: the bishops' conference or other body that
approved the edition and obtained the *recognitio* (`usccb`, `cbcew`, `cccb`, `cei`, `cef`,
`dbk`, `cea`, `cem`, `cee`, `cep`, `cnbb`, `celra`, …). Each has `name`, `type`
(`episcopal_conference`, `regional_conference`, `inter_conference_body`, `patriarchate`,
`holy_see`, `diocese`) and `territories` (ISO 3166-1 alpha-2). This is a placeholder until a
conferences registry exists (cdcf-uri-scheme#13 lists `institution/conference/` with no
registry).

Where a text comes from an inter-conference body (ICEL, AELF) but each conference
publishes its own edition (US 2011, E&W 2010, Canada 2011…), the edition's authority is
the conference. The translating body is recorded as `translation_body`.

### `data/editions.json`

Vernacular edition key: `<book_slug>_<year>_<lang>_<authority>`, with lowercase BCP 47
`lang` (`en`, `pt`, `zh-hant` where the script matters).

**The year in the key is the year of the edition as printed on the title page or
colophon** (decided in conversation, option (a)). It is the year the survey's
"Publication Year" column records, the year people cite, and the year the Liturgical
Calendar API's keys already use (`US_2011`, `IT_2020`, `NL_1978`). The *recognitio* or
confirmation date and the in-force date are separate fields (`recognitio`, `in_force`),
recorded wherever known. Where the survey's year isn't confirmed from a title page, the
key still uses it and `verification: pending` flags it. Fields, beyond the existing ones:

- `issuing_authority`: key into `authorities.json`.
- `title`: the title as printed (native script).
- `publisher`.
- `translation_of`: the Latin typical edition translated (the existing field).
- `recognitio` / `decree`: prot. number and date where the survey records them.
- `in_force`: the date from which the edition is prescribed, where known.
- `use`: for a use within the rite (Zaire).
- `verification`: `confirmed_title_page` | `confirmed_secondary` | `pending`, plus
  `verification_note` carrying the survey's verification text, minus Drive URLs.
- `scope`: kept on Latin editions (`universal`). Dropped on vernacular editions, where
  `issuing_authority` names who issued it and `usage.json` says where it is used. The
  predecessor/successor chain for vernacular editions runs within the same authority and
  language. `docs/schema.md`'s in-force rule is rewritten to point to `usage.json`.
- `aliases`: earlier keys and other systems' keys. Each alias is an object
  `{"key": "US_2011", "system": "litcal-api"}` (or `"system": "clbdr"` for former CLBDR
  keys), so an alias can't be mistaken for a CLBDR key.

Alias keys are unique across the registry, and each alias names one edition. The
Liturgical Calendar API keys come from its `src/Enum/RomanMissal.php`. Where an API key
names a printing with added national propers rather than a new translation (`CA_2016`
against `CA_2011`), it gets its own edition entry (`nature: reimpressio_emendata`,
predecessor the earlier one) if the survey or the API's description supports that.
Otherwise it becomes an alias on the base edition, with the reasoning in `note`.

Only the Missal entries move to the new key pattern in this change. Other existing
vernacular or unofficial keys (`martyrologium_romanum_2004_it_IT`, the `_unofficial`
translations) are left alone: the CRMEDR and martyrology-api depend on them, and they
are converted in the #4 rename pass. The validator applies the new key pattern only to
editions that carry `issuing_authority`.

The existing `missale_romanum_2011_en_US` is re-keyed to `missale_romanum_2011_en_usccb`,
with the old key in `aliases`. Its downstream use was checked: no repository references it.

Predecessor/successor chains link vernacular editions from the same authority in the same
language (Portuguese 1992 → 2022; German 1975 → 1988; Italian 1983 → 2020; Colombia's
earlier edition → 2025; Mexico 1991 → 2013; Vietnam 1992 → 2005). Prior official
editions that the survey lists under "Historical editions" become entries. Hand missals
don't.

### Books of other rites and traditions

Editions of the Armenian and Ge'ez books, and the Latin editions of the Ambrosian Missal,
are typical editions of their own book, promulgated by that Church's own authority
(the patriarch or synod, the Holy See for the Ge'ez common missal, the Archbishop of Milan
for the Ambrosian). They take `nature: editio_typica` (or the altera/emendata natures) and
the Latin-edition key form `<book_slug>_<year>`, with `language` as the liturgical language
(`xcl` Classical Armenian, `gez`, `la`) and `promulgated_by` naming the authority. Bilingual
editions (the 2007 Bzommar Grabar + Western Armenian) list both in `language` as an
array, with the liturgical language first. Translations of these books (the Italian
Ambrosian *Messale*) are vernacular editions under the general `<lang>_<authority>`
pattern, with `translation_of` pointing to that book's typical edition. Historical
editions of the Armenian book listed in the survey (Venice 1823, Vienna 1858 and 1879)
are included as editions where the survey names them as Catholic-recension printings.
Translations made as studies (Avedichian 1832) and critical editions (Gatrchean 1897) are
not editions of the liturgical book and go in `note`.

### `data/usage.json` (new)

One row per survey row (split where a row bundles territories, e.g. Aruba / Curaçao /
Caribbean Netherlands → AW, CW, BQ):

```json
{"territory": "AO", "language": "pt", "edition": "missale_romanum_1992_pt_cep",
 "status": "in_force", "from": null, "until": null},
{"territory": "AO", "language": "pt", "edition": "missale_romanum_2022_pt_cep",
 "status": "adopting", "note": "To become official after CEAST's own procedures."}
```

**History, not just the current state.** Rows carry `from` and `until` (both optional,
ISO dates or years), so (date, territory, language) resolves to the edition in force on
that date. Where the survey gives a superseded edition for a territory (Colombia before
30 Nov 2025, Portugal 1992 → 2022, Germany 1975 → 1988), the earlier edition gets its own
row with `until` set. A territory moving to a new edition gets two rows: the current one
`in_force` and the new one `adopting`. Overlapping `in_force` ranges for the same
(territory, language, church) are a validator error.

- `territory`: ISO 3166-1 alpha-2 (`XK` for Kosovo; `VA` for the Holy See), or ISO
  3166-2 where one country has several authorities (`GB-SCT` vs `GB-ENG`/`GB-WLS` for
  Scotland vs England & Wales). A lookup falls back from the subdivision to the country.
  Diocese-level differences go in `note` for now; a `circumscription` field (CECDR `circ:`)
  is a later extension.
- `language`: BCP 47 for the language of use.
- `edition`: edition key, or `null` where the survey names no edition ("local use").
- `status`: `in_force` | `adopting` | `de_facto` (a shared edition used without its own
  approval for the territory) | `unknown`.
- `since`: optional date.
- `church`: `esi:` key, defaulting to `esi:latin`. Set for the Armenian and Ge'ez rows.
- `note`, `verification`.

Rows that bundle a second edition (e.g. "French Missel / Arabic Roman Missal") become two
usage rows.

## Validator

`scripts/validate.py` (stdlib only): JSON parses; ids are unique; every `book`,
`translation_of`, `predecessor`, `successor`, `issuing_authority`, `rite`, usage `edition`
resolves; predecessor/successor are symmetric; key format matches the documented
patterns; aliases don't collide with live ids. When `../cesidr` is checked out, it also
checks `trad:`/`esi:` against it; otherwise it uses a pinned list in the script.

## Docs

`docs/schema.md`: the new fields, `rites.json`, `authorities.json`, `usage.json`, the
book-id rule for non-Latin titles, the vernacular key structure, and `aliases`.
`README.md`: the scope beyond the Roman Rite, the new files, and the vernacular key
example. `docs/missale-romanum.md`: the vernacular section answers its open CELAM
questions from the survey (the Southern Cone, Mexican and Spanish CEE families).

## Calls made while settling the reviewer's questions

Usage history with `from`/`until`; separate `adopting` rows; `scope` kept only on Latin
editions; ISO 3166-2 for subnational authorities; non-Missal keys not re-keyed here;
the rule for API aliases vs reprint entries; the key form and nature of non-Roman books.
All of these are the author's calls, not decisions taken in the conversation.

## Left to the builder

- Exact authority slugs and names, and which survey rows collapse to the same edition.
- Language tags for multi-script cases (Chinese 1982: Taiwan traditional vs Hebei
  simplified are two editions or one).
- Whether each row's verification text maps to `confirmed_title_page` or
  `confirmed_secondary`.

## Process

The survey is untrusted input: it is read with a script outside the repo, and no
spreadsheet content is executed. The import produces hand-reviewed JSON, not a generated
dump. Edition entries are written deliberately, row by row against the survey text.
