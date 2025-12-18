import os
import html
import random
import json
import streamlit as st
from PIL import Image
from dotenv import load_dotenv

from core.stylist import get_outfit_recommendation
from core.analyzer import analyze_clothing
from core.database import load_closet_data, save_item
from utils.helpers import img_to_b64_data_uri, split_recommendations, parse_recommendation

# --- Config ---
st.set_page_config(page_title="AI Personal Stylist v3", page_icon="👗", layout="wide", initial_sidebar_state="auto")
load_dotenv()
VARIATION_COUNT = int(os.getenv("VARIATION_COUNT", "3"))

# Inject CSS
with open(os.path.join("assets", "style.css")) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def generate_mannequin_outfit(recommendation_text: str, closet_data: list[dict]):
    rec_lower = recommendation_text.lower()
    selected_items = []
    for item in closet_data:
        item_id = str(item.get("id", ""))
        p = item.get("image_path")
        if p and os.path.exists(p):
            if f"item {item_id}:" in rec_lower or f"item {item_id} :" in rec_lower:
                selected_items.append(item)
    if not selected_items:
        return "No matching clothing items with images found in recommendation."
    image_paths = [i["image_path"] for i in selected_items if i.get("image_path")]
    if not image_paths:
        return "No images found for selected items."
    return {"selected_items": selected_items, "image_paths": image_paths}

def render_recommendation_panel_html(rec: str, outfit_result: object) -> None:
    if not rec:
        st.markdown("<div class='muted'>No recommendation yet. Describe an occasion and click \"Get Stylist Advice\".</div>", unsafe_allow_html=True)
        return
    rec_html_tiles = ""
    items = []
    if isinstance(outfit_result, dict) and outfit_result.get("selected_items"):
        items = outfit_result["selected_items"]
        tiles = []
        for idx, it in enumerate(items):
            uri = img_to_b64_data_uri(it["image_path"]) if it.get("image_path") else ""
            cls = "rec-card wide" if idx == 2 else "rec-card"
            meta = html.escape((it.get("item_type", "") + (" • " + it.get("color", "") if it.get("color") else "")).strip())
            caption = (
                f"<div class='rec-caption'>"
                f"<div class='meta'>{meta}</div>"
                f"</div>"
            )
            tiles.append(f"<div class='{cls}'><img src='{uri}' alt='rec'/> {caption}</div>")
        rec_html_tiles = f"<div class='rec-grid'>{''.join(tiles)}</div>"
    sel_items, short_notes = parse_recommendation(rec)
    # Extract full styling notes (not truncated)
    # parse_recommendation returns (selected_items, short_notes), but we want the full styling notes
    # We'll extract it directly here
    import re
    st_match = re.search(r"\*{0,2}\s*Styling Notes:\s*\*{0,2}(.*)", rec, flags=re.IGNORECASE | re.DOTALL)
    if st_match:
        full_styling_notes = st_match.group(1).strip()
    else:
        # fallback: everything after 'Styling Notes:'
        idx = rec.lower().find('styling notes:')
        full_styling_notes = rec[idx+len('styling notes:'):].strip() if idx != -1 else rec.strip()
    panel_html = f"""
<div class='rec-panel'>
  {rec_html_tiles}
  <div class='rec-description'>{html.escape(full_styling_notes)}</div>
</div>
"""
    st.markdown(panel_html, unsafe_allow_html=True)

# --- UI ---
container = st.container()
with container:
    cols = st.columns([7, 5], gap="large")
    left_col, right_col = cols
    with left_col:
        st.markdown("<div class='title'>Outfit Builder</div>", unsafe_allow_html=True)
        st.markdown("<div class='subtitle'>Curate your perfect look for any occasion</div>", unsafe_allow_html=True)
        occasion = st.text_input("Occasion", value="First date", placeholder="Where are you going?", key="v3_query", label_visibility="collapsed")
        action_cols = st.columns([3, 1], gap="small")
        default_index = max(0, min(VARIATION_COUNT, 5) - 1)
        with action_cols[0]:
            num_opts = st.selectbox("Options", options=[1, 2, 3, 4, 5], index=default_index, format_func=lambda x: f"{x} options", key="v3_variation_count", label_visibility="collapsed")
        with action_cols[1]:
            if st.button("Get Stylist Advice", key="v3_advice", help="Get an outfit suggestion", type="primary"):
                if not occasion.strip():
                    st.warning("Please enter an occasion or situation.")
                else:
                    closet_data = load_closet_data()
                    if not closet_data:
                        st.warning("Your closet is empty — please add some clothes first.")
                    else:
                        with st.spinner("Generating recommendations..."):
                            seed = random.randint(0, 999999999)
                            selected_variations = int(st.session_state.get("v3_variation_count", num_opts))
                            raw = get_outfit_recommendation(occasion, json.dumps(closet_data, indent=2), num_variations=selected_variations, temperature=0.8, seed=seed)
                            recs = split_recommendations(raw)
                            if not recs:
                                st.error("Failed to parse recommendations from the model response.")
                            else:
                                st.session_state["last_recommendations_v3"] = recs
                                st.session_state["last_recommendation_index_v3"] = 0
                                st.session_state["last_recommendation_v3"] = recs[0]
                                st.session_state["last_outfit_result_v3"] = generate_mannequin_outfit(recs[0], closet_data)
                                st.session_state["last_reroll_seed_v3"] = seed
                            st.session_state["last_reroll_seed_v3"] = seed
        # with st.container():
        #     st.markdown("<div class='mobile-only'>", unsafe_allow_html=True)
        #     render_recommendation_panel_html(st.session_state.get("last_recommendation_v3"), st.session_state.get("last_outfit_result_v3"))
        #     st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='display:flex;justify-content:space-between;align-items:center;margin-top:12px'><h2 style='margin:0;font-family:Playfair Display, serif'>Closet</h2></div>", unsafe_allow_html=True)
        with st.expander("Add Clothes", expanded=False):
            upload_mode = st.radio(
                "Mode",
                ["Single", "Multiple"],
                horizontal=True,
                label_visibility="collapsed",
                key="v3_upload_mode",
            )
            if upload_mode == "Single":
                uploaded_file = st.file_uploader(
                    "Upload",
                    type=["jpg", "jpeg", "png"],
                    key="v3_uploader",
                    label_visibility="collapsed",
                )
                if uploaded_file is not None:
                    image = Image.open(uploaded_file)
                    st.image(image, use_container_width=True)
                    if st.button("Analyze", key="v3_analyze_btn", use_container_width=True):
                        with st.spinner("Analyzing…"):
                            result = analyze_clothing(image)
                            try:
                                st.session_state["last_analysis_v3"] = json.loads(result)
                                st.session_state["last_image_v3"] = image
                                st.success("Analyzed!")
                            except Exception:
                                st.error("Failed to analyze (invalid JSON). See raw output for debugging.")
                                with st.expander("Raw analysis output", expanded=False):
                                    st.code(result)
                    if st.session_state.get("last_analysis_v3") and st.session_state.get("last_image_v3"):
                        if st.button("Save", key="v3_save_btn", use_container_width=True):
                            image_filename = f"item_{len(load_closet_data())}.jpg"
                            image_path = os.path.join("data/closet_images", image_filename)
                            try:
                                img_to_save = st.session_state["last_image_v3"].convert("RGB") if getattr(st.session_state["last_image_v3"], "mode", None) != "RGB" else st.session_state["last_image_v3"]
                                img_to_save.save(image_path, format="JPEG", quality=95)
                                if save_item(st.session_state["last_analysis_v3"], image_path):
                                    st.success("Saved to closet")
                                    st.session_state.pop("last_analysis_v3", None)
                                    st.session_state.pop("last_image_v3", None)
                                    st.rerun()
                                else:
                                    st.error("Failed to save metadata")
                            except Exception as e:
                                st.error(f"Failed to save image: {e}")
            else:
                uploaded_files = st.file_uploader(
                    "Upload Multiple",
                    type=["jpg", "jpeg", "png"],
                    accept_multiple_files=True,
                    key="v3_multi_uploader",
                    label_visibility="collapsed",
                )
                if uploaded_files and st.button("Analyze & Save All", key="v3_analyze_save_all", use_container_width=True):
                    existing = load_closet_data()
                    next_id = len(existing)
                    progress = st.progress(0)
                    success_count = 0
                    for idx, uf in enumerate(uploaded_files):
                        try:
                            image = Image.open(uf)
                            result = analyze_clothing(image)
                            parsed = None
                            try:
                                parsed = json.loads(result)
                            except Exception:
                                start = result.find("{")
                                end = result.rfind("}")
                                if start != -1 and end != -1 and end > start:
                                    try:
                                        parsed = json.loads(result[start : end + 1])
                                    except Exception:
                                        parsed = None
                            image_filename = f"item_{next_id}.jpg"
                            next_id += 1
                            image_path = os.path.join("data/closet_images", image_filename)
                            saved_image = False
                            try:
                                img_to_save = image.convert("RGB") if getattr(image, "mode", None) != "RGB" else image
                                img_to_save.save(image_path, format="JPEG", quality=95)
                                saved_image = True
                            except Exception:
                                saved_image = False
                            if parsed is not None and saved_image:
                                if isinstance(parsed, dict):
                                    parsed["analysis_raw"] = result
                                if save_item(parsed, image_path):
                                    success_count += 1
                        except Exception:
                            pass
                        progress.progress((idx + 1) / len(uploaded_files))
                    st.success(f"Added {success_count}/{len(uploaded_files)} items!")
                    st.rerun()
        closet_data = load_closet_data()
        if closet_data:
            tiles = []
            for it in closet_data:
                p = it.get("image_path")
                name = it.get("description", "Item")
                item_type = it.get("item_type", "")
                color = it.get("color", "")
                if p and os.path.exists(p):
                    uri = img_to_b64_data_uri(p)
                    title = html.escape(name[:40])
                    meta = html.escape((item_type + (" • " + color) if item_type or color else "").strip())
                    tiles.append(
                        f"<div class='closet-card'>"
                        f"<img src='{uri}' alt='item'/>"
                        f"<div class='closet-caption'>"
                        f"<div class='meta'>{meta}</div>"
                        f"</div></div>"
                    )
            st.markdown(f"<div class='closet-grid'>{''.join(tiles)}</div>", unsafe_allow_html=True)
        else:
            st.info("Your closet is empty. Use 'Add Clothes' to populate it.")
    with right_col:
        header_cols = st.columns([7, 1], gap="small")
        with header_cols[0]:
            st.markdown("<div class='section-title'><h2 style='margin:0;font-family:Playfair Display, serif'>Your Outfit</h2></div>", unsafe_allow_html=True)
        with header_cols[1]:
            recs = st.session_state.get("last_recommendations_v3")
            idx = st.session_state.get("last_recommendation_index_v3", 0)
            total = len(recs) if recs else 0
            if total > 0:
                st.markdown(f"<div style='text-align:center;color:#6b7280;font-size:0.95rem'>{idx+1}/{total}</div>", unsafe_allow_html=True)
            if st.button("↻", key="v3_reroll", help="Cycle to the next cached outfit alternative"):
                if not recs:
                    st.warning("Generate recommendations first using 'Get Stylist Advice'.")
                else:
                    new_idx = (idx + 1) % total
                    st.session_state["last_recommendation_index_v3"] = new_idx
                    new_rec = recs[new_idx]
                    st.session_state["last_recommendation_v3"] = new_rec
                    st.session_state["last_outfit_result_v3"] = generate_mannequin_outfit(new_rec, load_closet_data())
        st.markdown("<div class='desktop-only'>", unsafe_allow_html=True)
        render_recommendation_panel_html(st.session_state.get("last_recommendation_v3"), st.session_state.get("last_outfit_result_v3"))
        st.markdown("</div>", unsafe_allow_html=True)
        # if not st.session_state.get("last_recommendation_v3"):
        #     st.markdown("<div class='muted'>No recommendation yet. Describe an occasion and click \"Get Stylist Advice\".</div>", unsafe_allow_html=True)
