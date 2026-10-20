import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
from datetime import datetime

st.set_page_config(
    page_title="پنل مدیریت راهبری سینماها",
    page_icon="🎞️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
<style>
    /* وارد کردن فونت وزیرمتن */
    @import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');
    
    /* تنظیمات پایه */
    html, body, [class*="css"], div, h1, h2, h3, h4, h5, h6, p, span, label, th, td {
        font-family: 'Vazirmatn', sans-serif !important;
        direction: rtl;
        text-align: right;
        color: #1e293b;
    }
    
    /* پس‌زمینه کل اپلیکیشن */
    .stApp {
        background-color: #f4f7f9 !important;
    }

    /* مخفی کردن المان‌های پیش‌فرض استریم‌لیت */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    /* =========================================
       طراحی سایدبار تیره (مشابه عکس مرجع)
       ========================================= */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important; /* رنگ سرمه‌ای بسیار تیره */
        border-left: 1px solid #1e293b;
        width: 280px !important;
    }
    /* رنگ متن سایدبار */
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    /* استایل دکمه‌های منوی رادیویی در سایدبار */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 8px;
    }
    [data-testid="stSidebar"] .stRadio label {
        background-color: transparent;
        padding: 12px 20px;
        border-radius: 12px;
        transition: all 0.2s ease;
        cursor: pointer;
        border: 1px solid transparent;
        font-weight: 500;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background-color: rgba(16, 185, 129, 0.1);
        border-color: rgba(16, 185, 129, 0.3);
        color: #10b981 !important;
    }
    /* حالت انتخاب شده در سایدبار */
    [data-testid="stSidebar"] .stRadio label[data-checked="true"] {
        background: linear-gradient(90deg, #047857 0%, #10b981 100%);
        color: white !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        font-weight: bold;
    }
    
    /* لوگو و هدر سایدبار */
    .sidebar-brand {
        padding: 20px 10px;
        text-align: center;
        border-bottom: 1px solid #1e293b;
        margin-bottom: 20px;
    }
    .sidebar-brand i {
        font-size: 2.5rem;
        color: #10b981;
    }
    .sidebar-brand h3 {
        margin-top: 10px;
        font-weight: 800;
        color: white !important;
        font-size: 1.2rem;
    }

    /* =========================================
       طراحی هدر بالا (Top Navbar)
       ========================================= */
    .top-header {
        background-color: white;
        border-radius: 16px;
        padding: 16px 24px;
        margin-bottom: 24px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.02);
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #e2e8f0;
    }
    .top-header .search-box {
        background: #f1f5f9;
        border-radius: 99px;
        padding: 8px 16px;
        display: flex;
        align-items: center;
        gap: 10px;
        color: #64748b;
        width: 300px;
    }
    .user-profile {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .user-avatar {
        background: #10b981;
        color: white;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
    }

    /* =========================================
       طراحی ردیف‌های لیست (مشابه عکس ادمین پاکار)
       ========================================= */
    .list-row {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 16px 24px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 8px rgba(0,0,0,0.01);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .list-row:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.04);
        border-color: #cbd5e1;
    }
    
    .status-badge {
        padding: 6px 14px;
        border-radius: 99px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .status-excellent { background: #d1fae5; color: #065f46; }
    .status-good { background: #fef3c7; color: #92400e; }
    .status-needs-work { background: #fee2e2; color: #991b1b; }

    .action-icons {
        display: flex;
        gap: 10px;
    }
    .btn-icon {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        cursor: pointer;
        transition: all 0.2s;
        border: 1px solid transparent;
    }
    .btn-edit { background: #f0fdf4; color: #16a34a; border-color: #bbf7d0; }
    .btn-view { background: #eff6ff; color: #2563eb; border-color: #bfdbfe; }
    .btn-delete { background: #fef2f2; color: #dc2626; border-color: #fecaca; }
    .btn-icon:hover { filter: brightness(0.95); }

    /* =========================================
       کارت‌های آماری و فرم‌ها
       ========================================= */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 15px -5px rgba(0,0,0,0.03);
    }
    
    .stButton>button {
        border-radius: 12px !important;
        background: #10b981 !important;
        color: white !important;
        border: none !important;
        padding: 10px 24px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
    }
    .stButton>button:hover {
        background: #059669 !important;
    }

    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, textarea {
        border-radius: 12px !important;
        border: 1px solid #cbd5e1 !important;
        background-color: #f8fafc !important;
    }
    div[data-baseweb="input"] > div:focus-within {
        border-color: #10b981 !important;
        box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "").strip().rstrip('/')
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "").strip()

def get_headers():
    return {
        "apikey": SUPABASE_KEY, 
        "Authorization": f"Bearer {SUPABASE_KEY}", 
        "Content-Type": "application/json"
    }

@st.cache_data(ttl=10)
def fetch_cinemas():
    if not SUPABASE_URL: return pd.DataFrame()
    try:
        res = requests.get(f"{SUPABASE_URL}/rest/v1/cinemas?select=*&order=id.desc", headers=get_headers())
        if res.status_code == 200:
            return pd.DataFrame(res.json())
    except Exception as e:
        st.sidebar.error(f"خطای ارتباط: {e}")
    return pd.DataFrame()

@st.cache_data(ttl=10)
def fetch_weights():
    default_w = {"location": 0.20, "physical": 0.25, "technical": 0.25, "operations": 0.15, "amenities": 0.15}
    if not SUPABASE_URL: return default_w
    try:
        res = requests.get(f"{SUPABASE_URL}/rest/v1/app_config?key=eq.axis_weights", headers=get_headers())
        if res.status_code == 200 and len(res.json()) > 0: 
            return res.json()[0].get("value", default_w)
    except:
        pass
    return default_w

df = fetch_cinemas()
weights = fetch_weights()

if not df.empty:
    for col in ['score_location', 'score_physical', 'score_technical', 'score_operations', 'score_amenities']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df['weighted_score'] = (
        df['score_location'] * float(weights.get('location', 0.2)) +
        df['score_physical'] * float(weights.get('physical', 0.25)) +
        df['score_technical'] * float(weights.get('technical', 0.25)) +
        df['score_operations'] * float(weights.get('operations', 0.15)) +
        df['score_amenities'] * float(weights.get('amenities', 0.15))
    ).round(2)
    
    df['seat_efficiency'] = ((pd.to_numeric(df['operational_seats'], errors='coerce') / 
                              pd.to_numeric(df['total_seats'], errors='coerce').replace(0, 1)) * 100).round(1)

st.sidebar.markdown("""
<div class="sidebar-brand">
    <i class="bi bi-camera-reels-fill"></i>
    <h3>پنل مدیریت راهبری</h3>
    <p style="color: #94a3b8 !important; font-size: 0.8rem; margin:0;">نسخه حرفه‌ای • بهمن سبز</p>
</div>
""", unsafe_allow_html=True)

# استفاده از کاراکترهای خالی برای استایل‌دهی بهتر منوها با CSS
menu = st.sidebar.radio(
    "",
    [
        "داشبورد کلان و لیست", 
        "پروفایل و شناسنامه", 
        "ثبت و ارزیابی جدید",
        "تنظیمات وزن‌ها",
        "پشتیبان‌گیری امن"
    ],
    label_visibility="collapsed"
)

db_status = "<span style='color: #10b981;'><i class='bi bi-cloud-check-fill'></i> متصل به سرور</span>" if SUPABASE_URL else "<span style='color: #f59e0b;'><i class='bi bi-cloud-slash-fill'></i> حالت آفلاین</span>"

st.markdown(f"""
<div class="top-header">
    <div class="search-box">
        <i class="bi bi-search"></i>
        <span style="font-size: 0.9rem;">جستجوی شناسه، نام سینما یا استان...</span>
    </div>
    <div class="user-profile">
        <div style="text-align: left;">
            <b style="font-size: 0.9rem; display: block;">مدیریت سیستم</b>
            <span style="font-size: 0.75rem; color: #64748b;">{db_status}</span>
        </div>
        <div class="user-avatar"><i class="bi bi-person-fill"></i></div>
    </div>
</div>
""", unsafe_allow_html=True)

if menu == "داشبورد کلان و لیست":
    
    # KPIs Top Cards
    if not df.empty:
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f"<div style='background:white; padding:20px; border-radius:16px; border:1px solid #e2e8f0;'><div style='color:#64748b; font-size:0.9rem;'><i class='bi bi-buildings'></i> کل سینماها</div><div style='font-size:1.8rem; font-weight:bold; color:#0f172a;'>{len(df)}</div></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div style='background:white; padding:20px; border-radius:16px; border:1px solid #e2e8f0;'><div style='color:#64748b; font-size:0.9rem;'><i class='bi bi-people'></i> صندلی فعال</div><div style='font-size:1.8rem; font-weight:bold; color:#0f172a;'>{int(df['operational_seats'].sum()):,}</div></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div style='background:white; padding:20px; border-radius:16px; border:1px solid #e2e8f0;'><div style='color:#64748b; font-size:0.9rem;'><i class='bi bi-star'></i> میانگین شبکه</div><div style='font-size:1.8rem; font-weight:bold; color:#10b981;'>{df['weighted_score'].mean():.2f}<span style='font-size:0.9rem; color:#64748b;'> / 5</span></div></div>", unsafe_allow_html=True)
        with c4: st.markdown(f"<div style='background:white; padding:20px; border-radius:16px; border:1px solid #e2e8f0;'><div style='color:#64748b; font-size:0.9rem;'><i class='bi bi-graph-up-arrow'></i> بهره‌وری کل</div><div style='font-size:1.8rem; font-weight:bold; color:#3b82f6;'>{df['seat_efficiency'].mean():.1f}%</div></div>", unsafe_allow_html=True)
    
    st.write("<br>", unsafe_allow_html=True)
    st.markdown("### <i class='bi bi-list-task' style='color:#10b981;'></i> لیست جامع ارزیابی سینماها", unsafe_allow_html=True)
    
    # Custom List View (The core requirement requested by user)
    if not df.empty:
        # Header Row
        st.markdown("""
        <div style="display: flex; justify-content: space-between; padding: 0 24px 10px 24px; color: #64748b; font-size: 0.85rem; font-weight: bold; border-bottom: 2px solid #e2e8f0; margin-bottom: 15px;">
            <div style="flex: 0.5;">شناسه</div>
            <div style="flex: 2.5;">نام و استان</div>
            <div style="flex: 1.5;">وضعیت کیفی</div>
            <div style="flex: 1.5; text-align: center;">امتیاز کل</div>
            <div style="flex: 1.5; text-align: center;">ظرفیت</div>
            <div style="flex: 1; text-align: left;">عملیات</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Data Rows
        for idx, row in df.iterrows():
            score = row['weighted_score']
            if score >= 4.0:
                badge = "<span class='status-badge status-excellent'>سطح عالی</span>"
            elif score >= 3.0:
                badge = "<span class='status-badge status-good'>قابل قبول</span>"
            else:
                badge = "<span class='status-badge status-needs-work'>نیازمند بهبود</span>"
            
            st.markdown(f"""
            <div class="list-row">
                <div style="flex: 0.5; color: #94a3b8; font-weight: bold;">#{row['id']}</div>
                <div style="flex: 2.5;">
                    <b style="font-size: 1rem; color: #0f172a;">{row['name']}</b>
                    <div style="font-size: 0.8rem; color: #64748b; margin-top: 4px;"><i class="bi bi-geo-alt"></i> {row['province']} - {row['city']}</div>
                </div>
                <div style="flex: 1.5;">{badge}</div>
                <div style="flex: 1.5; text-align: center; font-weight: bold; font-size: 1.1rem;">{score:.2f}</div>
                <div style="flex: 1.5; text-align: center; font-size: 0.9rem; color: #475569;"><i class="bi bi-people"></i> {row['operational_seats']} صندلی</div>
                <div style="flex: 1; display: flex; justify-content: flex-end;" class="action-icons">
                    <div class="btn-icon btn-view" title="مشاهده پروفایل"><i class="bi bi-eye"></i></div>
                    <div class="btn-icon btn-edit" title="ویرایش"><i class="bi bi-pencil-square"></i></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    else:
        st.info("هیچ سینمایی در سیستم ثبت نشده است.")

elif menu == "پروفایل و شناسنامه":
    st.markdown("### <i class='bi bi-person-vcard' style='color:#10b981;'></i> پروفایل تخصصی سینما", unsafe_allow_html=True)
    if not df.empty:
        selected = st.selectbox("انتخاب سینما جهت مشاهده جزئیات:", df['name'].tolist())
        c_data = df[df['name'] == selected].iloc[0]
        
        st.markdown(f"""
        <div style="background: white; border-radius: 20px; padding: 24px; border: 1px solid #e2e8f0; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h2 style="margin: 0; color: #0f172a;">{c_data['name']}</h2>
                <p style="margin: 8px 0 0 0; color: #64748b;"><i class="bi bi-geo-alt"></i> {c_data['province']} - {c_data['city']} | <i class="bi bi-signpost"></i> {c_data['address']}</p>
            </div>
            <div style="text-align: center; background: #f8fafc; padding: 15px 30px; border-radius: 16px; border: 1px solid #cbd5e1;">
                <span style="font-size: 0.85rem; color: #64748b;">امتیاز ارزیابی</span>
                <h2 style="margin: 0; color: #10b981; font-size: 2.2rem;">{c_data['weighted_score']}</h2>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            categories = ['دسترسی', 'وضعیت فیزیکی', 'فنی و تجهیزات', 'راهبری', 'امکانات جانبی']
            scores = [c_data['score_location'], c_data['score_physical'], 
                      c_data['score_technical'], c_data['score_operations'], c_data['score_amenities']]
            
            fig_radar = go.Figure(data=go.Scatterpolar(
                r=scores + [scores[0]], theta=categories + [categories[0]], fill='toself', line_color='#10b981'
            ))
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                                    showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                    margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_radar, use_container_width=True)
            
        with col2:
            st.markdown(f"""
            <div style="background: white; border-radius: 20px; padding: 24px; border: 1px solid #e2e8f0;">
                <h4 style="margin-top:0; border-bottom: 1px solid #f1f5f9; padding-bottom: 10px;"><i class="bi bi-bar-chart-steps"></i> ریز امتیازات محورها</h4>
                <div style="margin-bottom: 12px; display: flex; justify-content: space-between;"><span><i class="bi bi-geo"></i> موقعیت و دسترسی</span> <b>{c_data['score_location']}</b></div>
                <div style="margin-bottom: 12px; display: flex; justify-content: space-between;"><span><i class="bi bi-building"></i> فضای فیزیکی</span> <b>{c_data['score_physical']}</b></div>
                <div style="margin-bottom: 12px; display: flex; justify-content: space-between;"><span><i class="bi bi-projector"></i> وضعیت فنی</span> <b>{c_data['score_technical']}</b></div>
                <div style="margin-bottom: 12px; display: flex; justify-content: space-between;"><span><i class="bi bi-diagram-3"></i> راهبری</span> <b>{c_data['score_operations']}</b></div>
                <div style="margin-bottom: 12px; display: flex; justify-content: space-between;"><span><i class="bi bi-cup-hot"></i> امکانات جانبی</span> <b>{c_data['score_amenities']}</b></div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("ابتدا یک سینما ثبت کنید.")

elif menu == "ثبت و ارزیابی جدید":
    st.markdown("### <i class='bi bi-file-earmark-plus' style='color:#10b981;'></i> فرم ثبت و ارزیابی", unsafe_allow_html=True)
    with st.form("cinema_form"):
        st.write("##### اطلاعات شناسنامه‌ای")
        g1, g2 = st.columns(2)
        name = g1.text_input("نام سینما*")
        city = g2.text_input("شهر")
        
        st.write("##### شاخص‌های ظرفیتی")
        g3, g4, g5 = st.columns(3)
        halls = g3.number_input("تعداد سالن", min_value=1, value=1)
        total = g4.number_input("کل صندلی", min_value=1, value=100)
        op_seats = g5.number_input("صندلی فعال", min_value=1, value=100)
        
        st.write("##### ارزیابی ۵ محور (مقیاس ۰ تا ۵)")
        c_ax1, c_ax2 = st.columns(2)
        with c_ax1:
            s_loc = st.slider("دسترسی و موقعیت", 0.0, 5.0, 3.0, 0.1)
            s_phy = st.slider("فیزیکی و نگهداشت", 0.0, 5.0, 3.0, 0.1)
            s_tech = st.slider("فنی و تجهیزات", 0.0, 5.0, 3.0, 0.1)
        with c_ax2:
            s_ops = st.slider("راهبری و بهره‌برداری", 0.0, 5.0, 3.0, 0.1)
            s_amen = st.slider("امکانات جانبی", 0.0, 5.0, 3.0, 0.1)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("ذخیره اطلاعات در سرور"):
            if name:
                data = {
                    "name": name, "city": city, "halls": halls, "total_seats": total, "operational_seats": op_seats,
                    "score_location": s_loc, "score_physical": s_phy, "score_technical": s_tech, 
                    "score_operations": s_ops, "score_amenities": s_amen
                }
                res = requests.post(f"{SUPABASE_URL}/rest/v1/cinemas", headers=get_headers(), json=data)
                if res.status_code in [200, 201]:
                    st.success("ارزیابی با موفقیت در پایگاه داده ثبت شد.")
                    st.cache_data.clear()
                else:
                    st.error("خطا در ارتباط با سرور.")
            else:
                st.error("وارد کردن نام سینما الزامی است.")

elif menu == "تنظیمات وزن‌ها":
    st.markdown("### <i class='bi bi-sliders' style='color:#10b981;'></i> پنل تنظیمات الگوریتم", unsafe_allow_html=True)
    st.info("تغییرات در این بخش مستقیماً روی فرمول محاسبه امتیاز نهایی در کل شبکه اعمال می‌شود.")
    
    with st.form("weights_form"):
        c1, c2 = st.columns(2)
        with c1:
            w_loc = st.number_input("وزن موقعیت و دسترسی", value=float(weights.get('location', 0.2)), step=0.05)
            w_phy = st.number_input("وزن وضعیت فیزیکی", value=float(weights.get('physical', 0.25)), step=0.05)
            w_tech = st.number_input("وزن وضعیت فنی", value=float(weights.get('technical', 0.25)), step=0.05)
        with c2:
            w_ops = st.number_input("وزن راهبری", value=float(weights.get('operations', 0.15)), step=0.05)
            w_amen = st.number_input("وزن امکانات جانبی", value=float(weights.get('amenities', 0.15)), step=0.05)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("اعمال وزن‌های جدید"):
            total_w = w_loc + w_phy + w_tech + w_ops + w_amen
            if abs(total_w - 1.0) > 0.01:
                st.error(f"مجموع وزن‌ها باید معادل ۱.۰ (۱۰۰٪) باشد. مجموع فعلی: {total_w:.2f}")
            else:
                new_w = {"location": w_loc, "physical": w_phy, "technical": w_tech, "operations": w_ops, "amenities": w_amen}
                payload = {"value": new_w}
                res = requests.patch(f"{SUPABASE_URL}/rest/v1/app_config?key=eq.axis_weights", 
                                     headers=get_headers(), json=payload)
                if res.status_code in [200, 204]:
                    st.success("الگوریتم با موفقیت بروزرسانی شد.")
                    st.cache_data.clear()
                else:
                    st.error("خطا در بروزرسانی تنظیمات سرور.")

elif menu == "پشتیبان‌گیری امن":
    st.markdown("### <i class='bi bi-shield-lock' style='color:#10b981;'></i> مرکز امنیت و خروجی داده", unsafe_allow_html=True)
    st.warning("دسترسی به فایل پشتیبان (Full JSON Backup) نیازمند احراز هویت مدیریت است.")
    
    pwd = st.text_input("رمز عبور سیستم را وارد کنید:", type="password")
    
    if pwd == "Ma9184364191":
        st.success("هویت تایید شد. دسترسی به داده‌ها مجاز است.")
        if not df.empty:
            json_str = df.to_json(orient='records', force_ascii=False)
            st.download_button(
                label="دانلود فایل پشتیبان (JSON)",
                data=json_str.encode('utf-8'),
                file_name="cinemas_database_backup.json",
                mime="application/json"
            )
        else:
            st.info("داده‌ای در سیستم وجود ندارد.")
