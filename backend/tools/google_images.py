"""
Wellsy Tools -- Google Images Automation
Search Google Images and download image results from the desktop.
"""
import os
import re
import json
import subprocess
import time
import requests
from urllib.parse import quote_plus
from langchain_core.tools import tool


# Chrome executable path
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# Default download directory for images
DEFAULT_DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "Wellsy_Images")

# Request headers to mimic a real browser visit
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def _open_chrome_url(url: str) -> None:
    """Open a URL in Chrome (new tab if Chrome is already running)."""
    subprocess.Popen([CHROME_PATH, url])


def _build_search_url(query: str) -> str:
    """Build a Google Images search URL for the given query."""
    encoded = quote_plus(query)
    return f"https://www.google.com/search?tbm=isch&q={encoded}"


def _scrape_image_urls(query: str, max_results: int = 5) -> list:
    """
    Fetch the Google Images search page and extract image URLs.

    Uses the requests library to GET the search page, then parses
    image URLs from the response. Google embeds image metadata as
    JSON-like structures inside the HTML which we can extract with
    regex patterns.

    Returns a list of image URL strings (up to max_results).
    """
    url = _build_search_url(query)
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[Google Images] Request failed: {e}")
        return []

    html = resp.text
    image_urls = []

    # Strategy 1: Extract full-size image URLs from Google's embedded JSON data.
    # Google embeds image info in patterns like ["https://...jpg",width,height]
    pattern = r'\["(https?://[^"]+\.(?:jpg|jpeg|png|gif|bmp|webp))",[0-9]+,[0-9]+\]'
    matches = re.findall(pattern, html, re.IGNORECASE)
    for match in matches:
        # Filter out Google's own assets / tracking pixels
        if "gstatic.com" in match or "google.com" in match:
            continue
        if match not in image_urls:
            image_urls.append(match)
        if len(image_urls) >= max_results:
            break

    # Strategy 2 (fallback): Look for thumbnail data URIs are not useful,
    # so try to find image src attributes from <img> tags as a backup.
    if not image_urls:
        img_pattern = r'<img[^>]+src="(https?://[^"]+)"'
        img_matches = re.findall(img_pattern, html)
        for src in img_matches:
            if "gstatic.com" in src or "google.com" in src or "googleapis.com" in src:
                continue
            if src not in image_urls:
                image_urls.append(src)
            if len(image_urls) >= max_results:
                break

    return image_urls


def _download_image(url: str, save_path: str) -> bool:
    """Download a single image from a URL and save it to save_path."""
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=20, stream=True)
        resp.raise_for_status()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"[Google Images] Failed to download {url}: {e}")
        return False


def _get_file_extension(url: str) -> str:
    """Extract file extension from URL, default to .jpg."""
    for ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]:
        if ext in url.lower().split("?")[0]:
            return ext
    return ".jpg"


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@tool
def search_images(query: str) -> str:
    """Search Google Images for a query. Opens Chrome with Google Image search results for the specified keywords."""
    url = _build_search_url(query)
    try:
        _open_chrome_url(url)
        print(f"[Google Images] Searching for: {query}")
        return f"Opened Google Images search results for '{query}'."
    except FileNotFoundError:
        return "Could not find Chrome. Is Google Chrome installed?"
    except Exception as e:
        return f"Error searching Google Images: {e}"


@tool
def download_images(query: str, num_images: int = 3, save_dir: str = "") -> str:
    """Download images from Google Images search results.

    Searches Google Images for the given query and downloads up to num_images
    results. Images are saved to save_dir (defaults to ~/Downloads/Wellsy_Images/<query>/).
    Returns a summary with the file paths of downloaded images.
    """
    if not save_dir:
        # Sanitize query for use as a folder name
        safe_name = re.sub(r'[^\w\s-]', '', query).strip().replace(' ', '_')
        save_dir = os.path.join(DEFAULT_DOWNLOAD_DIR, safe_name)

    os.makedirs(save_dir, exist_ok=True)

    print(f"[Google Images] Scraping image URLs for: {query}")
    urls = _scrape_image_urls(query, max_results=num_images)

    if not urls:
        return (
            f"Could not find any image URLs for '{query}'. "
            "Google may have blocked the request or the page structure changed."
        )

    downloaded = []
    for i, url in enumerate(urls):
        ext = _get_file_extension(url)
        filename = f"{re.sub(r'[^\\w\\s-]', '', query).strip().replace(' ', '_')}_{i+1}{ext}"
        filepath = os.path.join(save_dir, filename)
        print(f"[Google Images] Downloading image {i+1}/{len(urls)}...")
        if _download_image(url, filepath):
            downloaded.append(filepath)
            print(f"[Google Images] Saved: {filepath}")
        else:
            print(f"[Google Images] Skipped image {i+1} (download failed)")

    if not downloaded:
        return f"Found {len(urls)} image URL(s) but all downloads failed for '{query}'."

    paths_str = "\n".join(f"  - {p}" for p in downloaded)
    return (
        f"Downloaded {len(downloaded)} image(s) for '{query}' to {save_dir}:\n{paths_str}"
    )


@tool
def get_image_urls(query: str, num_results: int = 5) -> str:
    """Get image URLs from Google Images without downloading.

    Searches Google Images for the given query and returns up to num_results
    image URLs as a list. Useful when you just need the links.
    """
    print(f"[Google Images] Fetching image URLs for: {query}")
    urls = _scrape_image_urls(query, max_results=num_results)

    if not urls:
        return (
            f"Could not find any image URLs for '{query}'. "
            "Google may have blocked the request or the page structure changed."
        )

    urls_str = "\n".join(f"  {i+1}. {u}" for i, u in enumerate(urls))
    return f"Found {len(urls)} image URL(s) for '{query}':\n{urls_str}"


# Export all tools
GOOGLE_IMAGES_TOOLS = [
    search_images,
    download_images,
    get_image_urls,
]
