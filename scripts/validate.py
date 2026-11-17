#!/usr/bin/env python3
"""Referential-integrity checks for the CLBDR data files.

Usage: python3 scripts/validate.py [--cesidr PATH]

Exits 1 and prints one line per problem when the data is inconsistent.
CESIDR keys (trad:, esi:) are read from a CESIDR checkout (default: ../cesidr next
to this repository); without one, the pinned lists below are used.
"""

import argparse
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent

# CESIDR main @ e6f8af3
PINNED_TRAD = {"trad:latin", "trad:byzantine", "trad:alexandrian", "trad:antiochene",
               "trad:east-syriac", "trad:armenian"}
PINNED_ESI = {"esi:latin", "esi:albanian", "esi:belarusian", "esi:bulgarian", "esi:croatian-serbian",
              "esi:greek", "esi:hungarian", "esi:italo-albanian", "esi:macedonian", "esi:melkite",
              "esi:romanian", "esi:russian", "esi:ruthenian", "esi:slovak", "esi:ukrainian",
              "esi:coptic", "esi:eritrean", "esi:ethiopian", "esi:maronite", "esi:syriac",
              "esi:syro-malankara", "esi:chaldean", "esi:syro-malabar", "esi:armenian"}

VERNACULAR_KEY = re.compile(r"^(?P<book>[a-z0-9_]+?)_(?P<year>\d{4})_(?P<lang>[a-z]{2,3}(?:-[a-z0-9]+)*)_(?P<auth>[a-z0-9_]+)$")
TERRITORY = re.compile(r"^[A-Z]{2}(-[A-Z0-9]{1,3})?$")
LANG_TAG = re.compile(r"^[A-Za-z]{2,3}(-[A-Za-z0-9]+)*$")
DATE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")
USAGE_STATUS = {"in_force", "adopting", "de_facto", "unknown"}


def _load(path, required=True):
    if not path.exists():
        if required:
            raise FileNotFoundError(path)
        return []
    return json.loads(path.read_text(encoding="utf-8"))["entries"]


def _cesidr_keys(cesidr_dir, errors):
    if cesidr_dir is None or not (cesidr_dir / "data").is_dir():
        return PINNED_TRAD, PINNED_ESI
    keys = []
    for name, pinned in (("tradition.json", PINNED_TRAD), ("churches.json", PINNED_ESI)):
        path = cesidr_dir / "data" / name
        if not path.exists():
            errors.append(f"cesidr: {path} not found; using the pinned keys")
            keys.append(pinned)
        else:
            keys.append({e["id"] for e in _load(path) if "id" in e})
    return keys[0], keys[1]


def _ids(entries, label, errors):
    seen = set()
    for i, e in enumerate(entries):
        if "id" not in e:
            errors.append(f"{label}[{i}]: entry has no id")
            continue
        if e["id"] in seen:
            errors.append(f"{label}: duplicate id {e['id']}")
        seen.add(e["id"])
    return seen


def _bound(value, upper):
    """Normalise a year or ISO date to a comparable string; None = open."""
    if value is None:
        return "9999-99-99" if upper else "0000-00-00"
    value = str(value)
    if len(value) == 4:
        return value + ("-12-31" if upper else "-01-01")
    if len(value) == 7:
        return value + ("-31" if upper else "-01")
    return value


def validate(data_dir, cesidr_dir=REPO.parent / "cesidr"):
    data_dir = pathlib.Path(data_dir)
    errors = []
    books = _load(data_dir / "books.json")
    editions = _load(data_dir / "editions.json")
    rites = _load(data_dir / "rites.json", required=False)
    authorities = _load(data_dir / "authorities.json", required=False)
    usage = _load(data_dir / "usage.json", required=False)
    trad, esi = _cesidr_keys(cesidr_dir, errors)

    book_ids = _ids(books, "books", errors)
    edition_ids = _ids(editions, "editions", errors)
    rite_ids = _ids(rites, "rites", errors)
    auth_ids = _ids(authorities, "authorities", errors)
    books, editions, rites = ([e for e in x if "id" in e] for x in (books, editions, rites))

    rites_by_id = {r["id"]: r for r in rites}
    books_by_id = {b["id"]: b for b in books}
    for r in rites:
        if r.get("tradition") not in trad:
            errors.append(f"rites: {r['id']} has unknown tradition {r.get('tradition')}")

    for b in books:
        if b.get("tradition") not in trad:
            errors.append(f"books: {b['id']} has unknown tradition {b.get('tradition')}")
        churches = b.get("churches") or []
        if not churches:
            errors.append(f"books: {b['id']} has no churches")
        for c in churches:
            if c not in esi:
                errors.append(f"books: {b['id']} has unknown church {c}")
        if b.get("rite") not in rite_ids:
            errors.append(f"books: {b['id']} has unknown rite {b.get('rite')}")
        elif rites_by_id[b["rite"]].get("tradition") != b.get("tradition"):
            errors.append(f"books: {b['id']} has tradition {b.get('tradition')} but its rite {b['rite']} "
                          f"belongs to {rites_by_id[b['rite']].get('tradition')}")
        for ref in ("collection", "replaces"):
            if ref in b and b[ref] not in book_ids:
                errors.append(f"books: {b['id']} {ref} {b[ref]} does not resolve")

    by_id = {e["id"]: e for e in editions}
    aliases = {}
    for e in editions:
        eid = e["id"]
        if e.get("book") not in book_ids:
            errors.append(f"editions: {eid} has unknown book {e.get('book')}")
        for ref in ("translation_of", "predecessor", "successor"):
            if ref in e and e[ref] not in edition_ids:
                errors.append(f"editions: {eid} {ref} {e[ref]} does not resolve")
        langs = e.get("language")
        langs = langs if isinstance(langs, list) else [langs]
        for tag in langs:
            if not isinstance(tag, str) or not LANG_TAG.match(tag):
                errors.append(f"editions: {eid} has a malformed language tag {tag}")
        succ = e.get("successor")
        if succ in by_id and by_id[succ].get("predecessor") != eid:
            errors.append(f"editions: {eid} names successor {succ}, whose predecessor is not {eid}")
        if succ in by_id and "issuing_authority" in e and (
                by_id[succ].get("issuing_authority") != e["issuing_authority"]
                or str(by_id[succ].get("language")).lower() != str(e.get("language")).lower()):
            errors.append(f"editions: {eid} -> {succ}: a vernacular chain must stay within the same authority and language")
        pred = e.get("predecessor")
        if pred in by_id and by_id[pred].get("successor") != eid:
            errors.append(f"editions: {eid} names predecessor {pred}, whose successor is not {eid}")
        auth = e.get("issuing_authority")
        if auth is not None:
            if auth not in auth_ids:
                errors.append(f"editions: {eid} has unknown issuing_authority {auth}")
            m = VERNACULAR_KEY.match(eid)
            if not m or m["auth"] != auth.replace("-", "_"):
                errors.append(f"editions: {eid} does not match <book>_<year>_<lang>_{auth}")
            else:
                if m["lang"] != str(langs[0]).lower():
                    errors.append(f"editions: {eid} encodes language {m['lang']} but its language is {langs[0]}")
                if m["year"] != str(e.get("published", ""))[:4]:
                    errors.append(f"editions: {eid} encodes year {m['year']} but its published year is {e.get('published')}")
        for a in e.get("aliases", []):
            key = a["key"]
            if key in edition_ids:
                errors.append(f"editions: alias {key} on {eid} is a live edition id")
            if key in aliases:
                errors.append(f"editions: alias {key} on both {aliases[key]} and {eid}")
            aliases[key] = eid

    spans = {}
    for i, u in enumerate(usage):
        where = f"usage[{i}] {u.get('territory')}/{u.get('language')}"
        if not TERRITORY.match(str(u.get("territory") or "")):
            errors.append(f"{where}: bad territory code {u.get('territory')}")
        if u.get("edition") is not None and u["edition"] not in edition_ids:
            errors.append(f"{where}: unknown edition {u['edition']}")
        status = u.get("status")
        if status not in USAGE_STATUS:
            errors.append(f"{where}: bad status {status}")
        elif status == "unknown" and u.get("edition") is not None:
            errors.append(f"{where}: status unknown must have a null edition")
        elif status != "unknown" and u.get("edition") is None:
            errors.append(f"{where}: status {status} needs an edition")
        for k in ("from", "until"):
            if k in u and not DATE.match(str(u[k])):
                errors.append(f"{where}: {k} {u[k]} is not YYYY, YYYY-MM or YYYY-MM-DD")
        church = u.get("church", "esi:latin")
        if church not in esi:
            errors.append(f"{where}: unknown church {church}")
        rite = u.get("rite", "rite:roman")
        if rite not in rite_ids:
            errors.append(f"{where}: unknown rite {rite}")
        edition = by_id.get(u.get("edition"))
        book = books_by_id.get(edition["book"]) if edition else None
        start = u.get("from")
        if edition:
            lang = edition.get("language")
            lang = (lang[0] if isinstance(lang, list) else lang).lower()
            if str(u.get("language")).lower() != lang:
                errors.append(f"{where}: language {u.get('language')} differs from {edition['id']}'s language {lang}")
            if book and church not in book.get("churches", []):
                errors.append(f"{where}: church {church} is not among {book['id']}'s churches")
            if book and rite != book.get("rite"):
                errors.append(f"{where}: rite {rite} differs from {book['id']}'s rite {book.get('rite')}")
            # An edition is never in force before it was published: that is the implicit lower bound.
            issued = edition.get("published") or edition.get("promulgated")
            if start is not None and issued and _bound(start, False) < _bound(str(issued)[:4], False):
                errors.append(f"{where}: from {start} is before {edition['id']} was published ({issued})")
            if start is None:
                start = edition.get("in_force") or issued
        span = (_bound(start, False), _bound(u.get("until"), True))
        if span[1] < span[0]:
            errors.append(f"{where}: period ends before it starts ({start} – {u.get('until')})")
            continue
        if status == "in_force":
            key = (u.get("territory"), str(u.get("language")).lower(), church, rite, book["id"] if book else None)
            for other in spans.get(key, []):
                if span[0] <= other[1] and other[0] <= span[1]:
                    errors.append(f"{where}: in_force period overlaps another row for the same territory/language/church/rite/book")
            spans.setdefault(key, []).append(span)
    return errors


def main():
    parser = argparse.ArgumentParser(description="Check CLBDR data integrity.")
    parser.add_argument("--cesidr", type=pathlib.Path, default=REPO.parent / "cesidr")
    args = parser.parse_args()
    errors = validate(REPO / "data", args.cesidr)
    for e in errors:
        print(e)
    print(f"{len(errors)} problem(s)" if errors else "OK")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
