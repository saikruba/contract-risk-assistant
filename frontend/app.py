import streamlit as st
import requests


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Contract Risk Assistant",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>

.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    max-width: 1500px;
}

/* Header */
header[data-testid="stHeader"] {
    background: transparent;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    border-right: 1px solid #ececec;
}

/* Main Title */
.main-title {
    font-size: 2.3rem;
    font-weight: 700;
    margin-bottom: 0.2rem;
}

.subtitle {
    color: #666;
    margin-bottom: 1.4rem;
}

/* Metric Cards */
div[data-testid="metric-container"] {
    border: 1px solid #ececec;
    border-radius: 14px;
    padding: 16px;
    background: #fafafa;
}

/* Tabs */
button[data-baseweb="tab"] {
    font-size: 28px;
    font-weight: 600;
    padding: 14px 22px;
    margin-right: 6px;
}

/* Buttons */
div.stButton > button {
    border-radius: 10px;
    height: 44px;
    font-weight: 600;
}

/* Risk Box */
.risk-box {
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #ececec;
    margin-bottom: 14px;
    background: #fafafa;
}

/* Chat Area */
.chat-wrapper {
    border-left: 1px solid #f0f0f0;
    padding-left: 22px;
    height: 100%;
    position: sticky;
    top: 1rem;
}

.chat-title {
    font-size: 1.15rem;
    font-weight: 700;
    margin-bottom: 0.3rem;
}

.chat-subtitle {
    color: #666;
    font-size: 13px;
    margin-bottom: 1rem;
}

/* Chat Scroll Area */
.chat-container {
    max-height: 70vh;
    overflow-y: auto;
    padding-right: 4px;
    margin-bottom: 1rem;
}

/* User Message */
.user-msg {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 14px;
}

.user-bubble {
    background: #111827;
    color: white;
    padding: 12px 14px;
    border-radius: 18px 18px 4px 18px;
    max-width: 85%;
    font-size: 14px;
    line-height: 1.5;
}

/* Assistant Message */
.assistant-msg {
    display: flex;
    justify-content: flex-start;
    margin-bottom: 18px;
}

.assistant-bubble {
    background: #f8f9fb;
    border: 1px solid #ececec;
    padding: 14px;
    border-radius: 18px 18px 18px 4px;
    max-width: 90%;
    font-size: 14px;
    line-height: 1.7;
}

/* References */
.reference-block {
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid #ececec;
}

.reference-item {
    font-size: 12px;
    color: #666;
    margin-bottom: 8px;
    line-height: 1.6;
}

/* Hero Section */
.hero-title {
    font-size: 3rem;
    font-weight: 700;
    line-height: 1.1;
    margin-bottom: 1rem;
}

.hero-subtitle {
    color: #666;
    font-size: 1.1rem;
    line-height: 1.7;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION STATE
# =========================================================
defaults = {
    "analysis": None,
    "uploaded": False,
    "chat_input": "",
    "results": [],
    "answer": "",
    "uploader_key": 0,
    "reset_trigger": False,
    "chat_history": []
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown("# Contract Console")

st.sidebar.markdown(
    "Upload and analyze legal agreements"
)

st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader(
    "Choose a PDF file",
    type=["pdf"],
    key=f"uploader_{st.session_state.uploader_key}"
)

# =========================================================
# CLAUSE CATEGORIES
# =========================================================
st.sidebar.markdown("---")

with st.sidebar.expander(
    "📑 Supported Clause Categories",
    expanded=False
):

    clauses = [
        "Termination",
        "Indemnification",
        "Liability",
        "Payment Terms",
        "Confidentiality",
        "IP Ownership",
        "Auto Renewal",
        "Warranty",
        "Force Majeure",
        "Assignment",
        "Insurance",
        "Jurisdiction"
    ]

    for clause in clauses:
        st.write(f"• {clause}")

# =========================================================
# UPLOAD HANDLING
# =========================================================
if uploaded_file and not st.session_state.uploaded:

    with st.sidebar:

        with st.spinner("Analyzing contract..."):

            try:

                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue()
                    )
                }

                response = requests.post(
                    "http://127.0.0.1:8000/api/v1/upload-contract",
                    files=files
                )

                if response.status_code == 200:

                    st.session_state.analysis = response.json()

                    st.session_state.uploaded = True

                    st.success(
                        "✅ Contract analyzed successfully"
                    )

                else:
                    st.error(response.text)

            except Exception as e:
                st.error(f"Error: {e}")

# =========================================================
# RESET
# =========================================================
if st.sidebar.button(
    "🔄 Reset Workspace",
    use_container_width=True
):
    st.session_state.reset_trigger = True

if st.session_state.reset_trigger:

    try:

        requests.post(
            "http://127.0.0.1:8000/api/v1/reset"
        )

    except Exception as e:
        st.error(f"Backend reset failed: {e}")

    st.session_state.analysis = None
    st.session_state.uploaded = False
    st.session_state.chat_input = ""
    st.session_state.results = []
    st.session_state.answer = ""
    st.session_state.chat_history = []

    st.session_state.uploader_key += 1

    st.session_state.reset_trigger = False

    st.rerun()

# =========================================================
# MAIN TITLE
# =========================================================
st.markdown(
    '<div class="main-title">📄 Contract Risk Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">AI-powered contract review, legal Q&A, and risk analysis</div>',
    unsafe_allow_html=True
)

# =========================================================
# LANDING PAGE
# =========================================================
if not st.session_state.analysis:

    hero_left, hero_right = st.columns([1.2, 1])

    with hero_left:

        st.markdown(
            """
            <div style="padding-top:80px; padding-right:40px;">

            <div class="hero-title">
            AI Contract Review<br>for Legal Teams
            </div>

            <div class="hero-subtitle">
            Upload contracts, detect risks, analyze clauses,
            and ask legal questions with an AI copilot.
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with hero_right:

        st.markdown(
            """
            <div style="
                border:1px solid #ececec;
                border-radius:20px;
                padding:30px;
                margin-top:40px;
                background:#fafafa;
            ">

            <div style="
                font-size:1.1rem;
                font-weight:700;
                margin-bottom:20px;
            ">
            🤖 AI Contract Copilot
            </div>

            <div style="
                background:white;
                border:1px solid #ececec;
                border-radius:14px;
                padding:16px;
                margin-bottom:14px;
            ">
            What are the termination conditions?
            </div>

            <div style="
                background:#f8f9fb;
                border:1px solid #ececec;
                border-radius:14px;
                padding:16px;
                color:#444;
                line-height:1.7;
            ">
            The agreement allows termination with 30 days notice
            and immediate termination for material breach.
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

# =========================================================
# MAIN APPLICATION
# =========================================================
if st.session_state.analysis:

    data = st.session_state.analysis

    left_panel, right_panel = st.columns([2.2, 1])

    # =====================================================
    # LEFT PANEL
    # =====================================================
    with left_panel:

        overview_tab, risks_tab, debug_tab = st.tabs([
            "📊 Overview",
            "⚠️ Risks",
            "🛠 Debug"
        ])

        # =================================================
        # OVERVIEW
        # =================================================
        with overview_tab:

            st.metric(
                "Risk Level",
                data["risk"].upper()
            )

            if data.get("summary"):

                st.subheader(
                    "Executive Summary"
                )

                st.success(
                    data["summary"]
                )

        # =================================================
        # RISKS
        # =================================================
        with risks_tab:

            st.subheader("Risk Analysis")

            for issue in data["issues"]:

                st.markdown(
                    f"""
                    <div class="risk-box">
                    {issue}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # =================================================
        # DEBUG
        # =================================================
        with debug_tab:

            with st.expander("Debug Logs"):

                for log in data.get("debug", []):

                    st.write(log)

    # =====================================================
    # RIGHT PANEL CHATBOT
    # =====================================================
    with right_panel:

        st.markdown(
            '<div class="chat-wrapper">',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="chat-title">🤖 AI Contract Copilot</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="chat-subtitle">Ask questions about your agreement</div>',
            unsafe_allow_html=True
        )

        query = st.text_input(
            "Ask",
            placeholder="Ask about clauses, liabilities, payment terms...",
            key="chat_input",
            label_visibility="collapsed"
        )

        search_clicked = st.button(
            "Send",
            use_container_width=True,
            type="primary"
        )

        # =================================================
        # QUERY LOGIC
        # =================================================
        if search_clicked:

            if query:

                clean_query = (
                    query
                    .replace("what is", "")
                    .replace("the", "")
                    .strip()
                )

                with st.spinner("Analyzing..."):

                    try:

                        response = requests.post(
                            "http://127.0.0.1:8000/api/v1/query",
                            json={
                                "query": clean_query
                            }
                        )

                        if response.status_code == 200:

                            result = response.json()

                            answer = result.get(
                                "answer",
                                ""
                            )

                            refs = result.get(
                                "results",
                                []
                            )

                            st.session_state.chat_history.append({
                                "question": query,
                                "answer": answer,
                                "references": refs
                            })

                            st.rerun()

                        else:
                            st.error(response.text)

                    except Exception as e:
                        st.error(f"Error: {e}")

        # =================================================
        # CHAT HISTORY
        # =================================================
        st.markdown(
            '<div class="chat-container">',
            unsafe_allow_html=True
        )

        if st.session_state.chat_history:

            for chat in reversed(
                st.session_state.chat_history
            ):

                # USER MESSAGE
                st.markdown(
                    f"""
                    <div class="user-msg">
                        <div class="user-bubble">
                            {chat['question']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # ASSISTANT MESSAGE
                st.markdown(
                    f"""
                    <div class="assistant-msg">
                        <div class="assistant-bubble">
                            {chat['answer']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # REFERENCES
                seen_refs = set()

                refs_html = '<div class="reference-block">'

                for ref in chat.get("references", []):

                    page = ref.get("page", "unknown")

                    text = ref.get("text", "")

                    clean_text = " ".join(text.split())

                    if len(clean_text) > 220:

                        short_text = clean_text[:220]

                        short_text = short_text.rsplit(" ", 1)[0]

                        short_text += "..."

                    else:

                        short_text = clean_text

                    unique_key = f"{page}-{short_text}"

                    if unique_key in seen_refs:
                        continue

                    seen_refs.add(unique_key)

                    refs_html += (
                    f'<div class="reference-item">'
                    f'📄 <b>Page {page}</b> — {short_text}'
                    f'</div>'
                    )

                refs_html += "</div>"

                st.markdown(
                    refs_html,
                    unsafe_allow_html=True
                )

        else:

            st.info(
                "Start asking questions about your agreement."
            )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )
