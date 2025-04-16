import streamlit as st
import tempfile
import os
from utils import get_all_pdf_links, download_pdfs, build_or_load_index

st.set_page_config(page_title="3GPP Spec Assistant (Gemini)", layout="wide")
st.title("📡 3GPP Standards Chatbot (Powered by Google Gemini)")

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

root_url = st.text_input("Enter 3GPP spec index root URL:", "https://your-3gpp-folder.com/")
run = st.button("Build Knowledge Base")

if run:
    with st.spinner("Crawling and indexing documents..."):
        pdf_links = get_all_pdf_links(root_url)
        st.success(f"Found {len(pdf_links)} PDF documents.")
        with tempfile.TemporaryDirectory() as tmpdir:
            download_pdfs(pdf_links, tmpdir)
            index = build_or_load_index(tmpdir)
            st.session_state.index = index
            st.success("Knowledge base is ready! You can now ask questions.")

if "index" in st.session_state:
    user_input = st.text_input("Ask a question about 3GPP standards:")
    if user_input:
        query_engine = st.session_state.index.as_query_engine(similarity_top_k=3)
        response = query_engine.query(user_input)
        st.write("### ✅ Answer:")
        st.write(response.response)

        st.write("### 📎 Sources:")
        for s in response.source_nodes:
            st.markdown(f"- `{s.metadata.get('file_path')}` (Score: {s.score:.2f})")

