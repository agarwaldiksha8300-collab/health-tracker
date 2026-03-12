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

# --- 📂 BULK CSV LOADER (KAGGLE SYNC) ---
@st.cache_data
def load_kaggle_csv(uploaded_file):
    new_items = {}
    try:
        df = pd.read_csv(uploaded_file)
        for _, row in df.iterrows():
            name = str(row.get('Dish Name', 'Unknown')).strip()
            cals = float(row.get('Calories (kcal)', 0))
            p = float(row.get('Protein (g)', 0))
            c = float(row.get('Carbohydrates (g)', 0))
            f = float(row.get('Fats (g)', 0))
            
            if name != 'nan' and name != 'Unknown':
                new_items[name] = {"cals": cals, "p": p, "c": c, "f": f}
        return new_items
    except Exception as e:
        return {}

# --- 🔄 STATE & RESET ENGINE ---
current_date = datetime.now().date()
if 'last_reset_date' not in st.session_state:
    st.session_state.last_reset_date = current_date

if 'history_db' not in st.session_state:
    st.session_state.history_db = pd.DataFrame(columns=['Date', 'Cals', 'Protein', 'Water_ml', 'Calcium_Taken', 'Physio_Done'])

if 'weight_history' not in st.session_state:
    st.session_state.weight_history = pd.DataFrame({'Date': [current_date], 'Weight': [70.0]})

if 'cal_taken' not in st.session_state:
    st.session_state.cal_taken = False
if 'physio_done' not in st.session_state:
    st.session_state.physio_done = False

if st.session_state.last_reset_date != current_date:
    yesterday_data = pd.DataFrame([{
        'Date': st.session_state.last_reset_date,
        'Cals': st.session_state.daily_logs['Cals'].sum() if 'daily_logs' in st.session_state else 0,
        'Protein': st.session_state.daily_logs['P'].sum() if 'daily_logs' in st.session_state else 0,
        'Water_ml': st.session_state.water_ml if 'water_ml' in st.session_state else 0,
        'Calcium_Taken': st.session_state.cal_taken,
        'Physio_Done': st.session_state.physio_done
    }])
    st.session_state.history_db = pd.concat([st.session_state.history_db, yesterday_data], ignore_index=True)
    st.session_state.daily_logs = pd.DataFrame(columns=['Time', 'Meal', 'Qty', 'Cals', 'P', 'C', 'F'])
    st.session_state.water_ml = 0
    st.session_state.cal_taken = False
    st.session_state.physio_done = False
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
        "Masala Dosa (1 pc)": {"cals": 415, "p": 8, "c": 60, "f": 15},
        "Veg Biryani (1 bowl)": {"cals": 350, "p": 8, "c": 55, "f": 10},
        "Margherita Pizza (1 slice)": {"cals": 250, "p": 10, "c": 30, "f": 10}
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
            margin=dict(t=0, b=0, l=0, r=0), height=300
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

    st.divider()
    st.subheader("🩹 Daily Recovery Tracker")
    r1, r2 = st.columns(2)
    with r1:
        if st.session_state.cal_taken:
            st.success("✅ Calcium Taken")
        else:
            st.error("❌ Calcium Pending")
    with r2:
        if st.session_state.physio_done:
            st.success("✅ Physio Done")
        else:
            st.warning("⏳ Physio Pending (9 PM)")

# ==========================================
# PAGE 2: FOOD DIARY
# ==========================================
elif page == "🍽️ Food Diary":
    st.title("🍽️ Log Your Meals")
    
    tab1, tab2 = st.tabs(["📚 From Database / Pantry", "🍔 Quick Add Outside Meal"])
    
    with tab1:
        st.markdown("Search your expanding library of foods.")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            selected_food = st.selectbox("Search Food", list(st.session_state.nutrition_db.keys()))
        with col2:
            servings = st.number_input("Portion (e.g., 0.5)", min_value=0.01, value=1.00, step=0.10, format="%.2f")
        with col3:
