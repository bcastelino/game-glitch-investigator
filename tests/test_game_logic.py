import pytest

from logic_utils import (
    check_guess,
    get_temperature,
    load_high_score,
    new_game_state,
    parse_guess,
    save_high_score,
    update_score,
)


def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"


def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"


def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"


def test_too_high_tells_player_to_go_lower():
    # Regression for the swapped hints: a high guess must say "LOWER"
    _, message = check_guess(60, 50)
    assert "LOWER" in message


def test_too_low_tells_player_to_go_higher():
    # Regression for the swapped hints: a low guess must say "HIGHER"
    _, message = check_guess(40, 50)
    assert "HIGHER" in message


def test_numeric_not_text_comparison():
    # 9 vs 21 compared as text ("9" > "21") used to say Too High
    outcome, _ = check_guess(9, 21)
    assert outcome == "Too Low"


def test_new_game_state_resets_everything():
    # After a win, New Game must put status/score/history back to a fresh game
    state = new_game_state(1, 100)
    assert state["status"] == "playing"
    assert state["score"] == 0
    assert state["history"] == []
    assert state["attempts"] == 0
    assert state["rounds"] == []


def test_new_game_secret_stays_in_difficulty_range():
    # Hard is 1-50, the old code drew from 1-100 and gave secrets like 85
    for _ in range(500):
        assert 1 <= new_game_state(1, 50)["secret"] <= 50
        assert 1 <= new_game_state(1, 20)["secret"] <= 20


# ---- Challenge 1: edge-case inputs for parse_guess ----

@pytest.mark.parametrize("raw", ["-5", "0", "-100", "101", "1000"])
def test_out_of_range_numbers_are_rejected(raw):
    # Edge case 1: negatives, zero and numbers past the range
    ok, value, err = parse_guess(raw, 1, 100)
    assert ok is False
    assert value is None
    assert "between 1 and 100" in err


@pytest.mark.parametrize("raw", ["3.9", "50.0", "1e3", "0.5", "-2.5"])
def test_decimals_are_rejected_not_truncated(raw):
    # Edge case 2: "3.9" used to be silently turned into 3
    ok, value, err = parse_guess(raw, 1, 100)
    assert ok is False
    assert value is None
    assert "whole number" in err


@pytest.mark.parametrize(
    "raw",
    [
        pytest.param("99999999999999999999", id="20-digit-number"),
        pytest.param("9" * 5000, id="5000-digit-number"),
    ],
)
def test_extremely_large_values_are_rejected(raw):
    # Edge case 3: huge numbers must give an error, not crash or pass
    ok, value, err = parse_guess(raw, 1, 100)
    assert ok is False
    assert value is None
    assert "between 1 and 100" in err


@pytest.mark.parametrize("raw", [None, "", "   "])
def test_empty_input_asks_for_a_guess(raw):
    ok, value, err = parse_guess(raw, 1, 100)
    assert ok is False
    assert err == "Enter a guess."


@pytest.mark.parametrize("raw", ["abc", "inf", "nan", "12abc", "1_0"])
def test_non_numbers_are_rejected(raw):
    ok, value, err = parse_guess(raw, 1, 100)
    assert ok is False
    assert err == "That is not a number."


@pytest.mark.parametrize(
    "raw, expected", [("1", 1), ("100", 100), (" 42 ", 42), ("+7", 7)]
)
def test_valid_guesses_still_parse(raw, expected):
    ok, value, err = parse_guess(raw, 1, 100)
    assert ok is True
    assert value == expected
    assert err is None


def test_range_follows_difficulty():
    # 60 is fine on Normal (1-100) but out of range on Hard (1-50)
    assert parse_guess("60", 1, 100)[0] is True
    assert parse_guess("60", 1, 50)[0] is False


# ---- Challenge 2: scoring and the High Score file ----

@pytest.mark.parametrize("outcome", ["Too High", "Too Low"])
@pytest.mark.parametrize("attempt", [1, 2, 3, 4])
def test_wrong_guesses_always_cost_points(outcome, attempt):
    # Too High on an even attempt used to ADD 5 points
    assert update_score(0, outcome, attempt) == -5


def test_win_adds_points():
    assert update_score(0, "Win", 1) == 80


def test_load_high_score_missing_file(tmp_path):
    assert load_high_score(tmp_path / "nope.json") == 0


def test_load_high_score_corrupt_file(tmp_path):
    bad = tmp_path / "high_score.json"
    bad.write_text("{not json", encoding="utf-8")
    assert load_high_score(bad) == 0


def test_save_high_score_keeps_the_best(tmp_path):
    path = tmp_path / "high_score.json"
    assert save_high_score(50, path) == 50
    assert save_high_score(30, path) == 50   # lower score doesn't overwrite
    assert load_high_score(path) == 50
    assert save_high_score(80, path) == 80   # higher score replaces it
    assert load_high_score(path) == 80


# ---- Challenge 4: hot/cold helper ----

@pytest.mark.parametrize("guess, label", [
    (50, "Hot"),    # exact
    (54, "Hot"),    # 4% away
    (60, "Warm"),   # 10% away
    (69, "Warm"),   # 19 of a 99-wide span, just under the 20% edge
    (90, "Cold"),   # 40% away
    (1, "Cold"),
])
def test_temperature_bands(guess, label):
    assert get_temperature(guess, 50, 1, 100)[0] == label


def test_temperature_handles_tiny_range():
    assert get_temperature(5, 5, 5, 5)[0] == "Hot"
