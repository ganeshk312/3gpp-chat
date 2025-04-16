import os
import requests
from bs4 import BeautifulSoup
from llama_index.core import VectorStoreIndex, ServiceContext
from llama_index.llms.ghostwriter import Gemini
from llama_index.readers.file import PDFReader
from llama_index.embeddings.google import GeminiEmbedding
from llama_index.core.storage import StorageContext, load_index_from_storage
from pathlib import Path

def get_all_pdf_links(root_url):
    visited = set()
    pdf_links = []

    def crawl(url):
        if url in visited:
            return
        visited.add(url)

        try:
            r = requests.get(url)
            r.raise_for_status()
        except:
            return

        soup = BeautifulSoup(r.text, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.endswith('.pdf'):
                full_link = requests.compat.urljoin(url, href)
                pdf_links.append(full_link)
            elif href.endswith('/') or href.endswith('.html'):
                sub_url = requests.compat.urljoin(url, href)
                crawl(sub_url)

    crawl(root_url)
    return pdf_links

def download_pdfs(pdf_urls, dest_dir):
    for url in pdf_urls:
        filename = os.path.join(dest_dir, url.split("/")[-1])
        if not os.path.exists(filename):
            r = requests.get(url)
            with open(filename, 'wb') as f:
                f.write(r.content)

def build_or_load_index(pdf_dir, persist_dir="index_storage"):
    if os.path.exists(persist_dir):
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        index = load_index_from_storage(storage_context)
    else:
        documents = PDFReader().load_data(Path(pdf_dir))
        service_context = ServiceContext.from_defaults(
            chunk_size=1024,
            llm=Gemini(api_key=os.environ["GEMINI_API_KEY"]),
            embed_model=GeminiEmbedding(api_key=os.environ["GEMINI_API_KEY"])
        )
        index = VectorStoreIndex.from_documents(documents, service_context=service_context)
        index.storage_context.persist(persist_dir)
    return index

