import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="HealthifyDiksha AI", layout="centered")

# --- 🧠 DYNAMIC DATABASE & MEMORY ---
if 'nutrition_db' not in st.session_state:
    st.session_state.nutrition_db = {
        "Paneer (100g)": {"cals": 265, "p": 18, "c": 2, "f": 20},
        "Curd (200g)": {"cals": 196, "p": 22, "c": 9, "f": 8},
        "Milk (200ml)": {"cals": 120, "p": 6, "c": 10, "f": 5},
        "Protein Bread (1 slice)": {"cals": 70, "p": 5, "c": 10, "f": 1},
        "Avocado (1/2 pc)": {"cals": 160, "p": 2, "c": 9, "f": 15},
        "Banana (1 pc)": {"cals": 105, "p": 1, "c": 27, "f": 0},
        "Orange (1 pc)": {"cals": 45, "p": 1, "c": 11, "f": 0},
        "Unsweetened PB (1 tbsp)": {"cals": 90, "p": 4, "c": 3, "f": 8},
        "Oats (30g)": {"cals": 117, "p": 5, "c": 20, "f": 2},
        "Chia Seeds (1 tbsp)": {"cals": 60, "p": 2, "c": 5, "f": 4}
    }

if 'stock' not in st.session_state:
    st.session_state.stock = {
        "Paneer (100g)": 2, "Curd (200g)": 3, "Milk (200ml)": 5, 
        "Protein Bread (1 slice)": 10, "Avocado (1/2 pc)": 2, "Oats (30g)": 15
    }

if 'daily_logs' not in st.session_state:
    st.session_state.daily_logs = pd.DataFrame(columns=['Time', 'Meal', 'Qty', 'Cals', 'P', 'C', 'F'])

# New Memory State for Water
if 'water_ml' not in st.session_state:
    st.session_state.water_ml = 0

st.title("🍏 HealthifyDiksha")

# --- CALORIE & MACRO PROGRESS ---
target_cals = 1350
consumed_cals = st.session_state.daily_logs['Cals'].sum()
remaining_cals = max(0, target_cals - consumed_cals)
total_prot = st.session_state.daily_logs['P'].sum()

fig = go.Figure(go.Pie(
    values=[consumed_cals, remaining_cals],
    labels=["Consumed", "Remaining"],
    hole=.7,
    marker_colors=['#00e676', '#f5f5f5'],
    showlegend=False
))
fig.update_layout(annotations=[dict(text=f'{int(consumed_cals)}/{target_cals}\nkcal', x=0.5, y=0.5, font_size=20, showarrow=False)], margin=dict(t=0, b=0, l=0, r=0))
st.plotly_chart(fig, use_container_width=True)

st.progress(min(total_prot / 90.0, 1.0), text=f"Protein Goal: {total_prot}g / 90g")

# --- 💧 HYDRATION TRACKER ---
st.divider()
st.subheader("💧 Hydration Tracker")
water_goal = 3500 # 3.5 Liters

st.progress(min(st.session_state.water_ml / water_goal, 1.0), text=f"Water Intake: {st.session_state.water_ml} ml / {water_goal} ml")

w_col1, w_col2, w_col3 = st.columns(3)
if w_col1.button("🥤 + 250 ml (Glass)"):
    st.session_state.water_ml += 250
    st.rerun()
if w_col2.button("🍼 + 500 ml (Bottle)"):
    st.session_state.water_ml += 500
    st.rerun()
if w_col3.button("🔄 Reset Water"):
    st.session_state.water_ml = 0
    st.rerun()

# --- ✨ AI MEAL RECOMMENDATIONS ---
st.subheader("💡 AI Next-Meal Suggestion")
def get_recommendation():
    current_hour = datetime.now().hour
    if total_prot < 40 and st.session_state.stock.get("Paneer (100g)", 0) > 0:
        return "🥗 **Protein Gap**: Have **Paneer**. Supports quad/hamstring strengthening."
    elif current_hour >= 21 and st.session_state.stock.get("Curd (200g)", 0) > 0:
        return "🌙 **Night Recovery**: Have **Curd**. The casein aids ACL oedema repair overnight."
    return "🍎 Ensure you have your daily calcium for your bone contusion healing."

st.success(get_recommendation())

# --- ⚡ SMART LOGGING (FRACTIONAL PORTIONS) ---
with st.expander("➕ Log Food (Auto-Calculate)", expanded=True):
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_food = st.selectbox("What did you eat?", list(st.session_state.nutrition_db.keys()))
    with col2:
        servings = st.number_input("Portion (e.g., 0.5 for half)", min_value=0.01, value=1.00, step=0.10, format="%.2f")
    
    if st.button("Log Food"):
        item = st.session_state.nutrition_db[selected_food]
        new_entry = pd.DataFrame([[
            datetime.now().strftime("%H:%M"), selected_food, servings, 
            round(item['cals'] * servings, 1), round(item['p'] * servings, 1), 
            round(item['c'] * servings, 1), round(item['f'] * servings, 1)
        ]], columns=['Time', 'Meal', 'Qty', 'Cals', 'P', 'C', 'F'])
        
        st.session_state.daily_logs = pd.concat([st.session_state.daily_logs, new_entry], ignore_index=True)
        
        # Automatically deduct from stock if it exists
        if selected_food in st.session_state.stock:
            st.session_state.stock[selected_food] = max(0, st.session_state.stock[selected_food] - servings)
        st.rerun()

# --- 🛒 GROCERY RESTOCK MENU ---
with st.expander("🛒 Restock / Add Groceries"):
    tab1, tab2 = st.tabs(["Update Existing Stock", "Add Completely New Item"])
    
    with tab1:
        u_col1, u_col2 = st.columns(2)
        stock_item = u_col1.selectbox("Select existing item", list(st.session_state.stock.keys()))
        add_qty = u_col2.number_input("Units to add", min_value=0.0, step=1.0)
        if st.button("Update Inventory"):
            st.session_state.stock[stock_item] += add_qty
            st.rerun()
            
    with tab2:
        st.write("Add a new item to your database. It will appear in your food logger permanently.")
        new_name = st.text_input("Item Name & Serving Size (e.g., Almonds 30g)")
        n_col1, n_col2, n_col3, n_col4 = st.columns(4)
        new_cals = n_col1.number_input("Cals", 0)
        new_p = n_col2.number_input("Pro (g)", 0)
        new_c = n_col3.number_input("Carbs (g)", 0)
        new_f = n_col4.number_input("Fats (g)", 0)
        initial_stock = st.number_input("How many servings did you buy?", min_value=0.0, step=1.0)
        
        if st.button("Save New Item"):
            if new_name:
                st.session_state.nutrition_db[new_name] = {"cals": new_cals, "p": new_p, "c": new_c, "f": new_f}
                st.session_state.stock[new_name] = initial_stock
                st.rerun()

# --- DAILY SUMMARY & MEDICAL CHECK ---
st.divider()
st.subheader("📋 Today's Summary")
st.dataframe(st.session_state.daily_logs, use_container_width=True)

with st.sidebar:
    st.header("🩹 Recovery Hub")
    st.checkbox("Daily Calcium Tablet")
    st.checkbox("Daily Physio (9 PM)")
    if datetime.now().strftime("%A") == "Friday":
        st.warning("🚨 Take **Genivit D3**")
    
    st.write("---")
    st.subheader("🛒 Current Pantry")
    for item, qty in st.session_state.stock.items():
        if qty <= 1:
            st.error(f"{item}: {qty} (Low!)")
        else:
            st.success(f"{item}: {qty}")
