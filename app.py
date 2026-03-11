import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- PAGE SETUP ---
st.set_page_config(page_title="HealthifyDiksha AI", layout="centered")

# --- PERSISTENT DATABASE ---
if 'daily_logs' not in st.session_state:
    st.session_state.daily_logs = pd.DataFrame(columns=['Time', 'Meal', 'Cals', 'P', 'C', 'F'])
if 'stock' not in st.session_state:
    # Initializing from your current inventory
    st.session_state.stock = {
        "Paneer": 100, "Curd": 200, "Protein Bread": 10, 
        "Avocado": 1, "Milk": 500, "Oats": 500, "PB": 1
    }

# --- CALORIE & MACRO PROGRESS ---
st.title("🍏 HealthifyDiksha")

target_cals = 1350
consumed_cals = st.session_state.daily_logs['Cals'].sum()
remaining_cals = max(0, target_cals - consumed_cals)
total_prot = st.session_state.daily_logs['P'].sum()

# Visual Calorie Ring
fig = go.Figure(go.Pie(
    values=[consumed_cals, remaining_cals],
    labels=["Consumed", "Remaining"],
    hole=.7,
    marker_colors=['#00e676', '#f5f5f5'],
    showlegend=False
))
fig.update_layout(annotations=[dict(text=f'{int(consumed_cals)}/{target_cals}\nkcal', x=0.5, y=0.5, font_size=20, showarrow=False)], margin=dict(t=0, b=0, l=0, r=0))
st.plotly_chart(fig, use_container_width=True)

# --- ✨ AI MEAL RECOMMENDATIONS ---
st.subheader("💡 AI Next-Meal Suggestion")
def get_recommendation():
    current_hour = datetime.now().hour
    # Logic based on remaining macros and stock
    if total_prot < 40 and st.session_state.stock["Paneer"] > 0:
        return "🥗 **Protein Gap Detected**: Prepare **100g Paneer** with **Protein Bread**. This supports your quad/hamstring strengthening[cite: 135]."
    elif current_hour >= 21 and st.session_state.stock["Curd"] > 0:
        return "🌙 **Night Recovery**: Have **200g Curd**. The casein will aid your ACL oedema repair overnight[cite: 40]."
    elif st.session_state.stock["Avocado"] > 0:
        return "🥑 **Healthy Fat needed**: Add **Avocado** to your next meal to manage joint effusion[cite: 42]."
    return "🍎 Have an **Orange** for Vitamin C to support collagen synthesis."

st.success(get_recommendation())

# --- REAL-TIME LOGGING ---
with st.expander("➕ Log Food or Activity", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        meal = st.text_input("What did you eat?")
        cals = st.number_input("Calories", value=0)
        p = st.number_input("Protein (g)", value=0)
    with col2:
        c = st.number_input("Carbs (g)", value=0)
        f = st.number_input("Fats (g)", value=0)
    
    if st.button("Update Dashboard"):
        new_entry = pd.DataFrame([[datetime.now().strftime("%H:%M"), meal, cals, p, c, f]], columns=['Time', 'Meal', 'Cals', 'P', 'C', 'F'])
        st.session_state.daily_logs = pd.concat([st.session_state.daily_logs, new_entry], ignore_index=True)
        st.rerun()

# --- MEDICAL & PANTRY TRACKER ---
with st.sidebar:
    st.header("🩹 Recovery Hub")
    st.checkbox("Daily Calcium ")
    st.checkbox("Physio Session (Daily 9PM) [cite: 116, 135]")
    is_friday = datetime.now().strftime("%A") == "Friday"
    if is_friday:
        st.warning("🚨 Take **Genivit D3** ")
    
    st.write("---")
    st.subheader("🛒 Pantry Keeper")
    for item, qty in st.session_state.stock.items():
        st.write(f"{item}: {qty}")
