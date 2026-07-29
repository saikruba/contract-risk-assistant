import streamlit as st
import requests
import pandas as pd

# =========================================================
# PAGE CONFIG (MUST BE FIRST STREAMLIT CALL)
# =========================================================
st.set_page_config(
    page_title="Contract Risk Assistant",
    layout="wide"
)


st.markdown("""
<style>

/* ==========================
   Main Title
========================== */
.main-title {
    font-size: 2.3rem;
    font-weight: 700;
    margin-bottom: 0.2rem;
}

.subtitle {
    color: #666;
    margin-bottom: 1.4rem;
    font-size: 1rem;
}

/* ==========================
   Metric Cards
========================== */
div[data-testid="metric-container"] {
    border: 1px solid #ececec;
    border-radius: 14px;
    padding: 16px;
    background: #fafafa;
}

/* ==========================
   Tabs
========================== */
button[data-baseweb="tab"] {
    font-size: 16px;
    font-weight: 600;
    padding: 12px 20px;
    margin-right: 6px;
}

/* ==========================
   Buttons
========================== */
div.stButton > button {
    border-radius: 10px;
    height: 44px;
    font-weight: 600;
}

/* ==========================
   Risk Cards
========================== */
.risk-box {
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #ececec;
    margin-bottom: 14px;
    background: #fafafa;
}

/* ==========================
   Chat
========================== */
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

/* ==========================
   References
========================== */
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

/* ==========================
   Chat Messages
========================== */
div[data-testid="stChatMessage"] {
    padding-bottom: 0.4rem;
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
st.sidebar.markdown("Upload and analyze legal agreements")
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader(
    "Choose a PDF file",
    type=["pdf"],
    key=f"uploader_{st.session_state.uploader_key}"
)

# =========================================================
# UPLOAD HANDLING
# =========================================================
if uploaded_file and not st.session_state.uploaded:

    with st.sidebar:
        with st.spinner("Analyzing contract..."):

            files = {
                "file": (uploaded_file.name, uploaded_file.getvalue())
            }

            response = requests.post(
                "http://127.0.0.1:8000/api/v1/upload-contract",
                files=files
            )

            if response.status_code == 200:
                st.session_state.analysis = response.json()
                st.session_state.uploaded = True
                st.success("✅ Contract analyzed successfully")
            else:
                st.error(response.text)

# =========================================================
# RESET
# =========================================================
if st.sidebar.button("🔄 Reset Workspace", width="stretch"):

    try:
        requests.post("http://127.0.0.1:8000/api/v1/reset", timeout=10)
    except Exception as e:
        st.error(f"Backend reset failed: {e}")

    st.session_state.analysis = None
    st.session_state.uploaded = False
    st.session_state.chat_history = []
    st.session_state.uploader_key += 1

    st.rerun()

# =========================================================
# TITLE
# =========================================================
st.markdown(
    '<div style="font-size:2.3rem;font-weight:700;">📄 Contract Risk Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div style="color:#666;">AI-powered contract review system</div>',
    unsafe_allow_html=True
)

# =========================================================
# MAIN APP
# =========================================================
if not st.session_state.analysis:

    st.info("Upload a contract to begin analysis.")

else:

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

        # -----------------------------
        # OVERVIEW
        # -----------------------------
        with overview_tab:

        #    st.metric("Document", uploaded_file.name)

            if data.get("summary"):
                st.subheader("Executive Summary")
                st.markdown(data["summary"])

        # -----------------------------
        # RISKS (FIXED TABLE)
        # -----------------------------
        with risks_tab:

            st.subheader("Risk Analysis")

            df = pd.DataFrame(data.get("segment_analysis", []))

            if df.empty:
                st.warning("No risk data available")

            else:

                df = df[[
                    "clause_name",
                    "severity",
                    "score",
                    "clause_excerpt",
                    "reason"
                ]]

                df.columns = [
                    "Risk Category",
                    "Severity",
                    "Score",
                    "Evidence",
                    "Reason"
                ]

                # -----------------------------
                # COLOR FUNCTION (WORKING STYLE)
                # -----------------------------
                def highlight_severity(row):
                    colors = []

                    for col in row.index:
                        if row["Severity"] == "HIGH":
                            colors.append("background-color: #ffcccc")
                        elif row["Severity"] == "MEDIUM":
                            colors.append("background-color: #fff4cc")
                        else:
                            colors.append("background-color: #d6f5d6")

                    return colors

                styled_df = df.style.apply(highlight_severity, axis=1)

                st.dataframe(styled_df, width="stretch")

        # -----------------------------
        # DEBUG
        # -----------------------------
        with debug_tab:

            st.write(data.get("segment_analysis", []))



    # =====================================================
    # RIGHT PANEL CHATBOT
    # =====================================================
    with right_panel:

        st.markdown(
            '<div class="chat-title">🤖 AI Contract Copilot</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="chat-subtitle">Ask questions about your agreement</div>',
            unsafe_allow_html=True
        )

        chat_area = st.container(height=800)

        with chat_area:

            if st.session_state.chat_history:

                for chat in st.session_state.chat_history:

                    with st.chat_message("user"):
                        st.write(chat["question"])

                    with st.chat_message("assistant"):

                        st.write(chat["answer"])

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

        query = st.chat_input(
            "Ask about clauses, liabilities, payment terms..."
        )

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
                            "query": clean_query,
                            "chat_history": st.session_state.chat_history[-5:]
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
