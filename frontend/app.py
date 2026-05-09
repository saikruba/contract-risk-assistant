import streamlit as st
import requests


# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="Contract Risk Assistant",
    layout="wide"
)


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
st.sidebar.title("Upload Contract")

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

with st.sidebar.expander("📑 Contract Clause Categories"):
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

                    st.success("Uploaded & Processed")

                else:
                    st.error(response.text)

            except Exception as e:
                st.error(f"Error: {e}")


# -------------------------------
# RESET BUTTON
# -------------------------------
if st.sidebar.button("🔄 Reset"):
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

    st.success("Reset successful")

    st.session_state.reset_trigger = False


# -------------------------------
# MAIN TITLE
# -------------------------------
st.title("📄 Contract Risk Assistant")

st.caption(
    "AI-powered contract review, legal Q&A, and risk analysis"
)


# -------------------------------
# SEARCH SECTION
# -------------------------------
col1, col2, col3 = st.columns([1, 2, 1])

with col2:

    st.markdown(
        "### Ask questions about the contract"
    )

    st.text_input(
        "Search",
        placeholder="e.g. What is the termination clause?",
        key="query",
        label_visibility="collapsed"
    )

    search_clicked = st.button(
        "Search",
        use_container_width=True
    )


# -------------------------------
# QUERY LOGIC
# -------------------------------
if search_clicked:

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

                else:
                    st.error(response.text)

            except Exception as e:
                st.error(f"Error: {e}")


# -------------------------------
# DIVIDER
# -------------------------------
st.markdown("---")


# -------------------------------
# ANSWER DISPLAY
# -------------------------------
if st.session_state.answer:

    st.subheader("AI Answer")

    st.info(
        st.session_state.answer
    )


# -------------------------------
# RETRIEVED CHUNKS
# -------------------------------
if st.session_state.results:

    st.subheader("Relevant Sections")

    for r in st.session_state.results:

        page = r.get("page", "unknown")

        text = r.get("text", "")

        with st.expander(f"Page {page}"):

            st.write(text)


# -------------------------------
# CONTRACT ANALYSIS DISPLAY
# -------------------------------
if st.session_state.analysis:

    st.markdown("---")

    data = st.session_state.analysis

    col1, col2 = st.columns([1, 3])

    with col1:
        st.metric(
            "Overall Risk Level",
            data["risk"].upper()
        )

    with col2:
        st.markdown("### 📄 Upload Contract")

        st.info(data["filename"])

    # -------------------------------
    # EXECUTIVE SUMMARY
    # -------------------------------
    if data.get("summary"):

        st.subheader("Executive Summary")

        st.success(
            data["summary"]
        )

    st.markdown("---")

    # -------------------------------
    # RISK ANALYSIS
    # -------------------------------
    st.subheader("Risk Analysis")

    for issue in data["issues"]:
        st.markdown(issue)

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

    # -------------------------------
    # DEBUG LOGS
    # -------------------------------
    with st.expander("Debug Logs"):

        for log in data.get("debug", []):
            st.write(log)
