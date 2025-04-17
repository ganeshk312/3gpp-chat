import streamlit as st
import os
import tempfile
import google.generativeai as genai
from utils import get_all_pdf_links, download_pdfs, extract_text_chunks

st.set_page_config(page_title="3GPP Spec Chatbot (Gemini)", layout="wide")
st.title("📡 3GPP Standards Chatbot (Google Gemini)")

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

root_url = st.text_input("Enter root folder URL for 3GPP PDFs:")
run = st.button("📄 Build Knowledge Base")

if run:
    with st.spinner("Crawling and indexing PDF documents..."):
        pdf_links = get_all_pdf_links(root_url)
        st.success(f"Found {len(pdf_links)} PDFs")
        with tempfile.TemporaryDirectory() as tmpdir:
            download_pdfs(pdf_links, tmpdir)
            chunks = extract_text_chunks(tmpdir)
            st.session_state.chunks = chunks
            st.success("✅ Documents loaded and indexed!")

if "chunks" in st.session_state:
    prompt = st.text_input("Ask your 3GPP question:")
    if prompt:
        with st.spinner("Thinking..."):
            relevant = [
                c for c in st.session_state.chunks
                if any(word in c["text"].lower() for word in prompt.lower().split())
            ][:5]

            context = "\n\n---\n\n".join(f"{c['text']}\n(Source: {c['source']})" for c in relevant)

            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(f"""You are a technical assistant for 3GPP standards.

Use the context below to answer the question. Mention which document (source) it came from if relevant.

Context:
{context}

Question: {prompt}
""")

            st.write("### ✅ Answer")
            st.write(response.text)
