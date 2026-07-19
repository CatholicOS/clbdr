# CLBDR schema (draft for committee review)

## Books

```json
{
  "id": "book:ordo-celebrandi-matrimonium",
  "title_la": "Ordo celebrandi Matrimonium",
  "category": "ritual",
  "collection": "book:rituale-romanum"
}
```

- **`id`** — `book:` + the Latin title, ASCII-folded, lowercase, hyphenated.
- **`category`** — one of: `missal`, `lectionary`, `liturgy_of_the_hours`,
  `martyrology`, `pontifical`, `ritual`, `benedictional`, `ceremonial`,
  `sacramentary`, `chant`. The category expresses the *nature* of the book;
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

- **`id`** — `<book-slug>_<year>` for Latin editions (preserving the CLEDR's existing
  keys verbatim: `missale_romanum_1970`, `missale_romanum_2002`, `missale_romanum_2008`);
  `<book-slug>_<territory-or-conference>_<year>` for approved vernacular editions
  (`martyrologium_romanum_cei_2004`); a trailing `_unofficial` marks translations that
  are not sanctioned editions (`martyrologium_romanum_en_1916_unofficial`).
- **`nature`** — `editio_typica`, `editio_typica_altera` (tertia, …),
  `editio_emendata` (emended reprints, e.g. the 2008 Missal), `editio_vernacula`
  (approved vernacular edition), `translatio` (translation without the status of an
  edition).
- **`scope`** — `universal`, or an ISO 3166-1 alpha-2 / conference key for vernacular
  editions; finer scopes (circumscription, institute) use CECDR / CICLSALDR keys.
- **`promulgated` / `decree`** — the promulgation act; the in-force window is implicit:
  from promulgation until superseded by the successor of the same scope. This drives
  the martyrology-api's *(date, territory, locale)* edition resolution.
- **`predecessor` / `successor`** — the edition line within the same scope.

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
