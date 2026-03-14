#!/usr/bin/env python3
"""
wordle-faker: generates a realistic-looking Wordle share score.

The output mimics the text you copy after winning Wordle:
  - Header with today's puzzle number and guess count
  - 2–4 rows of emoji squares
  - Rows progress from mostly ⬛ (black) with some 🟨 (yellow)
    to fully 🟩 (green) on the final row
  - Result is printed and, when possible, copied to the clipboard
"""

import random
import subprocess
import sys
from datetime import date

# ── constants ───────────────────────────────────────────────────────────────
GREEN = "\U0001f7e9"   # 🟩
YELLOW = "\U0001f7e8"  # 🟨
BLACK = "\u2b1b"       # ⬛

WORD_LENGTH = 5

# Wordle puzzle #1 was published on June 19 2021 (Josh Wardle's original game)
WORDLE_EPOCH = date(2021, 6, 19)


# ── core logic ───────────────────────────────────────────────────────────────
def get_wordle_number(today: date | None = None) -> int:
    """Return today's Wordle puzzle number (1-based)."""
    if today is None:
        today = date.today()
    return (today - WORDLE_EPOCH).days + 1


def generate_row(green_prob: float, yellow_prob: float) -> list[str]:
    """
    Return a row of WORD_LENGTH emoji squares.

    Each cell is chosen independently:
      - green_prob   → 🟩
      - yellow_prob  → 🟨
      - remainder    → ⬛
    """
    row: list[str] = []
    for _ in range(WORD_LENGTH):
        roll = random.random()
        if roll < green_prob:
            row.append(GREEN)
        elif roll < green_prob + yellow_prob:
            row.append(YELLOW)
        else:
            row.append(BLACK)
    return row


def generate_score(num_guesses: int) -> list[list[str]]:
    """
    Build a grid of emoji rows for the given number of guesses.

    Rows gradually gain more green squares as the solver closes in on the
    answer.  The final row is always all-green (the winning guess).
    """
    if num_guesses < 2:
        raise ValueError("num_guesses must be at least 2")

    rows: list[list[str]] = []

    for i in range(num_guesses - 1):
        # 0.0 on the first row → up to 0.5 green on the row before the last
        progress = i / (num_guesses - 1)
        green_prob = progress * 0.5
        yellow_prob = 0.15 + progress * 0.10  # 15 % → 25 %
        rows.append(generate_row(green_prob, yellow_prob))

    # Winning (final) row is always fully green
    rows.append([GREEN] * WORD_LENGTH)
    return rows


def format_score(wordle_num: int, num_guesses: int, rows: list[list[str]]) -> str:
    """Render the score as the text Wordle copies to the clipboard."""
    lines = [f"Wordle {wordle_num} {num_guesses}/6", ""]
    for row in rows:
        lines.append("".join(row))
    return "\n".join(lines)


# ── clipboard helpers ────────────────────────────────────────────────────────
def _try_pyperclip(text: str) -> bool:
    try:
        import pyperclip  # type: ignore[import-untyped]
        pyperclip.copy(text)
        return True
    except Exception:
        return False


def _try_command(cmd: list[str], text: str) -> bool:
    try:
        subprocess.run(cmd, input=text.encode(), check=True, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return False


def copy_to_clipboard(text: str) -> bool:
    """
    Try every available clipboard mechanism.

    Returns True if the text was successfully placed on the clipboard.
    """
    if _try_pyperclip(text):
        return True
    # Linux – xclip / xsel
    if _try_command(["xclip", "-selection", "clipboard"], text):
        return True
    if _try_command(["xsel", "--clipboard", "--input"], text):
        return True
    # macOS
    if _try_command(["pbcopy"], text):
        return True
    # Windows – clip
    if _try_command(["clip"], text):
        return True
    return False


# ── entry point ──────────────────────────────────────────────────────────────
def main() -> None:
    num_guesses = random.randint(2, 4)
    wordle_num = get_wordle_number()
    rows = generate_score(num_guesses)
    score_text = format_score(wordle_num, num_guesses, rows)

    print(score_text)
    print()

    if copy_to_clipboard(score_text):
        print("✓ Copied to clipboard!")
    else:
        print("(Could not copy to clipboard – paste from terminal output above)")


if __name__ == "__main__":
    main()
