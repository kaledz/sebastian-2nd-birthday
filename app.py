"""
Birthday card for a 2-year-old, built with Streamlit + Lottie.

Run:
    pip install -r requirements.txt
    streamlit run app.py

Animations:
    Download free Lottie JSON files from https://lottiefiles.com
    (search "birthday cake", "balloons", "confetti", "teddy bear"),
    save them in an "animations" folder next to this file using the
    names in ANIMATIONS below. Any that are missing fall back to an emoji,
    so the card works even before you add them.
"""

import json
from datetime import date, datetime
from pathlib import Path

import requests
import streamlit as st
from streamlit_lottie import st_lottie

# ---------- Personalize here ----------
CHILD_NAME = "Sebastian"          # e.g. "Leo"
BIRTHDAY = date(2026, 11, 15)
AGE = 2
FROM_LINE = "Love always, Mom & Dad"
MESSAGE = (
    "Two years of giggles, hugs, wobbly first steps, and a whole lot of joy. "
    "You make every day brighter. We love watching you grow, explore, "
    "and discover the world. Happy 2nd Birthday, little one!"
)

# file name -> (optional URL fallback, emoji fallback)
ANIMATIONS = {
    "cake":     ("animations/cake.json",     "", "🎂"),
    "balloons": ("animations/balloons.json", "", "🎈"),
    "confetti": ("animations/confetti.json", "", "🎉"),
    "teddy":    ("animations/teddy.json",    "", "🧸"),
}
# --------------------------------------

st.set_page_config(page_title=f"Happy {AGE}nd Birthday!", page_icon="🎂", layout="centered")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #E3F2FD 0%, #FFF8E1 60%, #FCE4EC 100%);
    }
    .big-age {
        font-size: 9rem; font-weight: 900; text-align: center; line-height: 1;
        background: linear-gradient(90deg, #42A5F5, #AB47BC, #FF7043, #FFCA28);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .title {
        font-size: 2.6rem; font-weight: 800; text-align: center;
        color: #1E3A5F; margin-bottom: 0;
    }
    .subtitle { text-align: center; font-size: 1.2rem; color: #5C6B7A; }
    .card {
        background: white; border-radius: 24px; padding: 28px 32px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        font-size: 1.15rem; line-height: 1.7; color: #33475B; text-align: center;
    }
    .signoff { text-align: center; font-style: italic; color: #7E57C2; margin-top: 12px; }
    .emoji-fallback { font-size: 6rem; text-align: center; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_lottie(path: str, url: str):
    """Load a Lottie animation from a local file, then a URL. Returns None if neither works."""
    p = Path(__file__).parent / path
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    if url:
        try:
            r = requests.get(url, timeout=8)
            if r.status_code == 200:
                return r.json()
        except (requests.RequestException, ValueError):
            pass
    return None


def show_animation(key: str, height: int = 220):
    path, url, emoji = ANIMATIONS[key]
    data = load_lottie(path, url)
    if data:
        st_lottie(data, height=height, key=f"lottie_{key}", loop=True)
    else:
        st.markdown(f"<div class='emoji-fallback'>{emoji}</div>", unsafe_allow_html=True)


def ordinal(n: int) -> str:
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


# ---------- Header ----------
show_animation("balloons", height=180)
st.markdown(f"<p class='title'>Happy Birthday, {CHILD_NAME}!</p>", unsafe_allow_html=True)
st.markdown(f"<p class='big-age'>{AGE}</p>", unsafe_allow_html=True)
st.markdown(
    f"<p class='subtitle'>Celebrating your {ordinal(AGE)} birthday · "
    f"{BIRTHDAY.strftime('%B %d, %Y').replace(' 0', ' ')}</p>",
    unsafe_allow_html=True,
)

# ---------- Countdown / day-of ----------
today = date.today()
days_left = (BIRTHDAY - today).days
if days_left > 0:
    st.info(f"⏳ **{days_left} day{'s' if days_left != 1 else ''}** until the big day!")
elif days_left == 0:
    st.success("🎉 **Today's the day!** Happy Birthday! 🎉")
    st.balloons()
else:
    st.success(f"🎈 What a celebration! {CHILD_NAME} turned {AGE} on {BIRTHDAY.strftime('%B %d')}.")

# ---------- Cake + teddy ----------
col1, col2 = st.columns(2)
with col1:
    show_animation("cake", height=220)
with col2:
    show_animation("teddy", height=220)

# ---------- Message ----------
st.markdown(f"<div class='card'>{MESSAGE}</div>", unsafe_allow_html=True)
st.markdown(f"<p class='signoff'>{FROM_LINE}</p>", unsafe_allow_html=True)
st.write("")

# ---------- Fun facts about turning two ----------
with st.expander("🌟 Things we love about you at 2"):
    st.markdown(
        """
        - Your big belly laughs 😂
        - How you say "more!" at snack time 🍪
        - Dancing the second music comes on 🎶
        - Your hugs, which fix everything 🤗
        """
    )
    st.caption("Edit this list in app.py to make it yours.")

# ---------- Photos ----------
PHOTOS_DIR = Path(__file__).parent / "photos"

with st.expander("📸 Photos from the year", expanded=True):
    preloaded = sorted(PHOTOS_DIR.glob("*")) if PHOTOS_DIR.exists() else []
    uploaded = st.file_uploader(
        "Add more photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True
    )
    all_photos = list(preloaded) + list(uploaded or [])
    if all_photos:
        cols = st.columns(3)
        for i, photo in enumerate(all_photos):
            cols[i % 3].image(photo, use_container_width=True)

# ---------- Celebrate button ----------
st.write("")
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    if st.button("🎉 Make a wish & celebrate! 🎉", use_container_width=True):
        st.balloons()
        st.session_state["celebrated"] = True

if st.session_state.get("celebrated"):
    show_animation("confetti", height=260)
    st.markdown(
        f"<p class='title' style='font-size:2rem'>Hip hip hooray for {CHILD_NAME}! 🥳</p>",
        unsafe_allow_html=True,
    )

st.write("")
st.caption(f"Made with love on {datetime.now().strftime('%B %d, %Y')}")
