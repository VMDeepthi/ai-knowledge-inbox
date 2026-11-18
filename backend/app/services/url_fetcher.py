import ipaddress
import socket
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup

def _validate_url(url: str):
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Please provide a valid http or https URL.")
    host = parsed.hostname.lower()
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
        raise ValueError("Local URLs are not allowed.")
    try:
        addresses = socket.getaddrinfo(host, None)
        for address in addresses:
            ip = ipaddress.ip_address(address[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                raise ValueError("URLs resolving to private or local addresses are not allowed.")
    except socket.gaierror:
        raise ValueError("Could not resolve the URL hostname.")

def fetch_page(url: str) -> tuple[str, str]:
    _validate_url(url)
    headers = {"User-Agent": "AIKnowledgeInbox/1.0"}
    with httpx.Client(timeout=15.0, follow_redirects=False, headers=headers) as client:
        response = client.get(url)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type:
            raise ValueError("The URL must return an HTML page.")
        if len(response.content) > 2_000_000:
            raise ValueError("The webpage is too large (2 MB maximum).")
    soup = BeautifulSoup(response.text, "html.parser")
    for node in soup(["script", "style", "nav", "footer", "header", "noscript", "svg"]):
        node.decompose()
    title = soup.title.get_text(" ", strip=True) if soup.title else url
    main = soup.find("main") or soup.find("article") or soup.body or soup
    text = main.get_text(" ", strip=True)
    if len(text) < 30:
        raise ValueError("Could not extract enough readable text from this webpage.")
    return title[:500], text[:100_000]
