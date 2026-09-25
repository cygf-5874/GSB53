"""fmtnum 的既有用例。

只用十进制字面值与二进制精确值，避免踩到浮点表示误差。
"""

import unittest
from decimal import Decimal

from fmtnum import FmtNumError, format_fixed


class FormatFixedTest(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(format_fixed(1.5, 0, "HALF_UP"), "2")
        self.assertEqual(format_fixed(0.25, 1, "HALF_UP"), "0.3")
        self.assertEqual(format_fixed(-1.5, 0, "HALF_UP"), "-2")

    def test_half_even_non_tie(self):
        self.assertEqual(format_fixed(0.24, 1, "HALF_EVEN"), "0.2")
        self.assertEqual(format_fixed(0.26, 1, "HALF_EVEN"), "0.3")
        self.assertEqual(format_fixed(1.24, 1, "HALF_EVEN"), "1.2")
        self.assertEqual(format_fixed(-0.26, 1, "HALF_EVEN"), "-0.3")

    def test_down(self):
        self.assertEqual(format_fixed(1.29, 1, "DOWN"), "1.2")
        self.assertEqual(format_fixed(-1.29, 1, "DOWN"), "-1.2")
        self.assertEqual(format_fixed(9.99, 1, "DOWN"), "9.9")

    def test_up(self):
        self.assertEqual(format_fixed(1.21, 1, "UP"), "1.3")
        self.assertEqual(format_fixed(-1.21, 1, "UP"), "-1.3")
        self.assertEqual(format_fixed(2.001, 2, "UP"), "2.01")

    def test_digits_zero(self):
        self.assertEqual(format_fixed(7.4, 0, "HALF_UP"), "7")
        self.assertEqual(format_fixed(8.6, 0, "HALF_UP"), "9")
        self.assertEqual(format_fixed(-7.4, 0, "HALF_UP"), "-7")

    def test_padding(self):
        self.assertEqual(format_fixed(1, 2, "HALF_UP"), "1.00")
        self.assertEqual(format_fixed(2.5, 3, "DOWN"), "2.500")
        self.assertEqual(format_fixed(0, 2, "HALF_UP"), "0.00")

    def test_string_input(self):
        self.assertEqual(format_fixed("12.5", 1, "DOWN"), "12.5")
        self.assertEqual(format_fixed("-0.5", 1, "DOWN"), "-0.5")

    def test_decimal_input(self):
        self.assertEqual(format_fixed(Decimal("3.14"), 2, "HALF_UP"), "3.14")
        self.assertEqual(format_fixed(Decimal("0.25"), 1, "HALF_UP"), "0.3")

    def test_int_input(self):
        self.assertEqual(format_fixed(42, 2, "HALF_UP"), "42.00")
        self.assertEqual(format_fixed(-7, 3, "HALF_UP"), "-7.000")

    def test_negative_nonzero(self):
        self.assertEqual(format_fixed(-3.14, 2, "HALF_UP"), "-3.14")
        self.assertEqual(format_fixed(-2.5, 0, "DOWN"), "-2")
        self.assertEqual(format_fixed(-0.5, 1, "UP"), "-0.5")

    def test_grouping_thousand(self):
        self.assertEqual(format_fixed(1234567, 0, "HALF_UP", "thousand"), "1,234,567")
        self.assertEqual(format_fixed(1234, 0, "HALF_UP", "thousand"), "1,234")
        self.assertEqual(format_fixed(-1234567, 0, "HALF_UP", "thousand"), "-1,234,567")

    def test_grouping_none(self):
        self.assertEqual(format_fixed(1234567, 0, "HALF_UP"), "1234567")

    def test_nan_and_infinity(self):
        self.assertEqual(format_fixed(float("nan"), 2, "HALF_UP"), "NaN")
        self.assertEqual(format_fixed(float("inf"), 2, "HALF_UP"), "Infinity")
        self.assertEqual(format_fixed(float("-inf"), 2, "HALF_UP"), "-Infinity")

    def test_validation(self):
        with self.assertRaises(FmtNumError):
            format_fixed(1, 2, "NEAREST")
        with self.assertRaises(FmtNumError):
            format_fixed(1, 2, "HALF_UP", "european")
        with self.assertRaises(FmtNumError):
            format_fixed(1, -1, "HALF_UP")
        with self.assertRaises(FmtNumError):
            format_fixed("not-a-number", 2, "HALF_UP")


if __name__ == "__main__":
    unittest.main()
