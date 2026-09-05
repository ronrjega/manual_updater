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
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,
