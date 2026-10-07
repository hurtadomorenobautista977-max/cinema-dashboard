import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="داشبورد مدیریت و راهبری سینماها",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- RTL and Custom Styles ---
st.markdown("""
<style>
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
</style>
""", unsafe_allow_html=True)

# Initial Mock Data for demonstration / offline use
if 'local_data' not in st.session_state:
    st.session_state.local_data = pd.DataFrame([
        {
            "id": 1,
            "name": "سینما بهمن تهران",
            "city": "تهران",
            "halls": 4,
            "total_seats": 850,
            "operational_seats": 800,
            "score_location": 4.2,
            "score_physical": 3.8,
            "score_technical": 4.0,
            "score_operations": 4.5,
            "score_amenities": 3.5,
        },
        {
            "id": 2,
            "name": "سینما آزادی تهران",
            "city": "تهران",
            "halls": 5,
            "total_seats": 1100,
            "operational_seats": 1050,
            "score_location": 4.8,
            "score_physical": 4.5,
            "score_technical": 4.7,
            "score_operations": 4.6,
            "score_amenities": 4.3,
        },
        {
            "id": 3,
            "name": "سینما هویزه مشهد",
            "city": "مشهد",
            "halls": 8,
            "total_seats": 1500,
            "operational_seats": 1400,
            "score_location": 4.5,
            "score_physical": 4.2,
            "score_technical": 4.4,
            "score_operations": 4.3,
            "score_amenities": 4.2,
        }
    ])

df = st.session_state.local_data.copy()

# Calculate Weighted Score & Seat Efficiency
df['weighted_score'] = (
    df['score_location'] * 0.20 +
    df['score_physical'] * 0.25 +
    df['score_technical'] * 0.25 +
    df['score_operations'] * 0.15 +
    df['score_amenities'] * 0.15
).round(2)

df['seat_efficiency'] = ((df['operational_seats'] / df['total_seats'].replace(0, 1)) * 100).round(1)

# --- Sidebar Menu ---
st.sidebar.title("سامانه راهبری سینماها")
menu = st.sidebar.radio("منوی اصلی", ["📊 داشبورد تحلیلی", "📝 ثبت سینما و ارزیابی جدید", "🗃️ مدیریت داده‌ها و خروجی"])

# --- Header ---
st.title("🎬 داشبورد جامع مدیریت و ارزیابی راهبری سینماها")
st.caption("بر اساس مدل استاندارد ارزیابی شاخص‌های ۵‌گانه سینماهای کشور")
st.divider()

if menu == "📊 داشبورد تحلیلی":
    # --- Top KPIs ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("تعداد کل سینماها", len(df))
    with col2:
        st.metric("مجموع صندلی‌های فعال", f"{df['operational_seats'].sum():,}")
    with col3:
        st.metric("میانگین امتیاز کل", f"{df['weighted_score'].mean():.2f} / 5")
    with col4:
        st.metric("میانگین بهره‌وری صندلی", f"{df['seat_efficiency'].mean():.1f}%")

    st.divider()

    # --- Main Visualizations ---
    c1, c2 = st.columns([1, 1])

    with c1:
        st.subheader("📈 مقایسه امتیاز کل و بهره‌وری صندلی")
        fig_bar = px.bar(
            df,
            x="name",
            y="weighted_score",
            color="seat_efficiency",
            color_continuous_scale="Viridis",
            labels={"name": "نام سینما", "weighted_score": "امتیاز موزون کل (از ۵)", "seat_efficiency": "بهره‌وری صندلی (%)"},
            text="weighted_score"
        )
        fig_bar.update_layout(height=400)
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("🕸️ نمودار راداری ارزیابی ۵ گانه")
        selected_cinema = st.selectbox("انتخاب سینما جهت تحلیل راداری:", df["name"].unique())
        c_data = df[df["name"] == selected_cinema].iloc[0]

        categories = ['موقعیت مکانی', 'فضای عمومی', 'تجهیزات فنی', 'راهبری و مدیریت', 'امکانات جانبی']
        scores = [
            c_data['score_location'],
            c_data['score_physical'],
            c_data['score_technical'],
            c_data['score_operations'],
            c_data['score_amenities']
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
            height=400
        )
        st.plotly_chart(fig_radar, use_container_width=True)

elif menu == "📝 ثبت سینما و ارزیابی جدید":
    st.subheader("فرم ثبت مشخصات و ارزیابی دوره‌ای سینما")
    
    with st.form("cinema_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            name = st.text_input("نام سینما:")
            city = st.text_input("شهر:")
            halls = st.number_input("تعداد سالن:", min_value=1, value=2)
        with col_b:
            total_seats = st.number_input("ظرفیت کل صندلی‌ها:", min_value=10, value=300)
            op_seats = st.number_input("صندلی‌های فعال (عملیاتی):", min_value=10, value=280)
            
        st.markdown("#### 🎯 امتیازدهی به محورهای ۵‌گانه (۰ تا ۵)")
        f1, f2, f3 = st.columns(3)
        with f1:
            s_loc = st.slider("۱. موقعیت و دسترسی (وزن ۲۰٪)", 0.0, 5.0, 3.5, 0.1)
            s_phy = st.slider("۲. کیفیت فضای عمومی (وزن ۲۵٪)", 0.0, 5.0, 3.5, 0.1)
        with f2:
            s_tech = st.slider("۳. وضعیت فنی و تجهیزات (وزن ۲۵٪)", 0.0, 5.0, 3.5, 0.1)
            s_ops = st.slider("۴. راهبری و بهره‌برداری (وزن ۱۵٪)", 0.0, 5.0, 3.5, 0.1)
        with f3:
            s_amen = st.slider("۵. امکانات و فضاهای جانبی (وزن ۱۵٪)", 0.0, 5.0, 3.5, 0.1)
            
        submitted = st.form_submit_button("💾 ثبت اطلاعات در سامانه")
        
        if submitted and name:
            new_row = {
                "id": len(st.session_state.local_data) + 1,
                "name": name,
                "city": city,
                "halls": halls,
                "total_seats": total_seats,
                "operational_seats": op_seats,
                "score_location": s_loc,
                "score_physical": s_phy,
                "score_technical": s_tech,
                "score_operations": s_ops,
                "score_amenities": s_amen,
            }
            st.session_state.local_data = pd.concat([st.session_state.local_data, pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"اطلاعات سینمای «{name}» با موفقیت ثبت گردید.")
            st.rerun()

elif menu == "🗃️ مدیریت داده‌ها و خروجی":
    st.subheader("جدول کل داده‌های ثبت‌شده")
    st.dataframe(df, use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 دانلود خروجی اکسل / CSV",
        data=csv,
        file_name="cinemas_evaluation_data.csv",
        mime="text/csv"
    )
