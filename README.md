# CLBDR

The home of the **Common Liturgical Books Data Repository**, curated by the **Catholic Engineering Task Force** of the [Catholic Digital Commons Foundation](https://github.com/CatholicOS).

## What is CLBDR?

The Common Liturgical Books Data Repository (CLBDR) provides canonicalized identifiers for the **liturgical books of the Roman Rite and their editions**: the Roman Missal, the Lectionary, the Liturgy of the Hours, the Roman Martyrology, the Pontifical and Ritual *ordines* (Marriage, Baptism, Ordinations, Confirmation, Penance, Exsequies…), the Book of Blessings, the Ceremonial of Bishops — each as a *book* identity, with its Latin typical editions and its approved vernacular editions as *edition* identities.

CLBDR **absorbs and supersedes** the [CRMETDR](https://github.com/CatholicOS/crmetdr) (Common Roman Missal Editio Typica Data Repository): a single registry for all liturgical books avoids one acronym per book and dissolves naming collisions (a martyrology editions repository would also have been "CRMETDR"). The edition keys the [CLEDR](https://github.com/CatholicOS/cledr) already uses (`missale_romanum_1970`, `missale_romanum_2002`, …) are preserved unchanged.

## The two-level model

**Books** (`data/books.json`) — the abstract liturgical book, with a `category` (missal, lectionary, liturgy_of_the_hours, martyrology, pontifical, ritual, benedictional, ceremonial, sacramentary, chant) and, for the post-conciliar *ordines*, the `collection` they belong to (Pontificale Romanum, Rituale Romanum):

```
book:missale-romanum        book:ordo-lectionum-missae     book:martyrologium-romanum
book:liturgia-horarum       book:ordo-celebrandi-matrimonium (collection: rituale-romanum)
book:de-ordinatione         (collection: pontificale-romanum)  …
```

**Editions** (`data/editions.json`) — a specific promulgated edition of a book: `<book>_<year>` for Latin typical editions (`martyrologium_romanum_2004`), `<book>_<year>_<bcp47>` for approved vernacular editions (`martyrologium_romanum_2004_it_IT`). Each edition carries its nature (typical edition, revised typical edition, emended reprint, approved vernacular edition, translation), promulgation decree and date, scope, locale, predecessor/successor — and its **volume structure**.

### Volumes: the Latin reference is fixed, vernacular distributions vary

Multi-volume books are packaged differently across editions: the Latin Liturgia Horarum is four volumes, the Latin lectionary is defined by the *Ordo Lectionum Missae* (an index, not a set of physical volumes), while the Italian CEI lectionary spreads the same content over nine volumes and the US Lectionary for Mass over four. CLBDR therefore treats the **Latin typical edition as the fixed content reference**: each edition declares its own `volumes`, and each volume declares what it `covers` in terms of content sections defined by the Latin reference edition. See [docs/schema.md](docs/schema.md).

## Uses

- The [CLEDR](https://github.com/CatholicOS/cledr) references Missal editions as the source establishing each liturgical celebration;
- the [CRMEDR](https://github.com/CatholicOS/crmedr) anchors martyrology eulogies to `martyrologium_romanum_2004` and records per-edition attributes;
- the [martyrology-api](https://github.com/CatholicOS/martyrology-api) resolves *(date, territory, locale)* to the edition in force, to serve the right texts for any year.

> **Note:** all IDs are drafts pending committee review; edition metadata (decree dates, volume structures) marked *pending verification* awaits confirmation against the promulgation decrees.

## License

The data and documentation in this repository are licensed under the [Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License](https://creativecommons.org/licenses/by-nc-nd/4.0/) (CC BY-NC-ND 4.0). See [`LICENSE`](LICENSE) for the full legal code.
