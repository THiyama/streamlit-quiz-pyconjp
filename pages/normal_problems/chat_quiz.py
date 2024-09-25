import re
import streamlit as st
from typing import Optional
from snowflake.snowpark import Session
from snowflake.cortex import Complete as CompleteText

from utils.utils import save_table, init_state, clear_submit_button
from utils.attempt_limiter import check_is_failed, init_attempt, process_exceeded_limit
from utils.designs import display_problem_statement

MAX_ATTEMPTS_MAIN = 1000


def initialize_chat_history() -> None:
    """チャット履歴をセッションステートに初期化する。"""
    if "messages" not in st.session_state:
        st.session_state.messages = []


def display_chat_history(chat_container) -> None:
    """ユーザーとアシスタントのチャット履歴のみを表示する。

    Args:
        chat_container: チャットメッセージを表示するコンテナ。
    """
    for message in st.session_state.messages:
        if message["role"] in ["user", "assistant"]:
            with chat_container.chat_message(
                message["role"], avatar=message.get("avatar")
            ):
                st.markdown(message["content"])


def ai_problem(tab_name: str, max_attempts: int, session: Session) -> Optional[str]:
    """AI問題の作成

    Args:
        tab_name (str): タブの名前。
        max_attempts (int): 許可される最大試行回数。
        session (Session): Snowflakeセッション。

    Returns:
        str: ユーザーが選択した答え。
    """
    st.header("このひとだあれ？？？", divider="rainbow")

    display_problem_statement(
        """
                              <i>このひとだあれ？？？。
                              あなたはAIとの会話からその人が誰なのかを当ててみてください</i><br />
                              <br />
                              職業や勤務先を聞いてみよう！難しければ、ヒントを見てみましょう。
                              """
    )

    initialize_chat_history()

    chat_container = st.container()  # コンテナの高さは指定しない
    display_chat_history(chat_container)

    prompt = st.chat_input("何か質問はありますか？")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container.chat_message("user"):
            st.markdown(prompt)

        with chat_container.chat_message(
            "assistant", avatar="😺"
        ):  # アバターを明確に設定
            response = call_cortex_ai_model(
                "snowflake-arctic", prompt, st.session_state.messages, session
            )
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response,
                    "avatar": "😺",  # アバターもメッセージと共にセッションに保存
                }
            )
            st.rerun()  # メッセージが更新されたら再描画

    expander = st.expander("ヒント💡")
    expander.write(
        """
    私はStreamlitの共同創業者です！ペットは犬を飼っています。
    昨年末、Streamlitのコミュニティイベントにも来日しましたよ！
    https://info.streamlit.io/december-tokyo-meetup
    """
    )
    expander.image("pages/common/images/user_image.png", width=300)

    st.divider()
    # ラジオボタンの選択肢を定義（番号付き）
    choices = [
        "1. Guido van Rossum",
        "2. Amanda Kelly",
        "3. Sridhar Ramaswamy",
    ]

    # ラジオボタンの作成
    answer = st.radio("選択してください:", choices, index=None)

    return answer


def call_cortex_ai_model(
    model_name: str, prompt: str, context: list[dict], session: Session
) -> str:
    """AIモデルを呼び出して応答を取得する。

    Args:
        model_name (str): AIモデルの名前。
        prompt (str): ユーザーのプロンプト。
        context (list[dict]): 前のメッセージのコンテキスト。
        session (Session): Snowflakeセッション。

    Returns:
        str: AIモデルの応答。
    """
    context_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in context])
    prompt_text = f"""
    #命令文
    制約：
    あなたのプロフィール情報は以下です。
    ユーザーからの質問にたいしてプロフィール情報を元に回答してください。
    聞かれた情報にだけ、一つずつ答えるようにしてください。
    - 名前:??????
    - 性別：女性
    - 勤務先：Snowflake / Streamlit
    - 仕事/職業/経歴:Streamlitの共同創業者で、現在はSnowflakeでプロダクトディレクターを担っています。
    - 職場/住所:カリフォルニア
    Context: {context_str}
    Question: {prompt}
    Answer:
    """
    response = CompleteText(model_name, prompt_text, stream=False, session=session)
    return response


def process_answer(answer: str, state: dict, session: Session) -> None:
    """ユーザーの答えを処理し、フィードバックを提供する。

    Args:
        answer (str): ユーザーが選択した答え。
        state (dict): セッションの現在の状態。
        session (Session): Snowflakeセッション。
    """
    # 正解判定
    selected_number = int(answer.split(".")[0])
    if selected_number == 2:
        state["is_clear"] = True
        st.success("クイズに正解しました")
    else:
        state["is_clear"] = False
        st.error("不正解です")

    save_table(state, session)


def run(tab_name: str, session: Session) -> None:
    """メインチャットアプリケーションのロジックを実行する。

    Args:
        tab_name (str): タブの名前。
        session (Session): Snowflakeセッション。
    """
    state = init_state(tab_name, session, MAX_ATTEMPTS_MAIN)
    main_attempt = init_attempt(
        max_attempts=MAX_ATTEMPTS_MAIN, tab_name=tab_name, session=session, key="main"
    )

    answer = ai_problem(tab_name, MAX_ATTEMPTS_MAIN, session)

    placeholder = st.empty()
    if check_is_failed(session, state):
        process_exceeded_limit(placeholder, state)
    elif placeholder.button("submit", key=f"{tab_name}_submit"):
        if main_attempt.check_attempt():
            if answer:
                process_answer(answer, state, session)
            else:
                st.warning("選択してください")
        else:
            process_exceeded_limit(placeholder, state)

    clear_submit_button(placeholder, state)
