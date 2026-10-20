import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json

# --- Page Configuration ---
st.set_page_config(page_title="داشبورد راهبری سینماها (بهمن سبز)", page_icon="🎬", layout="wide", initial_sidebar_state="expanded")

# --- UI & Styling (Soft Minimal & Curved Green Theme) ---
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');
    
    html, body, [class*="css"], div, h1, h2, h3, h4, h5, h6, p, span, label {
        font-family: 'Vazirmatn', sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    
    /* Background and Layout */
    .stApp { background-color: #f4f7f6; }
    
    /* Capsule Buttons */
    .stButton>button {
        border-radius: 9999px !important;
        background-color: #10b981 !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 8px 24px -8px rgba(16, 185, 129, 0.4) !important;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 12px 32px -8px rgba(16, 185, 129, 0.6) !important; }
    
    /* Curved Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 24px;
        padding: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.05);
    }
    
    /* Curved Inputs & Containers */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input {
        border-radius: 16px !important;
        border: 1px solid #cbd5e1 !important;
    }
    div[data-testid="stExpander"] {
        background-color: white;
        border-radius: 24px !important;
        border: 1px solid #10b981 !important;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.02);
    }
    
    /* Custom Sidebar */
    [data-testid="stSidebar"] { background-color: #ffffff; border-left: 1px solid #e2e8f0; }
</style>
""", unsafe_allow_html=True)

# --- Supabase Configuration ---
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "").strip().rstrip('/')
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "").strip()

def get_headers():
    return {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

# --- Data Fetching ---
@st.cache_data(ttl=10)
def fetch_cinemas():
    if not SUPABASE_URL: return pd.DataFrame()
    res = requests.get(f"{SUPABASE_URL}/rest/v1/cinemas?select=*", headers=get_headers())
    return pd.DataFrame(res.json()) if res.status_code == 200 else pd.DataFrame()

@st.cache_data(ttl=10)
def fetch_weights():
    # اوزان پیش‌فرض برای ۵ محور ارزیابی
    default_w = {"location": 0.20, "physical": 0.25, "technical": 0.25, "operations": 0.15, "amenities": 0.15}
    if not SUPABASE_URL: return default_w
    res = requests.get(f"{SUPABASE_URL}/rest/v1/app_config?key=eq.axis_weights", headers=get_headers())
    if res.status_code == 200 and len(res.json()) > 0: return res.json()[0].get("value", default_w)
    return default_w

df = fetch_cinemas()
weights = fetch_weights()

# Data Pre-processing
if not df.empty:
    for col in ['score_location', 'score_physical', 'score_technical', 'score_operations', 'score_amenities']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Calculate weighted score using dynamic weights
    df['weighted_score'] = (
        df['score_location'] * float(weights['location']) +
        df['score_physical'] * float(weights['physical']) +
        df['score_technical'] * float(weights['technical']) +
        df['score_operations'] * float(weights['operations']) +
        df['score_amenities'] * float(weights['amenities'])
    ).round(2)
    
    # محاسبه بهره‌وری صندلی‌ها
    df['seat_efficiency'] = ((pd.to_numeric(df['operational_seats'], errors='coerce') / 
                              pd.to_numeric(df['total_seats'], errors='coerce').replace(0, 1)) * 100).round(1)

# --- Sidebar Navigation ---
st.sidebar.title("🎬 راهبری سینماها")
menu = st.sidebar.radio("منوی اصلی", [
    "📊 داشبورد کلان", 
    "🪪 پروفایل و شناسنامه سینما", 
    "📝 ارزیابی و ثبت چک‌لیست",
    "⚙️ تنظیمات وزن‌ها (مدیر)",
    "💾 خروجی و پشتیبان‌گیری"
])

# ==========================================
# 1. داشبورد کلان
# ==========================================
if menu == "📊 داشبورد کلان":
    st.title("🟢 داشبورد جامع راهبری سینماها")
    st.caption("سیستم هوشمند ارزیابی مبتنی بر معماری منحنی و منعطف")
    st.divider()
    
    if not df.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("کل سینماها", len(df))
        c2.metric("مجموع صندلی فعال", f"{int(df['operational_seats'].sum()):,}")
        c3.metric("میانگین امتیاز شبکه", f"{df['weighted_score'].mean():.2f} / 5")
        c4.metric("میانگین بهره‌وری", f"{df['seat_efficiency'].mean():.1f}%")
        
        st.write("### 📈 رتبه‌بندی کیفی سینماها")
        # رفع خطای ValueError با جایگزینی text_auto به جای text="weighted_score"
        fig = px.bar(df, x="name", y="weighted_score", color="weighted_score",
                     color_continuous_scale="Viridis", text_auto='.2f',
                     labels={"name": "سینما", "weighted_score": "امتیاز کل"})
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", 
                          margin=dict(t=20, b=20, l=20, r=20))
        fig.update_traces(marker_line_width=0, opacity=0.8, width=0.5, 
                          hovertemplate='<b>%{x}</b><br>امتیاز: %{y}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("هنوز داده‌ای ثبت نشده است.")

# ==========================================
# 2. پروفایل اختصاصی سینما
# ==========================================
elif menu == "🪪 پروفایل و شناسنامه سینما":
    st.title("🪪 پروفایل تخصصی سینما")
    if not df.empty:
        selected = st.selectbox("انتخاب سینما:", df['name'].tolist())
        c_data = df[df['name'] == selected].iloc[0]
        
        st.markdown(f"## 🏢 {c_data['name']}")
        st.caption(f"📍 {c_data['province']} - {c_data['city']} | 📝 {c_data['address']}")
        
        # اطلاعات پایه‌ای و ظرفیت‌ها
        sc1, sc2, sc3, sc4 = st.columns(4)
        sc1.metric("تعداد سالن", c_data['halls'])
        sc2.metric("ظرفیت اسمی", c_data['nominal_capacity'])
        sc3.metric("صندلی عملیاتی", c_data['operational_seats'])
        sc4.metric("بهره‌وری فضا", f"{c_data['seat_efficiency']}%")
        
        st.divider()
        st.write("### 🕸️ وضعیت ارزیابی در ۵ محور کلیدی")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            categories = ['دسترسی', 'وضعیت فیزیکی', 'فنی و تجهیزات', 'راهبری', 'امکانات جانبی']
            scores = [c_data['score_location'], c_data['score_physical'], 
                      c_data['score_technical'], c_data['score_operations'], c_data['score_amenities']]
            
            fig_radar = go.Figure(data=go.Scatterpolar(
                r=scores + [scores[0]], theta=categories + [categories[0]], fill='toself', line_color='#10b981'
            ))
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                                    showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_radar, use_container_width=True)
            
        with col2:
            st.markdown(f"""
            <div style='background: white; padding: 30px; border-radius: 24px; border: 1px solid #10b981;'>
                <h2 style='text-align: center; color: #10b981;'>امتیاز کل: {c_data['weighted_score']} / 5</h2>
                <hr>
                <p><b>🌍 موقعیت و دسترسی:</b> {c_data['score_location']} (وزن: {weights['location']*100}%)</p>
                <p><b>🏛️ فضای فیزیکی:</b> {c_data['score_physical']} (وزن: {weights['physical']*100}%)</p>
                <p><b>🎬 وضعیت فنی:</b> {c_data['score_technical']} (وزن: {weights['technical']*100}%)</p>
                <p><b>💼 راهبری:</b> {c_data['score_operations']} (وزن: {weights['operations']*100}%)</p>
                <p><b>☕ امکانات جانبی:</b> {c_data['score_amenities']} (وزن: {weights['amenities']*100}%)</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("ابتدا یک سینما ثبت کنید.")

# ==========================================
# 3. ارزیابی و ثبت
# ==========================================
elif menu == "📝 ارزیابی و ثبت چک‌لیست":
    st.title("📋 ثبت شناسنامه و ارزیابی")
    with st.form("cinema_form"):
        st.write("### 🏢 اطاعات پایه")
        g1, g2 = st.columns(2)
        name = g1.text_input("نام سینما*")
        city = g2.text_input("شهر")
        
        st.write("### 🧮 ظرفیت‌ها")
        g3, g4, g5 = st.columns(3)
        halls = g3.number_input("تعداد سالن", min_value=1, value=1)
        total = g4.number_input("کل صندلی", min_value=1, value=100)
        op_seats = g5.number_input("صندلی فعال", min_value=1, value=100)
        
        st.write("### 🎯 امتیازدهی محورها (۰ تا ۵)")
        with st.expander("📌 دسترسی و موقعیت"): s_loc = st.slider("امتیاز دسترسی", 0.0, 5.0, 3.0, 0.1)
        with st.expander("🏛️ فیزیکی و نگهداشت"): s_phy = st.slider("امتیاز فیزیکی", 0.0, 5.0, 3.0, 0.1)
        with st.expander("🎬 فنی و تجهیزات"): s_tech = st.slider("امتیاز فنی", 0.0, 5.0, 3.0, 0.1)
        with st.expander("💼 راهبری و بهره‌برداری"): s_ops = st.slider("امتیاز راهبری", 0.0, 5.0, 3.0, 0.1)
        with st.expander("☕ امکانات جانبی"): s_amen = st.slider("امتیاز امکانات", 0.0, 5.0, 3.0, 0.1)
        
        if st.form_submit_button("💾 ذخیره در دیتابیس"):
            if name:
                data = {
                    "name": name, "city": city, "halls": halls, "total_seats": total, "operational_seats": op_seats,
                    "score_location": s_loc, "score_physical": s_phy, "score_technical": s_tech, 
                    "score_operations": s_ops, "score_amenities": s_amen
                }
                res = requests.post(f"{SUPABASE_URL}/rest/v1/cinemas", headers=get_headers(), json=data)
                if res.status_code in [200, 201]:
                    st.success("✅ با موفقیت ثبت شد!")
                    st.cache_data.clear()
                else:
                    st.error(f"خطا در ثبت: {res.text}")
            else:
                st.error("نام سینما الزامی است.")

# ==========================================
# 4. تنظیمات ضرایب (پویا)
# ==========================================
elif menu == "⚙️ تنظیمات وزن‌ها (مدیر)":
    st.title("⚙️ مدیریت پویا ضرایب و وزن‌ها")
    st.info("تغییرات در این بخش مستقیماً روی فرمول محاسبه امتیاز کل سینماها در داشبورد اعمال می‌شود.")
    
    with st.form("weights_form"):
        w_loc = st.number_input("وزن موقعیت و دسترسی", value=float(weights['location']), step=0.05)
        w_phy = st.number_input("وزن وضعیت فیزیکی", value=float(weights['physical']), step=0.05)
        w_tech = st.number_input("وزن وضعیت فنی", value=float(weights['technical']), step=0.05)
        w_ops = st.number_input("وزن راهبری", value=float(weights['operations']), step=0.05)
        w_amen = st.number_input("وزن امکانات جانبی", value=float(weights['amenities']), step=0.05)
        
        if st.form_submit_button("✅ بروزرسانی وزن‌ها در سیستم"):
            total_w = w_loc + w_phy + w_tech + w_ops + w_amen
            if abs(total_w - 1.0) > 0.01:
                st.error(f"❌ مجموع وزن‌ها باید معادل ۱.۰ (۱۰۰٪) باشد. مجموع فعلی: {total_w:.2f}")
            else:
                new_w = {"location": w_loc, "physical": w_phy, "technical": w_tech, "operations": w_ops, "amenities": w_amen}
                payload = {"value": new_w}
                res = requests.patch(f"{SUPABASE_URL}/rest/v1/app_config?key=eq.axis_weights", 
                                     headers=get_headers(), json=payload)
                if res.status_code in [200, 204]:
                    st.success("وزن‌ها بروزرسانی شد.")
                    st.cache_data.clear()
                else:
                    st.error("خطا در بروزرسانی")

# ==========================================
# 5. خروجی و پشتیبان‌گیری
# ==========================================
elif menu == "💾 خروجی و پشتیبان‌گیری":
    st.title("💾 استخراج و پشتیبان‌گیری امن اطلاعات")
    st.warning("دسترسی به فول‌بکاپ JSON نیازمند رمز عبور مدیر است.")
    
    pwd = st.text_input("رمز عبور را وارد کنید:", type="password")
    
    if pwd == "Ma9184364191":
        st.success("🔓 احراز هویت موفق. سیستم آماده خروجی‌گیری است.")
        if not df.empty:
            json_str = df.to_json(orient='records', force_ascii=False)
            st.download_button(
                label="📥 دانلود فول‌بکاپ دیتابیس (JSON)",
                data=json_str.encode('utf-8'),
                file_name="cinemas_full_backup.json",
                mime="application/json"
            )
        else:
            st.info("داده‌ای برای خروجی وجود ندارد.")
    elif pwd != "":
        st.error("❌ رمز عبور اشتباه است.")
