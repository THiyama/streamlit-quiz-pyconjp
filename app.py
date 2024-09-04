import streamlit as st
from snowflake.snowpark import Session

from utils.utils import (
    create_session,
    display_team_id_sidebar,
    display_page_titles_sidebar,
)
from utils.designs import apply_default_custom_css, display_applied_message, background_image

display_page_titles_sidebar()

TEAMS = [
    "",
    "Account Admin",
    "Business Critical",
    "Cortex",
    "Data Clean Room",
    "Enterprise Edtion",
    "Fail Safe",
    "Git",
    "Horizon",
    "Iceberg",
    "JDBC",
    "Knowledge",
    "Lineage",
    "Marketplace",
    "Notebooks",
    "OrgAdmin",
    "POLARIS",
    "Quality Monitoring",
    "Resouce Monitor",
    "Snowpark",
    "Trust Center",
    "Universal Search",
    "Validate",
    "WAREHOUSE",
    "X-Small",
]


st.title("💎データクリスタルの挑戦")
display_team_id_sidebar()

css_name = apply_default_custom_css()
message = f"""
    長きにわたり、世界の繁栄と秩序を支え続けてきた「データクリスタル」。

    このクリスタルは、人々に知恵を授け、世界の未来を照らし続けています。  

    **今宵、あなたとチームはこの神秘的な祭典に参加し、クリスタルの力を解き放つ試練に挑むのです。**

    8つの知恵の的屋を攻略し、世界の未来を切り拓け。

    選ばれし者たちよ、運命はあなたの手に託されています。  

    <br>

    **さあ、共にこの旅を始めましょう。そのためにもまずは、チームを結成するのです。**

    """

display_applied_message(message, css_name)
if "team_id" in st.session_state:
    index = TEAMS.index(st.session_state.team_id)
else:
    index = 0

team_id = st.selectbox(
    label="結成するチームを選択", options=TEAMS, index=index, label_visibility="hidden"
)


if team_id:
    st.session_state.team_id = team_id
    placeholder = st.empty()
    if placeholder.button("挑戦を開始する"):
        st.switch_page("pages/01_normal_problems.py")
    st.session_state.snow_session = create_session(team_id, placeholder)


background_image('pages/common/images/sky.png', dark_mode = False)



