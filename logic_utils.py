import math
import random
import re


def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def parse_guess(raw: str, low: int = 1, high: int = 100):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    # FIX: Edge cases (negatives, decimals, huge numbers, stray spaces) used to
    # be accepted or silently truncated. Asked Claude Code for three risky
    # inputs and tightened this so bad input returns a clear error instead.
    if raw is None:
        return False, None, "Enter a guess."

    text = raw.strip()
    if text == "":
        return False, None, "Enter a guess."

    if not re.fullmatch(r"[+-]?\d+", text, re.ASCII):
        try:
            # float() quietly accepts things like "1_0", so rule those out first
            if "_" in text:
                raise ValueError(text)
            number = float(text)
        except ValueError:
            return False, None, "That is not a number."
        if math.isfinite(number):
            return False, None, "Enter a whole number (no decimals)."
        return False, None, "That is not a number."

    try:
        value = int(text)
    except ValueError:
        # Absurdly long digit strings (over Python's int conversion limit)
        return False, None, f"Enter a number between {low} and {high}."

    if value < low or value > high:
        return False, None, f"Enter a number between {low} and {high}."

    return True, value, None


def check_guess(guess, secret):
    """
    Compare guess to secret and return (outcome, message).

    outcome examples: "Win", "Too High", "Too Low"
    """
    # FIX: Swapped the hint messages so a high guess says "Go LOWER!" and a
    # low guess says "Go HIGHER!". Refactored out of app.py with Claude Code
    # (agent mode) and dropped the str fallback now that both sides are ints.
    if guess == secret:
        return "Win", "🎉 Correct!"

    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score


def new_game_state(low: int, high: int):
    """Return a fresh game state dict with the secret drawn from [low, high]."""
    # FIX: New Game used to only reset attempts and draw from 1-100, so a won
    # game stayed stuck and Easy/Hard secrets could be out of range. Built this
    # helper with Claude Code so the whole reset lives in one testable place.
    return {
        "attempts": 0,
        "secret": random.randint(low, high),
        "score": 0,
        "status": "playing",
        "history": [],
    }
