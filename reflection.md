# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

**What the game looked like on first run.** I ran `python -m streamlit run app.py` and drove it in a browser with the Playwright MCP, over two sessions: Normal difficulty, then Hard. The page loaded with no crash and no console errors. Right away the banner read "Attempts left: 7" even though the sidebar said "Attempts allowed: 8". Playing from there turned up the bugs below. All of them were reproduced live, using the "Developer Debug Info" panel to read the secret.

**Bugs found**

1. **Hints are backwards.** With secret 21, guessing 80 showed "Go HIGHER!" and guessing 9 showed "Go LOWER!". The outcome labels ("Too High" / "Too Low") are right but the messages are swapped. Cause: `check_guess`, [app.py:37-40](app.py#L37-L40).
2. **Hints and score behave differently on even attempts.** On even attempts `app.py` converts the secret to a string, so the comparison becomes a text comparison (`"5" > "21"`). With secret 21, guessing 5 on attempt 4 was labelled "Too High" even though 5 is below 21, and the score went up from -5 to 0 for a wrong guess. Causes: [app.py:158-163](app.py#L158-L163), the `TypeError` fallback in `check_guess` at [app.py:41-47](app.py#L41-L47), and `update_score` at [app.py:57-60](app.py#L57-L60).
3. **Attempt counter is off by one, and bad input costs an attempt.** The counter starts at 1, so a fresh Normal game shows 7 attempts left instead of 8. New Game resets it to 0, so the same screen then shows 8. Submitting an empty guess showed "Enter a guess." but still used an attempt and added `""` to history. Causes: [app.py:96](app.py#L96), [app.py:111](app.py#L111), [app.py:135](app.py#L135), and `attempts += 1` running before `parse_guess` at [app.py:148](app.py#L148).
4. **New Game doesn't restart a finished game.** After winning, clicking New Game still showed "You already won. Start a new game to play again." and play stayed blocked. The old score (25) and history were also kept. Cause: the New Game block only resets `attempts` and `secret`, not `status`, `score` or `history`, [app.py:134-138](app.py#L134-L138), so `st.stop()` at [app.py:140-145](app.py#L140-L145) fires.
5. **New Game ignores the difficulty range, and the banner is hard-coded.** On Hard (sidebar: "Range: 1 to 50") eight New Game clicks gave secrets of 85, 37, 25, 36, 7, 28, 5 and 20, so 85 is out of range. The banner also still said "Guess a number between 1 and 100". Hard (1-50) is easier than Normal (1-100). Causes: `random.randint(1, 100)` at [app.py:136](app.py#L136), the hard-coded text at [app.py:110](app.py#L110), and the ranges at [app.py:5-10](app.py#L5-L10).

**Bug Reproduction Log**

| Input Used | Expected Behavior | Actual Behavior | Console Error / Output | Suspected Code Location |
|------------|-------------------|-----------------|------------------------|-------------------------|
| Normal, secret 21, guess **80** (attempt 3) | "Too High" with the hint "Go LOWER!" | Shows "Go HIGHER!". Guess **9** shows "Go LOWER!" | none | `check_guess`, app.py:37-40 |
| Normal, secret 21, guess **5** on an even attempt (attempt 4) | "Too Low", and the score drops | Labelled "Too High", and the score goes from -5 to 0 (+5 for a wrong guess) | none | app.py:158-163 (secret cast to `str`), `check_guess` fallback at app.py:41-47, `update_score` at app.py:57-60 |
| Fresh load on Normal, no guess yet | "Attempts left: 8" | "Attempts left: 7" | none | `attempts` starts at 1, app.py:96 and app.py:111 |
| Click Submit with an empty guess box | Error shown and no attempt used | "Enter a guess." is shown, but an attempt is used and `""` is added to history | none | `attempts += 1` before parsing, app.py:148 |
| Win with guess **21** (secret 21), then click **New Game** | A fresh game that accepts guesses | "You already won. Start a new game to play again." Score stays 25 and history is kept | none | New Game block, app.py:134-138, with `st.stop()` at app.py:140-145 |
| Difficulty **Hard** (1-50), click **New Game** 8 times | Every secret between 1 and 50 | Secrets: 85, 37, 25, 36, 7, 28, 5, 20, and the banner still says "1 and 100" | none | `random.randint(1, 100)` at app.py:136, banner at app.py:110, ranges at app.py:5-10 |

---

## 2. How did you use AI as a teammate?

**Which AI tools I used.** I used Claude Code in VS Code, mostly as something to talk the bugs through with. I'd ask it why something in `app.py` might be acting weird and what a fix could look like, then go check the code myself. The Playwright MCP was the one thing that did hands-on work, because it opened the browser and clicked through the game for me, which the assignment asked for. I didn't hand it the whole assignment, though. I still read the code, decided which bugs counted, and wrote up what they meant.

**A suggestion that was correct.** When I asked about the hints acting strange, Claude pointed at `check_guess` and said the "Too High" / "Too Low" messages were swapped, so a guess that's too high tells you "Go HIGHER!". It also said that on even attempts `app.py` turns the secret into a string, which makes the comparison unreliable. I didn't just trust that. I played it with secret 21: guessing 80 gave "Go HIGHER!" and guessing 9 gave "Go LOWER!". On an even attempt, guessing 5 got labelled "Too High" and my score went up from -5 to 0 for a wrong guess. That matched what Claude said, so I knew the explanation held up.

**A suggestion I didn't accept as written.** Claude's first read of the code came back with a long list of suspects, like decimals getting cut off in `parse_guess`, the score not resetting, and the tests not matching what `check_guess` returns. I didn't paste that whole list into my bug log. Some of it was just a guess from reading the code, and I hadn't seen any of it happen in the game. I only kept the bugs I could reproduce myself, and I checked each one against the debug panel (secret, attempts, score). So the log has five bugs I actually saw break, and the rest of the list can wait until I'm fixing things.

**Phase 2 update (fixing the bugs).** For the repair I picked the backwards hints and the New Game bug, and used Claude Code to refactor the logic into `logic_utils.py` and make the edits. One suggestion I did *not* take as written was about the starter tests. They compare `check_guess(...)` to a bare string like `"Too High"`, and Claude gave me two ways to make them pass: return only the outcome string, or leave the function alone and change the tests to unpack the `(outcome, message)` tuple. Returning only the outcome would have made the old tests pass, but it would have broken the function's documented contract and forced the hint text to move into `app.py`. I picked the second option and checked it by running pytest (green) and replaying the hints in the live game. A suggestion that was correct and I kept: when I made `parse_guess` check the difficulty range, Claude pointed out that switching difficulty mid-game could leave a secret outside the new range (a Normal secret of 85 would be unwinnable on Hard), so the game should start fresh when the difficulty changes. I added that and tested it by switching to Hard in the browser.

---

## 3. Debugging and testing your fixes

**How I decided a bug was really fixed.** For me a bug counts as fixed only if I can't make it happen anymore in the live game *and* a pytest case fails without the fix. I took the exact inputs from my bug table and ran them again in the browser. With secret 61, guessing 1 now shows "Go HIGHER!" (it used to tell me the opposite), and guessing 58 shows "Go HIGHER! 🔥 Hot". After winning I clicked New Game and the game really restarted: attempts 0, score 0, empty history, and the old summary table was gone. I also clicked New Game 10 times on Hard and every secret was between 1 and 50 (the old code gave me 85 once).

**A test I ran and what it showed me.** My favourite is `test_numeric_not_text_comparison`, which checks that guessing 9 against a secret of 21 is "Too Low". It is simple, but it is the exact case where the old code compared `"9" > "21"` as text and got the wrong answer. When I wrote the edge-case tests, one of them failed and showed me something I hadn't thought about: Python's `float("1_0")` quietly works, so my parser called "1_0" a decimal instead of "not a number". Another failure was my own mistake: I wrote a Hot/Warm boundary test as if the range was 100 wide, but 1 to 100 is a span of 99, so the code was right and my test was wrong. I fixed the test, not the code. All 52 tests pass now and `flake8` reports nothing (the full output is in the README and `ai_interactions.md`).

**Did AI help with tests?** Yes. I asked Claude Code what edge-case inputs could still break the game and it suggested negative/out-of-range numbers, decimals and extremely large values. I asked it to turn those into parametrized pytest cases, then I ran the whole suite and replayed the same inputs in the live game instead of just trusting that they passed. It also explained why the starter tests were failing: they compared the result of `check_guess` to a plain string, but the function returns an `(outcome, message)` tuple. Still not fixed on purpose (to keep this small): Hard (1-50) is easier than Normal (1-100), and the win formula still has a `+1` in it.

---

## 4. What did you learn about Streamlit and state?

**Explaining it to a friend.** Streamlit re-runs your whole Python file from top to bottom every time you click a button or type something. That means normal variables get thrown away on every click, so anything you need to remember, like the secret number, the score and the attempts, has to live in `st.session_state`, which survives between reruns. I hit a good example of this myself: the "Attempts left" banner was always one guess behind. The banner was drawn near the top of the file, *before* the code lower down that handles the Submit click had updated the counter. I fixed it by drawing the banner into an `st.empty()` placeholder and redrawing it after the guess was scored. Streamlit's rerun model also means the order of lines in the file is the order things show up on the page.

---

## 5. Looking ahead: your developer habits

**A habit I want to keep.** I'll reproduce a bug myself before I let AI explain it, and I'll commit after every finished step. I made a separate commit for each fix, each challenge and the docs, so my history reads like a story and I could undo one piece without losing the rest. Marking the problem with a `# FIXME` comment first also helped me because I could point the AI at an exact spot instead of saying "the hints are wrong somewhere".

**What I'd do differently next time.** I'd be more specific in my prompts and ask for smaller changes. Some of the AI's work grew past what I asked for, like adding things the challenges needed, so I'd say up front "only touch this function" and then read the whole diff line by line. I'd also run the linter much earlier instead of at the end, because it would have been easier to keep the code tidy as I went.

**How my view of AI-generated code changed.** The starter code said it was "production-ready" and still had hints that lie, a secret that changed type, and a New Game button that didn't restart anything. It reads cleanly, so it's easy to trust, but it can still be wrong. Now I treat AI code like a first draft from a teammate: useful and fast, but I check it with tests and by actually playing the game.
