import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components
from datetime import datetime
import json
import os

st.set_page_config(page_title="HealthifyDiksha AI", layout="centered", page_icon="🍏")

# --- 💾 PERSISTENT STORAGE ENGINE ---
DATA_FILE = "healthify_data.json"

def save_state():
    """Saves the current session state to a local JSON file."""
    data = {
        'last_reset_date': str(st.session_state.last_reset_date),
        'history_db': st.session_state.history_db.to_dict('records') if not st.session_state.history_db.empty else [],
        'weight_history': st.session_state.weight_history.to_dict('records') if not st.session_state.weight_history.empty else [],
        'custom_tasks': st.session_state.custom_tasks,
        'nutrition_db': st.session_state.nutrition_db,
        'stock': st.session_state.stock,
        'daily_logs': st.session_state.daily_logs.to_dict('records') if not st.session_state.daily_logs.empty else [],
        'water_ml': st.session_state.water_ml
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def update_and_rerun():
    """Forces a save before refreshing the UI."""
    save_state()
    st.rerun()

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

# --- 📂 BULK CSV LOADER ---
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

# --- 🧠 INITIALIZE DATA FROM STORAGE ---
if 'initialized' not in st.session_state:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
            st.session_state.last_reset_date = datetime.strptime(data.get('last_reset_date', str(datetime.now().date())), "%Y-%m-%d").date()
            st.session_state.history_db = pd.DataFrame(data.get('history_db', []))
            st.session_state.weight_history = pd.DataFrame(data.get('weight_history', []))
            st.session_state.custom_tasks = data.get('custom_tasks', {})
            st.session_state.nutrition_db = data.get('nutrition_db', {})
            st.session_state.stock = data.get('stock', {})
            st.session_state.daily_logs = pd.DataFrame(data.get('daily_logs', []))
            st.session_state.water_ml = data.get('water_ml', 0)
        except Exception:
            pass
    st.session_state.initialized = True

# --- FALLBACK DEFAULTS (If file doesn't exist yet) ---
current_date = datetime.now().date()
if 'last_reset_date' not in st.session_state:
    st.session_state.last_reset_date = current_date
if 'history_db' not in st.session_state:
    st.session_state.history_db = pd.DataFrame(columns=['Date', 'Cals', 'Protein', 'Water_ml'])
if 'weight_history' not in st.session_state:
    st.session_state.weight_history = pd.DataFrame({'Date': [current_date], 'Weight': [70.0]})
if 'custom_tasks' not in st.session_state:
    st.session_state.custom_tasks = {
        "🦴 Calcium Tablet": {"freq": "Daily", "done": False},
        "✅ 9:00 PM Physio Session": {"freq": "Daily", "done": False},
        "☀️ Genivit D3": {"freq": "Friday", "done": False}
    }
if 'nutrition_db' not in st.session_state:
    st.session_state.nutrition_db = {
        "Paneer (100g)": {"cals": 265, "p": 18, "c": 2, "f": 20},
        "Curd (200g)": {"cals": 196, "p": 22, "c": 9, "f": 8},
        "Milk (200ml)": {"cals": 120, "p": 6, "c": 10, "f": 5},
        "Protein Bread (1 slice)": {"cals": 70, "p": 5, "c": 10, "f": 1},
        "Avocado (1/2 pc)": {"cals": 160, "p": 2, "c": 9, "f": 15},
        "Banana (1 pc)": {"cals": 105, "p": 1, "c": 27, "f": 0},
        "Orange (1 pc)": {"cals": 45, "p": 1, "c": 11, "f": 0},
        "Oats (30g)": {"cals": 117, "p": 5, "c": 20, "f": 2}
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

# --- 🔄 MIDNIGHT RESET ENGINE ---
if st.session_state.last_reset_date != current_date:
    yesterday_data = pd.DataFrame([{
        'Date': st.session_state.last_reset_date,
        'Cals': st.session_state.daily_logs['Cals'].sum() if not st.session_state.daily_logs.empty else 0,
        'Protein': st.session_state.daily_logs['P'].sum() if not st.session_state.daily_logs.empty else 0,
        'Water_ml': st.session_state.water_ml
    }])
    st.session_state.history_db = pd.concat([st.session_state.history_db, yesterday_data], ignore_index=True)
    st.session_state.daily_logs = pd.DataFrame(columns=['Time', 'Meal', 'Qty', 'Cals', 'P', 'C', 'F'])
    st.session_state.water_ml = 0
    for task in st.session_state.custom_tasks:
        st.session_state.custom_tasks[task]["done"] = False
    st.session_state.last_reset_date = current_date
    save_state()

# Base Calculations
target_cals = 1350
consumed_cals = st.session_state.daily_logs['Cals'].sum() if not st.session_state.daily_logs.empty else 0
remaining_cals = max(0, target_cals - consumed_cals)
total_prot = st.session_state.daily_logs['P'].sum() if not st.session_state.daily_logs.empty else 0

# --- 📱 NAVIGATION MENU ---
st.sidebar.title("🍏 HealthifyMenu")
page = st.sidebar.radio("Go to:", [
    "🏠 Dashboard", 
    "🍽️ Food Diary", 
    "💡 AI Diet Coach", 
    "🩹 Recovery & Tasks", 
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
            values=[consumed_cals, remaining_cals] if remaining_cals > 0 else [consumed_cals, 0],
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
            update_and_rerun()
        if w2.button("🍼 +500ml"):
            st.session_state.water_ml += 500
            update_and_rerun()

    st.divider()
    st.subheader("📋 Today's Tasks")
    today_name = datetime.now().strftime("%A")
    tasks_for_today = {k: v for k, v in st.session_state.custom_tasks.items() if v["freq"] in ["Daily", today_name]}
    
    if not tasks_for_today:
        st.info("No tasks scheduled for today!")
    else:
        for task_name, task_info in tasks_for_today.items():
            if task_info["done"]:
                st.success(f"✅ {task_name}")
            else:
                st.error(f"❌ {task_name} (Pending)")

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
            meal_time = st.time_input("Time Eaten", value=datetime.now())
        
        if st.button("Log Saved Food"):
            item = st.session_state.nutrition_db[selected_food]
            time_str = meal_time.strftime("%H:%M")
            new_entry = pd.DataFrame([[
                time_str, selected_food, servings, 
                round(item['cals'] * servings, 1), round(item['p'] * servings, 1), 
                round(item['c'] * servings, 1), round(item['f'] * servings, 1)
            ]], columns=['Time', 'Meal', 'Qty', 'Cals', 'P', 'C', 'F'])
            
            st.session_state.daily_logs = pd.concat([st.session_state.daily_logs, new_entry], ignore_index=True)
            if selected_food in st.session_state.stock:
                st.session_state.stock[selected_food] = max(0, st.session_state.stock[selected_food] - servings)
                
            st.success(f"Logged {servings}x {selected_food} at {time_str}!")
            update_and_rerun()
            
    with tab2:
        st.markdown("Ate at a restaurant? Log the macros here.")
        custom_meal = st.text_input("What did you eat? (e.g., Subway Sandwich)")
        
        c_col1, c_col2, c_col3, c_col4, c_col5 = st.columns(5)
        custom_cals = c_col1.number_input("Calories", min_value=0)
        custom_p = c_col2.number_input("Protein (g)", min_value=0)
        custom_c = c_col3.number_input("Carbs (g)", min_value=0)
        custom_f = c_col4.number_input("Fats (g)", min_value=0)
        custom_time = c_col5.time_input("Time", value=datetime.now())
        
        if st.button("Log Custom Meal"):
            if custom_meal:
                time_str = custom_time.strftime("%H:%M")
                new_entry = pd.DataFrame([[
                    time_str, f"Outside: {custom_meal}", 1, 
                    custom_cals, custom_p, custom_c, custom_f
                ]], columns=['Time', 'Meal', 'Qty', 'Cals', 'P', 'C', 'F'])
                st.session_state.daily_logs = pd.concat([st.session_state.daily_logs, new_entry], ignore_index=True)
                st.success(f"Logged {custom_meal} at {time_str}!")
                update_and_rerun()

    st.divider()
    st.markdown("### ✏️ Edit or Remove Logged Meals")
    if not st.session_state.daily_logs.empty:
        log_options = {f"{i}: {row['Time']} - {row['Meal']} ({row['Qty']} portions)": i for i, row in st.session_state.daily_logs.iterrows()}
        selected_log_str = st.selectbox("Select a meal to remove", list(log_options.keys()))
        
        if st.button("Remove Meal"):
            idx_to_remove = log_options[selected_log_str]
            row_to_remove = st.session_state.daily_logs.loc[idx_to_remove]
            
            meal_name = row_to_remove['Meal']
            qty_removed = row_to_remove['Qty']
            if meal_name in st.session_state.stock:
                st.session_state.stock[meal_name] += qty_removed
                
            st.session_state.daily_logs = st.session_state.daily_logs.drop(idx_to_remove).reset_index(drop=True)
            st.success("Meal removed and macros recalculated!")
            update_and_rerun()
    else:
        st.info("Your food diary is empty. Log a meal above first!")
        
    st.divider()
    st.subheader("📋 Today's Intake")
    if not st.session_state.daily_logs.empty:
        st.session_state.daily_logs = st.session_state.daily_logs.sort_values(by="Time").reset_index(drop=True)
    st.dataframe(st.session_state.daily_logs, use_container_width=True)

# ==========================================
# PAGE 3: AI DIET COACH
# ==========================================
elif page == "💡 AI Diet Coach":
    st.title("💡 Smart Suggestions")
    st.caption("Recipes suggested here are based purely on what is currently in your Pantry Stock.")
    
    current_hour = datetime.now().hour
    
    st.markdown("### 🎯 Your Current Status")
    st.write(f"- **Calories Remaining:** {remaining_cals} kcal")
    st.write(f"- **Protein Needed:** {max(0, 90 - total_prot)}g")
    
    st.divider()
    st.markdown("### 🥗 Recommended Pantry Meal")
    
    if total_prot < 40 and st.session_state.stock.get("Paneer (100g)", 0) > 0:
        st.success("**Protein Power Bowl**\n\nUse your stocked **Paneer**. This directly supports your quadriceps and hamstring recovery.")
    elif current_hour >= 21 and st.session_state.stock.get("Curd (200g)", 0) > 0:
        st.success("**Late Night Recovery**\n\nUse your stocked **Curd**. The slow-release casein protein aids tissue repair overnight.")
    else:
        st.info("Grab some fruit or hydration. Ensure you stick to your 1350 daily limit.")

# ==========================================
# PAGE 4: RECOVERY & TASKS
# ==========================================
elif page == "🩹 Recovery & Tasks":
    st.title("🩹 Tasks & Physical Check-in")
    
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
            update_and_rerun()

    if not st.session_state.weight_history.empty:
        chart_data = st.session_state.weight_history.set_index('Date')['Weight']
        st.line_chart(chart_data)

    st.divider()
    st.markdown("### 📋 Today's Tasks & Medications")
    today_name = datetime.now().strftime("%A")
    
    for task_name, task_info in st.session_state.custom_tasks.items():
        if task_info["freq"] in ["Daily", today_name]:
            new_status = st.checkbox(task_name, value=task_info["done"])
            if new_status != task_info["done"]:
                st.session_state.custom_tasks[task_name]["done"] = new_status
                update_and_rerun()
                
    st.divider()
    with st.expander("➕ Manage Custom Tasks & Reminders"):
        st.markdown("**Add a new task:**")
        t_col1, t_col2 = st.columns([2, 1])
        new_task_name = t_col1.text_input("Task Name (e.g., Change Bandage)")
        new_task_freq = t_col2.selectbox("Frequency", ["Daily", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        
        if st.button("Add Task"):
            if new_task_name:
                st.session_state.custom_tasks[new_task_name] = {"freq": new_task_freq, "done": False}
                st.success(f"Added {new_task_name} ({new_task_freq})")
                update_and_rerun()

        st.markdown("**Remove a task:**")
        if st.session_state.custom_tasks:
            del_task = st.selectbox("Select task to remove", list(st.session_state.custom_tasks.keys()))
            if st.button("Remove Task"):
                del st.session_state.custom_tasks[del_task]
                st.success("Task removed!")
                update_and_rerun()

    st.divider()
    st.markdown("### 🏃‍♀️ Physiotherapy Rules")
    st.info("⚖️ **Mobility Rule:** Strictly 50% Weight Bearing Walk with Walker.")
    st.info("💪 **Focus Areas:** Quadriceps, Hamstrings, and Calf Muscles Strengthening.")

# ==========================================
# PAGE 5: PANTRY MANAGER
# ==========================================
elif page == "🛒 Pantry Manager":
    st.title("🛒 Groceries & Library")
    
    st.markdown("### 📦 Current Inventory")
    if not st.session_state.stock:
        st.info("Your pantry is completely empty!")
    else:
        for item, qty in st.session_state.stock.items():
            if qty <= 1:
                st.error(f"{item}: {qty} (Restock Needed!)")
            else:
                st.success(f"{item}: {qty}")
                
    st.divider()
    
    st.markdown("### ✏️ Edit or Remove Stock")
    if st.session_state.stock:
        e_col1, e_col2 = st.columns(2)
        edit_item = e_col1.selectbox("Select item to modify", list(st.session_state.stock.keys()))
        
        current_qty = st.session_state.stock[edit_item]
        new_qty = e_col2.number_input("Set exact quantity (Set to 0 to remove)", min_value=0.0, value=float(current_qty), step=0.5)
        
        if st.button("Save Changes"):
            if new_qty == 0:
                del st.session_state.stock[edit_item]
                st.success(f"Removed {edit_item} from pantry.")
            else:
                st.session_state.stock[edit_item] = new_qty
                st.success(f"Updated {edit_item} to {new_qty}.")
            update_and_rerun()
    else:
        st.caption("Add items to your pantry to edit them here.")

    st.divider()
    
    with st.expander("📂 Bulk Import Data (Kaggle/CSV)"):
        st.markdown("Download your CSV and upload it here to expand your Food Diary instantly.")
        uploaded_csv = st.file_uploader("Upload Nutrition CSV", type=["csv"])
        if uploaded_csv:
            new_items = load_kaggle_csv(uploaded_csv)
            if new_items:
                st.session_state.nutrition_db.update(new_items)
                st.success(f"🔥 Successfully added {len(new_items)} new foods to your Diary!")
                save_state()
            else:
                st.error("Could not parse file. Ensure column names match.")

    st.divider()
    with st.expander("➕ Add Single Food & Restock"):
        st.markdown("Add a single custom item and put it straight into your pantry.")
        new_name = st.text_input("Item Name (e.g., Muesli 50g)")
        n_col1, n_col2, n_col3, n_col4 = st.columns(4)
        new_cals = n_col1.number_input("Cals", 0)
        new_p = n_col2.number_input("Pro (g)", 0)
        new_c = n_col3.number_input("Carbs (g)", 0)
        new_f = n_col4.number_input("Fats (g)", 0)
        initial_stock = st.number_input("Initial Stock (Servings)", min_value=0.0, step=1.0)
        
        if st.button("Save & Restock"):
            if new_name:
                st.session_state.nutrition_db[new_name] = {"cals": new_cals, "p": new_p, "c": new_c, "f": new_f}
                st.session_state.stock[new_name] = initial_stock
                st.success(f"{new_name} added to database and pantry!")
                update_and_rerun()
