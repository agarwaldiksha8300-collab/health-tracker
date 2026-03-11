import streamlit as st
from datetime import datetime, timedelta

# --- DASHBOARD CONFIG ---
st.set_page_config(page_title="Diksha's Recovery & Wedding Glow-Up", layout="wide")
st.title("🏃‍♀️ Wellness Dashboard: Road to 60kg")

# --- SIDEBAR: MEDICAL & GOALS ---
st.sidebar.header("🎯 Target: June 20 Wedding")
st.sidebar.metric("Weight Goal", "60 kg", "-10 kg")
st.sidebar.metric("Daily Calorie Budget", "1,350 kcal")

st.sidebar.subheader("💊 Daily Med-Check")
calcium = st.sidebar.checkbox("Daily Calcium Tablet (Bone Contusion)")
physio = st.sidebar.checkbox("9:00 PM Physio Session")
is_friday = datetime.now().strftime("%A") == "Friday"
if is_friday:
    st.sidebar.warning("🚨 FRIDAY: Take Genivit D3")
    d3 = st.sidebar.checkbox("Confirm D3 Intake")

# --- MAIN: LIVE MEAL TRACKER ---
st.header("🕒 3-Hour Interval Schedule")
day_mode = st.radio("Select Mode", ["Weekday (8:15 AM Start)", "Weekend (11:00 AM Start)"])

start_time = "08:15" if "Weekday" in day_mode else "11:00"
start_dt = datetime.strptime(start_time, "%H:%M")

meals = [
    {"label": "Wake Up", "menu": "Milk + Honey", "cals": 160, "note": "Sync with Calcium"},
    {"label": "Class Break", "menu": "Orange + Chia Seeds", "cals": 90, "note": "Vit C for ACL Oedema"},
    {"label": "Lunch", "menu": "Paneer (100g) + 2 Protein Toasts", "cals": 420, "note": "Muscle Repair"},
    {"label": "Evening Snack", "menu": "Banana + 1 tbsp Peanut Butter", "cals": 195, "note": "Energy"},
    {"label": "Pre-Physio", "menu": "1/2 Energy Bar", "cals": 110, "note": "Fuel for 9PM"},
    {"label": "Dinner", "menu": "Savory Oats + Olive Oil", "cals": 220, "note": "Anti-Inflammatory"},
    {"label": "Night Cap", "menu": "Curd (200g) + Chia Seeds", "cals": 155, "note": "Casein Recovery"}
]

cols = st.columns(len(meals))
for i, meal in enumerate(meals):
    slot = (start_dt + timedelta(hours=3 * i)).strftime("%I:%M %p")
    with cols[i]:
        st.button(f"{slot}\n{meal['label']}")
        st.caption(f"**{meal['menu']}**")
        st.info(meal['note'])

# --- RECOVERY PROGRESS ---
st.divider()
st.subheader("🩹 Right Knee Recovery Progress")
st.write("Status: **50% Weight Bearing**")
st.progress(50) 
st.write("Focus: Quadriceps & Hamstring Strengthening")
