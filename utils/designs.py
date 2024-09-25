import base64

import streamlit as st


DEFAULT_TOP_TEXT_AREA = "custom-text-area"
DEFAULT_PROBLEM_STATEMENT_AREA = "custom-problem-statement-area"

bright_streamlit = "#ff4b4b"
mid_streamlit = "#bd4043"
dark_streamlit = "#7d353b"


def apply_default_custom_css():
    st.markdown(
        """
        <style>
        ."""
        + DEFAULT_TOP_TEXT_AREA
        + """ {
            background-color: #1e1e1e;  /* ダーク背景 */
            padding: 20px;
            border-radius: 10px;
            border: 2px solid """
        + dark_streamlit
        + """;  /* グレーのボーダー */
            border-left: 5px solid """
        + mid_streamlit
        + """;  /* Streamlit 色のサイドライン */
            color: #ffffff;  /* 白文字 */
            font-size: 16px;
            line-height: 1.6;
        }
        ."""
        + DEFAULT_TOP_TEXT_AREA
        + """ h3 {
            color: """
        + bright_streamlit
        + """;  /* 淡いSnowflake色 */
            text-shadow: 2px 2px #000000;  /* 影を付けて浮き上がる効果 */
        }
        ."""
        + DEFAULT_TOP_TEXT_AREA
        + """ strong {
            color: """
        + bright_streamlit
        + """;  /* 強調部分も淡いSnowflake色に */
        }
        ."""
        + DEFAULT_TOP_TEXT_AREA
        + """ p:last-child {
            margin-bottom: 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    return DEFAULT_TOP_TEXT_AREA


def display_applied_message(message: str, css_name: str = DEFAULT_TOP_TEXT_AREA):
    if css_name == DEFAULT_TOP_TEXT_AREA:
        apply_default_custom_css()
    else:
        apply_default_custom_css()

    st.markdown(
        f"""
        <div class='{css_name}'>
        {message}
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def get_image_base64(image_file: str) -> str:

    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string


def display_problem_statement(
    html_message: str,
    css_name: str = DEFAULT_PROBLEM_STATEMENT_AREA,
):

    st.html(
        f"""
        <p>
            <div class="{css_name}">
            {html_message}
            </div>
            <style>
            .{css_name} .box {{
                border-radius: 10px;
            }}
            .{css_name} {{
                background-color: rgb(239, 228, 176);
                padding: 40px 5%;
                color: #9e1717;
            }}
            </style>
        </p>
        """
    )
