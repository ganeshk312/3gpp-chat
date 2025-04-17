import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import fitz  # PyMuPDF

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

            # Skip [To Parent Directory] or "../"
            if href.strip() == "../" or "parent" in link.text.lower():
                continue

            full_url = urljoin(url, href)

            # Make sure we stay under root_url
            if not full_url.startswith(root_url):
                continue

            if href.endswith(".pdf"):
                pdf_links.append(full_url)
            elif href.endswith("/") or href.endswith(".html"):
                crawl(full_url)

    crawl(root_url)
    return pdf_links

def download_pdfs(pdf_urls, dest_dir):
    for url in pdf_urls:
        filename = os.path.join(dest_dir, url.split("/")[-1])
        if not os.path.exists(filename):
            r = requests.get(url)
            with open(filename, 'wb') as f:
                f.write(r.content)

def extract_text_chunks(pdf_dir, chunk_size=1000):
    chunks = []
    for filename in os.listdir(pdf_dir):
        if filename.endswith('.pdf'):
            doc = fitz.open(os.path.join(pdf_dir, filename))
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            for i in range(0, len(full_text), chunk_size):
                chunk = full_text[i:i+chunk_size]
                chunks.append({"text": chunk, "source": filename})
    return chunks
