import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="داشبورد جامع ارزیابی و راهبری سینماها",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- RTL and Custom Styles ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppHeader {display: none !important;}
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    
    @import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');
    
    html, body, [class*="css"], div, h1, h2, h3, h4, h5, h6, p, span, label {
        font-family: 'Vazirmatn', sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    
    .stMetric {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        border-radius: 8px;
        font-weight: bold;
    }
    
    .axis-box {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- Supabase Helpers ---
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "").strip().rstrip('/')
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "").strip()

def get_supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def fetch_cinemas():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None, "تنظیمات Secrets انجام نشده است."
    try:
        url = f"{SUPABASE_URL}/rest/v1/cinemas?select=*&order=id.asc"
        res = requests.get(url, headers=get_supabase_headers(), timeout=5)
        if res.status_code == 200:
            data = res.json()
            return pd.DataFrame(data), "🟢 متصل به دیتابیس Supabase"
        elif res.status_code == 401:
            return None, "خطای 401 (کلید API نامعتبر است - نیاز به eyJ دارید)"
        else:
            return None, f"خطای {res.status_code}: {res.text}"
    except Exception as e:
        return None, f"خطای ارتباط: {str(e)}"

def insert_cinema(data_dict):
    if not SUPABASE_URL or not SUPABASE_KEY:
        return False, "کلیدهای Supabase در Secrets تنظیم نشده‌اند."
    try:
        url = f"{SUPABASE_URL}/rest/v1/cinemas"
        res = requests.post(url, headers=get_supabase_headers(), json=data_dict, timeout=7)
        if res.status_code in [200, 201]:
            return True, "با موفقیت در دیتابیس ذخیره شد."
        else:
            return False, f"خطای دیتابیس ({res.status_code}): {res.text}"
    except Exception as e:
        return False, f"خطای ارتباط: {str(e)}"

# Mock Data Fallback
if 'local_data' not in st.session_state:
    st.session_state.local_data = pd.DataFrame([
        {
            "id": 1,
            "name": "سینما بهمن تهران",
            "province": "تهران",
            "city": "تهران",
            "address": "میدان انقلاب، خیابان آزادی",
            "halls": 4,
            "hall_seats_detail": "سالن ۱: ۳۰۰، سالن ۲: ۲۵۰، سالن ۳: ۱۵۰، سالن ۴: ۱۵۰",
            "total_seats": 850,
            "nominal_capacity": 900,
            "operational_seats": 800,
            "daily_shows": 24,
            "score_location": 4.2,
            "score_physical": 3.8,
            "score_technical": 4.0,
            "score_operations": 4.5,
            "score_amenities": 3.5,
        },
        {
            "id": 2,
            "name": "سینما آزادی تهران",
            "province": "تهران",
            "city": "تهران",
            "address": "خیابان بهشتی، نبش وزرا",
            "halls": 5,
            "hall_seats_detail": "سالن ۱: ۴۰۰، سالن ۲: ۳۰۰، سالن ۳: ۲۰۰، سالن ۴: ۱۰۰، سالن ۵: ۱۰۰",
            "total_seats": 1100,
            "nominal_capacity": 1150,
            "operational_seats": 1050,
            "daily_shows": 30,
            "score_location": 4.8,
            "score_physical": 4.5,
            "score_technical": 4.7,
            "score_operations": 4.6,
            "score_amenities": 4.3,
        }
    ])

db_df, db_status = fetch_cinemas()
using_db = False
if db_df is not None and not db_df.empty:
    df = db_df.copy()
    using_db = True
else:
    df = st.session_state.local_data.copy()

# Ensure standard numeric columns exist
req_cols = {
    'score_location': 3.5, 'score_physical': 3.5, 'score_technical': 3.5,
    'score_operations': 3.5, 'score_amenities': 3.5,
    'total_seats': 100, 'operational_seats': 100, 'nominal_capacity': 100,
    'halls': 1, 'daily_shows': 10, 'province': 'نامشخص', 'city': 'نامشخص', 'address': 'ثبت نشده'
}
for col, val in req_cols.items():
    if col not in df.columns:
        df[col] = val

# Calculations
df['weighted_score'] = (
    df['score_location'].astype(float) * 0.20 +
    df['score_physical'].astype(float) * 0.25 +
    df['score_technical'].astype(float) * 0.25 +
    df['score_operations'].astype(float) * 0.15 +
    df['score_amenities'].astype(float) * 0.15
).round(2)

df['seat_efficiency'] = ((df['operational_seats'].astype(float) / df['total_seats'].astype(float).replace(0, 1)) * 100).round(1)

# Sidebar
st.sidebar.title("🎬 سامانه راهبری سینماها")
if using_db:
    st.sidebar.success(db_status)
else:
    st.sidebar.warning(f"🟡 حالت محلی / غیرمتصل\n({db_status})")

menu = st.sidebar.radio("منوی اصلی", [
    "📊 داشبورد تحلیلی و مقایسه‌ای",
    "📝 ثبت سینما و ارزیابی چک‌لیستی",
    "🗃️ مدیریت داده‌ها و خروجی"
])

st.title("🎬 داشبورد ارزیابی و راهبری سینماهای کشور")
st.caption("مبتنی بر مدل ۲۶ شاخصی ارزیابی ۵ محور کلیدی (مطابق مدل استاندارد راهبری)")
st.divider()

if menu == "📊 داشبورد تحلیلی و مقایسه‌ای":
    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("تعداد کل سینماها", len(df))
    with c2:
        st.metric("مجموع صندلی فعال", f"{int(df['operational_seats'].sum()):,}")
    with c3:
        st.metric("میانگین امتیاز موزون کل", f"{df['weighted_score'].mean():.2f} / 5")
    with c4:
        st.metric("میانگین بهره‌وری صندلی", f"{df['seat_efficiency'].mean():.1f}%")

    st.divider()

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("📈 مقایسه امتیاز کل و بهره‌وری صندلی")
        if not df.empty:
            fig_bar = px.bar(
                df,
                x="name",
                y="weighted_score",
                color="seat_efficiency",
                color_continuous_scale="Viridis",
                labels={"name": "سینما", "weighted_score": "امتیاز موزون (از ۵)", "seat_efficiency": "بهره‌وری صندلی (%)"},
                text="weighted_score"
            )
            fig_bar.update_layout(height=420)
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("اطلاعاتی جهت نمایش وجود ندارد.")

    with col_right:
        st.subheader("🕸️ نمودار راداری ارزیابی ۵ محور کلیدی")
        if not df.empty:
            selected_cinema = st.selectbox("انتخاب سینما جهت تحلیل راداری:", df["name"].unique())
            c_data = df[df["name"] == selected_cinema].iloc[0]

            categories = ['موقعیت و دسترسی', 'کیفیت فضای عمومی', 'تجهیزات فنی', 'راهبری و بهره‌برداری', 'امکانات جانبی']
            scores = [
                float(c_data['score_location']),
                float(c_data['score_physical']),
                float(c_data['score_technical']),
                float(c_data['score_operations']),
                float(c_data['score_amenities'])
            ]

            fig_radar = go.Figure(data=go.Scatterpolar(
                r=scores + [scores[0]],
                theta=categories + [categories[0]],
                fill='toself',
                name=selected_cinema,
                line_color='#e74c3c'
            ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                showlegend=False,
                height=420
            )
            st.plotly_chart(fig_radar, use_container_width=True)

elif menu == "📝 ثبت سینما و ارزیابی چک‌لیستی":
    st.subheader("📋 فرم جامع شناسنامه سینما و چک‌لیست ارزیابی ۵‌گانه")
    
    with st.form("cinema_full_form"):
        st.markdown("### 🏢 ۱. مشخصات و ظرفیت سینما")
        st.caption("اطلاعات شناسنامه‌ای و زیرساختی (بدون امتیازدهی مستقیم، جهت محاسبه بهره‌وری و تحلیل)")
        
        g1, g2, g3 = st.columns(3)
        with g1:
            name = st.text_input("نام سینما (اجباری)*:")
            province = st.text_input("استان:")
            city = st.text_input("شهر:")
        with g2:
            address = st.text_area("آدرس دقیق:", height=108)
            halls = st.number_input("تعداد سالن:", min_value=1, value=1)
        with g3:
            hall_seats_detail = st.text_area("تعداد صندلی هر سالن (مثال: سالن ۱: ۲۰۰، سالن ۲: ۱۵۰):", height=108)
            
        g4, g5, g6 = st.columns(3)
        with g4:
            total_seats = st.number_input("مجموع صندلی‌های سینما:", min_value=1, value=300)
        with g5:
            nominal_capacity = st.number_input("ظرفیت اسمی:", min_value=1, value=320)
            op_seats = st.number_input("تعداد صندلی عملیاتی (فعال):", min_value=1, value=280)
        with g6:
            daily_shows = st.number_input("تعداد سانس قابل ارائه در روز:", min_value=1, value=12)

        st.divider()
        st.markdown("### 🎯 ۲. چک‌لیست‌ها و امتیازدهی به شاخص‌های ۵‌گانه (۰ تا ۵)")
        st.info("هر شاخص بر اساس چک‌لیست مربوطه ارزیابی شده و در مقیاس ۰ تا ۵ امتیازدهی می‌شود.")

        # --- Axis 1: Location & Access ---
        with st.expander("📌 محور اول: موقعیت و دسترسی (وزن ۲۰٪)", expanded=True):
            st.markdown("#### شاخص‌ها و چک‌لیست‌های دسترسی")
            a1_col1, a1_col2 = st.columns(2)
            with a1_col1:
                st.checkbox("پارکینگ اختصاصی یا دسترسی به پارکینگ عمومی مناسب", key="chk_p1")
                st.checkbox("موقعیت مناسب نسبت به مراکز مهم شهری و مجتمع‌های تجاری/فرهنگی", key="chk_p2")
                st.checkbox("میزان تردد مناسب و دسترسی‌پذیری آسان معابر محدوده", key="chk_p3")
            with a1_col2:
                st.checkbox("دید و دسترسی بصری مناسب سینما از خیابان اصلی و تابلوهای راهنما", key="chk_p4")
                st.checkbox("مناسب‌سازی مسیرها برای افراد دارای معلولیت و جانبازان", key="chk_p5")
                st.checkbox("دسترسی آسان به حمل و نقل عمومی (مترو، اتوبوس، تاکسی)", key="chk_p6")
            
            s_loc = st.slider("امتیاز نهایی محور موقعیت و دسترسی (۰ تا ۵):", 0.0, 5.0, 3.8, 0.1)

        # --- Axis 2: Physical & Facility ---
        with st.expander("🏛️ محور دوم: وضعیت فیزیکی، ظاهری، کیفیت محیطی و نگهداشت (وزن ۲۵٪)"):
            st.markdown("#### شاخص‌های ۹‌گانه کیفیت فضای عمومی و نگهداشت")
            a2_c1, a2_c2 = st.columns(2)
            with a2_c1:
                st.checkbox("۱. کیفیت نمای بیرونی و سردر (حداقل ۸ گزینه چک‌لیست شامل تابلو، نورپردازی سردر، نظافت نما و...)", key="chk_f1")
                st.checkbox("۲. وضعیت لابی و فضای انتظار (مساحت، چیدمان، تهویه و مبلمان)", key="chk_f2")
                st.checkbox("۳. وضعیت عمومی سالن‌های نمایش (دیوارها، کف‌پوش، شیب سالن و خروج اضطراری)", key="chk_f3")
                st.checkbox("۴. کیفیت صندلی‌های سالن (ارگونومی، سلامت روکش، شماره‌گذاری و عملکرد)", key="chk_f4")
                st.checkbox("۵. فضاهای عمومی و راهروها", key="chk_f5")
            with a2_c2:
                st.checkbox("۶. وضعیت بهداشت و سلامت سرویس‌های بهداشتی", key="chk_f6")
                st.checkbox("۷. سیستم نورپردازی و روشنایی‌های عمومی", key="chk_f7")
                st.checkbox("۸. تابلوها، علائم راهنما و هدایت مخاطب", key="chk_f8")
                st.checkbox("۹. برنامه منظم نظافت و نگهداشت کلی مجموعه", key="chk_f9")
            
            s_phy = st.slider("امتیاز نهایی کیفیت فضای عمومی و فیزیکی (۰ تا ۵):", 0.0, 5.0, 3.5, 0.1)

        # --- Axis 3: Technical Equipment ---
        with st.expander("🎬 محور سوم: وضعیت فنی و کیفیت تجهیزات سینما (وزن ۲۵٪)"):
            st.markdown("#### شاخص‌های فنی، تصویر، صدا و سرویس نگهداری")
            a3_c1, a3_c2 = st.columns(2)
            with a3_c1:
                st.checkbox("۱. وضعیت تجهیزات نمایش (استاندارد D-Cinema / E-Cinema، نوع پروژکتور لیزری/لامپی)", key="chk_t1")
                st.checkbox("۲. کیفیت، تفکیک و روشنایی تصویر روی پرده", key="chk_t2")
                st.checkbox("۳. کیفیت، یکنواختی و سلامت پرده نمایش", key="chk_t3")
            with a3_c2:
                st.checkbox("۴. سیستم صوتی (استاندارد Dolby/Stereo، تراز صدا، آکوستیک سالن، عدم وجود نویز/اکو، کالیبراسیون و کابل‌ها)", key="chk_t4")
                st.checkbox("۵. تجهیزات فنی جانبی و اتاق پروژکتور", key="chk_t5")
                st.checkbox("۶. برنامه نگهداری و سرویس دوره‌ای (PM) تجهیزات فنی", key="chk_t6")
            
            s_tech = st.slider("امتیاز نهایی وضعیت فنی و تجهیزات (۰ تا ۵):", 0.0, 5.0, 4.0, 0.1)

        # --- Axis 4: Management & Operations ---
        with st.expander("💼 محور چهارم: راهبری و بهره‌برداری (وزن ۱۵٪)"):
            st.markdown("#### شاخص‌های مدیریت اکران، بلیت‌فروشی، منابع انسانی و بحران")
            a4_c1, a4_c2 = st.columns(2)
            with a4_c1:
                st.checkbox("۱. وضعیت برنامه‌ریزی و اجرای جدول اکران", key="chk_o1")
                st.checkbox("۲. وضعیت سیستم فروش و بلیت‌فروشی آنلاین و حضوری", key="chk_o2")
                st.checkbox("۳. کیفیت خدمات‌دهی، تکریم و پذیرش مخاطب", key="chk_o3")
            with a4_c2:
                st.checkbox("۴. ظرفیت و وضعیت بهره‌برداری از درآمدهای جانبی", key="chk_o4")
                st.checkbox("۵. ساختار منابع انسانی (تعداد نیرو، تناسب با ظرفیت، شرح وظایف و شیفت‌بندی)", key="chk_o5")
                st.checkbox("۶. آمادگی، دستورالعمل‌ها و امکانات مدیریت بحران و شرایط اضطراری", key="chk_o6")
            
            s_ops = st.slider("امتیاز نهایی راهبری و بهره‌برداری (۰ تا ۵):", 0.0, 5.0, 3.8, 0.1)

        # --- Axis 5: Amenities ---
        with st.expander("☕ محور پنجم: امکانات و فضاهای جانبی (وزن ۱۵٪)"):
            st.markdown("#### شاخص‌های فضاهای مکمل و درآمدزا"):
            a5_c1, a5_c2 = st.columns(2)
            with a5_c1:
                st.checkbox("۱. بوفه و امکانات پذیرایی (تنوع، بهداشت و کیفیت)", key="chk_m1")
                st.checkbox("۲. کافه و رستوران مجاور سالن‌ها", key="chk_m2")
                st.checkbox("۳. فضای بازی و سرگرمی خانواده/کودکان", key="chk_m3")
            with a5_c2:
                st.checkbox("۴. سالن و خدمات VIP (در صورت وجود)", key="chk_m4")
                st.checkbox("۵. ظرفیت برگزاری همایش، تئاتر و رویدادها", key="chk_m5")
                st.checkbox("۶. امکانات فرهنگی، آموزشی و فروشگاهی", key="chk_m6")
            
            s_amen = st.slider("امتیاز نهایی امکانات و فضاهای جانبی (۰ تا ۵):", 0.0, 5.0, 3.5, 0.1)

        submitted = st.form_submit_button("💾 ثبت کامل شناسنامه و ارزیابی سینما در سامانه")
        
        if submitted:
            if not name.strip():
                st.error("❌ لطفاً نام سینما را وارد کنید.")
            else:
                new_cinema = {
                    "name": name.strip(),
                    "province": province.strip() if province else "نامشخص",
                    "city": city.strip() if city else "نامشخص",
                    "address": address.strip() if address else "ثبت نشده",
                    "halls": int(halls),
                    "hall_seats_detail": hall_seats_detail.strip() if hall_seats_detail else "",
                    "total_seats": int(total_seats),
                    "nominal_capacity": int(nominal_capacity),
                    "operational_seats": int(op_seats),
                    "daily_shows": int(daily_shows),
                    "score_location": float(s_loc),
                    "score_physical": float(s_phy),
                    "score_technical": float(s_tech),
                    "score_operations": float(s_ops),
                    "score_amenities": float(s_amen),
                }
                
                success, msg = insert_cinema(new_cinema)
                if success:
                    st.success(f"✅ شناسنامه و ارزیابی سینمای «{name}» با موفقیت در دیتابیس Supabase ثبت شد!")
                    st.rerun()
                else:
                    new_cinema["id"] = len(st.session_state.local_data) + 1
                    st.session_state.local_data = pd.concat([st.session_state.local_data, pd.DataFrame([new_cinema])], ignore_index=True)
                    st.success(f"✅ اطلاعات در حافظه محلی ثبت شد. (پیام دیتابیس: {msg})")
                    st.rerun()

elif menu == "🗃️ مدیریت داده‌ها و خروجی":
    st.subheader("📋 بانک اطلاعاتی کامل سینماها و ارزیابی‌ها")
    
    # Display table with all main fields
    display_cols = [c for c in [
        'id', 'name', 'province', 'city', 'halls', 'total_seats', 'operational_seats',
        'daily_shows', 'weighted_score', 'seat_efficiency', 'score_location',
        'score_physical', 'score_technical', 'score_operations', 'score_amenities'
    ] if c in df.columns]
    
    st.dataframe(df[display_cols], use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 دانلود کامل خروجی گزارش (فرمت CSV / Excel)",
        data=csv,
        file_name="cinemas_comprehensive_evaluation.csv",
        mime="text/csv"
    )
