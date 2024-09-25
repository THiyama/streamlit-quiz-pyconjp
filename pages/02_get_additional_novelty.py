import streamlit as st

from utils.utils import (
    display_page_titles_sidebar,
    get_team_id,
)
from utils.designs import (
    apply_default_custom_css,
    display_applied_message,
)

st.title(":balloon: ノベルティゲット")
display_page_titles_sidebar()


team_id = get_team_id()
if f"{team_id}_display_preparation_message" not in st.session_state:
    st.session_state[f"{team_id}_display_preparation_message"] = True

css_name = apply_default_custom_css()
message = f"""
    いらっしゃい、**{team_id}** さん！

    Streamlit Forum に登録して、**さらなる Streamlit ノベルティ**を手に入れよう！
    """

display_applied_message(message, css_name)


st.write("")
st.write("")

st.write("まず、Streamlit Forum にアクセスして、ユーザー登録をしましょう。")
st.link_button(label="Forum に進む", url="https://discuss.streamlit.io/")
st.write(
    "Streamlit Forum に登録できたら（スタッフに確認してもらいましょう）、次の抽選に進みましょう！"
)
st.link_button(label="抽選に進む", url="https://pyconjp2024-st-lottery.streamlit.app/")
