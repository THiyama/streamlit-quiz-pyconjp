import hashlib
from datetime import datetime

import pandas as pd
import streamlit as st
import snowflake.snowpark.functions as F
from snowflake.snowpark import Session
from snowflake.snowpark.exceptions import SnowparkSQLException

from utils.attempt_limiter import check_is_failed, update_failed_status


TAB_TITLES = {
    "01_whats_streamlit": "Streamlitとは？",
    "02_which_code": "どのコードが正しい？",
    "03_chat_quiz": "このひとだあれ",
}


# Key: 表示されるチーム名
# Value: secretsに記載されているチームID
TEAMS = {
    "": "",
    "Account Admin": "Account_Admin",
}


def check_all_clear(team_id):
    # チームIDに関連するすべての "_is_clear" フラグが True かどうか確認
    return any(
        st.session_state[key]
        for key in st.session_state
        if key.endswith(f"_{team_id}_is_clear")
    )


@st.cache_resource(ttl=3600)
def create_session(team_id: str, is_info: bool = True) -> Session:
    try:
        session = st.connection(team_id, type="snowflake", max_entries=1).session()
        session.sql("SELECT 1").collect()
        if is_info:
            pass
            # st.success("データクリスタルとのリンクに成功したぞ。次なる試練へ進むのだ！")
        return session

    except SnowparkSQLException as e:
        print(e)
        print("セッションの有効期限切れエラーが発生しました。")
        print("セッションの再作成を試みます。")
        session = st.connection(team_id, type="snowflake", max_entries=1).session()
        session.sql("SELECT 1").collect()
        print("セッションの再作成に成功しました。")
        if is_info:
            pass
            # st.success("データクリスタルとのリンクに成功したぞ。次なる試練へ進むのだ！")
        return session

    except Exception as e:
        if is_info:
            st.error(
                "Snowflake との接続時に問題が発生したようです。スタッフに相談してみてください。"
            )
            print(e)
            st.stop()


def get_session():
    if "snow_session" not in st.session_state:
        st.warning("ユーザー名の入力ができていないようです。")
        if st.button("ユーザー名入力に戻る"):
            st.switch_page("app.py")
        st.stop()
    else:
        session = st.session_state.snow_session
        return session


def display_page_titles_sidebar():
    with st.sidebar:
        st.page_link("app.py", label="ユーザー名の入力", icon="👥")
        st.page_link("pages/01_normal_problems.py", label="クイズ", icon="💡")
        st.page_link(
            "pages/03_aggregate_results.py", label="Overall Progress", icon="📊"
        )


def display_team_id_sidebar():
    with st.sidebar:
        try:
            st.divider()
            if "team_id" not in st.session_state:
                st.write(f"ユーザー名: 未登録")

            elif st.session_state.team_id == "":
                st.write(f"ユーザー名: 未登録")
            else:
                st.write(f"ユーザー名: {st.session_state.team_id}")
        except AttributeError as e:
            print(e)


def display_team_id():
    st.write(f"そなたらのチームは 「**{st.session_state.team_id}**」 だ。")


def get_team_id():
    if "team_id" not in st.session_state:
        st.warning("ユーザー名の入力ができていないようです。")
        if st.button("ユーザー名入力に戻る"):
            st.switch_page("app.py")
        st.stop()
    elif st.session_state.team_id == "":
        st.warning("ユーザー名の入力ができていないようです。")
        if st.button("ユーザー名入力に戻る"):
            st.switch_page("app.py")
        st.stop()
    else:
        return st.session_state.team_id


def init_state(tab_name: str, session: Session, max_attempts: int = 3):
    state_name = f"{tab_name}_state"
    if state_name not in st.session_state:
        st.session_state.state = {}

    state = st.session_state.state

    state["team_id"] = st.session_state.team_id
    state["problem_id"] = tab_name

    state["is_clear"] = check_is_clear(session, state)
    state["max_attempts"] = max_attempts

    return state


def save_table(state: dict, session: Session):
    df = pd.DataFrame(
        [
            {
                "team_id": state["team_id"],
                "problem_id": state["problem_id"],
                "timestamp": datetime.now(),
                "is_clear": state["is_clear"],
                "key": "main",
                "max_attempts": state["max_attempts"],
            }
        ],
        columns=[
            "team_id",
            "problem_id",
            "timestamp",
            "is_clear",
            "key",
            "max_attempts",
        ],
    )

    with st.spinner("Snowflake と通信中... 少しお待ち下さい"):
        # session.write_pandas(df, "SUBMIT2", auto_create_table=False, overwrite=False)

        if state["is_clear"]:
            snow_df = session.create_dataframe(df)
            snow_df.write.mode("append").save_as_table("submit2")
            # はじめてのクリアの場合、if文内のロジックを実行する。
            if not st.session_state[
                f"{state['problem_id']}_{state['team_id']}_is_clear"
            ]:
                update_clear_status(session, state)
                st.session_state[f"{state['problem_id']}_{state['team_id']}_title"] = (
                    "✅️ "
                    + st.session_state[
                        f"{state['problem_id']}_{state['team_id']}_title"
                    ]
                )
                st.session_state[
                    f"{state['problem_id']}_{state['team_id']}_is_clear"
                ] = True

                st.rerun()

        else:
            update_failed_status(session, state)
            # 制限に到達している かつ クリアしていない 場合、if文内のロジックを実行する。
            if (
                check_is_failed(session, state)
                and not st.session_state[
                    f"{state['problem_id']}_{state['team_id']}_is_clear"
                ]
            ):
                st.session_state[f"{state['problem_id']}_{state['team_id']}_title"] = (
                    "❌️ "
                    + st.session_state[
                        f"{state['problem_id']}_{state['team_id']}_title"
                    ]
                )
                st.session_state[
                    f"{state['problem_id']}_{state['team_id']}_is_failed"
                ] = True

                st.rerun()


def update_clear_status(session: Session, state: dict) -> None:
    submit_table = session.table("submit2")

    try:
        result = submit_table.filter(
            (F.col("team_id") == state["team_id"])
            & (F.col("problem_id") == state["problem_id"])
            & (F.col("is_clear") == True)
        ).count()

        st.session_state[f"{state['problem_id']}_{state['team_id']}_is_clear"] = (
            result > 0
        )

    except IndexError as e:
        print(e)
        st.session_state[f"{state['problem_id']}_{state['team_id']}_is_clear"] = False


def check_is_clear(session: Session, state: dict):
    # 呼び出し側が session 引数を入力しているため、一旦この関数では使っていないが定義する。
    return st.session_state[f"{state['problem_id']}_{state['team_id']}_is_clear"]


def reset_problem_status() -> None:
    team_id = TEAMS[get_team_id()]

    for problem_id in st.session_state["problem_ids"]:
        # if f"{problem_id}_{team_id}_title" in st.session_state:
        del st.session_state[f"{problem_id}_{team_id}_title"]

    st.session_state[f"{team_id}_display_preparation_message"] = True


def clear_submit_button(placeholder, state):
    if st.session_state[f"{state['problem_id']}_{state['team_id']}_is_clear"]:
        placeholder.empty()
        placeholder.success(
            "このクイズには正解しました！上のドロップダウンから、次の問題を選択してください。"
        )
    elif st.session_state[f"{state['problem_id']}_{state['team_id']}_is_failed"]:
        placeholder.empty()
        placeholder.error("このクイズに挑戦するにはパワーが足りないみたいです。")


def string_to_hash_int(base_string: str) -> int:
    # 文字列をUTF-8でエンコードし、SHA256ハッシュを計算
    hash_object = hashlib.sha256(base_string.encode("utf-8"))
    hash_hex = hash_object.hexdigest()

    # 16進数の文字列を整数に変換
    hash_int = int(hash_hex, 16)

    # 整数値をシードとして返す
    return hash_int
