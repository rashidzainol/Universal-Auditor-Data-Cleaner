import sys, os, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from processor import (column_letter_to_number, column_number_to_letter, is_numeric,
                       to_float, extract_account_info, is_transaction_row)


class TestProcessor(unittest.TestCase):
    def test_column_letter_to_number(self):
        self.assertEqual(column_letter_to_number("A"), 0)
        self.assertEqual(column_letter_to_number("Z"), 25)
        self.assertEqual(column_letter_to_number("AA"), 26)
        self.assertEqual(column_letter_to_number("auto"), "auto")
        self.assertEqual(column_letter_to_number(""), "auto")

    def test_column_number_to_letter(self):
        self.assertEqual(column_number_to_letter(0), "A")
        self.assertEqual(column_number_to_letter(25), "Z")
        self.assertEqual(column_number_to_letter(26), "AA")
        self.assertEqual(column_number_to_letter(-1), "")

    def test_is_numeric(self):
        self.assertTrue(is_numeric("123"))
        self.assertTrue(is_numeric("1,234.56"))
        self.assertFalse(is_numeric("abc"))
        self.assertFalse(is_numeric(None))

    def test_to_float(self):
        self.assertEqual(to_float("1,500.00"), 1500.0)
        self.assertEqual(to_float("(500.00)"), -500.0)
        self.assertEqual(to_float("500.00 Dr"), 500.0)
        self.assertEqual(to_float("abc"), 0.0)

    def test_extract_account_info(self):
        row = ["ACCOUNT CODE: 11000-000 CASH AND BANK"]
        code, name = extract_account_info(row)
        self.assertEqual(code, "11000-000")
        self.assertIn("CASH", name.upper())

        row2 = ["12345-A01", "Some Name"]
        code2, _ = extract_account_info(row2)
        self.assertEqual(code2, "12345-A01")

    def test_is_transaction_row(self):
        self.assertTrue(is_transaction_row("01/01/2024", "REF1", 100, ""))
        self.assertFalse(is_transaction_row("", "REF1", 100, ""))
        self.assertTrue(is_transaction_row("01/01/2024", "", "", 50))
        self.assertFalse(is_transaction_row("", "", 0, 0))


if __name__ == "__main__":
    unittest.main()