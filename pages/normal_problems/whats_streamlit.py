import streamlit as st
from snowflake.snowpark import Session

from utils.utils import save_table, init_state, clear_submit_button, string_to_hash_int
from utils.designs import header_animation, display_problem_statement
from utils.attempt_limiter import check_is_failed, init_attempt, process_exceeded_limit

MAX_ATTEMPTS_MAIN = 1000

def present_quiz(tab_name: str, max_attempts: int) -> str:
    answer_option = [
                     "機械学習に用いるもの",
                     "データを可視化する際に用いるもの",
                     "インタラクティブなWebアプリを作るもの",
                     "大規模データベースを管理するもの"
                     ]
    header_animation()
    display_problem_statement(f"""
                              <div>
                                <p style="font-weight:bold; font-size: 24px; margin-bottom: 5px;">Streamlitは何のためのフレームワークでしょうか？</p>
                                <p>※最も適切な選択肢を選んでください。</p>
                                <ol style="margin-top: 20px; color:#333; font-size: 18px; font-weight:bold;">
                                    <li style="margin: 7px 0 0 20px;">{answer_option[0]}</li>
                                    <li style="margin: 7px 0 0 20px;">{answer_option[1]}</li>
                                    <li style="margin: 7px 0 0 20px;">{answer_option[2]}</li>
                                    <li style="margin: 7px 0 0 20px;">{answer_option[3]}</li>
                                </ol>
                              </div>
                              """)
    st.html("""<p style="font-weight:bold; font-size: 24px; margin-bottom: 0;">Your answer:</p>""")
    answer = st.radio("", answer_option, index=None)
    return answer

def process_answer(answer: str, state, session: Session) -> None:
    correct_answer = "PythonでインタラクティブなWebアプリを作るもの"
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
