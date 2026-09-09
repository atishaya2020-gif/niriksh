import unittest

from app.services.normalization import (
    canonicalize_identifier,
    canonicalize_integer_identifier,
    normalize_identifier,
    normalize_phone,
)


class NormalizationTests(unittest.TestCase):
    def test_scientific_notation_is_expanded_without_float_conversion(self):
        self.assertEqual(canonicalize_identifier("9.18826E+11"), "918826000000")
        self.assertEqual(canonicalize_identifier("2.639E+13"), "26390000000000")

    def test_normal_digit_identifiers_preserve_leading_zeroes(self):
        self.assertEqual(canonicalize_identifier("001234"), "001234")
        self.assertEqual(canonicalize_integer_identifier("001234"), "001234")

    def test_non_integral_scientific_identifiers_are_not_truncated(self):
        self.assertEqual(canonicalize_identifier("1.234E+2"), "123.4")
        self.assertEqual(canonicalize_identifier("123.4500"), "123.4500")
        self.assertIsNone(canonicalize_integer_identifier("1.234E+2"))

    def test_masked_and_structured_identifiers_preserve_meaningful_characters(self):
        self.assertEqual(normalize_identifier(" XXXX5163 "), "XXXX5163")
        self.assertEqual(normalize_identifier("fir/2025/83874"), "FIR/2025/83874")
        self.assertEqual(normalize_identifier("txn101041356456"), "TXN101041356456")

    def test_empty_identifier_values_are_rejected(self):
        for value in (None, "", "  ", "NaN", "NULL", "<NA>"):
            self.assertIsNone(canonicalize_identifier(value))

    def test_phone_normalization_expands_scientific_notation_before_indian_rule(self):
        self.assertEqual(normalize_phone("9.18826E+11"), "8826000000")
        self.assertEqual(normalize_phone("+91 88260-00000"), "8826000000")
        self.assertEqual(normalize_phone("08826000000"), "8826000000")
        self.assertEqual(normalize_phone("00918826000000"), "8826000000")

    def test_phone_normalization_does_not_silently_truncate(self):
        self.assertIsNone(normalize_phone("123456789"))
        self.assertIsNone(normalize_phone("12345678901"))
        self.assertIsNone(normalize_phone("1.234E+2"))
