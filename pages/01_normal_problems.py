# from streamlit_profiler import Profiler

import streamlit as st
import os
import importlib

from utils.utils import (
    check_is_clear,
    check_all_clear,
    update_clear_status,
    display_page_titles_sidebar,
    display_team_id_sidebar,
    get_session,
    get_team_id,
    TAB_TITLES,
)
from utils.designs import (
    apply_default_custom_css,
    display_applied_message,
)
from utils.attempt_limiter import check_is_failed, update_failed_status


@st.cache_resource
def get_module(module_path: str):
    return importlib.import_module(module_path)


display_page_titles_sidebar()

st.title("💡クイズの間")

display_team_id_sidebar()
team_id = get_team_id()
print(team_id)
if f"{team_id}_display_preparation_message" not in st.session_state:
    st.session_state[f"{team_id}_display_preparation_message"] = True

css_name = apply_default_custom_css()
message = f"""
    いらっしゃい、**{team_id}** さん！

    3つのクイズに挑戦して、ステッカーやノベルティをゲットしましょう！
    """
display_applied_message(message, css_name)

st.write("")

session = get_session()


problems_dir = "pages/normal_problems"
problem_files = [f for f in os.listdir(problems_dir) if f.endswith(".py")]

tabs = {}
for file in problem_files:
    module_name = file[:-3]
    if module_name not in TAB_TITLES:
        continue
    module_path = f"pages.normal_problems.{module_name}"
    tabs[module_name] = get_module(module_path)

tab_titles = []
problem_ids = []
state = {}
state["team_id"] = st.session_state.team_id

progress_text = "Loading..."
progress_bar = st.progress(value=0, text=progress_text)
total_steps = len(tabs.keys())

for i, problem_id in enumerate(tabs.keys()):
    progress_bar.progress(int((i + 1) / total_steps * 100), progress_text)
    state["problem_id"] = problem_id

    # タブタイトルの定義にない問題はスキップする
    if problem_id not in TAB_TITLES:
        continue

    #
    if (
        f"{state['problem_id']}_{state['team_id']}_is_init_updated"
        not in st.session_state
    ):
        st.session_state[
            f"{state['problem_id']}_{state['team_id']}_is_init_updated"
        ] = True
        update_clear_status(session, state)
        update_failed_status(session, state)

    # タブ名、タブステートの初期化
    if f"{state['problem_id']}_{state['team_id']}_title" not in st.session_state:

        # クリアフラグを追加するIFステートメント
        if check_is_clear(session, state):

            checker = "✅️ "
            st.session_state[f"{state['problem_id']}_{state['team_id']}_is_clear"] = (
                True
            )
            st.session_state[f"{state['problem_id']}_{state['team_id']}_is_failed"] = (
                False
            )
        elif check_is_failed(session, state):
            checker = "❌️ "
            st.session_state[f"{state['problem_id']}_{state['team_id']}_is_clear"] = (
                False
            )
            st.session_state[f"{state['problem_id']}_{state['team_id']}_is_failed"] = (
                True
            )
        else:
            checker = ""
            st.session_state[f"{state['problem_id']}_{state['team_id']}_is_clear"] = (
                False
            )
            st.session_state[f"{state['problem_id']}_{state['team_id']}_is_failed"] = (
                False
            )

        # タブタイトル（物理名）にフラグを追加する処理
        st.session_state[f"{state['problem_id']}_{state['team_id']}_title"] = (
            checker + TAB_TITLES[problem_id]
        )

    # タブタイトル（物理名）の追加
    tab_titles.append(
        st.session_state[f"{state['problem_id']}_{state['team_id']}_title"]
    )
    problem_ids.append(problem_id)

print(check_all_clear(state["team_id"]))
if check_all_clear(state["team_id"]):
    st.balloons()
    st.balloons()
    st.balloons()
    st.success(
        """
        あなたはすべてのクイズに正解しました！
        ステッカーをスタッフから受け取ってください。
        Streamlit Forum に登録することで、さらにノベルティをゲットできます！
    """
    )
    if st.button("さらなるノベルティ獲得に進む", type="primary"):
        st.switch_page("pages/02_get_additional_novelty.py")


success_placeholder = st.empty()
if st.session_state[f"{team_id}_display_preparation_message"]:
    success_placeholder.success("クイズの準備が整いました。")
    st.session_state[f"{team_id}_display_preparation_message"] = False
else:
    success_placeholder.empty()

st.session_state["problem_ids"] = problem_ids


# セレクトボックスの実装の場合
if "rerun" not in st.session_state:
    st.session_state["rerun"] = False

selected_index_state_name = f"{team_id}_selected_index"
if selected_index_state_name not in st.session_state:
    st.session_state[selected_index_state_name] = 0


def update_selected_index():
    st.session_state[selected_index_state_name] = tab_titles.index(
        st.session_state[f"{team_id}_selected_problem"]
    )


selected_problem = st.selectbox(
    "クイズを選択してください",
    options=tab_titles,
    index=st.session_state[selected_index_state_name],
    on_change=update_selected_index,
    key=f"{team_id}_selected_problem",
)

selected_problem_id = problem_ids[tab_titles.index(selected_problem)]

tabs[selected_problem_id].run(selected_problem_id, session)


# タブの実装の場合
# selected_tab = st.tabs(tab_titles)

# for i, tab_title in enumerate(problem_ids):
#     with selected_tab[i]:
#         tabs[tab_title].run(tab_title, session)


progress_bar.empty()
