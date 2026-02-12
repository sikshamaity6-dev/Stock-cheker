#!/usr/bin/env python3
"""
Shein Wishlist Checker Bot (simple)
- Uses Playwright to fetch wishlist pages (handles JS-rendered content)
- Compares current snapshot to previous one stored in state.json
- Sends notifications via Telegram Bot API when detects changes
"""

import json
import os
import re
import time
from typing import Dict, List
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright

STATE_FILE = "state.json"
CONFIG_FILE = "config.json"

def load_config() -> Dict:
    if not os.path.exists(CONFIG_FILE):
        raise SystemExit(f"{CONFIG_FILE} not found. Copy config.example.json -> {CONFIG_FILE} and update it.")
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state: Dict):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def load_state() -> Dict:
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def normalize_price(raw: str) -> float:
    if not raw:
        return 0.0
    # keep digits, dots, commas; convert comma decimal to dot
    s = raw.replace(",", ".")
    m = re.findall(r"\d+(\.\d+)?", s)
    if not m:
        # fallback: extract first number-like token
        nums = re.findall(r"\d+", s)
        return float(nums[0]) if nums else 0.0
    # join integer + fraction if exist
    first = re.search(r"\d+(\.\d+)?", s)
    return float(first.group()) if first else 0.0

def send_telegram(token: str, chat_id: str, text: str):
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        resp = requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print("Telegram send failed:", e)

def extract_items_from_page(page) -> List[Dict]:
    # Run JS in page to find product anchors and try to extract title, price, link
    script = """ 
    () => {
      const anchors = Array.from(document.querySelectorAll('a[href*="/product/"], a[href*="/item/"]'));
      const seen = new Set();
      return anchors.map(a => {
        const container = a.closest('div') || a;
        let title = '';
        let price = '';
        try {
          // try several selectors commonly found
          title = (a.querySelector('img') && a.querySelector('img').alt) ||
                  (container.querySelector('.product-title') && container.querySelector('.product-title').innerText) ||
                  (container.querySelector('.S-product-card__title') && container.querySelector('.S-product-card__title').innerText) ||
                  (container.querySelector('.S-product-card__name') && container.querySelector('.S-product-card__name').innerText) ||
                  (a.getAttribute('title')) ||
                  (a.innerText) || '';
          price = (container.querySelector('.price') && container.querySelector('.price').innerText) ||
                  (container.querySelector('.S-product-price__current') && container.querySelector('.S-product-price__current').innerText) ||
                  (container.querySelector('.S-product-price__value') && container.querySelector('.S-product-price__value').innerText) ||
                  '';
        } catch (e) {}
        const href = a.href || '';
        const key = href || title;
        if (seen.has(key)) return null;
        seen.add(key);
        return { title: title.trim(), price: price.trim(), link: href };
      }).filter(Boolean);
    }
    """
    try:
        items = page.evaluate(script)
        # Ensure unique by link
        unique = []
        seen = set()
        for it in items:
            if not it.get("link"):
                key = it.get("title", "")[:60]
            else:
                key = it["link"]
            if key in seen:
                continue
            seen.add(key)
            unique.append(it)
        return unique
    except Exception as e:
        print("JS evaluation error:", e)
        return []

def item_key(item: Dict) -> str:
    # Use link as key if present, else title
    return item.get("link") or item.get("title") or ""

def format_message(event_type: str, item: Dict, old: Dict = None) -> str:
    title = item.get("title", "Unknown")
    link = item.get("link", "")
    price = item.get("price", "")
    msg = ""
    if event_type == "new":
        msg = f"🆕 New item in wishlist:\n<b>{title}</b>\nPrice: {price}\n{link}"
    elif event_type == "price_drop":
        msg = f"🔻 Price drop:\n<b>{title}</b>\nOld: {old.get('price', 'N/A')} → Now: {price}\n{link}"
    elif event_type == "price_up":
        msg = f"🔺 Price increased:\n<b>{title}</b>\nOld: {old.get('price', 'N/A')} → Now: {price}\n{link}"
    elif event_type == "removed":
        msg = f"❌ Removed from wishlist:\n<b>{title}</b>\nLast seen price: {old.get('price', 'N/A')}\n{link}"
    else:
        msg = f"ℹ️ Update for: <b>{title}</b>\nPrice: {price}\n{link}"
    return msg

def check_wishlists(config: Dict):
    token = config.get("telegram_token")
    chat_id = str(config.get("telegram_chat_id")) if config.get("telegram_chat_id") is not None else ""
    poll_delay = int(config.get("poll_interval_seconds", 300))
    wishlists = config.get("wishlist_urls", [])
    user_agent = config.get("user_agent", "Mozilla/5.0 (compatible)")

    state = load_state()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=user_agent)
        page = context.new_page()

        while True:
            any_changes = False
            new_state = state.copy()
            for url in wishlists:
                try:
                    print("Loading", url)
                    page.goto(url, wait_until="networkidle", timeout=30000)
                    time.sleep(1)  # little pause to let dynamic content settle
                    items = extract_items_from_page(page)
                    print(f"Found {len(items)} items on page.")
                    for it in items:
                        key = item_key(it)
                        if not key:
                            continue
                        new_price_val = normalize_price(it.get("price", ""))
                        prev = state.get(key)
                        if not prev:
                            # new item
                            print("New item:", it.get("title"))
                            msg = format_message("new", it, None)
                            send_telegram(token, chat_id, msg)
                            any_changes = True
                            new_state[key] = {"title": it.get("title"), "price": it.get("price")}
                        else:
                            prev_price_val = normalize_price(prev.get("price", ""))
                            if new_price_val != prev_price_val:
                                event = "price_drop" if new_price_val < prev_price_val else "price_up"
                                print(f"{event} detected for {it.get('title')}: {prev.get('price')} -> {it.get('price')}")
                                msg = format_message(event, it, prev)
                                send_telegram(token, chat_id, msg)
                                any_changes = True
                                new_state[key] = {"title": it.get("title"), "price": it.get("price")}
                            else:
                                # update title if changed
                                if it.get("title") != prev.get("title"):
                                    new_state[key] = {"title": it.get("title"), "price": it.get("price")}
                    # detect removals: keys previously present that are not in current scrape for this URL
                    # For simplicity we only mark removal if key contained the URL (best effort)
                    current_keys = {item_key(it) for it in items}
                    for prev_key in list(state.keys()):
                        if prev_key.startswith(url) or (prev_key and url in prev_key) or True:
                            # only check keys that look like they belong; here we do a conservative check:
                            if prev_key not in current_keys and prev_key in state:
                                # It may be just on another wishlist url; we avoid aggressive removal across multiple lists.
                                # Skip global removal unless you want that behavior.
                                pass

                except Exception as exc:
                    print("Error checking", url, ":", exc)

            if any_changes:
                save_state(new_state)
                state = new_state
            else:
                # keep previous state if unchanged
                save_state(state)

            print(f"Sleeping {poll_delay} seconds...")
            time.sleep(poll_delay)

if __name__ == "__main__":
    config = load_config()
    check_wishlists(config)