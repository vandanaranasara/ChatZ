import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="ChatZ", layout="wide")
st.title("📚 ChatZ – PDF AI Assistant")

# Initialize session keys
if "file_id" not in st.session_state:
    st.session_state.file_id = None
if "extracted" not in st.session_state:
    st.session_state.extracted = False
if "embeddings_done" not in st.session_state:
    st.session_state.embeddings_done = False

# ----------------------------
# ACCESS CONTROL
# ----------------------------

def restrict(page):
    """Show an error & stop page execution if access is invalid."""

    fid = st.session_state.file_id
    extracted = st.session_state.extracted
    embedded = st.session_state.embeddings_done

    # CONDITION 3 → No file
    if fid is None:
        if page != "Upload":
            st.error("❌ Please upload a PDF first.")
            st.stop()

    # CONDITION 2 → File uploaded but NO embeddings
    if fid and not embedded:
        if page not in ["Extract", "Embed"]:
            st.error("⚠️ Embeddings not ready. Please Extract → Embed first.")
            st.stop()

    # CONDITION 1 → File + embeddings ready
    if fid and embedded:
        if page != "Query":
            st.error("✔ Embeddings ready. Access allowed only to Query page.")
            st.stop()

# Sidebar Navigation
page = st.sidebar.radio("Navigation", ["Upload", "Extract", "Embed", "Query"])
restrict(page)



# ----------------------------
# PAGE: UPLOAD
# ----------------------------

if page == "Upload":
    st.header("📤 Upload PDF")

    # ---- Fetch existing uploaded PDFs from DB ----
    try:
        list_resp = requests.get(f"{API_URL}/upload/list_files")
        if list_resp.status_code == 200:
            pdf_files = list_resp.json()
        else:
            pdf_files = []
            st.warning("Could not load existing files.")
    except:
        pdf_files = []
        st.warning("Server not reachable.")

    # ---- Show dropdown of uploaded PDFs ----
    st.subheader("📂 Existing Uploaded PDFs")

    if pdf_files:
        # Dropdown list of file names
        file_names = [f"{pdf['file_name']}" 
                      for pdf in pdf_files]

        selected = st.selectbox("Select a file to view details:", ["-- Select --"] + file_names)

        if selected != "-- Select --":
            selected_index = file_names.index(selected)
            selected_file = pdf_files[selected_index]

            st.info("### File Metadata")
            st.json(selected_file)
    else:
        st.info("No files uploaded yet.")

    st.write("---")

    # ---- Upload new file ----
    st.subheader("📤 Upload a New PDF")

    uploaded = st.file_uploader("Select PDF file", type=["pdf"])

    if uploaded and st.button("Upload File"):
        files = {"file": uploaded}
        resp = requests.post(f"{API_URL}/upload/upload_file", files=files)

        if resp.status_code == 200:
            data = resp.json()

            st.session_state.file_id = data["file_id"]
            st.session_state.file_name = data["file_name"]
            st.session_state.embeddings_done = data["embedding_status"]
            st.session_state.extracted = False

            if st.session_state.embeddings_done:
                st.success("🎉 File exists and embeddings already available. Go to Query!")
            else:
                st.info("File uploaded. Please extract text.")

        else:
            st.error(resp.text)


# ----------------------------
# PAGE: EXTRACT
# ----------------------------
elif page == "Extract":
    st.header("📑 Extract Text")

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

    if not st.session_state.extracted:
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

    q = st.text_input("Your question:")

    if st.button("Ask"):
        fid = st.session_state.file_id
        resp = requests.post(f"{API_URL}/query/", json={"question": q, "file_id": fid})

        if resp.status_code == 200:
            data = resp.json()
            st.success(data["answer"])

        else:
            st.error(resp.text)
