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
        page = st.radio("Navigate:", ["Home", "Upload File", "Chat"])
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
            upload_to_backend(uploaded_file)
            

# ------------------------------------
# PAGE: EXTRACT
# ------------------------------------

# ------------------------------------
# PAGE: EMBEDDING
# ------------------------------------


# ------------------------------------
# PAGE: Chat
# ------------------------------------


