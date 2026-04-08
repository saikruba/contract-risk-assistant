import streamlit as st
import requests

st.title("Contract Risk Assistant")

uploaded_file = st.file_uploader("Upload a contract file")

if uploaded_file is not None:
    st.write("Uploading and analyzing...")

    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}

        response = requests.post(
            "http://127.0.0.1:8000/api/v1/upload-contract",
            files=files
        )

        if response.status_code == 200:
            data = response.json()

            st.success("Analysis Complete ✅")
            st.subheader("Results")
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
