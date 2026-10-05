import random
from pathlib import Path

import streamlit as st

from logic_utils import (
    check_guess,
    get_range_for_difficulty,
    load_high_score,
    new_game_state,
    parse_guess,
    save_high_score,
    update_score,
)

HIGH_SCORE_FILE = Path(__file__).parent / "high_score.json"

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

# Challenge 2: High Score tracker saved to high_score.json
previous_best = load_high_score(HIGH_SCORE_FILE)
best_score_slot = st.sidebar.empty()
best_score_slot.metric("🏆 Best score", previous_best)

# Guesses are now validated against the current range, so switching difficulty
# has to start a fresh game or an old secret could end up outside the range.
if st.session_state.get("difficulty") != difficulty:
    for key, value in new_game_state(low, high).items():
        st.session_state[key] = value
    st.session_state.difficulty = difficulty

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

st.subheader("Make a guess")

st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

# FIX: New Game now resets attempts, score, status and history, and draws the
# secret from the current difficulty range (was a hard-coded 1-100). Used
# Claude Code to move the reset into logic_utils.new_game_state.
if new_game:
    for key, value in new_game_state(low, high).items():
        st.session_state[key] = value
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    ok, guess_int, err = parse_guess(raw_guess, low, high)

    if not ok:
        # FIX: Invalid input no longer uses up an attempt (the counter used to
        # go up before parsing). Worked this out with Claude Code.
        st.error(err)
    else:
        st.session_state.attempts += 1
        st.session_state.history.append(guess_int)

        # FIX: Removed the even-attempt str(secret) cast so the guess and the
        # secret are always compared as ints. Found by asking Claude Code to
        # explain the odd hints, then confirmed in the live game.
        outcome, message = check_guess(guess_int, st.session_state.secret)

        if show_hint:
            st.warning(message)

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
            new_best = save_high_score(st.session_state.score, HIGH_SCORE_FILE)
            best_score_slot.metric("🏆 Best score", new_best)
            if st.session_state.score > previous_best:
                st.success("🏆 New high score!")
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
