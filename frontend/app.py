import streamlit as st
import requests

st.title("Contract Risk Assistant")

uploaded_file = st.file_uploader("Upload a contract file")

if uploaded_file is not None:
    st.write("Uploading and analyzing...")

    try:
        response = requests.post(
            "http://127.0.0.1:8000/upload-contract",
            files={"file": uploaded_file}
        )

        if response.status_code == 200:
            data = response.json()

            st.success("Analysis Complete ✅")

            st.subheader("Results")
            st.write("Filename:", data["filename"])
            st.write("Risk:", data["risk"])

            st.subheader("Issues")
            if data["issues"]:
                for issue in data["issues"]:
                    st.warning(issue)
            else:
                st.success("No issues found 🎉")

        else:
            st.error("Backend error")

    except:
        st.error("FastAPI not running")
