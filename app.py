import streamlit as st
from datetime import datetime, timedelta

# --- DASHBOARD CONFIG ---
st.set_page_status(page_title="Diksha's Recovery & Wedding Glow-Up", layout="wide")
st.title("🏃‍♀️ Wellness Dashboard: Road to 60kg")

# --- SIDEBAR: MEDICAL & GOALS ---
st.sidebar.header("🎯 Target: June 20 Wedding")
st.sidebar.metric("Weight Goal", "60 kg", "-10 kg")
st.sidebar.metric("Daily Calorie Budget", "1,350 kcal")

st.sidebar.subheader("💊 Daily Med-Check")
calcium = st.sidebar.checkbox("Daily Calcium Tablet")
physio = st.sidebar.checkbox("9:00 PM Physio Session")
is_friday = datetime.now().strftime("%A") == "Friday"
if is_friday:
    d3 = st.sidebar.checkbox("🚨 FRIDAY: Genivit D3")

# --- MAIN: LIVE MEAL TRACKER ---
st.header("🕒 3-Hour Interval Schedule")
day_mode = st.radio("Select Mode", ["Weekday (8:15 AM Start)", "Weekend (11:00 AM Start)"])

start_time = "08:15" if "Weekday" in day_mode else "11:00"
start_dt = datetime.strptime(start_time, "%H:%M")

meals = [
    {"label": "Wake Up", "menu": "Milk (200ml) + Honey", "cals": 160, "note": "Take Calcium now"},
    {"label": "Class Break", "menu": "Orange + Chia Seeds", "cals": 90, "note": "Vit C for Ligament"},
    {"label": "Lunch", "menu": "Paneer (100g) + 2 Protein Toasts", "cals": 420, "note": "High Protein Recovery"},
    {"label": "Evening Snack", "menu": "Banana + 1 tbsp Peanut Butter", "cals": 195, "note": "Potassium Spike"},
    {"label": "Pre-Physio", "menu": "1/2 Energy Bar", "cals": 110, "note": "Glucose for 9PM Session"},
    {"label": "Dinner", "menu": "Savory Oats with Olive Oil", "cals": 220, "note": "Anti-Inflammatory"},
    {"label": "Night Cap", "menu": "Curd (200g) + Chia Seeds", "cals": 155, "note": "Casein for Tissue Repair"}
]

cols = st.columns(len(meals))
for i, meal in enumerate(meals):
    slot = (start_dt + timedelta(hours=3 * i)).strftime("%I:%M %p")
    with cols[i]:
        st.button(f"{slot}\n{meal['label']}")
        st.caption(f"**{meal['menu']}**")
        st.write(f"{meal['cals']} kcal")

# --- KITCHEN INVENTORY (GROCERY KEEPER) ---
st.divider()
st.header("🛒 Grocery Tab Keeper")
stock_data = {
    "Paneer": 1, "Curd": 1, "Avocado": 1, "Milk": 3, "Oranges": 4, "Bananas": 5, "Oats": 10
}

col1, col2 = st.columns(2)
with col1:
    st.subheader("Current Stock")
    for item, qty in stock_data.items():
        status = "🔴 Low" if qty <= 1 else "🟢 In Stock"
        st.write(f"{item}: {qty} units ({status})")

with col2:
    st.subheader("Buy List (Recovery Focus)")
    st.info("- Low Fat Paneer\n- Fresh Spinach (for Oats)\n- Cucumber (Satiety)")

# --- RECOVERY PROGRESS ---
st.divider()
st.subheader("🩹 MPFL Recovery Progress")
st.write("Current Phase: **50% Weight Bearing with Walker**")
st.progress(50) 
st.warning("Note: Avoid Maggi/Chips to reduce joint effusion (swelling)[cite: 15, 42].")
