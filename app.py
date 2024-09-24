import streamlit as st
import snowflake.snowpark.functions as F
from snowflake.snowpark import Session

from utils.utils import (
    create_session,
    display_team_id_sidebar,
    display_page_titles_sidebar,
    TEAMS,
)
from utils.designs import (
    apply_default_custom_css,
    display_applied_message,
    background_image,
)


@st.dialog("ユーザー名の確認")
def show_duplicate_username_dialog(team_id: str) -> None:
    st.write("ユーザー名がすでに登録されているようです。")
    st.write("このまま続けますか？")
    st.session_state.is_ignoring_duplicates = False

    col1, col2 = st.columns(2)
    if col1.button("はい"):
        st.session_state.is_ignoring_duplicates = True
        st.rerun()

    if col2.button("いいえ"):
        st.session_state.is_ignoring_duplicates = False
        st.rerun()


def confirm_duplicate_username() -> None:
    st.session_state.is_submitted_main_page = True

    session = st.session_state.snow_session
    team_id = st.session_state.team_id

    is_duplicated = session.table("Submit2").filter(F.col("TEAM_ID") == team_id).count()

    if is_duplicated:
        show_duplicate_username_dialog(team_id)
    else:
        if "is_ignoring_duplicates" in st.session_state:
            del st.session_state.is_ignoring_duplicates


st.title("Streamlit クイズへようこそ！")

css_name = apply_default_custom_css()
message = f"""
    PyCon JP の Streamlit ブースに遊びに来ていただきありがとうございます！
    このアプリでは、Streamlit に関する3つのクイズに挑戦します。

    クイズにクリアして、**ステッカーやノベルティ** をゲットしましょう！
    
    Streamlit の機能や使い方を学び、理解する絶好のチャンスです！
    <br>

    **さあ、クイズに挑戦しましょう！**
    """

display_page_titles_sidebar()
display_team_id_sidebar()
display_applied_message(message, css_name)
background_image("pages/common/images/background1.jpg", dark_mode=False)

st.write("")

team_id = st.text_input(label="ユーザー名を入力してください。")

st.session_state.snow_session = snow_session = create_session(TEAMS["Account Admin"])
st.session_state.team_id = team_id

if "is_submitted_main_page" not in st.session_state:
    st.session_state.is_submitted_main_page = False

st.button("挑戦を開始する", on_click=confirm_duplicate_username)

if st.session_state.is_submitted_main_page:
    if team_id == "":
        st.error("ユーザー名を入力してみましょう！")
    else:
        if "is_ignoring_duplicates" not in st.session_state:
            st.session_state.is_submitted_main_page = False
            st.switch_page("pages/01_normal_problems.py")
        elif st.session_state.is_ignoring_duplicates:
            st.session_state.is_submitted_main_page = False
            st.switch_page("pages/01_normal_problems.py")
