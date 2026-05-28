import streamlit as st
import requests


# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="Contract Risk Assistant",
    layout="wide"
)

st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1450px;
}

header[data-testid="stHeader"] {
    background: transparent;
}

section[data-testid="stSidebar"] {
    border-right: 1px solid #ececec;
}

/* Metric Cards */
div[data-testid="metric-container"] {
    border: 1px solid #eaeaea;
    padding: 18px;
    border-radius: 12px;
    background-color: rgba(250,250,250,0.6);
}

/* Expanders */
div[data-testid="stExpander"] {
    border-radius: 12px;
    border: 1px solid #eaeaea;
    overflow: hidden;
}

/* Search Container */
div[data-testid="stTextInputRootElement"] {
    border-radius: 12px;
}

div[data-testid="stTextInputRootElement"] input {
    padding: 0.8rem;
    font-size: 15px;
}

div.stButton > button {
    border-radius: 10px;
    height: 48px;
    font-weight: 600;
}

/* Tabs */
button[data-baseweb="tab"] {
    font-size: 15px;
    font-weight: 600;
    padding: 10px 18px;
}

/* Main Title */
.main-title {
    font-size: 2.2rem;
    font-weight: 700;
    margin-bottom: 0.2rem;
}

/* Subtitle */
.subtitle {
    color: #666;
    margin-bottom: 2rem;
}

/* AI Answer Box */
.answer-box {
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #eaeaea;
    background-color: rgba(248,248,248,0.7);
}

/* Risk Box */
.risk-box {
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #ececec;
    margin-bottom: 15px;
    background-color: rgba(250,250,250,0.5);
}

</style>
""", unsafe_allow_html=True)


# -------------------------------
# SESSION STATE
# -------------------------------
defaults = {
    "analysis": None,
    "uploaded": False,
    "query": "",
    "results": [],
    "answer": "",
    "uploader_key": 0,
    "reset_trigger": False
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -------------------------------
# SIDEBAR
# -------------------------------
st.sidebar.markdown("# 📄 Contract Console")

st.sidebar.markdown(
    "Upload and analyze legal agreements"
)

st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader(
    "Choose a PDF file",
    type=["pdf"],
    key=f"uploader_{st.session_state.uploader_key}"
)


# -------------------------------
# CLAUSE CATEGORIES
# -------------------------------
st.sidebar.markdown("---")

clauses = [
    "Parties",
    "Effective Date",
    "Term / Duration",
    "Renewal",
    "Notices",
    "Governing Law",
    "Jurisdiction",
    "Dispute Resolution",
    "Arbitration",
    "Limitation of Liability",
    "Indemnification",
    "Liability Cap",
    "Liquidated Damages",
    "Warranty",
    "Disclaimer of Warranties",
    "Non-Compete",
    "Non-Solicitation (Employees)",
    "Non-Solicitation (Customers)",
    "Exclusivity",
    "Non-Disparagement",
    "Pricing",
    "Payment Terms",
    "Taxes",
    "Minimum Commitment",
    "Revenue Sharing",
    "Refund Policy",
    "License Grant",
    "IP Ownership",
    "Joint IP Ownership",
    "Source Code Escrow",
    "Confidentiality",
    "Data Protection / Privacy",
    "Termination for Convenience",
    "Termination for Cause",
    "Change of Control",
    "Assignment",
    "Subcontracting",
    "Audit Rights",
    "Insurance",
    "Force Majeure",
    "Entire Agreement"
]

with st.sidebar.expander(
    "📑 Supported Clause Categories",
    expanded=False
):
    for clause in clauses:
        st.write(f"• {clause}")


# -------------------------------
# UPLOAD HANDLING
# -------------------------------
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

                    st.success("✅ Contract analyzed successfully")

                else:
                    st.error(response.text)

            except Exception as e:
                st.error(f"Error: {e}")


# -------------------------------
# RESET BUTTON
# -------------------------------
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
    st.session_state.query = ""
    st.session_state.results = []
    st.session_state.answer = ""

    st.session_state.uploader_key += 1

    st.success("Workspace reset successful")

    st.session_state.reset_trigger = False


# -------------------------------
# MAIN TITLE
# -------------------------------
st.markdown(
    '<div class="main-title">📄 Contract Risk Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">AI-powered contract review, legal Q&A, and risk analysis</div>',
    unsafe_allow_html=True
)


# -------------------------------
# SEARCH SECTION
# -------------------------------

st.markdown(
    "### 🔍 Ask Questions About Your Contract"
)

st.caption(
    "Search clauses, obligations, liabilities, payment terms, termination conditions, and more."
)

search_col1, search_col2 = st.columns([5, 1])

with search_col1:

    
    st.text_input(
        "Search",
        placeholder="e.g. What are the termination conditions?",
        key="query",
        label_visibility="collapsed",
        on_change=lambda: st.session_state.update(
            {"enter_pressed": True}
        )
    )

with search_col2:

#    search_clicked = st.button(
#        "Search",
#        use_container_width=True
#    )

    search_clicked = st.button(
        "Search",
        use_container_width=True,
        type="primary"
    )

    if st.session_state.query and not search_clicked:
        search_clicked = False


# -------------------------------
# QUERY LOGIC
# -------------------------------
if search_clicked or st.session_state.get("enter_pressed"):

    if not st.session_state.uploaded:

        st.warning(
            "Please upload a contract first."
        )

    elif st.session_state.query:

        clean_query = (
            st.session_state.query
            .replace("what is", "")
            .replace("the", "")
            .strip()
        )

        with st.spinner("Analyzing query..."):

            try:

                response = requests.post(
                    "http://127.0.0.1:8000/api/v1/query",
                    json={
                        "query": clean_query
                    }
                )

                if response.status_code == 200:

                    data = response.json()

                    st.session_state.results = data.get(
                        "results",
                        []
                    )

                    st.session_state.answer = data.get(
                        "answer",
                        ""
                    )
                    
                    st.session_state.enter_pressed = False

                else:
                    st.error(response.text)

            except Exception as e:
                st.error(f"Error: {e}")


# -------------------------------
# DIVIDER
# -------------------------------
st.markdown("---")


# -------------------------------
# CONTRACT ANALYSIS DISPLAY
# -------------------------------
if st.session_state.analysis:

    data = st.session_state.analysis

    # -------------------------------
    # TABS
    # -------------------------------
    overview_tab, risks_tab, qa_tab, debug_tab = st.tabs([
        "📊 Overview",
        "⚠️ Risks",
        "🔍 Q&A",
        "🛠 Debug"
    ])

    # =========================================================
    # OVERVIEW TAB
    # =========================================================
    with overview_tab:

        col1, col2 = st.columns([1, 3])

        with col1:
            st.metric(
                "Overall Risk Level",
                data["risk"].upper()
            )

        with col2:
            st.markdown("### 📄 Uploaded Contract")

            st.info(data["filename"])

        # -------------------------------
        # EXECUTIVE SUMMARY
        # -------------------------------
        if data.get("summary"):

            st.subheader("Executive Summary")

            st.success(
                data["summary"]
            )

    # =========================================================
    # RISKS TAB
    # =========================================================
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

    # =========================================================
    # Q&A TAB
    # =========================================================
    with qa_tab:

        # -------------------------------
        # ANSWER DISPLAY
        # -------------------------------
        if st.session_state.answer:

            st.subheader("AI Answer")

            st.markdown(
                f"""
                <div class="answer-box">
                {st.session_state.answer}
                </div>
                """,
                unsafe_allow_html=True
            )

        # -------------------------------
        # RETRIEVED CHUNKS
        # -------------------------------
        if st.session_state.results:

            st.subheader("Relevant Sections")

            for r in st.session_state.results:

                page = r.get("page", "unknown")

                text = r.get("text", "")

                with st.expander(f"📄 Page {page}"):

                    st.write(text)

        # -------------------------------
        # AGENT QA RESULTS
        # -------------------------------
        if data.get("qa_results"):

            st.markdown("---")

            st.subheader("Agent QA Results")

            for qa in data["qa_results"]:

                st.markdown(
                    f"### {qa['question']}"
                )

                st.info(
                    qa["answer"]
                )

                for ref in qa.get(
                    "references",
                    []
                ):

                    page = ref.get(
                        "page",
                        "unknown"
                    )

                    text = ref.get(
                        "text",
                        ""
                    )

                    with st.expander(
                        f"Reference - Page {page}"
                    ):

                        st.write(text)

    # =========================================================
    # DEBUG TAB
    # =========================================================
    with debug_tab:

        with st.expander("Debug Logs"):

            for log in data.get("debug", []):
                st.write(log)
