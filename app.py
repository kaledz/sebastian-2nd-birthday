"""
Birthday party invitation for a 2-year-old, built with Streamlit + Lottie.

Run:
    pip install -r requirements.txt
    streamlit run app.py

Animations:
    Download free Lottie JSON files from https://lottiefiles.com
    (search "birthday cake", "balloons", "confetti", "teddy bear"),
    save them in an "animations" folder next to this file using the
    names in ANIMATIONS below. Any that are missing fall back to an emoji,
    so the card works even before you add them.

RSVPs:
    Every RSVP is always saved to rsvps.json next to this file and shown
    on the "View RSVPs" sidebar panel, gated by ADMIN_PASSCODE below (a
    plain constant -- change it to whatever you like, no external secret
    needed). That part needs zero setup and always works.

    Caveat: Streamlit Community Cloud's filesystem is ephemeral -- it
    survives fine while the app is just running/sleeping, but a fresh
    deploy (pushing new code) wipes it. Fine for a one-off party page;
    don't rely on it as permanent storage.

    Email notification via Brevo's free transactional-email API (300/day,
    no domain needed, no Gmail/App Password) -- optional but recommended,
    see https://www.brevo.com:
      1. Sign up free, then Settings -> Senders, Domains & Dedicated IPs
         -> Senders -> add the address you want these emails to come
         FROM, and verify it with the 6-digit code Brevo emails there.
      2. Settings -> SMTP & API -> API Keys -> generate a new key.
      3. In Streamlit Community Cloud, App settings -> Secrets, add:
            brevo_api_key = "xkeysib-..."
            brevo_sender_email = "the address you verified in step 1"
            rsvp_to_email = "the address that should receive RSVPs"
    Leave these unset and RSVPs are still saved/viewable in-app, you just
    won't get emailed.

    Optional bonus on top of that: a live push notification on your phone
    via ntfy.sh (https://ntfy.sh), free, no signup, no account, no API
    key -- a "topic" is just a name you make up (treat it like a
    password, since anyone who knows it can publish/subscribe to it).
      1. Make up a topic name, e.g. sebastian-rsvp-7f3ac91e2b.
      2. Install the ntfy app (iOS/Android) or open https://ntfy.sh/app in
         a browser, and subscribe to that exact topic name.
      3. In Streamlit secrets, add:
            ntfy_topic = "sebastian-rsvp-7f3ac91e2b"

    .streamlit/secrets.toml is gitignored so none of this reaches the
    (public) repo. Guests never need an email: the party date/time/
    address and a Google Maps link are shown directly in the app right
    after they submit.
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
MESSAGE = (
    "Two years of giggles, hugs, wobbly first steps, and a whole lot of joy. "
    "You make every day brighter. We love watching you grow, explore, "
    "and discover the world. Happy 2nd Birthday, little one!"
)

# ---------- Party details ----------
PARTY_TIME = "1:00 PM - 3:00 PM"
PARTY_LOCATION = "157 Olympic Drive, Stafford, VA 22554"
PARTY_MAPS_URL = "https://www.google.com/maps/search/?api=1&query=" + PARTY_LOCATION.replace(" ", "+")
RSVP_BY = date(2026, 11, 8)        # ask guests to respond by this date
RSVPS_FILE = Path(__file__).parent / "rsvps.json"
ADMIN_PASSCODE = "sebastian2"      # change to whatever you like -- see "View RSVPs" below

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
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@500;700&family=Poppins:wght@400;500;600&display=swap');

    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

    .stApp {
        background:
            radial-gradient(circle at 15% 10%, rgba(255,202,40,0.25), transparent 45%),
            radial-gradient(circle at 85% 15%, rgba(255,112,67,0.18), transparent 45%),
            radial-gradient(circle at 50% 100%, rgba(171,71,188,0.15), transparent 50%),
            linear-gradient(180deg, #EAF4FF 0%, #FBF6FF 55%, #FFF3F8 100%);
    }
    .block-container { padding-top: 2.5rem; max-width: 640px; }

    .big-age {
        font-family: 'Fredoka', sans-serif;
        font-size: 8.5rem; font-weight: 700; text-align: center; line-height: 1;
        background: linear-gradient(90deg, #4F8EF7, #B15CDE, #FF7A59, #FFC93C);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin: 0.1em 0 0;
        filter: drop-shadow(0 6px 18px rgba(177,92,222,0.25));
    }
    .title {
        font-family: 'Fredoka', sans-serif;
        font-size: 2.4rem; font-weight: 700; text-align: center;
        color: #27314A; margin-bottom: 0; letter-spacing: -0.01em;
    }
    .subtitle {
        text-align: center; font-size: 1.05rem; color: #6B7686;
        letter-spacing: 0.02em; margin-top: 0.3em;
    }
    .hero-photo-wrap { display: flex; justify-content: center; margin: 1.6em 0; }
    .hero-photo-wrap img {
        width: min(78vw, 360px);
        aspect-ratio: 3 / 4;
        object-fit: cover;
        border-radius: 28px;
        box-shadow: 0 18px 40px -12px rgba(39,49,74,0.35), 0 0 0 6px #FFFFFF, 0 0 0 10px rgba(255,201,60,0.55);
    }
    .card {
        background: rgba(255,255,255,0.72);
        backdrop-filter: blur(10px);
        border-radius: 26px; padding: 30px 34px;
        box-shadow: 0 10px 30px rgba(39,49,74,0.1);
        font-size: 1.12rem; line-height: 1.75; color: #33475B; text-align: center;
        border: 1px solid rgba(255,255,255,0.6);
    }
    .signoff {
        text-align: center; font-style: italic; color: #B15CDE;
        font-weight: 500; margin-top: 14px;
    }
    .emoji-fallback { font-size: 6rem; text-align: center; }

    .stButton > button {
        font-family: 'Fredoka', sans-serif; font-weight: 700; font-size: 1.1rem;
        border: none; border-radius: 999px; padding: 0.7em 1em;
        background: linear-gradient(90deg, #4F8EF7, #B15CDE, #FF7A59);
        color: white; box-shadow: 0 10px 24px -8px rgba(177,92,222,0.6);
        transition: transform 150ms ease, box-shadow 150ms ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 14px 28px -8px rgba(177,92,222,0.75);
        color: white;
    }
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


def notify_host_push(name: str, attending: str, guest_count: int, notes: str) -> tuple[bool, str]:
    """Push one RSVP to the host via ntfy.sh. No account/email anywhere --
    just a shared, hard-to-guess topic name (see the module docstring).

    Returns (sent, status) where status is "ok", "not_configured" (no
    secret set yet -- not an error, just not wired up), or an error
    message string.
    """
    topic = st.secrets.get("ntfy_topic")
    if not topic:
        return False, "not_configured"

    body = (
        f"{attending}\n"
        f"Guests: {guest_count}\n"
        f"Notes: {notes or '-'}"
    )
    try:
        r = requests.post(
            f"https://ntfy.sh/{topic}",
            data=body.encode("utf-8"),
            headers={"Title": f"RSVP: {name}", "Tags": "tada,birthday"},
            timeout=10,
        )
        if r.status_code == 200:
            return True, "ok"
        return False, f"ntfy {r.status_code}: {r.text[:200]}"
    except requests.RequestException as exc:
        return False, str(exc)


def notify_host_email(name: str, attending: str, guest_count: int, notes: str) -> tuple[bool, str]:
    """Email one RSVP to the host via Brevo's free transactional-email API.
    No Gmail/SMTP/App Password involved -- Brevo just needs a one-time-
    verified sender address and an API key (see module docstring).

    Returns (sent, status) -- same shape as notify_host_push.
    """
    api_key = st.secrets.get("brevo_api_key")
    sender_email = st.secrets.get("brevo_sender_email")
    to_email = st.secrets.get("rsvp_to_email")
    if not api_key or not sender_email or not to_email:
        return False, "not_configured"

    body = (
        f"RSVP for {CHILD_NAME}'s {ordinal(AGE)} birthday party\n\n"
        f"Name: {name}\n"
        f"Attending: {attending}\n"
        f"Total guests (incl. themselves): {guest_count}\n"
        f"Notes: {notes or '-'}\n"
    )
    payload = {
        "sender": {"email": sender_email},
        "to": [{"email": to_email}],
        "subject": f"RSVP from {name} -- {CHILD_NAME}'s birthday",
        "textContent": body,
    }
    try:
        r = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "api-key": api_key,
                "accept": "application/json",
                "content-type": "application/json",
            },
            json=payload,
            timeout=10,
        )
        if r.status_code in (200, 201):
            return True, "ok"
        return False, f"Brevo {r.status_code}: {r.text[:200]}"
    except requests.RequestException as exc:
        return False, str(exc)


def load_rsvps() -> list[dict]:
    if not RSVPS_FILE.exists():
        return []
    try:
        return json.loads(RSVPS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []


def save_rsvp(name: str, attending: str, guest_count: int, notes: str) -> None:
    rsvps = load_rsvps()
    rsvps.append(
        {
            "name": name,
            "attending": attending,
            "guest_count": guest_count,
            "notes": notes,
            "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    )
    RSVPS_FILE.write_text(json.dumps(rsvps, indent=2), encoding="utf-8")


@st.dialog("RSVP 💌")
def rsvp_dialog():
    st.write(f"Let us know if you can make it to {CHILD_NAME}'s party!")
    with st.form("rsvp_form", clear_on_submit=False):
        name = st.text_input("Your name")
        attending = st.radio(
            "Will you be there?",
            ["Yes, can't wait! 🎉", "So sorry, can't make it", "Not sure yet"],
        )
        guest_count = st.number_input(
            "Total guests, including you", min_value=1, max_value=20, value=1, step=1
        )
        notes = st.text_area("Anything we should know? (allergies, well wishes, etc.)", height=80)
        submitted = st.form_submit_button("Send RSVP", use_container_width=True)

    if submitted:
        if not name.strip():
            st.error("Please enter your name.")
            return
        name, notes = name.strip(), notes.strip()

        save_rsvp(name, attending, int(guest_count), notes)
        notify_host_push(name, attending, int(guest_count), notes)
        notify_host_email(name, attending, int(guest_count), notes)
        st.success("Thank you! We've got your RSVP. 🎈")

        if "can't make it" not in attending.lower():
            party_date_str = BIRTHDAY.strftime("%A, %B %d, %Y").replace(" 0", " ")
            st.markdown(
                f"""<div class='card' style='margin-top:1em;'>
                See you here!<br><br>
                📅 {party_date_str}<br>
                🕒 {PARTY_TIME}<br>
                📍 <a href='{PARTY_MAPS_URL}' target='_blank'>{PARTY_LOCATION}</a>
                </div>""",
                unsafe_allow_html=True,
            )


PHOTO_PATH = Path(__file__).parent / "photos" / "slide.jpg"

# ---------- Header ----------
show_animation("balloons", height=180)
st.markdown(f"<p class='title'>Happy Birthday, {CHILD_NAME}!</p>", unsafe_allow_html=True)
st.markdown(f"<p class='big-age'>{AGE}</p>", unsafe_allow_html=True)

if PHOTO_PATH.exists():
    import base64

    encoded = base64.b64encode(PHOTO_PATH.read_bytes()).decode()
    st.markdown(
        f"<div class='hero-photo-wrap'><img src='data:image/jpeg;base64,{encoded}' /></div>",
        unsafe_allow_html=True,
    )

st.markdown(
    f"<p class='subtitle'>You're invited to celebrate his {ordinal(AGE)} birthday!</p>",
    unsafe_allow_html=True,
)

# ---------- Invitation details ----------
party_date_str = BIRTHDAY.strftime("%A, %B %d, %Y").replace(" 0", " ")
st.markdown(
    f"""<div class='card'>
    Please join us as {CHILD_NAME} turns {AGE}!<br><br>
    📅 {party_date_str}<br>
    🕒 {PARTY_TIME}<br>
    📍 {PARTY_LOCATION}
    </div>""",
    unsafe_allow_html=True,
)
st.write("")

c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    if st.button("💌 RSVP Now", use_container_width=True):
        rsvp_dialog()
st.markdown(
    f"<p class='subtitle' style='font-size:0.9rem; margin-top:0.5em;'>"
    f"Please respond by {RSVP_BY.strftime('%B %d').replace(' 0', ' ')}</p>",
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
st.write("")

# ---------- Fun facts about turning two ----------
with st.expander("🌟 Things we love about you at 2"):
    st.markdown(
        """
        - Your big belly laughs 😂
        - How you say "more!" at snack time 🍪
        - Dancing the second music comes on 🎶
        - Your hugs, which fix everything 🤗
        - How you say "WOW" at absolutely everything 😮
        - Your crazy opening and closing of every cabinet in the house 🚪
        """
    )

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

# ---------- Host: View RSVPs (sidebar, passcode-gated) ----------
with st.sidebar:
    st.subheader("View RSVPs")
    passcode = st.text_input("Passcode", type="password", key="admin_passcode")
    if passcode == ADMIN_PASSCODE:
        rsvps = load_rsvps()
        if not rsvps:
            st.caption("No RSVPs yet.")
        else:
            yes_count = sum(
                r["guest_count"] for r in rsvps if "can't make it" not in r["attending"].lower()
            )
            st.metric("Total attending (incl. guests)", yes_count)
            for r in reversed(rsvps):
                st.write(f"**{r['name']}** -- {r['attending']}")
                st.caption(
                    f"{r['guest_count']} guest(s) · {r['submitted_at']}"
                    + (f" · {r['notes']}" if r["notes"] else "")
                )
    elif passcode:
        st.error("Wrong passcode.")
