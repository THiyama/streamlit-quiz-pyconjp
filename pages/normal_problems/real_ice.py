import streamlit as st
from snowflake.snowpark import Session

from utils.utils import save_table, init_state, clear_submit_button
from utils.attempt_limiter import check_is_failed, init_attempt, process_exceeded_limit
from utils.designs import header_animation, display_problem_statement

MAX_ATTEMPTS_MAIN = 3


def present_quiz(tab_name: str, max_attempts: int) -> str:
    header_animation()
    st.header("リアル課題", divider="rainbow")

    display_problem_statement("""
                              <i>“Icebergがデータレイクの在り方を一変させる様子は、残暑を払う削り氷のように爽快。
                              好みの蜜で楽しめるしね。”———氷の賢者、ショーゴ</i><br />
                              <br />
                              かき氷エリアの課題をクリアし呪文を入手するのだ！
                              """)
    st.write(f"回答回数の上限は {max_attempts}回です。")
    answer = st.text_input("Your answer:", key=f"{tab_name}_answer")

    return answer


def process_answer(answer: str, state, session: Session) -> None:
    correct_answer = "Iceberg"
    if answer.lower() == correct_answer.lower():
        state["is_clear"] = True
        st.success("クイズに正解しました")
    else:
        state["is_clear"] = False
        st.error("不正解です")

    save_table(state, session)


def run(tab_name: str, session: Session):
    state = init_state(tab_name, session, MAX_ATTEMPTS_MAIN)
    main_attempt = init_attempt(
        max_attempts=MAX_ATTEMPTS_MAIN, tab_name=tab_name, session=session, key="main"
    )

    answer = present_quiz(tab_name, MAX_ATTEMPTS_MAIN)  # ★

    placeholder = st.empty()
    if check_is_failed(session, state):
        process_exceeded_limit(placeholder, state)
    elif placeholder.button("submit", key=f"{tab_name}_submit"):
        if main_attempt.check_attempt():
            if answer:
                process_answer(answer, state, session)  # ★
            else:
                st.warning("選択してください")

        else:
            process_exceeded_limit(placeholder, state)

    clear_submit_button(placeholder, state)
