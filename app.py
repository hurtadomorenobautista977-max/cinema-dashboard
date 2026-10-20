import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
import uuid

st.set_page_config(page_title="داشبورد مدیریت راهبری سینماها", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
<style>
    @import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');
    
    /* تنظیمات پایه، فونت و راست‌چین کردن ایمن */
    html, body, [class*="css"], h1, h2, h3, h4, h5, h6, p, span, label, th, td, li {
        font-family: 'Vazirmatn', sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    
    /* رنگ پس‌زمینه کل اپلیکیشن */
    .stApp { background-color: #f8fafc; }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* سایدبار تیره (مشابه الگوی شما) */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-left: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] * { color: #f8fafc !important; }
    
    /* استایل منوهای رادیویی سایدبار */
    .stRadio label {
        padding: 10px 15px;
        border-radius: 12px;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    .stRadio label:hover { background-color: rgba(16, 185, 129, 0.1); }
    .stRadio label[data-checked="true"] {
        background: #10b981;
        color: white !important;
        font-weight: bold;
    }
    
    /* کارت‌های متریک (آمار بالای صفحه) */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    /* دکمه‌های مینیمال */
    .stButton>button {
        border-radius: 12px !important;
        background-color: #10b981 !important;
        color: white !important;
        border: none !important;
        padding: 8px 24px !important;
        font-weight: bold;
        transition: transform 0.2s;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.3) !important; }
    
    /* کارت‌های سفارشی برای لیست و پروفایل */
    .custom-card {
        background-color: white;
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    
    /* ردیف‌های لیست سینماها */
    .list-row {
        background: white; border-radius: 12px; padding: 15px 20px; margin-bottom: 10px;
        display: flex; align-items: center; justify-content: space-between;
        border: 1px solid #e2e8f0; transition: transform 0.2s;
    }
    .list-row:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "").strip().rstrip('/')
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "").strip()

def get_headers():
    return {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

@st.cache_data(ttl=5)
def fetch_schema():
    if not SUPABASE_URL: return []
    res = requests.get(f"{SUPABASE_URL}/rest/v1/app_config?key=eq.evaluation_schema", headers=get_headers())
    if res.status_code == 200 and len(res.json()) > 0:
        return res.json()[0].get("value", [])
    return []

@st.cache_data(ttl=5)
def fetch_cinemas():
    if not SUPABASE_URL: return pd.DataFrame()
    res = requests.get(f"{SUPABASE_URL}/rest/v1/cinemas?select=*&order=id.desc", headers=get_headers())
    return pd.DataFrame(res.json()) if res.status_code == 200 else pd.DataFrame()

if 'edit_schema' not in st.session_state:
    st.session_state.edit_schema = fetch_schema()

st.sidebar.markdown("""
<div style="text-align:center; padding: 20px 0; border-bottom: 1px solid #1e293b; margin-bottom:20px;">
    <i class="bi bi-camera-reels-fill" style="font-size: 3rem; color: #10b981;"></i>
    <h3 style="color:white !important; font-weight:800; margin-top:10px;">مدیریت راهبری</h3>
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "",
    [
        "📊 داشبورد و لیست سینماها", 
        "🪪 پروفایل جامع سینما", 
        "📝 ثبت سینما و ارزیابی",
        "⚙️ مدیریت ساختار و وزن‌ها",
        "💾 خروجی و پشتیبان‌گیری"
    ],
    label_visibility="collapsed"
)

schema = fetch_schema()
df = fetch_cinemas()

if menu == "📊 داشبورد و لیست سینماها":
    st.markdown("<h2><i class='bi bi-grid-1x2-fill' style='color:#10b981;'></i> داشبورد تحلیلی شبکه</h2>", unsafe_allow_html=True)
    
    if not df.empty:
        df['seat_efficiency'] = ((pd.to_numeric(df['operational_seats'], errors='coerce') / 
                                  pd.to_numeric(df['total_seats'], errors='coerce').replace(0, 1)) * 100).round(1)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("تعداد کل سینماها", len(df))
        c2.metric("مجموع صندلی فعال", f"{int(df['operational_seats'].sum()):,}")
        c3.metric("میانگین امتیاز شبکه", f"{df['total_score'].mean():.2f} / 5")
        c4.metric("میانگین بهره‌وری ظرفیت", f"{df['seat_efficiency'].mean():.1f}%")
        
        st.markdown("<h4 style='margin-top:40px;'><i class='bi bi-list-ul'></i> لیست وضعیت سینماها</h4>", unsafe_allow_html=True)
        
        # هدر لیست
        st.markdown("""
        <div style="display: flex; padding: 0 20px 10px 20px; color: #64748b; font-size: 0.85rem; font-weight: bold; border-bottom: 2px solid #e2e8f0; margin-bottom: 10px;">
            <div style="flex: 2;">نام و موقعیت سینما</div>
            <div style="flex: 1; text-align: center;">ظرفیت فعال</div>
            <div style="flex: 1; text-align: center;">امتیاز کل ارزیابی</div>
            <div style="flex: 1; text-align: left;">عملیات</div>
        </div>
        """, unsafe_allow_html=True)
        
        for _, row in df.iterrows():
            score = float(row['total_score'])
            badge_color = "#10b981" if score >= 4 else "#f59e0b" if score >= 3 else "#ef4444"
            badge_text = "ممتاز" if score >= 4 else "مطلوب" if score >= 3 else "نیازمند بهبود"
            
            st.markdown(f"""
            <div class="list-row">
                <div style="flex: 2;">
                    <b style="font-size: 1.1rem; color: #0f172a;">{row['name']}</b>
                    <div style="font-size: 0.8rem; color: #64748b;"><i class="bi bi-geo-alt"></i> {row['province']} - {row['city']}</div>
                </div>
                <div style="flex: 1; text-align: center; color: #475569; font-size: 0.9rem;">
                    <i class="bi bi-door-open"></i> {row['halls']} سالن <br>
                    <i class="bi bi-people"></i> {row['operational_seats']} صندلی
                </div>
                <div style="flex: 1; text-align: center;">
                    <span style="background: {badge_color}20; color: {badge_color}; padding: 6px 12px; border-radius: 99px; font-weight: bold; font-size: 0.9rem;">
                        {score:.2f} ({badge_text})
                    </span>
                </div>
                <div style="flex: 1; text-align: left; font-size: 1.2rem;">
                    <span style="color:#10b981; cursor:pointer;" title="مشاهده جزئیات"><i class="bi bi-arrow-left-circle-fill"></i></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("هیچ سینمایی در سیستم ثبت نشده است.")

elif menu == "🪪 پروفایل جامع سینما":
    st.markdown("<h2><i class='bi bi-person-vcard' style='color:#10b981;'></i> شناسنامه و پروفایل سینما</h2>", unsafe_allow_html=True)
    
    if not df.empty:
        selected_name = st.selectbox("انتخاب سینما جهت مشاهده پروفایل:", df['name'].tolist())
        c_data = df[df['name'] == selected_name].iloc[0]
        eval_data = c_data.get('evaluation_data', {}) if isinstance(c_data.get('evaluation_data'), dict) else {}
        
        st.markdown(f"""
        <div class="custom-card" style="display:flex; justify-content:space-between; align-items:center; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);">
            <div>
                <h2 style="margin:0; color:#0f172a;">{c_data['name']}</h2>
                <p style="margin: 8px 0 0 0; color:#475569;"><i class="bi bi-geo-alt-fill"></i> {c_data['province']}، {c_data['city']} | <i class="bi bi-signpost"></i> {c_data['address']}</p>
            </div>
            <div style="text-align:center; background: white; padding: 15px 30px; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                <span style="font-size:0.9rem; color:#64748b; font-weight:bold;">امتیاز نهایی راهبری</span>
                <h1 style="margin:0; color:#10b981; font-size:2.5rem;">{c_data['total_score']}</h1>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### <i class='bi bi-building'></i> ظرفیت‌ها و مشخصات پایه‌ای", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("تعداد سالن", c_data['halls'])
        col2.metric("ظرفیت اسمی کل", c_data['nominal_capacity'])
        col3.metric("صندلی عملیاتی", c_data['operational_seats'])
        col4.metric("تعداد سانس روزانه", c_data['daily_shows'])
        
        st.markdown("#### <i class='bi bi-bar-chart-steps'></i> ریز نمرات و جزئیات ارزیابی", unsafe_allow_html=True)
        
        for cat in schema:
            cat_id = cat['id']
            cat_score = eval_data.get(cat_id, {}).get("score", 0.0)
            
            with st.expander(f"📌 {cat['name']} (وزن: {cat['weight']*100}%) | امتیاز کسب شده: {cat_score:.2f} / 5"):
                cat_params_data = eval_data.get(cat_id, {}).get("parameters", {})
                
                for param in cat['parameters']:
                    p_id = param['id']
                    p_data = cat_params_data.get(p_id, {"score": 0.0, "value": ""})
                    p_score = p_data['score']
                    p_value = p_data['value']
                    
                    st.markdown(f"""
                    <div style="padding: 12px; border-bottom: 1px dashed #cbd5e1; display:flex; justify-content:space-between; align-items: center;">
                        <div style="flex:2;"><b>{param['name']}</b> <br><span style="font-size:0.8rem; color:#64748b;">وزن در شاخص: {param['weight']*100}%</span></div>
                        <div style="flex:3; color:#475569; font-size:0.95rem; padding-right:15px; border-right: 2px solid #e2e8f0;">{p_value if p_value else '<span style="color:#cbd5e1;">بدون توضیح</span>'}</div>
                        <div style="flex:1; text-align:left; font-weight:bold; color:#10b981; font-size: 1.1rem;">امتیاز: {p_score}</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.warning("داده‌ای برای نمایش وجود ندارد.")

elif menu == "📝 ثبت سینما و ارزیابی":
    st.markdown("<h2><i class='bi bi-clipboard-check-fill' style='color:#10b981;'></i> فرم ثبت و ارزیابی هوشمند</h2>", unsafe_allow_html=True)
    
    if not schema:
        st.error("ساختار ارزیابی در دیتابیس یافت نشد. لطفاً از بخش مدیریت، ساختار را تعریف کنید.")
    else:
        with st.form("cinema_eval_form"):
            st.markdown("<div class='custom-card'><h4><i class='bi bi-info-circle'></i> مشخصات پایه‌ای</h4>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            name = c1.text_input("نام سینما*")
            province = c2.text_input("استان")
            city = c1.text_input("شهر")
            address = c2.text_input("آدرس دقیق")
            
            c3, c4, c5, c6 = st.columns(4)
            halls = c3.number_input("تعداد سالن", min_value=1, value=1)
            total = c4.number_input("کل صندلی", min_value=1, value=100)
            nom_cap = c5.number_input("ظرفیت اسمی", min_value=1, value=100)
            op_seats = c6.number_input("صندلی عملیاتی", min_value=1, value=100)
            shows = c3.number_input("سانس روزانه", min_value=1, value=10)
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("#### <i class='bi bi-check2-square'></i> امتیازدهی پارامترهای تخصصی", unsafe_allow_html=True)
            eval_payload = {}
            total_cinema_score = 0.0
            
            for cat in schema:
                with st.expander(f"📁 {cat['name']} (وزن شاخص: {cat['weight']})"):
                    cat_id = cat['id']
                    eval_payload[cat_id] = {"score": 0.0, "parameters": {}}
                    cat_total_score = 0.0
                    
                    for param in cat['parameters']:
                        p_id = param['id']
                        st.markdown(f"**{param['name']}** <span style='color:#64748b; font-size:0.8rem;'>(وزن: {param['weight']})</span>", unsafe_allow_html=True)
                        pc1, pc2 = st.columns([1, 2])
                        p_score = pc1.slider(f"امتیاز {p_id}", 0.0, 5.0, 3.0, 0.5, key=f"score_{cat_id}_{p_id}", label_visibility="collapsed")
                        p_val = pc2.text_input(f"توضیحات {p_id}", key=f"val_{cat_id}_{p_id}", placeholder="یادداشت، مقدار عددی یا توضیحات تکمیلی...", label_visibility="collapsed")
                        
                        eval_payload[cat_id]["parameters"][p_id] = {"score": p_score, "value": p_val}
                        cat_total_score += (p_score * param['weight'])
                        st.markdown("<hr style='margin:10px 0; border-color:#e2e8f0;'>", unsafe_allow_html=True)
                    
                    eval_payload[cat_id]["score"] = round(cat_total_score, 2)
                    st.info(f"💡 میانگین موزون محاسبه شده برای شاخص «{cat['name']}»: {cat_total_score:.2f} از ۵")
                
                total_cinema_score += (cat_total_score * cat['weight'])

            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("💾 ثبت نهایی شناسنامه و ارزیابی در دیتابیس"):
                if not name:
                    st.error("نام سینما الزامی است.")
                else:
                    data = {
                        "name": name, "province": province, "city": city, "address": address,
                        "halls": halls, "total_seats": total, "nominal_capacity": nom_cap, 
                        "operational_seats": op_seats, "daily_shows": shows,
                        "evaluation_data": eval_payload,
                        "total_score": round(total_cinema_score, 2)
                    }
                    res = requests.post(f"{SUPABASE_URL}/rest/v1/cinemas", headers=get_headers(), json=data)
                    if res.status_code in [200, 201]:
                        st.success("✅ شناسنامه و ارزیابی با موفقیت ثبت شد.")
                        st.cache_data.clear()
                    else:
                        st.error(f"خطا در ثبت: {res.text}")

elif menu == "⚙️ مدیریت ساختار و وزن‌ها":
    st.markdown("<h2><i class='bi bi-sliders' style='color:#10b981;'></i> پنل مدیریت ساختار ارزیابی (پویا)</h2>", unsafe_allow_html=True)
    st.info("در این بخش می‌توانید شاخص‌های اصلی و پارامترهای زیرمجموعه آن‌ها را اضافه، حذف یا وزن‌دهی کنید. منطق محاسبات داشبورد مستقیماً از این ساختار پیروی می‌کند.")
    
    edit_schema = st.session_state.edit_schema
    
    total_cat_weight = sum(c['weight'] for c in edit_schema)
    if abs(total_cat_weight - 1.0) > 0.01:
        st.warning(f"مجموع وزن شاخص‌های اصلی باید دقیقاً ۱.۰ باشد. (مجموع فعلی: {total_cat_weight:.2f})")
    
    for c_idx, cat in enumerate(edit_schema):
        with st.expander(f"📁 {cat['name']} (وزن: {cat['weight']})", expanded=False):
            cc1, cc2, cc3 = st.columns([3, 2, 1])
            cat['name'] = cc1.text_input("نام شاخص اصلی", value=cat['name'], key=f"cname_{c_idx}")
            cat['weight'] = cc2.number_input("وزن شاخص (۰ تا ۱)", min_value=0.0, max_value=1.0, value=float(cat['weight']), step=0.05, key=f"cw_{c_idx}")
            if cc3.button("🗑️ حذف شاخص", key=f"del_c_{c_idx}"):
                edit_schema.pop(c_idx)
                st.rerun()
            
            st.markdown("##### پارامترهای زیرمجموعه:")
            param_weight_sum = sum(p['weight'] for p in cat['parameters'])
            if abs(param_weight_sum - 1.0) > 0.01:
                st.caption(f"<span style='color:#ef4444;'>هشدار: مجموع وزن پارامترهای این شاخص {param_weight_sum:.2f} است (باید دقیقاً ۱.۰ باشد).</span>", unsafe_allow_html=True)
                
            for p_idx, param in enumerate(cat['parameters']):
                pc1, pc2, pc3 = st.columns([4, 2, 1])
                param['name'] = pc1.text_input("نام پارامتر", value=param['name'], key=f"pname_{c_idx}_{p_idx}", label_visibility="collapsed")
                param['weight'] = pc2.number_input("وزن", min_value=0.0, max_value=1.0, value=float(param['weight']), step=0.05, key=f"pw_{c_idx}_{p_idx}", label_visibility="collapsed")
                if pc3.button("حذف", key=f"del_p_{c_idx}_{p_idx}"):
                    cat['parameters'].pop(p_idx)
                    st.rerun()
            
            if st.button("➕ افزودن پارامتر جدید", key=f"add_p_{c_idx}"):
                cat['parameters'].append({"id": f"p_{str(uuid.uuid4())[:6]}", "name": "پارامتر جدید", "weight": 0.1})
                st.rerun()
                
    st.divider()
    ac1, ac2 = st.columns(2)
    if ac1.button("➕ ایجاد شاخص اصلی جدید"):
        edit_schema.append({"id": f"cat_{str(uuid.uuid4())[:6]}", "name": "شاخص جدید", "weight": 0.1, "parameters": []})
        st.rerun()
        
    if ac2.button("💾 ذخیره ساختار جدید در دیتابیس (اعمال نهایی)"):
        payload = {"value": edit_schema}
        res = requests.patch(f"{SUPABASE_URL}/rest/v1/app_config?key=eq.evaluation_schema", headers=get_headers(), json=payload)
        if res.status_code in [200, 204]:
            st.success("✅ ساختار ارزیابی با موفقیت در سیستم مرکزی بروزرسانی شد.")
            st.cache_data.clear()
        else:
            st.error("خطا در ذخیره‌سازی")

elif menu == "💾 خروجی و پشتیبان‌گیری":
    st.markdown("<h2><i class='bi bi-shield-lock-fill' style='color:#10b981;'></i> خروجی امن داده‌ها</h2>", unsafe_allow_html=True)
    pwd = st.text_input("رمز عبور مدیر سیستم را وارد کنید:", type="password")
    
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
    elif pwd != "":
        st.error("❌ رمز عبور اشتباه است.")
