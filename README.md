# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [x] **The game's purpose.** Glitchy Guesser is a Streamlit number guessing game. You pick a difficulty (Easy 1-20, Normal 1-100, Hard 1-50), guess the secret number before you run out of attempts, and get hints and a score. The starter version was written by an AI and hid several bugs that this project finds and repairs.
- [x] **Bugs I found** (reproduced in the live game with the Playwright MCP, full table in `reflection.md`):
  1. The hints were backwards: a guess that was too high said "Go HIGHER!".
  2. On even attempts the secret was turned into a string, so the comparison was text-based (`"9" > "21"`), and wrong guesses could even raise the score.
  3. "Attempts left" started one too low (7 instead of 8), and invalid input still used up an attempt.
  4. New Game did not restart a finished game (status, score and history were kept).
  5. New Game ignored the difficulty (a Hard game could get a secret of 85) and the banner always said "1 and 100".
- [x] **Fixes I applied** (built with Claude Code, one commit per step):
  - Moved the game rules into `logic_utils.py` and fixed `check_guess` so a high guess says "Go LOWER!" and a low guess says "Go HIGHER!", always comparing ints.
  - Added `new_game_state()` so New Game resets attempts, score, status, history and draws the secret from the current difficulty range. Changing difficulty also starts a fresh game.
  - Hardened `parse_guess()` (Challenge 1), added a saved High Score (Challenge 2), docstrings and a clean `flake8` run (Challenge 3) and a nicer UI (Challenge 4). Wrong guesses now always cost 5 points, and the attempts banner no longer lags one guess behind.
  - Still not changed: Hard (1-50) is easier than Normal (1-100), and the win formula has a `+1` in it.

## 📸 Demo Walkthrough

A sample game on **Normal** difficulty with the secret number 61 (shown in the "Developer Debug Info" panel):

1. The page opens with "Guess a number between 1 and 100. Attempts left: 8" and the sidebar shows "🏆 Best score 0".
2. The player types `3.9` and clicks Submit. The game says "Enter a whole number (no decimals)." and the attempts left stay the same. `-5` and `99999999999999999999` give "Enter a number between 1 and 100." instead.
3. The player guesses `1`. The game shows a blue hint "📈 Go HIGHER! ❄️ Cold", the score drops to -5 and "Attempts left" goes to 7.
4. The player guesses `58`. The hint is "📈 Go HIGHER! 🔥 Hot", the score is -10 and the table in "Session summary" now has two rows.
5. The player guesses `61`. The game shows "🎉 Correct! 🔥 Hot", "You won! The secret was 61. Final score: 50" and "🏆 New high score!". The sidebar's Best score becomes 50, and it is still 50 after reloading the page.
6. In another game with the secret 30, guessing `90` shows a red hint "📉 Go LOWER! ❄️ Cold" (Too High) and costs 5 points.
7. Clicking **New Game** after a win starts a fresh game: attempts 0, score 0, empty history, no summary table, and a new secret from the current difficulty range (on Hard it is always between 1 and 50).

Session summary table after step 5:

| Attempt | Guess | Score | Result | Temperature |
|---------|-------|-------|--------|-------------|
| 1 | 1 | -5 | Too Low | ❄️ Cold |
| 2 | 58 | -10 | Too Low | 🔥 Hot |
| 3 | 61 | 50 | Win | 🔥 Hot |

**Screenshot** *(optional)*: not included, the walkthrough above is a text record of what the game shows.

## 🧪 Test Results

`python -m pytest -v` (52 tests, including the three starter tests and the Challenge 1 edge-case suite):

```
============================= test session starts =============================
platform win32 -- Python 3.11.6, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\brian\AppData\Local\Programs\Python\Python311\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\brian\Projects\codepath\AI110-3\game-glitch-investigator
plugins: anyio-4.15.1
collecting ... collected 52 items

tests/test_game_logic.py::test_winning_guess PASSED                      [  1%]
tests/test_game_logic.py::test_guess_too_high PASSED                     [  3%]
tests/test_game_logic.py::test_guess_too_low PASSED                      [  5%]
tests/test_game_logic.py::test_too_high_tells_player_to_go_lower PASSED  [  7%]
tests/test_game_logic.py::test_too_low_tells_player_to_go_higher PASSED  [  9%]
tests/test_game_logic.py::test_numeric_not_text_comparison PASSED        [ 11%]
tests/test_game_logic.py::test_new_game_state_resets_everything PASSED   [ 13%]
tests/test_game_logic.py::test_new_game_secret_stays_in_difficulty_range PASSED [ 15%]
tests/test_game_logic.py::test_out_of_range_numbers_are_rejected[-5] PASSED [ 17%]
tests/test_game_logic.py::test_out_of_range_numbers_are_rejected[0] PASSED [ 19%]
tests/test_game_logic.py::test_out_of_range_numbers_are_rejected[-100] PASSED [ 21%]
tests/test_game_logic.py::test_out_of_range_numbers_are_rejected[101] PASSED [ 23%]
tests/test_game_logic.py::test_out_of_range_numbers_are_rejected[1000] PASSED [ 25%]
tests/test_game_logic.py::test_decimals_are_rejected_not_truncated[3.9] PASSED [ 26%]
tests/test_game_logic.py::test_decimals_are_rejected_not_truncated[50.0] PASSED [ 28%]
tests/test_game_logic.py::test_decimals_are_rejected_not_truncated[1e3] PASSED [ 30%]
tests/test_game_logic.py::test_decimals_are_rejected_not_truncated[0.5] PASSED [ 32%]
tests/test_game_logic.py::test_decimals_are_rejected_not_truncated[-2.5] PASSED [ 34%]
tests/test_game_logic.py::test_extremely_large_values_are_rejected[20-digit-number] PASSED [ 36%]
tests/test_game_logic.py::test_extremely_large_values_are_rejected[5000-digit-number] PASSED [ 38%]
tests/test_game_logic.py::test_empty_input_asks_for_a_guess[None] PASSED [ 40%]
tests/test_game_logic.py::test_empty_input_asks_for_a_guess[] PASSED     [ 42%]
tests/test_game_logic.py::test_empty_input_asks_for_a_guess[   ] PASSED  [ 44%]
tests/test_game_logic.py::test_non_numbers_are_rejected[abc] PASSED      [ 46%]
tests/test_game_logic.py::test_non_numbers_are_rejected[inf] PASSED      [ 48%]
tests/test_game_logic.py::test_non_numbers_are_rejected[nan] PASSED      [ 50%]
tests/test_game_logic.py::test_non_numbers_are_rejected[12abc] PASSED    [ 51%]
tests/test_game_logic.py::test_non_numbers_are_rejected[1_0] PASSED      [ 53%]
tests/test_game_logic.py::test_valid_guesses_still_parse[1-1] PASSED     [ 55%]
tests/test_game_logic.py::test_valid_guesses_still_parse[100-100] PASSED [ 57%]
tests/test_game_logic.py::test_valid_guesses_still_parse[ 42 -42] PASSED [ 59%]
tests/test_game_logic.py::test_valid_guesses_still_parse[+7-7] PASSED    [ 61%]
tests/test_game_logic.py::test_range_follows_difficulty PASSED           [ 63%]
tests/test_game_logic.py::test_wrong_guesses_always_cost_points[1-Too High] PASSED [ 65%]
tests/test_game_logic.py::test_wrong_guesses_always_cost_points[1-Too Low] PASSED [ 67%]
tests/test_game_logic.py::test_wrong_guesses_always_cost_points[2-Too High] PASSED [ 69%]
tests/test_game_logic.py::test_wrong_guesses_always_cost_points[2-Too Low] PASSED [ 71%]
tests/test_game_logic.py::test_wrong_guesses_always_cost_points[3-Too High] PASSED [ 73%]
tests/test_game_logic.py::test_wrong_guesses_always_cost_points[3-Too Low] PASSED [ 75%]
tests/test_game_logic.py::test_wrong_guesses_always_cost_points[4-Too High] PASSED [ 76%]
tests/test_game_logic.py::test_wrong_guesses_always_cost_points[4-Too Low] PASSED [ 78%]
tests/test_game_logic.py::test_win_adds_points PASSED                    [ 80%]
tests/test_game_logic.py::test_load_high_score_missing_file PASSED       [ 82%]
tests/test_game_logic.py::test_load_high_score_corrupt_file PASSED       [ 84%]
tests/test_game_logic.py::test_save_high_score_keeps_the_best PASSED     [ 86%]
tests/test_game_logic.py::test_temperature_bands[50-Hot] PASSED          [ 88%]
tests/test_game_logic.py::test_temperature_bands[54-Hot] PASSED          [ 90%]
tests/test_game_logic.py::test_temperature_bands[60-Warm] PASSED         [ 92%]
tests/test_game_logic.py::test_temperature_bands[69-Warm] PASSED         [ 94%]
tests/test_game_logic.py::test_temperature_bands[90-Cold] PASSED         [ 96%]
tests/test_game_logic.py::test_temperature_bands[1-Cold] PASSED          [ 98%]
tests/test_game_logic.py::test_temperature_handles_tiny_range PASSED     [100%]

============================= 52 passed in 0.14s ==============================
```

`python -m flake8 app.py logic_utils.py tests/` prints nothing (clean). The before/after output is in `ai_interactions.md`.

## 🚀 Stretch Features

- [x] **Challenge 1: Advanced Edge-Case Testing.** `parse_guess()` in `logic_utils.py` now handles three risky kinds of input: negative or out-of-range numbers, decimals like `3.9` (rejected instead of silently cut to 3) and extremely large values. The parametrized tests are in `tests/test_game_logic.py` and the prompt and reasoning are in `ai_interactions.md`.
- [x] **Challenge 2: Feature Expansion.** A **High Score tracker** saved to `high_score.json` (ignored by git). `load_high_score()` and `save_high_score()` in `logic_utils.py` do the file work and `app.py` shows "🏆 Best score" in the sidebar and a "New high score!" message. The agent workflow is written up in `ai_interactions.md`.
- [x] **Challenge 3: Professional Documentation and Linting.** Every function in `logic_utils.py` has a Google-style docstring and type hints, and `flake8` is clean (the six line-length warnings were fixed). Prompts and linter output are in `ai_interactions.md`.
- [x] **Challenge 4: Enhanced Game UI.** What changed and where:
  - **Colour-coded hints** in the submit section of `app.py`: red (`st.error`) for Too High, blue (`st.info`) for Too Low and green (`st.success`) for a win.
  - **Hot/Warm/Cold emoji** from the new `get_temperature()` in `logic_utils.py`. It uses the distance as a share of the range: within 5% is 🔥 Hot, within 20% is 🌤️ Warm, further is ❄️ Cold. It is added to the end of the hint text.
  - **Session summary table** drawn by `render_summary()` in `app.py` (one row per guess: attempt, guess, score, result, temperature). It leaves out the Result and Temperature columns when "Show hint" is off so it doesn't give hints away, and it clears on New Game.
  - **Attempts banner** is now drawn by `show_banner()` into a placeholder so it updates right after each guess.
  - Core game logic is unchanged by these UI additions.
