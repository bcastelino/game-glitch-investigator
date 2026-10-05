from logic_utils import check_guess


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
