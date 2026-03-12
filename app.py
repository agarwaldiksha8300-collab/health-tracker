import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components
from datetime import datetime

st.set_page_config(page_title="HealthifyDiksha AI", layout="centered", page_icon="🍏")

# --- 🕒 LIVE CORNER CLOCK ---
components.html("""
    <div style="font-family: sans-serif; text-align: right; color: #888; font-size: 14px;">
        <span id="clock" style="font-weight: bold;"></span>
    </div>
    <script>
        function updateTime() {
            var d = new Date();
            var options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            document.getElementById('clock').innerText = d.toLocaleDateString('en-US', options) + " | " + d.toLocaleTimeString();
        }
        setInterval(updateTime, 1000);
        updateTime();
    </script>
""", height=30)

# --- 🔄 STATE & RESET ENGINE ---
current_date = datetime.now().date()
if 'last_reset_date' not in st.session_state:
    st.session_state.last_reset_date = current_date

if 'history_db' not in st.session_state:
    st.session_state.history_db = pd.DataFrame(columns=['Date', 'Cals', 'Protein', 'Water_ml'])

if 'weight_history' not in st.session_state:
    st.session_state.weight_history = pd.DataFrame({'Date': [current_date], 'Weight': [70.0]})

if st.session_state.last_reset_date != current_date:
    yesterday_data = pd.DataFrame([{
        'Date': st.session_state.last_reset_date,
        'Cals': st.session_state.daily_logs['Cals'].sum() if 'daily_logs' in st.session_state else 0,
        'Protein': st.session_state.daily_logs['P'].sum() if 'daily_logs' in st.session_state else 0,
        'Water_ml': st.session_state.water_ml if 'water_ml' in st.session_state else 0
    }])
    st.session_state.history_db = pd.concat([st.session_state.history_db, yesterday_data], ignore_index=True)
    st.session_state.daily_logs = pd.DataFrame(columns=['Time', 'Meal', 'Qty', 'Cals', 'P', 'C', 'F'])
    st.session_state.water_ml = 0
    st.session_state.last_reset_date = current_date

# --- 🧠 DATABASE ---
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

if 'water_ml' not in st.session_state:
    st.session_state.water_ml = 0

# Base Calculations
target_cals = 1350
consumed_cals = st.session_state.daily_logs['Cals'].sum()
remaining_cals = max(0, target_cals - consumed_cals)
total_prot = st.session_state.daily_logs['P'].sum()

# --- 📱 NAVIGATION MENU ---
st.sidebar.title("🍏 HealthifyMenu")
page = st.sidebar.radio("Go to:", [
    "🏠 Dashboard", 
    "🍽️ Food Diary", 
    "💡 AI Diet Coach", 
    "🩹 Recovery & Body", 
    "🛒 Pantry Manager"
])

# ==========================================
# PAGE 1: DASHBOARD
# ==========================================
if page == "🏠 Dashboard":
    st.title("🏠 Overview")
    
    col1, col2 = st.columns([1.5, 1])
    with col1:
        fig = go.Figure(go.Pie(
            values=[consumed_cals, remaining_cals],
            labels=["Consumed", "Remaining"],
            hole=.7,
            marker_colors=['#00e676', '#f5f5f5'],
            showlegend=False
        ))
        fig.update_layout(
            annotations=[dict(text=f'{int(consumed_cals)} / {target_cals}\nkcal', x=0.5, y=0.5, font_size=20, showarrow=False)], 
            margin=dict(t=0, b=0, l=0, r=0),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("Protein Goal")
        st.progress(min(total_prot / 90.0, 1.0), text=f"{total_prot}g / 90g")
        st.write("---")
        st.subheader("💧 Hydration")
        st.progress(min(st.session_state.water_ml / 3500, 1.0), text=f"{st.session_state.water_ml} / 3500 ml")
        
        w1, w2 = st.columns(2)
        if w1.button("🥤 +250ml"):
            st.session_state.water_ml += 250
            st.rerun()
        if w2.button("🍼 +500ml"):
            st.session_state.water_ml += 500
            st.rerun()

# ==========================================
# PAGE 2: FOOD DIARY
# ==========================================
elif page == "🍽️ Food Diary":
    st.title("🍽️ Log Your Meals")
    
    st.markdown("### ➕ Quick Add")
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_food = st.selectbox("Search Food", list(st.session_state.nutrition_db.keys()))
    with col2:
        servings = st.number_input("Portion (e.g., 0.5)", min_value=0.01, value=1.00, step=0.10, format="%.2f")
    
    if st.button("Log Food"):
        item = st.session_state.nutrition_db[selected_food]
        new_entry = pd.DataFrame([[
            datetime.now().strftime("%H:%M"), selected_food, servings, 
            round(item['cals'] * servings, 1), round(item['p'] * servings, 1), 
            round(item['c'] * servings, 1), round(item['f'] * servings, 1)
        ]], columns=['Time', 'Meal', 'Qty', 'Cals', 'P', 'C', 'F'])
        
        st.session_state.daily_logs = pd.concat([st.session_state.daily_logs, new_entry], ignore_index=True)
        if selected_food in st.session_state.stock:
            st.session_state.stock[selected_food] = max(0, st.session_state.stock[selected_food] - servings)
        st.success(f"Logged {servings}x {selected_food}!")
        st.rerun()
        
    st.divider()
    st.subheader("📋 Today's Intake")
    if st.session_state.daily_logs.empty:
        st.info("You haven't logged any meals yet today.")
    else:
        st.dataframe(st.session_state.daily_logs, use_container_width=True)

# ==========================================
# PAGE 3: AI DIET COACH
# ==========================================
elif page == "💡 AI Diet Coach":
    st.title("💡 Smart Suggestions")
    
    current_hour = datetime.now().hour
    
    st.markdown("### 🎯 Your Current Status")
    st.write(f"- **Calories Remaining:** {remaining_cals} kcal")
    st.write(f"- **Protein Needed:** {max(0, 90 - total_prot)}g")
    
    st.divider()
    st.markdown("### 🥗 Recommended Next Meal")
    
    if total_prot < 40 and st.session_state.stock.get("Paneer (100g)", 0) > 0:
        st.success("**Protein Power Bowl**\n\nPrepare **Paneer** with **Olive Oil**. This directly supports your muscle recovery needs.")
    elif current_hour >= 21 and st.session_state.stock.get("Curd (200g)", 0) > 0:
        st.success("**Late Night Recovery**\n\nHave **Curd** mixed with **Chia Seeds**. The slow-release casein protein aids tissue repair overnight.")
    elif st.session_state.stock.get("Avocado (1/2 pc)", 0) > 0:
        st.success("**Joint Support Snack**\n\nHave **Avocado**. The healthy fats are essential for managing inflammation.")
    else:
        st.info("Have an **Orange** or a piece of fruit to support your vitamin goals.")

# ==========================================
# PAGE 4: RECOVERY & BODY
# ==========================================
elif page == "🩹 Recovery & Body":
    st.title("🩹 Physical Check-in")
    
    st.markdown("### 📉 Weight Log (Target: 60kg)")
    w_col1, w_col2 = st.columns([2,1])
    with w_col1:
        new_weight = st.number_input("Log Today's Weight (kg)", min_value=40.0, max_value=100.0, value=70.0, step=0.1)
    with w_col2:
        st.write("")
        st.write("")
        if st.button("Save Weight"):
            new_w_entry = pd.DataFrame({'Date': [datetime.now().date()], 'Weight': [new_weight]})
            st.session_state.weight_history = pd.concat([st.session_state.weight_history, new_w_entry], ignore_index=True)
            st.success("Weight saved!")
            st.rerun()

    if not st.session_state.weight_history.empty:
        # Streamlit line chart handles pandas series perfectly
        chart_data = st.session_state.weight_history.set_index('Date')['Weight']
        st.line_chart(chart_data)

    st.divider()
    st.markdown("### 💊 Daily Medications")
    cal_taken = st.checkbox("🦴 Calcium Tablet (For Bone Contusion)")
    
    if datetime.now().strftime("%A") == "Friday":
        st.error("🚨 **FRIDAY ALERT:** Take your Genivit D3 today!")
        d3_taken = st.checkbox("☀️ Genivit D3 Taken")
        
    st.divider()
    st.markdown("### 🏃‍♀️ Physiotherapy")
    st.info("⚖️ **Mobility Rule:** Strictly 50% Weight Bearing Walk with Walker.")
    st.info("💪 **Focus Areas:** Quadriceps, Hamstrings, and Calf Muscles Strengthening.")
    
    physio_done = st.checkbox("✅ 9:00 PM Physio Session Completed")
    if physio_done:
        st.success("Great job keeping up with your strengthening routine!")

# ==========================================
# PAGE 5: PANTRY MANAGER
# ==========================================
elif page == "🛒 Pantry Manager":
    st.title("🛒 Groceries & Stock")
    
    st.markdown("### 📦 Current Inventory")
    for item, qty in st.session_state.stock.items():
        if qty <= 1:
            st.error(f"{item}: {qty} (Restock Needed!)")
        else:
            st.success(f"{item}: {qty}")
            
    st.divider()
    st.markdown("### 🔄 Restock Items")
    u_col1, u_col2 = st.columns(2)
    stock_item = u_col1.selectbox("Select existing item", list(st.session_state.stock.keys()))
    add_qty = u_col2.number_input("Units to add", min_value=0.0, step=1.0)
    if st.button("Update Inventory"):
        st.session_state.stock[stock_item] += add_qty
        st.success(f"Added {add_qty} to {stock_item}!")
        st.rerun()
        
    st.divider()
    with st.expander("➕ Add Completely New Food to Database"):
        new_name = st.text_input("Item Name (e.g., Almonds 30g)")
        n_col1, n_col2, n_col3, n_col4 = st.columns(4)
        new_cals = n_col1.number_input("Cals", 0)
        new_p = n_col2.number_input("Pro (g)", 0)
        new_c = n_col3.number_input("Carbs (g)", 0)
        new_f = n_col4.number_input("Fats (g)", 0)
        initial_stock = st.number_input("Initial Stock (Servings)", min_value=0.0, step=1.0)
        
        if st.button("Save New Item"):
            if new_name:
                st.session_state.nutrition_db[new_name] = {"cals": new_cals, "p": new_p, "c": new_c, "f": new_f}
                st.session_state.stock[new_name] = initial_stock
                st.success(f"{new_name} added to database!")
                st.rerun()
