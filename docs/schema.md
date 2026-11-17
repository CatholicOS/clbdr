# CLBDR schema (draft for committee review)

## Books

```json
{
  "id": "book:ordo-celebrandi-matrimonium",
  "title_la": "Ordo celebrandi Matrimonium",
  "category": "ritual",
  "collection": "book:rituale-romanum",
  "tradition": "trad:latin",
  "churches": ["esi:latin"],
  "rite": "rite:roman"
}
```

- **`id`** — `book:` + the Latin title, ASCII-folded, lowercase, hyphenated. A book
  with no Latin title (the Eastern Catholic books) takes the standard transliteration
  of its native title instead (`book:khorhrdatetr`, `book:metshafe-qeddase`), and
  carries `title` (native script) and `title_translit` in place of `title_la`.
- **`tradition`** — the liturgical tradition the book belongs to, as a
  [CESIDR](https://github.com/CatholicOS/cesidr) `trad:` key (`trad:latin`,
  `trad:armenian`, `trad:alexandrian`, …).
- **`churches`** — the Churches *sui iuris* whose book it is, as CESIDR `esi:` keys. A
  book can be shared: the Ge'ez *Metshafe Qeddase* belongs to `esi:ethiopian` and
  `esi:eritrean`. Books are therefore not only "Roman": the Armenian *Khorhrdatetr* is not
  a Roman Missal, but it is the Catholic book for the celebration of the Eucharist in the
  Armenian Catholic Church.
- **`rite`** — the rite within the tradition, as a key into `data/rites.json`
  (`rite:roman`, `rite:ambrosian`, …). CESIDR identifies Churches and traditions, not the
  rites within a tradition, so this vocabulary is kept here until it moves there. A *use*
  within a rite (the Zaire Use) is not a rite: it is the `use` attribute of an edition.
- **`category`** — one of: `missal`, `lectionary`, `liturgy_of_the_hours`,
  `martyrology`, `pontifical`, `ritual`, `benedictional`, `ceremonial`,
  `sacramentary`, `chant`. The category expresses the *nature* of the book in any
  tradition (`missal`: the book for the celebration of the Eucharist);
  historical sacramentaries (Gelasian, Gregorian) and chant books are in scope for
  future compilation.
- **`collection`** — for the post-conciliar *ordines* published as parts of the
  Pontificale Romanum or Rituale Romanum, the collection book they belong to. The
  pre-conciliar single-volume Rituale Romanum and Pontificale Romanum are themselves
  book entries (they have their own edition lines).

A book identity survives its revisions: `book:martyrologium-romanum` covers 1584
through 2004. Where the post-conciliar reform *replaced* a book rather than revising
it (Breviarium Romanum → Liturgia Horarum), the successor is a distinct book with a
`replaces` attribute.

## Editions

```json
{
  "id": "liturgia_horarum_1971",
  "book": "book:liturgia-horarum",
  "nature": "editio_typica",
  "language": "la",
  "scope": "universal",
  "promulgated": "1971-04-11",
  "decree": "SCCD, Decr. Horarum Liturgia, 11 aprilis 1971",
  "volumes": [
    {"n": 1, "title": "Tempus Adventus, Tempus Nativitatis", "covers": ["adventus", "nativitas"]},
    {"n": 2, "title": "Tempus Quadragesimæ, Tempus Paschale", "covers": ["quadragesima", "pascha"]},
    {"n": 3, "title": "Tempus per annum, hebdomadæ I–XVII", "covers": ["per-annum-1-17"]},
    {"n": 4, "title": "Tempus per annum, hebdomadæ XVIII–XXXIV", "covers": ["per-annum-18-34"]}
  ]
}
```

- **`id`** — `<book-slug>_<year>` for typical editions (preserving the CLEDR's existing
  keys verbatim: `missale_romanum_1970`, `missale_romanum_2002`, `missale_romanum_2008`;
  likewise for the typical editions of Eastern books, `khorhrdatetr_2007`).
  Vernacular editions are `<book-slug>_<year>_<lang>_<authority>`:
  - `<year>` is the year of the edition **as printed on the title page or colophon**.
    The approval and in-force dates are separate fields (below).
  - `<lang>` is a lowercase BCP 47 language tag (`en`, `pt`, `zh-hant` where the script
    matters).
  - `<authority>` is the issuing authority's key from `data/authorities.json`, with `-`
    written `_` (`missale_romanum_2011_en_usccb`, `missale_romanum_2022_pt_cep_pt`).

  The authority, not the territory, identifies a vernacular edition. One edition is
  often used across many countries (the Southern Cone *Misal Romano*, CELRA's Arabic
  Missal), and where it is used is recorded in `data/usage.json`. A trailing
  `_unofficial` marks translations that are not sanctioned editions
  (`martyrologium_romanum_1914_en_unofficial`). Keys minted under the earlier
  `<book>_<year>_<bcp47>` pattern (`martyrologium_romanum_2004_it_IT`) will be converted
  when the registry's identifiers are renamed (clbdr#4). Latin Missal editions also
  carry the CRMETDR's proposed `short_form` (`mr1970`) as an attribute; see clbdr#6 for
  its collision with CRMEDR's `mr:` prefix.
- **`nature`** — `editio_princeps` (pre-typical first prints), `editio_typica`,
  `editio_typica_altera` (tertia, …), `editio_typica_recognita` (historical
  revisions), `reimpressio_emendata` (emended reprints, e.g. the 1971 and 2008
  Missals), `editio_vernacula` (approved vernacular edition), `translatio`
  (translation without the status of an edition), `impressio` (a historical printing
  whose standing as a typical edition is not established, e.g. the Mekhitarist printings
  of the Armenian *Khorhrdatetr*). The vocabulary needs committee harmonization against
  the title pages of the books themselves.
- **`language`** — BCP 47; an array where an edition is bilingual, liturgical language
  first (`["xcl", "hyw"]`: Classical with Western Armenian).
- **`scope`** — `universal` for typical editions. The Missal's vernacular editions don't
  carry it: `issuing_authority` says who issued the edition and `data/usage.json` says
  where it is used. Older vernacular editions of other books keep their `scope` until
  they get usage rows.
- **`issuing_authority`** (vernacular editions) — the body that approved the edition and
  obtained the *recognitio*: a key into `data/authorities.json`. Where an inter-conference
  body prepared the text (ICEL, AELF), each conference's edition names that conference,
  and the body goes in `translation_body`.
- **`promulgated` / `promulgated_by` / `decree`** — the promulgation act of a typical
  edition. For vernacular editions: `published` (the key's year), `approved`,
  `recognitio`, `decree` and `in_force`, each where known.
- **`title`, `publisher`, `use`** — the title as printed; the publisher; a use within
  the rite (`"use": "zairean"`).
- **`translation_of`** — the typical edition a vernacular edition translates.
- **`predecessor` / `successor`** — the edition line: within the book for typical
  editions; within the same authority and language for vernacular ones.
- **`aliases`** — other keys that name this edition, each as `{"key", "system"}`:
  former CLBDR keys (`{"key": "missale_romanum_2011_en_US", "system": "clbdr"}`) and
  other systems' keys (`{"key": "US_2011", "system": "litcal-api"}`, the Liturgical
  Calendar API's `missal_id`). An alias is never reused and never equals a live key.
  Consumers can resolve through it until they move to the published keys, after which
  the field can be frozen or dropped.
- **`verification`** — `confirmed_title_page` (read from the title page or colophon),
  `confirmed_secondary` (confirmed from conference or press sources) or `pending`.

### Volumes and the fixed Latin reference

Multi-volume packaging is an **edition attribute**, not a book attribute. The rule:

1. The Latin typical edition defines the **content sections** of the book (for the
   Liturgia Horarum: the seasonal volumes above; for the lectionary: the *Ordo
   Lectionum Missae* defines the section structure — Sundays and festivities by cycle
   A/B/C, weekdays by year I/II, proper of saints, ritual Masses, votive Masses, Masses
   for the dead — without binding them to physical volumes).
2. Every edition (Latin or vernacular) declares its `volumes`, and each volume's
   `covers` lists the content sections it contains, using the section keys of the
   Latin reference.
3. Vernacular volume distributions therefore vary freely without schema changes: the
   US Lectionary for Mass covers the same OLM sections in 4 volumes, the Italian CEI
   lectionary in 9, and a future one-volume edition would simply cover everything.

Section keys are defined per book in the Latin reference edition's entry (a
`sections` attribute) and reused by all its vernacular editions.

## Issuing authorities

`data/authorities.json` lists the bodies that issue vernacular editions: episcopal
conferences, regional conferences (CELRA, the Tarraconense), inter-conference bodies (the
German-language *Ständige Kommission*), dioceses (Milan for the Ambrosian books), each
with `name`, `type` and `territories` (ISO 3166-1 alpha-2 or ISO 3166-2). The keys are
placeholders until a registry of episcopal conferences exists (cf.
cdcf-uri-scheme#13, `institution/conference/`).

## Usage: which edition a territory uses

`data/usage.json` records, for each territory and language, the edition in use:

```json
{"territory": "PT", "language": "pt", "edition": "missale_romanum_1992_pt_cep_pt", "status": "in_force", "until": "2022-04-13"},
{"territory": "PT", "language": "pt", "edition": "missale_romanum_2022_pt_cep_pt", "status": "in_force", "from": "2022-04-14"},
{"territory": "AO", "language": "pt", "edition": "missale_romanum_1992_pt_cep_pt", "status": "de_facto"},
{"territory": "AO", "language": "pt", "edition": "missale_romanum_2022_pt_cep_pt", "status": "adopting"}
```

- **`territory`** — ISO 3166-1 alpha-2 (`XK` for Kosovo), or ISO 3166-2 where one country
  has several authorities (`GB-SCT`, `ES-CT`). A lookup falls back from a subdivision to
  its country.
- **`church`** / **`rite`** — CESIDR `esi:` key (default `esi:latin`) and rite (default
  `rite:roman`): the Ambrosian and Roman Missals are both in force for Italian in Italy;
  the Armenian Catholic Church in Armenia uses its own book.
- **`status`**:
  - `in_force`: the edition issued or formally adopted for the territory.
  - `de_facto`: a shared edition used without the territory's own edition or a recorded
    adoption.
  - `adopting`: approved, pending local promulgation.
  - `unknown`: no edition recorded; `edition` is `null`, so the gap stays visible.
- **`from` / `until`** — the period of an `in_force` row, where known (date or year).

To resolve *(book, date, territory, language)*:

1. Consider the rows whose edition is of that book, with church `esi:latin` and rite
   `rite:roman` unless the caller asks for another (the Ambrosian Missal is found only by
   asking for `rite:ambrosian`).
2. Take the `in_force` row whose period contains the date, falling back from a
   subdivision to its country. A row without `from` starts at its edition's own
   `in_force` date, or else at its publication year: an edition is never in force before
   it was published. A date before every recorded period resolves to nothing, not to the
   earliest recorded edition.
3. Without an `in_force` row, take the `de_facto` row.

In-force periods never overlap for the same book, territory, language, church and rite.

The rows currently cover the Missal only. Other books (the Martyrology's
`martyrologium_romanum_2004_it_IT`) keep the earlier rule until they get rows: the
in-force window runs from promulgation until superseded by the successor of the same
`scope`.

## Validation

`python3 scripts/validate.py` checks:
- every cross-reference resolves, within this repository and against CESIDR (read from
  a `../cesidr` checkout, or else from a pinned key list);
- predecessor/successor links are symmetric;
- vernacular keys end in their issuing authority;
- aliases are unique;
- in-force periods don't overlap.

`python3 -m unittest discover -s tests` runs its tests.

## Open questions for the committee

1. Granularity of the `sections` vocabulary per book (fine enough for volume mapping,
   coarse enough to stay stable across typical editions).
2. Whether emended reprints (Missale 2008) are editions in their own right (current
   draft: yes, `editio_emendata`, as the CLEDR already references
   `missale_romanum_2008`).
3. Historical depth: pre-Tridentine books, manuscript sacramentaries, and chant books
   — in scope for the schema, but compilation is future work.
4. Whether decrees that modify a book without a new edition (e.g. the 2021
   *Postquam Summus Pontifex* Variationes for the Martyrology, or the addition of
   saints' memorials to the Missal by decree) should be registered as first-class
   *acts* attached to editions — the CLEDR already cites such decrees as sources.
5. Whether the `rite` vocabulary (`data/rites.json`) should move into CESIDR, which
   identifies the Churches *sui iuris* and the traditions but not the rites within a
   tradition.
6. Whether vernacular hand missals, people's missals and unofficial compilations should
   ever be registered (current draft: no; only editions of the liturgical book itself).
