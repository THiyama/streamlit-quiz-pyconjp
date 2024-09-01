import pandas as pd
import plotly.express as px
import streamlit as st
import snowflake.snowpark.functions as F
from snowflake.snowpark import Session

from utils.utils import (
    display_team_id_sidebar,
    display_page_titles_sidebar,
    get_session,
    get_team_id,
)
from utils.designs import apply_default_custom_css, display_applied_message

st.title("📊挑戦状況")

display_page_titles_sidebar()
display_team_id_sidebar()
get_team_id()

css_name = apply_default_custom_css()
message = "ここでは、現在の各チームの挑戦状況を確認できるぞ。\n\nそなたらもどんどん挑戦して進むのだ！"
display_applied_message(message, css_name)

session = get_session()


session = st.session_state.snow_session
problem_ids = st.session_state.problem_ids
pdf_problem_ids = pd.DataFrame(problem_ids, columns=["problem_id"])


@st.fragment(run_every="10s")
def update_chart():
    df = session.table("submit2")
    df_grouped = (
        df.select(F.col("problem_id"), F.col("team_id"), F.col("is_clear"))
        .group_by([F.col("problem_id"), F.col("team_id")])
        .agg(F.call_builtin("boolor_agg", F.col("is_clear")).alias("is_clear"))
        .group_by([F.col("problem_id")])
        .agg(F.count(F.col("is_clear")).alias("is_clear"))
        .to_pandas()
    )

    result = pdf_problem_ids.merge(
        df_grouped, left_on="problem_id", right_on="PROBLEM_ID", how="left"
    )

    result["IS_CLEAR"] = result["IS_CLEAR"].fillna(0)

    fig = px.bar(result, x="problem_id", y="IS_CLEAR")
    fig.update_layout(yaxis_range=[0, 30])
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(result)


update_chart()
