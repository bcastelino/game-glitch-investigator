# AI Interactions Log

> **Stretch features only.** This file covers the stretch challenges I completed (1: edge-case testing, 2: feature expansion, 3: docstrings and linting). The AI tool was Claude Code in VS Code.

---

## Agent Workflow (SF8) — Challenge 2: High Score tracker

**What task did you give the agent?**

> "Plan and implement a meaningful new feature, like a High Score tracker that saves my best score to a file. Do it in small steps, keep the game rules in `logic_utils.py`, and add tests."

**What did the agent do?**

Files modified: `logic_utils.py`, `app.py`, `tests/test_game_logic.py`, `.gitignore`.

1. Added `load_high_score(path)` and `save_high_score(score, path)` to `logic_utils.py`. They store `{"best": <int>}` as JSON, return 0 when the file is missing or corrupt, and only write when the new score beats the old one.
2. Changed `update_score` so every wrong guess costs 5 points. The old code gave +5 for "Too High" on even attempts, which would have let a player farm a high score by guessing wrong.
3. In `app.py`, loaded the best score into the sidebar (`st.sidebar.empty()` placeholder with `st.metric`) and, on a win, saved the score, updated the metric and showed "🏆 New high score!" when it beat the previous best.
4. Added `high_score.json` to `.gitignore` so a local score file never gets committed.
5. Wrote pytest cases with `tmp_path` (missing file, corrupt file, lower score doesn't overwrite, higher score does, wrong guesses always cost 5, a win adds points).
6. Committed it on its own: `feat: add persistent high score tracker`.

**What did you have to verify or fix manually?**

- I ran the real game in a browser: a win with score 50 showed "New high score!", and the sidebar still said 50 after reloading the page. A second win with 80 replaced it.
- The sidebar metric has to be updated *after* the win is scored because Streamlit draws the page top to bottom, so I used a placeholder (`st.empty()`) instead of a plain `st.metric`.
- The live browser check showed that the "Attempts left" banner lagged one guess behind (it was drawn before the guess was scored). None of the unit tests could catch that because it only shows up in the running UI, so the fix was to redraw the banner after scoring (`fix: refresh attempts-left banner after each guess`).
- Challenge 1 made `parse_guess` check the range, so a secret picked on Normal could be unwinnable after switching to Hard. I had the game start a new game whenever the difficulty changes and checked it by switching difficulty in the browser.

---

## Test Generation (SF7) — Challenge 1: Advanced Edge-Case Testing

> I used the AI to find edge-case inputs that might still break the game and to generate a pytest suite for them.

**Prompt used:**

```
Look at parse_guess in logic_utils.py. Identify three edge-case inputs that might
still break my game (for example negative numbers, decimals, or extremely large
values) and generate a suite of pytest cases that verify the game handles them
gracefully. Keep the tests simple and parametrized.
```

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| Negative numbers, zero and numbers past the range (`-5`, `0`, `101`, `1000`) | The prompt above | `test_out_of_range_numbers_are_rejected` (parametrized) | Passes with the new range check in `parse_guess` (the original code accepted all of these) | A guess outside the range can never be the answer and used to waste an attempt, so it should be rejected with a clear message. |
| Decimals (`3.9`, `50.0`, `1e3`, `0.5`, `-2.5`) | The prompt above | `test_decimals_are_rejected_not_truncated` | Passes with the new check | The old code turned `3.9` into `3` silently, so the player guessed something they never typed. |
| Extremely large values (`99999999999999999999` and a 5000-digit number) | The prompt above | `test_extremely_large_values_are_rejected` | Passes with the new check | Huge numbers must give an error instead of crashing (Python refuses to convert very long digit strings to an int). |
| Empty, `None` and whitespace-only input | The prompt above | `test_empty_input_asks_for_a_guess` | Passes | Empty input should ask for a guess without using an attempt. |
| Not numbers (`abc`, `inf`, `nan`, `12abc`, `1_0`) | The prompt above | `test_non_numbers_are_rejected` | **First run: failed on `1_0`**, fixed in `parse_guess`, then passes | `float("1_0")` works in Python, so my parser called it a decimal. Good reminder to test, not assume. |
| Valid guesses still work (`1`, `100`, ` 42 `, `+7`) | The prompt above | `test_valid_guesses_still_parse` | Passes | Makes sure the stricter parser didn't break normal play. |

**One-line reason for each of the three main edge cases:**

- **Negative / out-of-range numbers:** they look like numbers but can never be correct, and they used to cost an attempt.
- **Decimals:** `3.9` was silently changed to `3`, hiding what the player really typed.
- **Extremely large values:** a very long number is a classic way to overflow or crash a parser.

---

## Linting & Style (SF9) — Challenge 3

**Prompt used:**

```
Add professional-grade docstrings to every function in logic_utils.py (Google
style, with Args and Returns). Then review my code for PEP 8 style compliance
using flake8 and apply your suggestions to fix any formatting or naming issues.
```

**Linting output before:**

Command: `python -m flake8 app.py logic_utils.py tests/` (flake8 7.4.1, default 79 character limit)

```
app.py:27:80: E501 line too long (81 > 79 characters)
logic_utils.py:36:80: E501 line too long (80 > 79 characters)
logic_utils.py:93:80: E501 line too long (80 > 79 characters)
logic_utils.py:108:80: E501 line too long (81 > 79 characters)
logic_utils.py:131:80: E501 line too long (81 > 79 characters)
tests/test_game_logic.py:110:80: E501 line too long (92 > 79 characters)
```

**Linting output after:**

```
$ python -m flake8 app.py logic_utils.py tests/
$ echo $?
0
```

**Changes applied:**

Suggested by the AI and applied:

- Added a module docstring and Google-style docstrings (Args / Returns) with type hints to every function in `logic_utils.py`. I also expanded the docstring of the `render_summary` helper in `app.py`.
- Wrapped the six lines flagged as E501 (a long dict literal in `app.py`, a comment and docstring in `logic_utils.py`, and a long `parametrize` line in the tests).
- Renamed the one-letter loop variable `r` in `render_summary` to `entry` so it reads better.
- Added `from __future__ import annotations` so the `int | None` type hints also work on older Python versions.

Suggested but not applied:

- Renaming the file handle `f` in the high score functions. It is the standard Python idiom for a short `with open(...) as f` block, so I left it.

After the style commit I re-ran `pytest` (52 passed) and a quick check of the app to make sure nothing changed in behaviour.
