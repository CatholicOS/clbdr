"""Tests for scripts/validate.py. Run: python3 -m unittest discover -s tests -v"""

import json
import pathlib
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from validate import validate  # noqa: E402


def write(d, name, entries):
    (d / name).write_text(json.dumps({"entries": entries}), encoding="utf-8")


BOOK = {"id": "book:missale-romanum", "title_la": "Missale Romanum", "category": "missal",
        "tradition": "trad:latin", "churches": ["esi:latin"], "rite": "rite:roman"}
RITE = {"id": "rite:roman", "name_la": "ritus Romanus", "name_en": "Roman Rite", "tradition": "trad:latin"}
AUTH = {"id": "usccb", "name": "United States Conference of Catholic Bishops",
        "type": "episcopal_conference", "territories": ["US"]}
LATIN = {"id": "missale_romanum_2008", "book": "book:missale-romanum", "nature": "reimpressio_emendata",
         "language": "la", "scope": "universal", "promulgated": "2008"}
US = {"id": "missale_romanum_2011_en_usccb", "book": "book:missale-romanum", "nature": "editio_vernacula",
      "language": "en", "issuing_authority": "usccb", "translation_of": "missale_romanum_2008",
      "aliases": [{"key": "missale_romanum_2011_en_US", "system": "clbdr"}, {"key": "US_2011", "system": "litcal-api"}]}
USE = {"territory": "US", "language": "en", "edition": "missale_romanum_2011_en_usccb", "status": "in_force"}


class ValidateTest(unittest.TestCase):
    def fixture(self, books=None, editions=None, rites=None, authorities=None, usage=None):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        d = pathlib.Path(tmp.name)
        write(d, "books.json", books if books is not None else [BOOK])
        write(d, "editions.json", editions if editions is not None else [LATIN, US])
        write(d, "rites.json", rites if rites is not None else [RITE])
        write(d, "authorities.json", authorities if authorities is not None else [AUTH])
        write(d, "usage.json", usage if usage is not None else [USE])
        return d

    def assertError(self, errors, needle):
        self.assertTrue(any(needle in e for e in errors), f"no error mentioning {needle!r} in {errors}")

    def test_valid_fixture(self):
        self.assertEqual(validate(self.fixture(), cesidr_dir=None), [])

    def test_current_data_valid(self):
        self.assertEqual(validate(REPO / "data"), [])

    def test_usage_unknown_edition(self):
        errs = validate(self.fixture(usage=[dict(USE, edition="missale_romanum_2011_en_usccbb")]))
        self.assertError(errs, "missale_romanum_2011_en_usccbb")

    def test_overlapping_in_force(self):
        rows = [dict(USE, **{"from": "2011-11-27"}), dict(USE, **{"from": "2015", "until": "2020"})]
        self.assertError(validate(self.fixture(usage=rows)), "overlap")

    def test_sequential_in_force_ok(self):
        older = dict(LATIN, id="missale_romanum_1975")
        rows = [dict(USE, edition="missale_romanum_1975", until="2011-11-26"),
                dict(USE, **{"from": "2011-11-27"})]
        self.assertEqual(validate(self.fixture(editions=[older, LATIN, US], usage=rows)), [])

    def test_other_rite_same_territory_ok(self):
        amb_book = dict(BOOK, id="book:missale-ambrosianum", rite="rite:ambrosian")
        amb_rite = dict(RITE, id="rite:ambrosian")
        amb = dict(US, id="missale_ambrosianum_2024_en_usccb", book="book:missale-ambrosianum", aliases=[])
        rows = [USE, dict(USE, edition="missale_ambrosianum_2024_en_usccb", rite="rite:ambrosian")]
        errs = validate(self.fixture(books=[BOOK, amb_book], rites=[RITE, amb_rite],
                                     editions=[LATIN, US, amb], usage=rows))
        self.assertEqual(errs, [])

    def test_usage_unknown_rite(self):
        self.assertError(validate(self.fixture(usage=[dict(USE, rite="rite:romanus")])), "rite:romanus")

    def test_alias_collisions(self):
        dup = dict(US, id="missale_romanum_2016_en_usccb", aliases=[{"key": "US_2011", "system": "litcal-api"}])
        self.assertError(validate(self.fixture(editions=[LATIN, US, dup])), "US_2011")
        live = dict(US, aliases=[{"key": "missale_romanum_2008", "system": "clbdr"}])
        self.assertError(validate(self.fixture(editions=[LATIN, live])), "missale_romanum_2008")

    def test_asymmetric_chain(self):
        older = dict(LATIN, id="missale_romanum_2002", successor="missale_romanum_2008")
        self.assertError(validate(self.fixture(editions=[older, LATIN, US])), "missale_romanum_2002")

    def test_unknown_cesidr_key(self):
        bad = dict(BOOK, churches=["esi:armenian-catholic"])
        self.assertError(validate(self.fixture(books=[bad])), "esi:armenian-catholic")

    def test_unknown_book_rite_authority(self):
        errs = validate(self.fixture(books=[dict(BOOK, rite="rite:romanus")],
                                     editions=[LATIN, dict(US, issuing_authority="usccbx")]))
        self.assertError(errs, "rite:romanus")
        self.assertError(errs, "usccbx")

    def test_vernacular_key_must_end_with_authority(self):
        bad = dict(US, id="missale_romanum_2011_en_US")
        bad.pop("aliases")
        self.assertError(validate(self.fixture(editions=[LATIN, bad], usage=[])), "missale_romanum_2011_en_US")

    def test_bad_territory(self):
        self.assertError(validate(self.fixture(usage=[dict(USE, territory="USA")])), "USA")

    def test_duplicate_ids(self):
        self.assertError(validate(self.fixture(editions=[LATIN, LATIN, US])), "duplicate")


if __name__ == "__main__":
    unittest.main()
