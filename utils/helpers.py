# Helper functions for image encoding and parsing
import os
import base64
import re
import html

def img_to_b64_data_uri(path: str) -> str:
    with open(path, "rb") as f:
        b = f.read()
    ext = os.path.splitext(path)[1].lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(b).decode('utf-8')}"

def split_recommendations(raw: str) -> list:
    if not raw or not isinstance(raw, str):
        return []
    parts = re.split(r"===\s*Recommendation\s*\d+\s*===", raw)
    parts = [p.strip() for p in parts if p and p.strip()]
    if parts:
        return parts
    fallback = re.split(r"\n\s*\d+\s*[\.)]", raw)
    fallback = [p.strip() for p in fallback if p and p.strip()]
    return fallback if fallback else [raw.strip()]

def parse_recommendation(rec_text: str):
    if not rec_text:
        return [], ""
    rec = re.sub(r"\s+", " ", rec_text).strip()
    sel_items = []
    st_match = ""
    sel_match = re.search(r"\*{0,2}\s*Selected Items:\s*\*{0,2}(.*?)(\*{0,2}\s*Styling Notes:|$)", rec, flags=re.IGNORECASE)
    if sel_match:
        items_blob = sel_match.group(1).strip()
        parts = re.split(r"(?:-\s*Item\s*\d+:|-)+\s*", items_blob)
        sel_items = [p.strip() for p in parts if p.strip()]
    st_match = re.search(r"\*{0,2}\s*Styling Notes:\s*\*{0,2}(.*)", rec, flags=re.IGNORECASE)
    if st_match:
        styling_blob = st_match.group(1).strip()
    else:
        styling_blob = rec[len(sel_match.group(0)):] if sel_match else rec
    sentences = re.split(r"(?<=[.!?])\s+", styling_blob)
    short = " ".join(sentences[:]).strip()
    if not short:
        short = (styling_blob[:220] + "...") if len(styling_blob) > 220 else styling_blob
    return sel_items, short
