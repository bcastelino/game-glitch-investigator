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

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
