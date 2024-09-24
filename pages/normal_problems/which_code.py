import streamlit as st
from snowflake.snowpark import Session
import pandas as pd
from datetime import date

from utils.utils import save_table, init_state, clear_submit_button, string_to_hash_int
from utils.designs import header_animation, display_problem_statement
from utils.attempt_limiter import check_is_failed, init_attempt, process_exceeded_limit

MAX_ATTEMPTS_MAIN = 1000


def present_quiz(tab_name: str, max_attempts: int) -> str:
    # データ読み込み
    chart_data = pd.read_csv("pages/common/data/tokyo_temperature.tsv", sep="\t")
    chart_data["日付"] = pd.to_datetime(chart_data["日付"])
    chart_data = chart_data.set_index("日付")

    header_animation()
    # 設問表示
    display_problem_statement(
        f"""<p style="font-weight:bold; font-size: 24px; margin-bottom: 0;">下記の画面を実現するソースコードはどれでしょうか？</p>"""
    )
    with st.container(border=True):
        st.header("🌞東京の最高気温推移🌞")
        date_range = st.date_input(
            "表示期間",
            value=(date(2024, 4, 1), date(2024, 8, 31)),
            min_value=date(2024, 1, 1),
            max_value=date(2024, 9, 30),
            format="YYYY/MM/DD",
        )
        try:
            st.line_chart(
                chart_data[date_range[0] : date_range[1]], use_container_width=True
            )
        except:
            st.error("日付を指定してください。")
    # 回答選択肢表示(No.1~No.3)
    # No.1
    st.html(
        """<p style="font-weight:bold; font-size: 20px; margin-bottom: 0;">No.1</p>"""
    )
    st.code(
        """
        st.header('🌞東京都の最高気温推移🌞')
        date_range = st.number_input('表示期間')
        st.line_chart(chart_data[date_range[0] : date_range[1]])
            """
    )
    with st.expander("ヒント：「st.number_input」"):
        st.number_input("「st.number_input」の実装例です。")
    # No.2
    st.html(
        """<p style="font-weight:bold; font-size: 20px; margin-bottom: 0;">No.2</p>"""
    )
    st.code(
        """
        st.header('🌞東京都の最高気温推移🌞')
        date_range = st.slider(
            "表示期間", 
            value=(date(2024, 4, 1), date(2024, 8, 31)),
            min_value=date(2024, 1, 1),
            max_value=date(2024, 9, 30)
            )
        st.line_chart(chart_data[date_range[0] : date_range[1]])
            """
    )
    with st.expander("ヒント：「st.slider」"):
        st.slider(
            "「st.slider」の実装例です。", value=(40, 60), min_value=0, max_value=100
        )
    # No.3
    st.html(
        """<p style="font-weight:bold; font-size: 20px; margin-bottom: 0;">No.3</p>"""
    )
    st.code(
        """
        st.header('🌞東京都の最高気温推移🌞')
        date_range = st.date_input(
            "表示期間",
            value=(date(2024, 4, 1), date(2024, 8, 31)),
            min_value=date(2024, 1, 1),
            max_value=date(2024, 9, 30),
            format="YYYY/MM/DD",
        )
        st.line_chart(chart_data[date_range[0] : date_range[1]])
            """
    )
    with st.expander("ヒント：「st.date_input」"):
        st.date_input(
            "「st.date_input」の実装例です。",
            value=(date(2024, 8, 10), date(2024, 8, 15)),
            min_value=date(2024, 8, 1),
            max_value=date(2024, 8, 31),
            format="YYYY/MM/DD",
        )
    # 回答
    st.html(
        """<p style="font-weight:bold; font-size: 24px; margin-bottom: 0;">Your answer:</p>"""
    )
    answer = st.radio(
        "",
        ["No.1: st.number_input", "No.2: st.slider", "No.3: st.date_input"],
        index=None,
    )
    return answer


def process_answer(answer: str, state, session: Session) -> None:
    correct_answer = "No.3"
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
