import streamlit as st
import requests

# toggle icon state
if "sidebar" not in st.session_state:
    st.session_state.sidebar = False

# toggle function
def toggle_sidebar():
    st.session_state.sidebar = not st.session_state.sidebar

# toggle button (hamburger icon)
st.button("☰", on_click=toggle_sidebar)

# show / hide sidebar
if st.session_state.sidebar:
    with st.sidebar:
        st.title("Menu")
        page = st.radio("Go to:", ["Home", "Upload File", "Chat"])
else:
    page = "Home"   # default page when sidebar is hidden

# page content
if page == "Home":
    st.title("Home Page")
    st.write("Welcome to the ChatZ!")
    

elif page == "Upload File":
    # st.title("Upload File Page")
    # st.write("Upload your pdf here!")

    # -------------------------
    # UPLOAD BLOCK (Box Style)
    # -------------------------
    st.markdown("""
        <style>
            .upload-block {
                background: #ffffff;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.15);
                margin-top: 20px;
            }
        </style>
    """, unsafe_allow_html=True)

    # st.markdown('<div class="upload-block">', unsafe_allow_html=True)
    

    st.subheader("📄 Upload PDF")
    
    st.markdown("""
    <style>
        div[data-testid="file-uploader"] label {
            font-size: 80px;  /* Increase font size */
            font-weight: bold; /* Make it bold like subheader */
        }
    </style>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    # STATUS MESSAGE
    status_placeholder = st.empty()

    if uploaded_file is not None:
        status_placeholder.info("📤 Uploading file to backend...")

        try:
            # send file to backend API
            files = {"file": uploaded_file}
            response = requests.post("http://127.0.0.1:8000/upload", files=files)

            if response.status_code == 200:
                status_placeholder.success("✅ File uploaded successfully!")
            else:
                status_placeholder.error(f"❌ Upload failed: {response.text}")

        except Exception as e:
            status_placeholder.error(f"⚠️ Error: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Chat":
    st.title("Chat Page")
    st.write("Start chatting with your bot here!")


