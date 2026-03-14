"""Unit tests for wordle_faker."""

import unittest
from datetime import date
from unittest.mock import patch

from wordle_faker import (
    BLACK,
    GREEN,
    WORD_LENGTH,
    WORDLE_EPOCH,
    YELLOW,
    format_score,
    generate_row,
    generate_score,
    get_wordle_number,
)


class TestGetWordleNumber(unittest.TestCase):
    def test_epoch_is_puzzle_one(self):
        self.assertEqual(get_wordle_number(WORDLE_EPOCH), 1)

    def test_next_day_is_puzzle_two(self):
        from datetime import timedelta
        self.assertEqual(get_wordle_number(WORDLE_EPOCH + timedelta(days=1)), 2)

    def test_returns_positive_integer_for_today(self):
        num = get_wordle_number()
        self.assertIsInstance(num, int)
        self.assertGreater(num, 0)

    def test_known_date(self):
        # 2022-01-14 is 209 days after 2021-06-19, so puzzle 210
        self.assertEqual(get_wordle_number(date(2022, 1, 14)), 210)


class TestGenerateRow(unittest.TestCase):
    def test_row_length(self):
        row = generate_row(0.5, 0.2)
        self.assertEqual(len(row), WORD_LENGTH)

    def test_all_black_when_zero_probs(self):
        for _ in range(20):
            row = generate_row(0.0, 0.0)
            self.assertTrue(all(c == BLACK for c in row), row)

    def test_all_green_when_full_green_prob(self):
        for _ in range(20):
            row = generate_row(1.0, 0.0)
            self.assertTrue(all(c == GREEN for c in row), row)

    def test_only_valid_emoji_values(self):
        valid = {GREEN, YELLOW, BLACK}
        for _ in range(50):
            row = generate_row(0.3, 0.3)
            self.assertTrue(set(row).issubset(valid), row)


class TestGenerateScore(unittest.TestCase):
    def test_row_count_matches_num_guesses(self):
        for n in (2, 3, 4):
            rows = generate_score(n)
            self.assertEqual(len(rows), n)

    def test_last_row_is_all_green(self):
        for n in (2, 3, 4):
            rows = generate_score(n)
            self.assertEqual(rows[-1], [GREEN] * WORD_LENGTH)

    def test_each_row_has_correct_length(self):
        rows = generate_score(3)
        for row in rows:
            self.assertEqual(len(row), WORD_LENGTH)

    def test_raises_for_too_few_guesses(self):
        with self.assertRaises(ValueError):
            generate_score(1)

    def test_first_row_has_no_guaranteed_greens(self):
        """With 4 guesses the first row is generated with green_prob=0."""
        # Seed the RNG so the first row never gets a green by chance
        with patch("wordle_faker.random.random", return_value=0.5):
            rows = generate_score(4)
        # 0.5 >= 0.0 (green_prob) + 0.15 (yellow_prob) so cell should be BLACK
        self.assertEqual(rows[0], [BLACK] * WORD_LENGTH)


class TestFormatScore(unittest.TestCase):
    def test_header_format(self):
        rows = [[GREEN] * WORD_LENGTH]
        text = format_score(623, 1, rows)
        self.assertTrue(text.startswith("Wordle 623 1/6"))

    def test_blank_line_after_header(self):
        rows = [[GREEN] * WORD_LENGTH]
        lines = format_score(100, 1, rows).splitlines()
        self.assertEqual(lines[1], "")

    def test_emoji_rows_appear_after_blank_line(self):
        rows = [[GREEN] * WORD_LENGTH, [BLACK] * WORD_LENGTH]
        lines = format_score(1, 2, rows).splitlines()
        # line 0: header, line 1: blank, line 2+: emoji rows
        self.assertIn(GREEN, lines[2])

    def test_correct_number_of_lines(self):
        rows = generate_score(3)
        text = format_score(1, 3, rows)
        lines = text.splitlines()
        # header + blank + 3 emoji rows = 5 lines
        self.assertEqual(len(lines), 5)


if __name__ == "__main__":
    unittest.main()
