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
    "uploader_key": 0,
    "reset_trigger": False
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -------------------------------
# SIDEBAR (UPLOAD)
# -------------------------------
st.sidebar.title("Upload Contract")

uploaded_file = st.sidebar.file_uploader(
    "Choose a PDF file",
    type=["pdf"],
    key=f"uploader_{st.session_state.uploader_key}"
)

# -------------------------------
# CLAUSE LIST
# -------------------------------
st.sidebar.markdown("---")

clauses = [
    "Parties", "Effective Date", "Term / Duration", "Renewal", "Notices",
    "Governing Law", "Jurisdiction", "Dispute Resolution", "Arbitration",
    "Limitation of Liability", "Indemnification", "Liability Cap",
    "Liquidated Damages", "Warranty", "Disclaimer of Warranties",
    "Non-Compete", "Non-Solicitation (Employees)", "Non-Solicitation (Customers)",
    "Exclusivity", "Non-Disparagement",
    "Pricing", "Payment Terms", "Taxes", "Minimum Commitment",
    "Revenue Sharing", "Refund Policy",
    "License Grant", "IP Ownership", "Joint IP Ownership",
    "Source Code Escrow", "Confidentiality", "Data Protection / Privacy",
    "Termination for Convenience", "Termination for Cause",
    "Change of Control", "Assignment", "Subcontracting",
    "Audit Rights", "Insurance", "Force Majeure",
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
                    "file": (uploaded_file.name, uploaded_file.getvalue())
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
# RESET BUTTON (FIXED)
# -------------------------------
if st.sidebar.button("🔄 Reset"):
    st.session_state.reset_trigger = True

# Execute reset ONCE
if st.session_state.reset_trigger:
    try:
        requests.post("http://127.0.0.1:8000/api/v1/reset")
    except Exception as e:
        st.error(f"Backend reset failed: {e}")

    # clear frontend state
    st.session_state.analysis = None
    st.session_state.uploaded = False
    st.session_state.query = ""
    st.session_state.results = []

    # 🔥 CRITICAL: reset uploader
    st.session_state.uploader_key += 1

    st.success("Reset successful")

    # prevent duplicate calls
    st.session_state.reset_trigger = False

# -------------------------------
# MAIN TITLE
# -------------------------------
st.title("📄 Contract Risk Assistant")

# -------------------------------
# SEARCH SECTION
# -------------------------------
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("### Search contract clauses")

    st.text_input(
        "Search",
        placeholder="e.g. termination clause",
        key="query",
        label_visibility="collapsed"
    )

    search_clicked = st.button(
        "Search",
        use_container_width=True
    )

# -------------------------------
# RESULTS SECTION
# -------------------------------
st.markdown("---")

# -------------------------------
# SHOW ANALYSIS
# -------------------------------
if st.session_state.analysis:
    data = st.session_state.analysis

    col1, col2 = st.columns(2)
    col1.metric("Risk Level", data["risk"])
    col2.write(f"{data['filename']}")

    st.subheader("Issues")
    for issue in data["issues"]:
        st.warning(issue)

    with st.expander("Debug Logs"):
        for log in data.get("debug", []):
            st.write(log)

# -------------------------------
# QUERY LOGIC
# -------------------------------
if search_clicked:
    if not st.session_state.uploaded:
        st.warning("Please upload a contract first.")
    elif st.session_state.query:
        clean_query = (
            st.session_state.query.lower()
            .replace("what is", "")
            .replace("the", "")
            .strip()
        )

        with st.spinner("Searching..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/api/v1/query",
                    json={"query": clean_query}
                )

                if response.status_code == 200:
                    st.session_state.results = response.json()["results"]
                else:
                    st.error(response.text)

            except Exception as e:
                st.error(f"Error: {e}")

# -------------------------------
# DISPLAY RESULTS
# -------------------------------
if st.session_state.results:
    st.subheader("Relevant Sections")

    for r in st.session_state.results:
        st.info(r)
