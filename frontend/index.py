import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="ChatZ", layout="wide")

# ------------------------------------
# CSS for better UI
# ------------------------------------
st.markdown("""
<style>
/* Center container for a cleaner look */
.main-container {
    max-width: 850px;
    margin: auto;
}

/* Floating hamburger button */
.hamburger-btn {
    position: fixed;
    top: 15px;
    left: 15px;
    z-index: 9999;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------
# Toggle Sidebar State
# ------------------------------------
if "sidebar" not in st.session_state:
    st.session_state.sidebar = False

def toggle_sidebar():
    st.session_state.sidebar = not st.session_state.sidebar

# Floating Hamburger Button
with st.container():
    st.markdown('<div class="hamburger-btn">', unsafe_allow_html=True)
    st.button("☰", on_click=toggle_sidebar)
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------
# Sidebar
# ------------------------------------
if st.session_state.sidebar:
    with st.sidebar:
        st.title("Menu")
        page = st.radio("Navigate:", ["Home", "Upload File"])
else:
    page = "Home"

# Page Container
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# ------------------------------------
# PAGE: HOME
# ------------------------------------
if page == "Home":
    st.title("🏠 Home")
    st.write("Welcome to **ChatZ** — your AI-powered assistant!")
    

# ------------------------------------
# PAGE: UPLOAD
# ------------------------------------
elif page == "Upload File":
    st.title("📤 Upload PDF")
    st.write("Upload your document to process it.")

    uploaded_file = st.file_uploader("Select PDF File", type=["pdf"])
    status = st.empty()

    # Upload function
    def upload_to_backend(file):
        status.info("📡 Uploading... Please wait.")
        try:
            files = {"file": file}
            resp = requests.post(f"{API_URL}/upload/upload_file", files=files)

            if resp.status_code == 200:
                status.success("✅ File uploaded successfully!")
                return resp.json()
            else:
                status.error(f"❌ Failed: {resp.text}")
                return None
        except Exception as e:
            status.error(f"⚠️ Error: {e}")

    # Upload on file selection
    if uploaded_file:
        with st.spinner("Processing..."):
            response = upload_to_backend(uploaded_file)
            if response and "file_id" in response:
                st.session_state.uploaded_file_id = response["file_id"]
            

# ------------------------------------
# PAGE: EXTRACT
# ------------------------------------

if page == "Upload File":

    # Only show extract if a file was successfully uploaded
    if "uploaded_file_id" in st.session_state and st.session_state.uploaded_file_id:

        st.markdown("---")
        st.subheader("📑 Extract Text")
        extract_status = st.empty()
        preview_area = st.empty()

        # Extract button
        if st.button("🔍 Extract"):
            with st.spinner("Extracting text..."):
                try:
                    file_id = st.session_state.uploaded_file_id
                    resp = requests.get(f"{API_URL}/extract/{file_id}")
                    if resp.status_code == 200:
                        data = resp.json()
                        preview_text = data.get("preview_text", "")
                        extract_status.success("✅ Text extracted successfully!")
                        preview_area.text_area("Preview Extracted Text", preview_text, height=300)
                    else:
                        extract_status.error(f"❌ Extract failed: {resp.text}")
                except Exception as e:
                    extract_status.error(f"⚠️ Error: {e}")
                    
                    
# ------------------------------------
# PAGE: EMBEDDING
# ------------------------------------


# ------------------------------------
# PAGE: Chat
# ------------------------------------


