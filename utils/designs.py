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


def display_problem_statement(
    html_message: str,
    css_name: str = DEFAULT_PROBLEM_STATEMENT_AREA,
    image_file: str = "pages/common/images/quest.jpeg",
):
    import base64

    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
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
                background-color: rgba(2, 2, 2, 0);
                background-image: url(data:image/{"png"};base64,{encoded_string});
                background-position: top;
                padding: 40px 5%;
                color: #9e1717;
                background-size: cover;
            }}
            </style>
        </p>
        """
    )
