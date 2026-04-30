import streamlit as st
import requests

st.title("Contract Risk Assistant")

BACKEND_URL = "http://127.0.0.1:8000/api/v1"

# -------------------------------
# Session State (NEW)
# -------------------------------
if "filename" not in st.session_state:
    st.session_state.filename = None

# -------------------------------
# Upload Section
# -------------------------------

uploaded_file = st.file_uploader("Upload a contract file", type=["pdf"])

if uploaded_file is not None:
    st.write("Uploading and analyzing...")

    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}

        with st.spinner("Processing contract..."):
            response = requests.post(
                f"{BACKEND_URL}/upload-contract",
                files=files
            )

        if response.status_code == 200:
            data = response.json()

            st.success("Analysis Complete ✅")

            # ✅ STORE filename (CRITICAL FIX)
            st.session_state.filename = data["filename"]

            st.write("Filename:", data["filename"])
            st.write("Risk:", data["risk"])

            st.subheader("Issues")
            for issue in data["issues"]:
                st.warning(issue)

            st.subheader("Debug Logs")
            for log in data.get("debug", []):
                st.write(log)
        else:
            st.error(response.text)

    except Exception as e:
        st.error(f"Error: {e}")


# -------------------------------
# Query Section
# -------------------------------

st.subheader("Ask Questions About Contract")

query = st.text_input("Enter your question")

if st.button("Search"):

    # ✅ VALIDATIONS (NEW)
    if not st.session_state.filename:
        st.warning("Please upload a contract first.")
        st.stop()

    if not query:
        st.warning("Please enter a question.")
        st.stop()

    try:
        with st.spinner("Searching contract..."):
            response = requests.post(
                f"{BACKEND_URL}/query",
                json={
                    "query": query,
                    "filename": st.session_state.filename  # ✅ FIX
                }
            )

        if response.status_code == 200:
            data = response.json()

            # ✅ NEW OUTPUT FORMAT
            st.subheader("Answer")
            st.write(data["answer"])

            st.subheader("Relevant Sections")
            for r in data["sources"]:
                st.info(r)

        else:
            st.error(response.text)

    except Exception as e:
        st.error(f"Error: {e}")
