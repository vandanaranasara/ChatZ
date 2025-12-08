import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="ChatZ", layout="wide")

st.title("📚 ChatZ – PDF AI Assistant")

# ----------------------------
# PAGE SELECTION
# ----------------------------
page = st.sidebar.radio("Navigation", ["Upload", "Extract", "Embed", "Query"])


# ----------------------------
# PAGE: UPLOAD
# ----------------------------
if page == "Upload":
    st.header("📤 Upload PDF")

    uploaded = st.file_uploader("Select PDF file", type=["pdf"])

    if uploaded:
        if st.button("Upload File"):
            files = {"file": uploaded}

            resp = requests.post(f"{API_URL}/upload/upload_file", files=files)

            if resp.status_code == 200:
                data = resp.json()
                st.success("Uploaded successfully!")
                st.session_state.file_id = data["file_id"]
                st.write("File ID:", data["file_id"])
            else:
                st.error(resp.text)


# ----------------------------
# PAGE: EXTRACT
# ----------------------------
elif page == "Extract":
    st.header("📑 Extract Text")

    if "file_id" not in st.session_state:
        st.warning("Upload a file first!")
    else:
        if st.button("Extract Text"):
            fid = st.session_state.file_id
            resp = requests.get(f"{API_URL}/extract/{fid}")

            if resp.status_code == 200:
                data = resp.json()
                st.success("Text extracted!")
                st.text_area("Preview", data["preview_text"])
                st.session_state.extracted = True
            else:
                st.error(resp.text)


# ----------------------------
# PAGE: EMBED
# ----------------------------
elif page == "Embed":
    st.header("🧠 Generate Embeddings")

    if "extracted" not in st.session_state:
        st.warning("Extract text first!")
    else:
        if st.button("Create Embeddings"):
            fid = st.session_state.file_id
            resp = requests.post(f"{API_URL}/embed/{fid}")

            if resp.status_code == 200:
                st.success("Embeddings created!")
                st.session_state.embeddings_done = True
            else:
                st.error(resp.text)


# ----------------------------
# PAGE: QUERY
# ----------------------------
elif page == "Query":
    st.header("💬 Ask Questions")

    if "embeddings_done" not in st.session_state:
        st.warning("Create embeddings first!")
    else:
        q = st.text_input("Your question:")

        if st.button("Ask"):
            fid = st.session_state.file_id
            resp = requests.post(f"{API_URL}/query/", json={"question": q, "file_id": fid})

            if resp.status_code == 200:
                data = resp.json()
                st.success(data["answer"])

                st.subheader("Sources")
                for src in data["sources"]:
                    st.write(src)

            else:
                st.error(resp.text)