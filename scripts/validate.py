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

VERNACULAR_KEY = re.compile(r"^[a-z0-9_]+_\d{4}_[a-z]{2,3}(-[a-z0-9]+)*_[a-z0-9_]+$")
TERRITORY = re.compile(r"^[A-Z]{2}(-[A-Z0-9]{1,3})?$")
USAGE_STATUS = {"in_force", "adopting", "de_facto", "superseded", "unknown"}


def _load(path, required=True):
    if not path.exists():
        if required:
            raise FileNotFoundError(path)
        return []
    return json.loads(path.read_text(encoding="utf-8"))["entries"]


def _cesidr_keys(cesidr_dir):
    if cesidr_dir is not None and (cesidr_dir / "data" / "churches.json").exists():
        trad = {e["id"] for e in _load(cesidr_dir / "data" / "tradition.json")}
        esi = {e["id"] for e in _load(cesidr_dir / "data" / "churches.json")}
        return trad, esi
    return PINNED_TRAD, PINNED_ESI


def _ids(entries, label, errors):
    seen = set()
    for e in entries:
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
    trad, esi = _cesidr_keys(cesidr_dir)

    book_ids = _ids(books, "books", errors)
    edition_ids = _ids(editions, "editions", errors)
    rite_ids = _ids(rites, "rites", errors)
    auth_ids = _ids(authorities, "authorities", errors)

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
        succ = e.get("successor")
        if succ in by_id and by_id[succ].get("predecessor") != eid:
            errors.append(f"editions: {eid} names successor {succ}, whose predecessor is not {eid}")
        pred = e.get("predecessor")
        if pred in by_id and by_id[pred].get("successor") != eid:
            errors.append(f"editions: {eid} names predecessor {pred}, whose successor is not {eid}")
        auth = e.get("issuing_authority")
        if auth is not None:
            if auth not in auth_ids:
                errors.append(f"editions: {eid} has unknown issuing_authority {auth}")
            if not VERNACULAR_KEY.match(eid) or not eid.endswith("_" + auth.replace("-", "_")):
                errors.append(f"editions: {eid} does not match <book>_<year>_<lang>_{auth}")
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
        if not TERRITORY.match(u.get("territory", "")):
            errors.append(f"{where}: bad territory code {u.get('territory')}")
        if u.get("edition") is not None and u["edition"] not in edition_ids:
            errors.append(f"{where}: unknown edition {u['edition']}")
        if u.get("status") not in USAGE_STATUS:
            errors.append(f"{where}: bad status {u.get('status')}")
        church = u.get("church", "esi:latin")
        if church not in esi:
            errors.append(f"{where}: unknown church {church}")
        rite = u.get("rite", "rite:roman")
        if rite not in rite_ids:
            errors.append(f"{where}: unknown rite {rite}")
        if u.get("status") == "in_force":
            span = (_bound(u.get("from"), False), _bound(u.get("until"), True))
            key = (u.get("territory"), u.get("language"), church, rite)
            for other in spans.get(key, []):
                if span[0] <= other[1] and other[0] <= span[1]:
                    errors.append(f"{where}: in_force period overlaps another row for the same territory/language/church/rite")
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
