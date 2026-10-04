import io
import requests
from datetime import date
import streamlit as st

# PDF Generation Engine
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

# Optional MyFitnessPal client
try:
    import myfitnesspal
    MFP_AVAILABLE = True
except ImportError:
    MFP_AVAILABLE = False

st.set_page_config(page_title="Multi-Option Macro Planner", layout="wide")

# ---------------------------------------------------------
# Default Multi-Option Blueprint (Macros per 100g)
# ---------------------------------------------------------
DEFAULT_MULTI_PLAN = {
    "Meal 1 (Pre-Workout)": {
        "Option A": [
            {"name": "Cream of Rice (dry)", "grams": 50.0, "cal_100": 360.0, "pro_100": 7.0, "carb_100": 80.0, "fat_100": 1.0},
            {"name": "USN BlueLab Whey (Chocolate)", "grams": 32.0, "cal_100": 384.4, "pro_100": 80.0, "carb_100": 8.1, "fat_100": 4.1},
            {"name": "Banana", "grams": 75.0, "cal_100": 96.0, "pro_100": 1.3, "carb_100": 22.7, "fat_100": 0.0},
        ],
        "Option B": [
            {"name": "Health Connection Oat Bran", "grams": 60.0, "cal_100": 334.7, "pro_100": 17.3, "carb_100": 51.1, "fat_100": 7.1},
            {"name": "USN BlueLab Whey (Chocolate)", "grams": 30.0, "cal_100": 384.4, "pro_100": 80.0, "carb_100": 8.1, "fat_100": 4.1},
            {"name": "Blueberries / Strawberries", "grams": 100.0, "cal_100": 45.0, "pro_100": 0.8, "carb_100": 10.0, "fat_100": 0.4},
        ]
    },
    "Intra-Workout": {
        "Option A": [
            {"name": "Dextrose Monohydrate", "grams": 30.0, "cal_100": 390.0, "pro_100": 0.0, "carb_100": 90.0, "fat_100": 0.0},
            {"name": "NPL BCAA 12:1:1", "grams": 15.0, "cal_100": 140.0, "pro_100": 0.0, "carb_100": 0.0, "fat_100": 0.0},
        ]
    },
    "Meal 2 (Post-Workout)": {
        "Option A": [
            {"name": "White Star Maize Meal (raw dry)", "grams": 100.0, "cal_100": 346.0, "pro_100": 7.2, "carb_100": 75.2, "fat_100": 2.4},
            {"name": "USN BlueLab Whey (Caramel Super M)", "grams": 50.0, "cal_100": 384.0, "pro_100": 80.0, "carb_100": 8.0, "fat_100": 4.0},
        ],
        "Option B": [
            {"name": "Jasmine Rice (cooked)", "grams": 260.0, "cal_100": 130.0, "pro_100": 2.7, "carb_100": 28.2, "fat_100": 0.3},
            {"name": "USN BlueLab Whey (Caramel Super M)", "grams": 50.0, "cal_100": 384.0, "pro_100": 80.0, "carb_100": 8.0, "fat_100": 4.0},
        ]
    },
    "Meal 3": {
        "Option A": [
            {"name": "Chicken Breast (cooked, skinless)", "grams": 150.0, "cal_100": 159.3, "pro_100": 33.3, "carb_100": 0.0, "fat_100": 3.3},
            {"name": "Courgette / Zucchini", "grams": 200.0, "cal_100": 16.0, "pro_100": 2.0, "carb_100": 2.0, "fat_100": 0.0},
            {"name": "Avocado (Hass)", "grams": 50.0, "cal_100": 180.0, "pro_100": 2.0, "carb_100": 9.0, "fat_100": 15.0},
        ],
        "Option B": [
            {"name": "White Fish / Hake (cooked)", "grams": 190.0, "cal_100": 95.0, "pro_100": 20.0, "carb_100": 0.0, "fat_100": 1.5},
            {"name": "Courgette / Zucchini", "grams": 200.0, "cal_100": 16.0, "pro_100": 2.0, "carb_100": 2.0, "fat_100": 0.0},
            {"name": "Olive Oil (cold pressed)", "grams": 12.0, "cal_100": 884.0, "pro_100": 0.0, "carb_100": 0.0, "fat_100": 100.0},
        ]
    },
    "Meal 4": {
        "Option A": [
            {"name": "Lean Beef Steak (raw, trimmed)", "grams": 150.0, "cal_100": 106.7, "pro_100": 20.7, "carb_100": 0.0, "fat_100": 2.5},
            {"name": "Pumpkin (cooked/steamed)", "grams": 333.0, "cal_100": 45.0, "pro_100": 2.0, "carb_100": 6.4, "fat_100": 1.2},
        ],
        "Option B": [
            {"name": "Extra Lean Beef Mince (<5% fat, raw)", "grams": 150.0, "cal_100": 125.0, "pro_100": 21.0, "carb_100": 0.0, "fat_100": 4.5},
            {"name": "Baby Potatoes (boiled/steamed)", "grams": 120.0, "cal_100": 77.0, "pro_100": 2.0, "carb_100": 17.5, "fat_100": 0.1},
        ]
    },
    "Meal 5": {
        "Option A": [
            {"name": "NPL Micellar Casein", "grams": 50.0, "cal_100": 370.0, "pro_100": 74.0, "carb_100": 14.0, "fat_100": 2.0},
            {"name": "Health Connection Oat Bran", "grams": 75.0, "cal_100": 334.7, "pro_100": 17.3, "carb_100": 51.1, "fat_100": 7.1},
            {"name": "Almond Butter", "grams": 10.0, "cal_100": 630.0, "pro_100": 20.0, "carb_100": 10.0, "fat_100": 60.0},
        ],
        "Option B": [
            {"name": "Fat Free Plain Cottage Cheese", "grams": 250.0, "cal_100": 72.0, "pro_100": 12.5, "carb_100": 4.0, "fat_100": 0.5},
            {"name": "Health Connection Oat Bran", "grams": 70.0, "cal_100": 334.7, "pro_100": 17.3, "carb_100": 51.1, "fat_100": 7.1},
            {"name": "Walnuts / Almonds", "grams": 15.0, "cal_100": 650.0, "pro_100": 15.0, "carb_100": 14.0, "fat_100": 65.0},
        ]
    }
}

if "multi_plan" not in st.session_state:
    st.session_state.multi_plan = DEFAULT_MULTI_PLAN

if "active_selections" not in st.session_state:
    st.session_state.active_selections = {m: list(opts.keys())[0] for m, opts in st.session_state.multi_plan.items()}

# ---------------------------------------------------------
# Calculations & Online Food Search
# ---------------------------------------------------------
def search_online_food(query):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&search_simple=1&action=process&json=1&page_size=6"
    headers = {"User-Agent": "MultiOptionMacroPlanner/1.0"}
    try:
        res = requests.get(url, headers=headers, timeout=6)
        if res.status_code == 200:
            data = res.json()
            products = []
            for item in data.get("products", []):
                nutriments = item.get("nutriments", {})
                name = item.get("product_name", "Unknown item")
                cal = nutriments.get("energy-kcal_100g", nutriments.get("energy-kcal", 0))
                if not cal and "energy_100g" in nutriments:
                    cal = round(nutriments.get("energy_100g", 0) / 4.184, 1)
                pro = nutriments.get("proteins_100g", nutriments.get("proteins", 0))
                carb = nutriments.get("carbohydrates_100g", nutriments.get("carbohydrates", 0))
                fat = nutriments.get("fat_100g", nutriments.get("fat", 0))

                products.append({
                    "name": name,
                    "cal_100": float(cal or 0),
                    "pro_100": float(pro or 0),
                    "carb_100": float(carb or 0),
                    "fat_100": float(fat or 0)
                })
            return products
    except Exception as e:
        st.error(f"Network error contacting nutrition database: {e}")
    return []

def calculate_totals(items):
    c, p, carb, f = 0.0, 0.0, 0.0, 0.0
    for item in items:
        scale = item["grams"] / 100.0
        c += scale * item["cal_100"]
        p += scale * item["pro_100"]
        carb += scale * item["carb_100"]
        f += scale * item["fat_100"]
    return c, p, carb, f

# ---------------------------------------------------------
# PDF Generator
# ---------------------------------------------------------
def generate_pdf(multi_plan, active_selections):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor('#0F172A'), fontName='Helvetica-Bold')
    section_heading = ParagraphStyle('SecHeading', parent=styles['Heading2'], fontSize=11, leading=14, textColor=colors.HexColor('#1E3A8A'), fontName='Helvetica-Bold', spaceBefore=6, spaceAfter=4)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=8.5, leading=11, textColor=colors.HexColor('#334155'))
    cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.HexColor('#1E293B'))
    cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.HexColor('#0F172A'), fontName='Helvetica-Bold')

    elements.append(Paragraph("TRAINING DAY MEAL PLAN — MULTI-OPTION BLUEPRINT", title_style))
    elements.append(Paragraph("Interchangeable Meal Variations with Precision Macro Balancing", body_style))
    elements.append(Spacer(1, 10))

    act_cal, act_pro, act_carb, act_fat = 0.0, 0.0, 0.0, 0.0
    for meal_name, opt_name in active_selections.items():
        if meal_name in multi_plan and opt_name in multi_plan[meal_name]:
            c, p, cb, f = calculate_totals(multi_plan[meal_name][opt_name])
            act_cal += c
            act_pro += p
            act_carb += cb
            act_fat += f

    summary_data = [
        [Paragraph("<b>Active Blueprint Calories</b>", cell_bold), Paragraph("<b>Protein</b>", cell_bold), Paragraph("<b>Carbohydrates</b>", cell_bold), Paragraph("<b>Total Fats</b>", cell_bold)],
        [Paragraph(f"<b>{act_cal:.0f} kcal</b>", cell_style), Paragraph(f"<b>{act_pro:.1f} g</b>", cell_style), Paragraph(f"<b>{act_carb:.1f} g</b>", cell_style), Paragraph(f"<b>{act_fat:.1f} g</b>", cell_style)]
    ]
    t_summary = Table(summary_data, colWidths=[135, 135, 135, 135])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#FFFFFF')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t_summary)
    elements.append(Spacer(1, 10))

    for meal_name, options in multi_plan.items():
        meal_block = []
        meal_block.append(Paragraph(meal_name.upper(), section_heading))
        for opt_name, items in options.items():
            is_active = "(ACTIVE BLUEPRINT)" if active_selections.get(meal_name) == opt_name else ""
            meal_block.append(Paragraph(f"<b>{opt_name}</b> {is_active}", body_style))
            
            table_data = [[
                Paragraph("<b>Item Description</b>", cell_bold),
                Paragraph("<b>Grams</b>", cell_bold),
                Paragraph("<b>Calories</b>", cell_bold),
                Paragraph("<b>Protein</b>", cell_bold),
                Paragraph("<b>Carbs</b>", cell_bold),
                Paragraph("<b>Fat</b>", cell_bold)
            ]]

            c_tot, p_tot, carb_tot, f_tot = 0.0, 0.0, 0.0, 0.0
            for item in items:
                scale = item["grams"] / 100.0
                i_cal = scale * item["cal_100"]
                i_pro = scale * item["pro_100"]
                i_carb = scale * item["carb_100"]
                i_fat = scale * item["fat_100"]
                c_tot += i_cal
                p_tot += i_pro
                carb_tot += i_carb
                f_tot += i_fat

                table_data.append([
                    Paragraph(item["name"], cell_style),
                    Paragraph(f"{item['grams']:.0f} g", cell_style),
                    Paragraph(f"{i_cal:.0f} kcal", cell_style),
                    Paragraph(f"{i_pro:.1f} g", cell_style),
                    Paragraph(f"{i_carb:.1f} g", cell_style),
                    Paragraph(f"{i_fat:.1f} g", cell_style),
                ])

            table_data.append([
                Paragraph(f"<b>{opt_name} Subtotal</b>", cell_bold),
                Paragraph("-", cell_bold),
                Paragraph(f"<b>{c_tot:.0f} kcal</b>", cell_bold),
                Paragraph(f"<b>{p_tot:.1f} g</b>", cell_bold),
                Paragraph(f"<b>{carb_tot:.1f} g</b>", cell_bold),
                Paragraph(f"<b>{f_tot:.1f} g</b>", cell_bold),
            ])

            t_opt = Table(table_data, colWidths=[200, 60, 70, 70, 70, 70])
            t_opt.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F8FAFC')),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F1F5F9')),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#94A3B8')),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#94A3B8')),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                ('INNERGRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#E2E8F0')),
                ('TOPPADDING', (0, 0), (-1, -1), 2.5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
            ]))
            meal_block.append(t_opt)
            meal_block.append(Spacer(1, 4))

        elements.append(KeepTogether(meal_block))
        elements.append(Spacer(1, 6))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ---------------------------------------------------------
# Sidebar: Target Config, Online Search & MFP Integration
# ---------------------------------------------------------
st.sidebar.title("🛠️ Tools & Food Lookup")

target_meal = st.sidebar.selectbox("Target Meal Slot:", list(st.session_state.multi_plan.keys()))
options_for_meal = list(st.session_state.multi_plan[target_meal].keys())
target_option = st.sidebar.selectbox(f"Target Variant for {target_meal}:", options_for_meal)

with st.sidebar.expander("➕ Create New Meal Option"):
    new_opt_name = st.text_input("Option Name:", value=f"Option {chr(65 + len(options_for_meal))}")
    if st.button("Create Option"):
        if new_opt_name not in st.session_state.multi_plan[target_meal]:
            st.session_state.multi_plan[target_meal][new_opt_name] = []
            st.success(f"Added {new_opt_name} to {target_meal}!")
            st.rerun()

with st.sidebar.expander("Search Live Nutrition Database", expanded=True):
    search_term = st.text_input("Product Name:", placeholder="e.g. basmati rice, lean steak")
    if st.button("Search Web"):
        if search_term.strip():
            with st.spinner("Searching online database..."):
                results = search_online_food(search_term)
                st.session_state.search_results = results
        else:
            st.warning("Please enter a search term.")

    if "search_results" in st.session_state and st.session_state.search_results:
        options = {f"{p['name'][:30]} ({p['cal_100']:.0f} kcal/100g)": p for p in st.session_state.search_results}
        selected_label = st.selectbox("Select Result:", list(options.keys()))
        selected_item = options[selected_label]
        
        add_grams = st.number_input("Serving Grams:", min_value=1.0, max_value=1000.0, value=100.0, step=5.0)
        if st.button("➕ Add to Selected Variant"):
            st.session_state.multi_plan[target_meal][target_option].append({
                "name": selected_item["name"],
                "grams": float(add_grams),
                "cal_100": selected_item["cal_100"],
                "pro_100": selected_item["pro_100"],
                "carb_100": selected_item["carb_100"],
                "fat_100": selected_item["fat_100"]
            })
            st.success(f"Added to {target_meal} [{target_option}]!")
            st.rerun()

# MyFitnessPal Sidebar Integration
with st.sidebar.expander("📲 MyFitnessPal Sync"):
    st.caption("Direct Diary Push (requires active session without bot-checks)")
    mfp_user = st.text_input("MFP Username/Email")
    mfp_pass = st.text_input("MFP Password", type="password")
    if st.button("Sync Active Plan to Today's Diary"):
        if not MFP_AVAILABLE:
            st.error("The 'myfitnesspal' package is not installed. Run `pip install myfitnesspal`.")
        elif mfp_user and mfp_pass:
            try:
                with st.spinner("Authenticating with MyFitnessPal..."):
                    client = myfitnesspal.Client(mfp_user, password=mfp_pass)
                    today = date.today()
                    day = client.get_date(today.year, today.month, today.day)
                    
                    meal_slot_map = {
                        "Meal 1 (Pre-Workout)": "Meal 1",
                        "Intra-Workout": "Meal 2",
                        "Meal 2 (Post-Workout)": "Meal 3",
                        "Meal 3": "Meal 4",
                        "Meal 4": "Meal 5",
                        "Meal 5": "Meal 6"
                    }

                    for m_name, chosen_opt in st.session_state.active_selections.items():
                        slot = meal_slot_map.get(m_name, "Meal 1")
                        for itm in st.session_state.multi_plan[m_name][chosen_opt]:
                            results = client.get_food_search_results(itm["name"])
                            if results:
                                day.meals[slot].add_entry(results[0], itm["grams"] / 100.0)

                    st.success("Active plan synced to your MyFitnessPal diary!")
            except Exception as ex:
                st.error(f"Sync failed: {ex}. MFP frequently blocks script logins via Cloudflare; use the Quick-Add card below for instant logging.")
        else:
            st.warning("Enter your MFP credentials.")

# ---------------------------------------------------------
# Main Page: Multi-Option Meal Designer & Macro Balancer
# ---------------------------------------------------------
st.title("🏋️ Multi-Option Meal Plan Designer")
st.markdown("Build interchangeable meals (Option A vs. Option B), balance macros dynamically, and export clean PDFs.")

active_daily_cal, active_daily_pro, active_daily_carb, active_daily_fat = 0.0, 0.0, 0.0, 0.0

for meal_name, options in st.session_state.multi_plan.items():
    with st.expander(f"🍽️ {meal_name.upper()}", expanded=True):
        opt_names = list(options.keys())
        c_pick, c_delta = st.columns([2, 4])
        with c_pick:
            chosen = st.radio(
                f"Active variant for {meal_name}:",
                opt_names,
                index=opt_names.index(st.session_state.active_selections.get(meal_name, opt_names[0])),
                key=f"radio_{meal_name}",
                horizontal=True
            )
            st.session_state.active_selections[meal_name] = chosen

        # Calculate macro differences across first two options
        if len(opt_names) >= 2:
            c1, p1, cb1, f1 = calculate_totals(options[opt_names[0]])
            c2, p2, cb2, f2 = calculate_totals(options[opt_names[1]])
            diff_cal = c2 - c1
            diff_pro = p2 - p1
            diff_carb = cb2 - cb1
            diff_fat = f2 - f1
            with c_delta:
                st.info(
                    f"**Variance ({opt_names[1]} vs {opt_names[0]}):** "
                    f"`Δ {diff_cal:+.0f} kcal` | `P: {diff_pro:+.1f}g` | `C: {diff_carb:+.1f}g` | `F: {diff_fat:+.1f}g`"
                )

        # Tabs for editing Option A, Option B, etc.
        tabs = st.tabs([f"📝 {opt}" for opt in opt_names])
        for opt_idx, opt_name in enumerate(opt_names):
            with tabs[opt_idx]:
                items = options[opt_name]
                if not items:
                    st.write("_No food items in this option. Add items via the sidebar._")
                else:
                    cols = st.columns([3, 2, 1, 1, 1, 1, 0.5])
                    cols[0].markdown("**Food Item**")
                    cols[1].markdown("**Grams**")
                    cols[2].markdown("**Calories**")
                    cols[3].markdown("**Protein**")
                    cols[4].markdown("**Carbs**")
                    cols[5].markdown("**Fat**")
                    cols[6].markdown("**Del**")
                    st.divider()

                    items_to_remove = []
                    for idx, item in enumerate(items):
                        c = st.columns([3, 2, 1, 1, 1, 1, 0.5])
                        c[0].write(item["name"])
                        new_grams = c[1].number_input(
                            f"g_{meal_name}_{opt_name}_{idx}",
                            min_value=0.0,
                            max_value=1500.0,
                            value=float(item["grams"]),
                            step=5.0,
                            label_visibility="collapsed"
                        )
                        item["grams"] = new_grams

                        scale = new_grams / 100.0
                        i_cal = scale * item["cal_100"]
                        i_pro = scale * item["pro_100"]
                        i_carb = scale * item["carb_100"]
                        i_fat = scale * item["fat_100"]

                        c[2].write(f"{i_cal:.0f} kcal")
                        c[3].write(f"{i_pro:.1f}g")
                        c[4].write(f"{i_carb:.1f}g")
                        c[5].write(f"{i_fat:.1f}g")

                        if c[6].button("🗑️", key=f"del_{meal_name}_{opt_name}_{idx}"):
                            items_to_remove.append(idx)

                    if items_to_remove:
                        for idx in sorted(items_to_remove, reverse=True):
                            items.pop(idx)
                        st.rerun()

                m_cal, m_pro, m_carb, m_fat = calculate_totals(items)
                st.markdown(
                    f"**{opt_name} Subtotal:** `{m_cal:.0f} kcal` | **P:** `{m_pro:.1f}g` | **C:** `{m_carb:.1f}g` | **F:** `{m_fat:.1f}g`"
                )

        # Accumulate active selection macros
        act_c, act_p, act_cb, act_f = calculate_totals(options[st.session_state.active_selections[meal_name]])
        active_daily_cal += act_c
        active_daily_pro += act_p
        active_daily_carb += act_cb
        active_daily_fat += act_f

# ---------------------------------------------------------
# Daily Totals & MFP Quick-Add Reference Card
# ---------------------------------------------------------
st.markdown("## 📊 Active Blueprint Daily Totals")
st.caption("Reflects the exact combination of active meal options selected above.")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Calories", f"{active_daily_cal:.0f} kcal")
col2.metric("Protein", f"{active_daily_pro:.1f} g")
col3.metric("Carbohydrates", f"{active_daily_carb:.1f} g")
col4.metric("Fats", f"{active_daily_fat:.1f} g")

with st.expander("⚡ MyFitnessPal Manual Quick-Add Numbers (Bypasses Login Blocks)"):
    st.write("Use the **Quick Add** button in MyFitnessPal to enter these calculated values directly:")
    q_data = []
    for m_name, chosen_opt in st.session_state.active_selections.items():
        c, p, cb, f = calculate_totals(st.session_state.multi_plan[m_name][chosen_opt])
        q_data.append({
            "Meal": m_name,
            "Active Variant": chosen_opt,
            "Calories (kcal)": f"{c:.0f}",
            "Protein (g)": f"{p:.1f}",
            "Carbs (g)": f"{cb:.1f}",
            "Fat (g)": f"{f:.1f}"
        })
    st.table(q_data)

st.divider()

col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    if st.button("🔄 Reset to Default Plans"):
        st.session_state.multi_plan = DEFAULT_MULTI_PLAN
        st.session_state.active_selections = {m: list(opts.keys())[0] for m, opts in DEFAULT_MULTI_PLAN.items()}
        st.rerun()

with col_btn2:
    pdf_buffer = generate_pdf(st.session_state.multi_plan, st.session_state.active_selections)
    st.download_button(
        label="📄 Download Multi-Option PDF Blueprint",
        data=pdf_buffer,
        file_name="Multi_Option_Meal_Plan_Blueprint.pdf",
        mime="application/pdf"
    )