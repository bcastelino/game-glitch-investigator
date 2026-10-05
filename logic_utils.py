"""Game logic for the Glitchy Guesser number guessing game.

These helpers hold all of the rules (ranges, parsing, hints, scoring, the high
score file) so they can be unit tested without running Streamlit. ``app.py``
only handles the UI and imports everything from here.
"""

from __future__ import annotations

import json
import math
import random
import re


def get_range_for_difficulty(difficulty: str) -> tuple[int, int]:
    """Return the inclusive number range for a difficulty level.

    Args:
        difficulty: One of "Easy", "Normal" or "Hard". Any other value falls
            back to the Normal range.

    Returns:
        A ``(low, high)`` tuple. Easy is 1-20, Normal is 1-100 and Hard is
        1-50.
    """
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def parse_guess(
    raw: str, low: int = 1, high: int = 100
) -> tuple[bool, int | None, str | None]:
    """Parse and validate the text a player typed as a guess.

    Surrounding spaces are ignored. Empty input, non-numbers, decimals and
    whole numbers outside ``low``..``high`` are rejected with a message, and
    this function never raises.

    Args:
        raw: The raw text from the input box. May be ``None``.
        low: Smallest allowed guess (inclusive).
        high: Largest allowed guess (inclusive).

    Returns:
        A ``(ok, guess_int, error_message)`` tuple. When ``ok`` is True,
        ``guess_int`` is the parsed number and ``error_message`` is ``None``.
        When ``ok`` is False, ``guess_int`` is ``None`` and
        ``error_message`` explains what was wrong.
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
            # float() quietly accepts things like "1_0", so rule them out
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


def check_guess(guess: int, secret: int) -> tuple[str, str]:
    """Compare a guess to the secret number.

    Args:
        guess: The player's guess.
        secret: The secret number to find.

    Returns:
        An ``(outcome, message)`` tuple. ``outcome`` is "Win", "Too High" or
        "Too Low", and ``message`` is the hint to show the player (a high
        guess says to go lower, a low guess says to go higher).
    """
    # FIX: Swapped the hint messages so a high guess says "Go LOWER!" and a
    # low guess says "Go HIGHER!". Refactored out of app.py with Claude Code
    # (agent mode) and dropped the str fallback now that both sides are ints.
    if guess == secret:
        return "Win", "🎉 Correct!"

    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int) -> int:
    """Work out the new score after a guess.

    A win earns ``100 - 10 * (attempt_number + 1)`` points (never less than
    10). Every wrong guess costs 5 points.

    Args:
        current_score: The score before this guess.
        outcome: "Win", "Too High" or "Too Low" from :func:`check_guess`.
        attempt_number: Which attempt this guess was (1 for the first).

    Returns:
        The updated score. An unknown outcome leaves the score unchanged.
    """
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    # FIX: Too High used to give +5 on even attempts, so wrong guesses could
    # raise the score. Every wrong guess now costs 5 points. Needed this before
    # a High Score tracker made sense (planned with Claude Code agent mode).
    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score


def new_game_state(low: int, high: int) -> dict:
    """Build the starting game state for a new round.

    Args:
        low: Smallest possible secret number (inclusive).
        high: Largest possible secret number (inclusive).

    Returns:
        A dict with the keys ``attempts``, ``secret``, ``score``, ``status``,
        ``history`` and ``rounds``, ready to copy into ``st.session_state``.
    """
    # FIX: New Game used to only reset attempts and draw from 1-100, so a won
    # game stayed stuck and Easy/Hard secrets could be out of range. Built this
    # helper with Claude Code so the whole reset lives in one testable place.
    return {
        "attempts": 0,
        "secret": random.randint(low, high),
        "score": 0,
        "status": "playing",
        "history": [],
        "rounds": [],
    }


def load_high_score(path) -> int:
    """Read the best score saved on disk.

    Args:
        path: Location of the JSON high score file (``str`` or ``Path``).

    Returns:
        The saved best score, or 0 if the file is missing, corrupt or does not
        hold a whole number.
    """
    try:
        with open(path, encoding="utf-8") as f:
            best = json.load(f)["best"]
    except (OSError, ValueError, KeyError, TypeError):
        return 0
    return best if isinstance(best, int) else 0


def save_high_score(score: int, path) -> int:
    """Save a score only if it beats the best score already on disk.

    Args:
        score: The score to consider saving.
        path: Location of the JSON high score file (``str`` or ``Path``).

    Returns:
        The best score after this call: ``score`` if it was a new record,
        otherwise the previously saved best.
    """
    best = load_high_score(path)
    if score <= best:
        return best
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"best": score}, f)
    except OSError:
        return best
    return score


def get_temperature(
    guess: int, secret: int, low: int, high: int
) -> tuple[str, str]:
    """Describe how close a guess is as a hot/cold label and emoji.

    The distance is measured as a fraction of the range: within 5% is Hot,
    within 20% is Warm, anything further is Cold.

    Args:
        guess: The player's guess.
        secret: The secret number.
        low: Smallest number in the current range.
        high: Largest number in the current range.

    Returns:
        A ``(label, emoji)`` tuple such as ``("Hot", "🔥")``.
    """
    span = max(high - low, 1)
    distance = abs(guess - secret) / span
    if distance <= 0.05:
        return "Hot", "🔥"
    if distance <= 0.20:
        return "Warm", "🌤️"
    return "Cold", "❄️"
