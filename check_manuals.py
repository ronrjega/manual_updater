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
HEADERS = {"User-Agent": "Mozilla/5.0"}


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
    return WEBDAV_BASE + quote(path)


def upload_to_pcloud(path, content):
    resp = requests.put(webdav_url(path), data=content, auth=webdav_auth(), timeout=60)
    resp.raise_for_status()


def delete_from_pcloud(path):
    resp = requests.delete(webdav_url(path), auth=webdav_auth(), timeout=30)
    if resp.status_code not in (200, 204, 404):
        resp.raise_for_status()


def main():
    state = load_state()
    changed = False
    for device in DEVICES:
        did = device["id"]
        try:
            manual_url = extract_manual_url(device["page_url"], device["heading"], device["keyword"])
        except Exception as e:
            print(f"[{did}] Fehler beim Prüfen: {e}")
            continue

        prev = state.get(did, {})
        if prev.get("manual_url") == manual_url:
            print(f"[{did}] Keine Änderung.")
            continue

        print(f"[{did}] Neue Version gefunden: {manual_url}")
        pdf_resp = requests.get(manual_url, timeout=60, headers=HEADERS)
        pdf_resp.raise_for_status()

        filename = manual_url.rsplit("/", 1)[-1]
        new_path = f"{PCLOUD_FOLDER}/{filename}"
        old_path = prev.get("pcloud_path")

        if old_path and old_path != new_path:
            print(f"[{did}] Lösche alte Datei: {old_path}")
            delete_from_pcloud(old_path)

        print(f"[{did}] Lade hoch: {new_path}")
        upload_to_pcloud(new_path, pdf_resp.content)

        state[did] = {"manual_url": manual_url, "pcloud_path": new_path}
        changed = True

    save_state(state)
    if changed:
        print("STATE_CHANGED")


if __name__ == "__main__":
    main()
