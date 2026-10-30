import unittest

from core_logic import (
    parse_original,
    parse_transformed,
    tree_to_string,
)


class TestGrammarFix(unittest.TestCase):

    def test_simple_statement(self):
        source = "x;"

        original = parse_original(source)
        transformed = parse_transformed(source)

        self.assertEqual(len(original), 1)
        self.assertEqual(
            tree_to_string(original[0]),
            tree_to_string(transformed),
        )

    def test_if_without_else(self):
        source = "if (a) x;"

        original = parse_original(source)
        transformed = parse_transformed(source)

        self.assertEqual(len(original), 1)
        self.assertEqual(
            tree_to_string(original[0]),
            tree_to_string(transformed),
        )

    def test_dangling_else_is_ambiguous(self):
        source = """
        if (a)
            if (b)
                x;
            else
                y;
        """

        original = parse_original(source)
        transformed = parse_transformed(source)

        self.assertEqual(len(original), 2)
        self.assertIn("ELSE=", tree_to_string(transformed))

    def test_two_else_clauses(self):
        source = """
        if (a)
            if (b)
                x;
            else
                y;
        else
            z;
        """

        original = parse_original(source)
        transformed = parse_transformed(source)

        self.assertGreaterEqual(len(original), 1)
        self.assertIn("ELSE=", tree_to_string(transformed))

    def test_three_levels_of_nesting(self):
        source = """
        if (a)
            if (b)
                if (c)
                    x;
                else
                    y;
        """

        original = parse_original(source)
        transformed = parse_transformed(source)

        self.assertGreaterEqual(len(original), 1)
        self.assertIsNotNone(transformed)

    def test_invalid_input(self):
        with self.assertRaises(SyntaxError):
            parse_transformed("if (a)")

    def test_missing_closing_parenthesis(self):
        with self.assertRaises(SyntaxError):
            parse_transformed("if (a x;")


if __name__ == "__main__":
    unittest.main()