"""Tests unitaires des transformations indépendantes de PostgreSQL."""

import unittest

import pandas as pd

from etl.transform import build_date_dimension, build_time_dimension, clean_text, decimal, integer, normalize_commune


class TransformTests(unittest.TestCase):
    def test_decimal_comma(self) -> None:
        self.assertAlmostEqual(decimal(pd.Series(["48,8962100"])).iloc[0], 48.89621)

    def test_non_breaking_spaces_are_removed(self) -> None:
        self.assertEqual(clean_text(pd.Series(["203\u00a0988\u00a0581"])).iloc[0], "203988581")

    def test_commune_is_padded(self) -> None:
        self.assertEqual(normalize_commune(pd.Series(["1001"])).iloc[0], "01001")

    def test_missing_integer_remains_nullable(self) -> None:
        values = integer(pd.Series(["", "-1", "2"]))
        self.assertTrue(pd.isna(values.iloc[0]))
        self.assertTrue(pd.isna(values.iloc[1]))
        self.assertEqual(values.iloc[2], 2)

    def test_date_dimension_covers_leap_year(self) -> None:
        dimension = build_date_dimension(2024, 2024)
        self.assertEqual(len(dimension), 366)
        self.assertIn(20240229, dimension["date_key"].tolist())

    def test_time_dimension_has_1440_minutes(self) -> None:
        dimension = build_time_dimension()
        self.assertEqual(len(dimension), 1440)
        self.assertEqual(dimension.iloc[0]["heure_libelle"], "00:00")
        self.assertEqual(dimension.iloc[-1]["heure_libelle"], "23:59")


if __name__ == "__main__":
    unittest.main()
