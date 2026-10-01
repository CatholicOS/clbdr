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
  `<book-slug>_<year>_<bcp47>` for approved vernacular editions, following the pattern
  proposed in the absorbed CRMETDR (`missale_romanum_2011_en_US`,
  `martyrologium_romanum_2004_it_IT`); a trailing `_unofficial` marks translations that
  are not sanctioned editions (`martyrologium_romanum_1914_en_unofficial`). Latin
  Missal editions also carry the CRMETDR's proposed `short_form` (`mr1970`) as an
  attribute.
- **`nature`** — `editio_princeps` (pre-typical first prints), `editio_typica`,
  `editio_typica_altera` (tertia, …), `editio_typica_recognita` (historical
  revisions), `reimpressio_emendata` (emended reprints, e.g. the 1971 and 2008
  Missals), `editio_vernacula` (approved vernacular edition), `translatio`
  (translation without the status of an edition). The vocabulary needs committee
  harmonization against the title pages of the books themselves.
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

## Identifier durability

Three cases are already on this repository's record. None is an execution mistake; each is
what a name-derived identifier does when a name, a fact, or the registry's scope moves.

- **Two documented schemes disagreed, and one of them named an edition that does not
  exist.** `README.md` described vernacular edition IDs as
  `<book>_<territory-or-locale>_<year>`, with the example `martyrologium_romanum_cei_2004`;
  this file specifies `<book-slug>_<year>_<bcp47>`, with the example
  `martyrologium_romanum_2004_it_IT`. The data follows this file:
  `martyrologium_romanum_2004_it_IT` is in `data/editions.json`, and
  `martyrologium_romanum_cei_2004` appears nowhere in the registry. The README is corrected
  in the same change that adds this section, but the divergence is the recorded case: a
  scheme whose every segment carries a claim (territory *or* locale? before *or* after the
  year?) drifts from the prose documenting it, and the documented identifier resolves to
  nothing.
- **An unverified year is baked into every edition ID.** `data/editions.json` opens by
  recording that "Decree citations and dates given as year-only are pending verification
  against the promulgation decrees" — and the year is the one segment every edition ID is
  built from. The Missal shows the exposure precisely: `missale_romanum_1970` carries
  `"promulgated": "1970-03-26"`, while its own decree field reads "promulgated by Paulus
  VI, Const. Ap. Missale Romanum (1969-04-03)", and the short form `mr1970` repeats the
  choice a second time. Whichever year verification confirms, one of the two is already
  written into an identifier, a short form, and the CLEDR keys preserved unchanged here.
- **An acronym collision forced a whole registry to be absorbed.** CLBDR "absorbs and
  supersedes" the CRMETDR because "a martyrology editions repository would also have been
  'CRMETDR'". No book changed; the naming space did. Identity derived from names inherits
  every collision the names have.

Each case dissolves when the canonical identifier is machine-readable and the
human-readable layer is guaranteed beside it — both, not one at the cost of the other:

```text
id:      R7kQp2mXf4LdTbz9Ns3Hc1              # canonical, machine-readable, minted once
                                             # (illustrative value: shape only, not a minted ID)
aliases: martyrologium_romanum_2004_it_IT    # permanent, resolvable, never reused
         martyrologium_romanum_cei_2004      # the README's former form, resolvable too
labels:  "Martyrologium Romanum"@la · "Martirologio Romano"@it · "Roman Martyrology"@en
year:    2004                                # an attribute — verifiable, and correctable
scope:   IT                                  # an attribute, not a segment
```

Under that shape the two documented schemes stop competing, because both spellings are
aliases on one record rather than rival claims to be the identity; verifying 1970 against
1969 edits a field and adds a label, leaving `missale_romanum_1970` and `mr1970` resolvable
forever; and absorbing a registry re-parents records without re-minting them. The
alias-and-label mechanism generalizes what the CRMEDR already ships:
`data/deprecated_ids.json` beside `i18n/{la,it,en}.json`.

The general argument — why canonical identifiers should be machine-readable, what that
costs, and how the human-readable layer is guaranteed rather than left optional — is set
out once in *Identifier Durability: Machine-Readable Canonical IRIs* (CDCF
`foundation-docs`, `research/identifier-durability-opaque-canonical-iris.md`) and is not
restated here.

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
5. Whether the canonical ID of an edition should be machine-readable and minted once, with
   every key this schema produces (`missale_romanum_1970`, its short form `mr1970`,
   `martyrologium_romanum_2004_it_IT`) kept as a permanent resolvable alias and every
   edition title carried as a multilingual label — keeping this scheme intact as the
   human-readable layer rather than replacing it (see "Identifier durability").
