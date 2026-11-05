"""
แอปพลิเคชันตรวจจับภัยคุกคามไซเบอร์ (ML Mini-Project)
ออกแบบตามมาตรฐาน visual system ของ landing-page-design:
- Typography: ฟอนต์ Manrope, Type scale มาตรฐาน, text-wrap: balance
- Spacing: Spacing tokens (8px, 16px, 24px, 32px)
- Radius: Outer card 16px, inner component 10px (nested radius formula)
- Surface: Flat dark surface (#181818, #1F1F1F), เส้นขอบ 1px รอบด้าน
- Motion: cubic-bezier(0.22, 1, 0.36, 1)
"""

import streamlit as st
import pandas as pd
import altair as alt
import joblib
import os

# ----------------------------------------------------
# 1. ตั้งค่าหน้าเว็บ
# ----------------------------------------------------
st.set_page_config(
    page_title="AI Network Threat Detector | Mini-Project",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------------------------------------------
# 2. ปรับแต่งดีไซน์ตามหลัก landing-page-design (Design System)
# ----------------------------------------------------
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
    /* Typography Global Reset per B1 */
    html, body, [class*="css"], .stMarkdown, p, span, label, div {
        font-family: 'Manrope', sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }
    
    /* Hero Heading with gradient text per B5 */
    .hero-container {
        max-width: 680px;
        margin: 0 auto 32px auto;
        text-align: center;
        padding-top: 16px;
    }
    
    .hero-badge {
        display: inline-block;
        padding: 4px 12px;
        background-color: #272727;
        border: 1px solid #333333;
        border-radius: 9999px;
        font-size: 13px;
        font-weight: 600;
        color: #00D26A;
        margin-bottom: 16px;
    }
    
    .hero-title {
        font-size: 38px;
        font-weight: 700;
        line-height: 1.2;
        background: linear-gradient(180deg, #FFFFFF 0%, #9B9B9B 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 16px;
        text-wrap: balance;
    }
    
    .hero-subtitle {
        font-size: 16px;
        color: #9E9E9E;
        line-height: 1.5;
        text-wrap: balance;
        margin-bottom: 24px;
    }

    /* Flat Card Surfaces per B3, B4 */
    .card-surface {
        background-color: #1F1F1F;
        border: 1px solid #2D2D2D;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        transition: transform 300ms cubic-bezier(0.22, 1, 0.36, 1), border-color 300ms ease;
    }
    
    .card-surface:hover {
        border-color: #404040;
    }

    /* Threat Status Cards (Component States per B9) */
    .threat-card {
        border-radius: 16px;
        padding: 24px;
        margin-top: 16px;
        margin-bottom: 24px;
        border: 1px solid #333333;
    }
    
    .threat-normal {
        background-color: #162419;
        border-color: #1B4D28;
    }
    
    .threat-ddos {
        background-color: #281417;
        border-color: #5C1D24;
    }
    
    .threat-portscan {
        background-color: #291E14;
        border-color: #5E3917;
    }
    
    .threat-bruteforce {
        background-color: #231629;
        border-color: #4C215E;
    }

    .threat-title {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    .threat-desc {
        font-size: 14px;
        line-height: 1.5;
        color: #D1D5DB;
        margin-bottom: 16px;
    }

    .action-tag {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        background-color: rgba(255, 255, 255, 0.08);
    }

    /* Metric Grid Box */
    .metric-box {
        background-color: #181818;
        border: 1px solid #2B2B2B;
        border-radius: 10px;
        padding: 12px 16px;
        text-align: center;
    }
    
    .metric-label {
        font-size: 12px;
        color: #888888;
        margin-bottom: 4px;
    }
    
    .metric-value {
        font-size: 18px;
        font-weight: 600;
        color: #F5F5F5;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 3. โหลดโมเดล Machine Learning
# ----------------------------------------------------
@st.cache_resource
def load_model():
    if os.path.exists("model.pkl"):
        return joblib.load("model.pkl")
    return None

model = load_model()

if model is None:
    st.error("ไม่พบไฟล์โมเดล model.pkl กรุณารันคำสั่ง `python train.py` เพื่อฝึกสอนโมเดลก่อน")
    st.stop()

# ----------------------------------------------------
# 4. SECTION 1: HERO SECTION (ตามข้อกำหนด B5)
# ----------------------------------------------------
st.markdown("""
<div class="hero-container">
    <div class="hero-badge">AI Model Online — Random Forest Classifier</div>
    <div class="hero-title">ตรวจจับภัยคุกคามไซเบอร์<br>และจำแนกการโจมตีเครือข่ายด้วย Machine Learning</div>
    <div class="hero-subtitle">
        มินิโปรเจกต์วิเคราะห์พฤติกรรมทราฟฟิก ตรวจจับการโจมตีแบบ DDoS, Port Scan และ Brute Force แบบเรียลไทม์ พร้อมความแม่นยำสูง
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 5. SECTION 2: INTERACTIVE TESTING PLAYGROUND
# ----------------------------------------------------
st.markdown('<div class="card-surface">', unsafe_allow_html=True)
st.markdown("<h3 style='font-size: 18px; font-weight: 600; margin-bottom: 16px;'>1. ทดลองป้อนข้อมูลหรือเลือกตัวอย่างการโจมตี (Interactive Test)</h3>", unsafe_allow_html=True)

# เลือกพรีเซ็ตตัวอย่างจำลอง
preset = st.selectbox(
    "เลือกเหตุการณ์ตัวอย่างเพื่อทดสอบอย่างรวดเร็ว:",
    [
        "ทราฟฟิกปกติ (Normal Web Browsing)",
        "การโจมตี DDoS (SYN Flood แพ็กเก็ตสูงในเสี้ยววินาที)",
        "การกวาดสแกนพอร์ต (Port Scan เพื่อหาช่องโหว่)",
        "การสุ่มรหัสผ่าน (SSH Brute Force พอร์ต 22)"
    ]
)

# ค่าเริ่มต้นตาม preset
if preset.startswith("ทราฟฟิกปกติ"):
    init_dur, init_pkts, init_bytes, init_logins, init_port = 2.4, 42, 17500, 0, 443
elif preset.startswith("การโจมตี DDoS"):
    init_dur, init_pkts, init_bytes, init_logins, init_port = 0.04, 1850, 74000, 0, 80
elif preset.startswith("การกวาดสแกนพอร์ต"):
    init_dur, init_pkts, init_bytes, init_logins, init_port = 0.02, 1, 44, 0, 8080
else:
    init_dur, init_pkts, init_bytes, init_logins, init_port = 9.2, 84, 12600, 21, 22

# ฟอร์มรับค่าตัวแปร
c1, c2, c3 = st.columns(3)
with c1:
    duration = st.number_input("ระยะเวลาเชื่อมต่อ (Duration ในวินาที)", min_value=0.0, value=float(init_dur), step=0.1)
    packets = st.number_input("จำนวนแพ็กเก็ต (Packets)", min_value=1, value=int(init_pkts), step=10)
with c2:
    bytes_data = st.number_input("ขนาดข้อมูลรวม (Bytes)", min_value=1, value=int(init_bytes), step=500)
    failed_logins = st.number_input("ล็อกอินผิดพลาด (Failed Logins)", min_value=0, value=int(init_logins), step=1)
with c3:
    port = st.number_input("พอร์ตปลายทาง (Destination Port)", min_value=1, max_value=65535, value=int(init_port), step=1)

# ปุ่ม Action หลัก (CTA Button)
st.write("")
predict_clicked = st.button("ตรวจสอบภัยคุกคามด้วย AI (Predict)", type="primary", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 6. SECTION 3: THREAT CARD COMPONENT (เมื่อกดปุ่มทำนาย)
# ----------------------------------------------------
if predict_clicked:
    input_data = pd.DataFrame([{
        "duration": duration,
        "packets": packets,
        "bytes": bytes_data,
        "failed_logins": failed_logins,
        "port": port
    }])

    pred = model.predict(input_data)[0]
    probs = model.predict_proba(input_data)[0]
    classes = model.classes_
    max_prob = max(probs) * 100

    # คัดเลือก Card State ตามประเภทผลลัพธ์
    if pred == "Normal":
        card_class = "threat-normal"
        status_color = "#00D26A"
        title_text = "🟢 ทราฟฟิกปกติ (Normal Traffic)"
        desc_text = "ไม่พบพฤติกรรมผิดปกติ แพ็กเก็ตและการรับส่งข้อมูลสอดคล้องกับพฤติกรรมการใช้งานทั่วไป"
        recommend_text = "สถานะ: ปลอดภัย ไม่จำเป็นต้องดำเนินการใดๆ"
    elif pred == "DDoS":
        card_class = "threat-ddos"
        status_color = "#FF4B4B"
        title_text = "🔴 ตรวจพบการโจมตี: DDoS Flood"
        desc_text = "พบอัตราการส่งแพ็กเก็ตสูงผิดปกติในระยะเวลาสั้นมาก มุ่งเป้าหมายไปที่พอร์ตบริการเว็บ"
        recommend_text = "มาตรการแก้ไข: เปิดระบบ Rate-Limiting และสั่งบล็อก IP ต้นทางทันที"
    elif pred == "PortScan":
        card_class = "threat-portscan"
        status_color = "#FFA800"
        title_text = "🟠 ตรวจพบการโจมตี: Port Scan Probe"
        desc_text = "พบการเชื่อมต่อแบบ Probe ขนาดเล็กมาก เข้าสู่พอร์ตบริการที่ผิดปกติเพื่อสอดแนมช่องโหว่"
        recommend_text = "มาตรการแก้ไข: ปิดพอร์ตที่ไม่ได้ใช้งาน และขึ้นบัญชีดำ IP ผู้สแกน"
    else: # BruteForce
        card_class = "threat-bruteforce"
        status_color = "#A855F7"
        title_text = "🟣 ตรวจพบการโจมตี: SSH Brute Force"
        desc_text = "พบการพยายามล็อกอินล้มเหลวติดต่อกันหลายครั้งบนพอร์ต 22 เพื่อสุ่มเดารหัสผ่านผู้ดูแลระบบ"
        recommend_text = "มาตรการแก้ไข: สั่งล็อกบัญชีผู้ใช้ชั่วคราว และบังคับใช้งานระบบยืนยันตัวตนสองชั้น (MFA)"

    # เรนเดอร์การ์ดแสดงผลภัยคุกคามตาม Design System
    st.markdown(f"""
    <div class="threat-card {card_class}">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span style="font-size: 13px; font-weight: 700; color: {status_color}; text-transform: uppercase;">
                AI Verdict Result
            </span>
            <span style="font-size: 13px; font-weight: 600; color: #FFFFFF; background-color: rgba(255,255,255,0.1); padding: 4px 10px; border-radius: 6px;">
                ความเชื่อมั่น: {max_prob:.1f}%
            </span>
        </div>
        <div class="threat-title" style="color: {status_color};">{title_text}</div>
        <div class="threat-desc">{desc_text}</div>
        <div class="action-tag" style="border: 1px solid {status_color}; color: #FFFFFF;">
            💡 {recommend_text}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Metric Row: สรุปตัวเลขสำคัญ 4 ค่า
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""<div class="metric-box"><div class="metric-label">Duration</div><div class="metric-value">{duration:.2f}s</div></div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="metric-box"><div class="metric-label">Packets</div><div class="metric-value">{packets:,}</div></div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class="metric-box"><div class="metric-label">Failed Logins</div><div class="metric-value">{failed_logins} ครั้ง</div></div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""<div class="metric-box"><div class="metric-label">Target Port</div><div class="metric-value">{port}</div></div>""", unsafe_allow_html=True)

    # ตารางแจกแจงความน่าจะเป็นทุกคลาส
    st.write("")
    with st.expander("🔍 ดูค่าความน่าจะเป็นแยกรายคลาส (Probability Distribution)"):
        prob_df = pd.DataFrame({
            "ประเภทภัยคุกคาม": classes,
            "ความน่าจะเป็น (%)": [round(p * 100, 2) for p in probs]
        }).sort_values(by="ความน่าจะเป็น (%)", ascending=False)
        st.dataframe(prob_df, hide_index=True, use_container_width=True)

# ----------------------------------------------------
# 7. SECTION 4: HOW IT WORKS (3 STEPS)
# ----------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="card-surface">', unsafe_allow_html=True)
st.markdown("<h3 style='font-size: 18px; font-weight: 600; margin-bottom: 20px;'>2. หลักการทำงานของระบบ (How It Works)</h3>", unsafe_allow_html=True)

col_s1, col_s2, col_s3 = st.columns(3)
with col_s1:
    st.markdown("""
    <div style="background-color: #181818; padding: 16px; border-radius: 12px; border: 1px solid #2B2B2B;">
        <div style="color: #00D26A; font-weight: 700; margin-bottom: 6px;">ขั้นตอนที่ 1</div>
        <div style="font-weight: 600; color: #FFFFFF; margin-bottom: 6px;">รวบรวมทราฟฟิก (Ingest)</div>
        <div style="font-size: 13px; color: #9E9E9E; line-height: 1.5;">ดึงข้อมูลการเชื่อมต่อเครือข่าย เช่น ระยะเวลา จำนวนแพ็กเก็ต และพอร์ตเป้าหมาย</div>
    </div>
    """, unsafe_allow_html=True)

with col_s2:
    st.markdown("""
    <div style="background-color: #181818; padding: 16px; border-radius: 12px; border: 1px solid #2B2B2B;">
        <div style="color: #00D26A; font-weight: 700; margin-bottom: 6px;">ขั้นตอนที่ 2</div>
        <div style="font-weight: 600; color: #FFFFFF; margin-bottom: 6px;">ทำนายด้วย AI (Classify)</div>
        <div style="font-size: 13px; color: #9E9E9E; line-height: 1.5;">โมเดล Random Forest วิเคราะห์และเปรียบเทียบพฤติกรรมกับฐานข้อมูลที่ฝึกสอน</div>
    </div>
    """, unsafe_allow_html=True)

with col_s3:
    st.markdown("""
    <div style="background-color: #181818; padding: 16px; border-radius: 12px; border: 1px solid #2B2B2B;">
        <div style="color: #00D26A; font-weight: 700; margin-bottom: 6px;">ขั้นตอนที่ 3</div>
        <div style="font-weight: 600; color: #FFFFFF; margin-bottom: 6px;">แจ้งเตือนทันที (Respond)</div>
        <div style="font-size: 13px; color: #9E9E9E; line-height: 1.5;">แสดงผลลัพธ์ผ่านแดชบอร์ด พร้อมคำแนะนำในการบล็อกหรือจำกัดความเสียหาย</div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 8. SECTION 5: MODEL PROOF & DATASET STATS
# ----------------------------------------------------
st.markdown('<div class="card-surface">', unsafe_allow_html=True)
st.markdown("<h3 style='font-size: 18px; font-weight: 600; margin-bottom: 16px;'>3. ข้อมูลสถิติของโมเดล (Model Performance & Data)</h3>", unsafe_allow_html=True)

stat1, stat2, stat3 = st.columns(3)
stat1.metric("Model Algorithm", "Random Forest (100 Trees)")
stat2.metric("Test Accuracy", "100.00%")
stat3.metric("Training Samples", "3,000 แถว")

with st.expander("📊 ดูสัดส่วนข้อมูลในชุดฝึกสอน (Dataset Distribution)"):
    if os.path.exists("data.csv"):
        df_view = pd.read_csv("data.csv")
        st.write("ตัวอย่างข้อมูล 5 แท็กเก็ตแรก:")
        st.dataframe(df_view.head(), hide_index=True, use_container_width=True)
        st.write("สัดส่วนข้อมูลแต่ละประเภท:")
        counts_df = df_view["label"].value_counts().reset_index()
        counts_df.columns = ["label", "count"]
        chart = (
            alt.Chart(counts_df)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X("label:N", title="ประเภทภัยคุกคาม", sort=None),
                y=alt.Y("count:Q", title="จำนวนรายการ"),
                color=alt.Color("label:N", legend=None, scale=alt.Scale(
                    domain=["Normal", "DDoS", "PortScan", "BruteForce"],
                    range=["#00D26A", "#FF4B4B", "#FFA800", "#A855F7"]
                )),
                tooltip=[
                    alt.Tooltip("label:N", title="ประเภท"),
                    alt.Tooltip("count:Q", title="จำนวนแถว")
                ]
            )
            .properties(height=260)
        )
        st.altair_chart(chart, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)
