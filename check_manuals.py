import json
import os
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

DEVICES = [
    {
        "id": "reliq",
        "name": "Reliq",
        "page_url": "https://reliq-instruments.com/pages/support",
        "heading": "Reliq manual",
        "keyword": "download pdf",
    },
    {
        "id": "bitbox_mk2",
        "name": "1010music bitbox mk2",
        "page_url": "https://1010music.com/downloads",
        "heading": "bitbox mk2",
        "keyword": "user manual",
    },
]

STATE_FILE = "state.json"
PCLOUD_FOLDER = "/schaltraum_productions/samples/software_and_drivers/manuals"
WEBDAV_BASE = "https://ewebdav.pcloud.com"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/128.0.0.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def extract_manual_url(page_url, heading_text, keyword):
    resp = requests.get(page_url, timeout=30, headers=HEADERS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    heading = soup.find(
        lambda tag: tag.name in ["h1", "h2", "h3"]
        and tag.get_text(strip=True).lower() == heading_text.lower()
    )
    if not heading:
        raise RuntimeError(f"Heading '{heading_text}' not found on {page_url}")
    for el in heading.find_all_next():
        if el.name in ["h1", "h2"] and el is not heading:
            break
        if el.name == "a" and keyword in el.get_text(strip=True).lower():
            href = el.get("href")
            if href:
                return href
    raise RuntimeError(f"No link containing '{keyword}' found under heading '{heading_text}'")


def webdav_auth():
    return (os.environ["PCLOUD_USER"], os.environ["PCLOUD_PASSWORD"])


def webdav_url(path):
