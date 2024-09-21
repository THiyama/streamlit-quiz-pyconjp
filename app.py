import streamlit as st
from snowflake.snowpark import Session

from utils.utils import (
    create_session,
    display_team_id_sidebar,
    display_page_titles_sidebar,
    prompt_for_duplicate_username_continue,
    is_team_id_exists,
    TEAMS,
)
from utils.designs import (
    apply_default_custom_css,
    display_applied_message,
    background_image,
)


display_page_titles_sidebar()


st.title("Streamlit クイズへようこそ！")
display_team_id_sidebar()

css_name = apply_default_custom_css()
message = f"""
    PyCon JP の Streamlit ブースに遊びに来ていただきありがとうございます！
    このアプリでは、Streamlit に関する3つのクイズに挑戦します。

    クイズにクリアして、**ステッカーやノベルティ** をゲットしましょう！
    
    Streamlit の機能や使い方を学び、理解する絶好のチャンスです！
    <br>

    **さあ、クイズに挑戦しましょう！**
    """

display_applied_message(message, css_name)
background_image("pages/common/images/background1.jpg", dark_mode=False)

st.write("")


snow_session = create_session(TEAMS["Account Admin"])
st.session_state.snow_session = snow_session

team_id = st.text_input(label="ユーザー名を入力してください。")

if is_team_id_exists(snow_session, team_id):
    if f"is_prompt_for_{team_id}" not in st.session_state:
        prompt_for_duplicate_username_continue(team_id)

    else:
        if not st.session_state[f"is_prompt_for_{team_id}"]:
            st.warning("ユーザー名を変更してください。")
            st.stop()

else:
    keys_to_clear = [
        key for key in st.session_state if key.startswith("is_prompt_for_")
    ]

    for key in keys_to_clear:
        del st.session_state[key]

st.session_state.team_id = team_id

if st.button("挑戦を開始する"):
    print(st.session_state)
    if team_id == "":
        st.error("ユーザー名を入力してみましょう！")
    else:
        st.switch_page("pages/01_normal_problems.py")
