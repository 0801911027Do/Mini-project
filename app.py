"""
แอปพลิเคชันตรวจจับภัยคุกคามไซเบอร์ (ML Mini-Project)
รองรับโหมดมืด (Dark Mode) และโหมดสว่าง (Light Mode) สลับได้ทันที
ออกแบบตามมาตรฐาน visual system ของ landing-page-design:
- Typography: ฟอนต์ Manrope, Type scale มาตรฐาน, text-wrap: balance
- Spacing: Spacing tokens (8px, 16px, 24px, 32px)
- Radius: Outer card 16px, inner component 10px (nested radius formula)
- Surface: Flat surfaces ไม่ใช้ gradient background
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
# 2. ตัวสลับธีม: โหมดมืด (Dark) / โหมดสว่าง (Light)
# ----------------------------------------------------
if "is_dark" not in st.session_state:
    st.session_state.is_dark = True

# แถบควบคุมด้านบนขวาสำหรับสลับโหมด
top_space, top_toggle = st.columns([6, 1.2])
with top_toggle:
    theme_text = "🌙 โหมดมืด (Dark)" if st.session_state.is_dark else "☀️ โหมดสว่าง (Light)"
    selected_dark = st.toggle(theme_text, value=st.session_state.is_dark)
    if selected_dark != st.session_state.is_dark:
        st.session_state.is_dark = selected_dark
        st.rerun()

# ----------------------------------------------------
# 3. กำหนดค่าสีตาม Design Tokens (Dark vs Light)
# ----------------------------------------------------
if st.session_state.is_dark:
    # DARK MODE (ตามมาตรฐาน B4, B5)
    bg_app = "#121212"
    bg_card = "#1F1F1F"
    border_card = "#2D2D2D"
    text_primary = "#FFFFFF"
    text_secondary = "#9E9E9E"
    badge_bg = "#272727"
    badge_border = "#333333"
    hero_grad = "linear-gradient(180deg, #FFFFFF 0%, #9B9B9B 100%)"
    metric_bg = "#181818"
    metric_border = "#2B2B2B"
    step_bg = "#181818"
    step_border = "#2B2B2B"
    
    # การ์ดสถานะภัยคุกคามในโหมดมืด
    c_norm_bg = "#162419"
    c_norm_border = "#1B4D28"
    c_ddos_bg = "#281417"
    c_ddos_border = "#5C1D24"
    c_scan_bg = "#291E14"
    c_scan_border = "#5E3917"
    c_brute_bg = "#231629"
    c_brute_border = "#4C215E"
    threat_desc_color = "#D1D5DB"
    action_tag_bg = "rgba(255, 255, 255, 0.08)"
    action_tag_text = "#FFFFFF"
else:
    # LIGHT MODE (ตามมาตรฐาน B4, B5)
    bg_app = "#F8FAFC"
    bg_card = "#FFFFFF"
    border_card = "#E2E8F0"
    text_primary = "#0F172A"
    text_secondary = "#64748B"
    badge_bg = "#F1F5F9"
    badge_border = "#CBD5E1"
    hero_grad = "linear-gradient(180deg, #000000 0%, #666666 100%)"
    metric_bg = "#F8FAFC"
    metric_border = "#E2E8F0"
    step_bg = "#F8FAFC"
    step_border = "#E2E8F0"
    
    # การ์ดสถานะภัยคุกคามในโหมดสว่าง (โทนพาสเทลสะอาดตา)
    c_norm_bg = "#F0FDF4"
    c_norm_border = "#BBF7D0"
    c_ddos_bg = "#FEF2F2"
    c_ddos_border = "#FECACA"
    c_scan_bg = "#FFFBEB"
    c_scan_border = "#FDE68A"
    c_brute_bg = "#FAF5FF"
    c_brute_border = "#E9D5FF"
    threat_desc_color = "#334155"
    action_tag_bg = "rgba(0, 0, 0, 0.05)"
    action_tag_text = "#0F172A"

# ----------------------------------------------------
# 4. Inject Dynamic CSS
# ----------------------------------------------------
st.markdown(f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">

<style>
    /* ตั้งค่าฟอนต์สากล Manrope ให้กับองค์ประกอบข้อความหลัก */
    .stApp, .stApp p, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp button, .stApp input {{
        font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }}
    
    /* โทนสีพื้นหลังหลักของแอป */
    .stApp {{
        background-color: {bg_app} !important;
        color: {text_primary} !important;
    }}
    
    /* ป้องกันตัวอักษร ligature หลุดซ้อนข้อความ เช่น keyboard_arrow_down หรือ arrd_ */
    [data-testid="stIconMaterial"],
    [data-testid*="stIcon"],
    [data-testid="stExpanderToggleIcon"],
    [data-testid="stExpanderToggleIcon"] *,
    [data-testid="stExpander"] summary span:first-child,
    .material-symbols-rounded,
    [class*="material-symbols"] {{
        font-family: "Material Symbols Rounded" !important;
        font-weight: normal !important;
        font-style: normal !important;
        line-height: 1 !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
        direction: ltr !important;
        -webkit-font-feature-settings: 'liga' 1 !important;
        font-feature-settings: 'liga' 1 !important;
        -webkit-font-smoothing: antialiased !important;
        overflow: hidden !important;
        vertical-align: middle !important;
    }}
    
    /* Hero Heading with gradient text per B5 */
    .hero-container {{
        max-width: 680px;
        margin: 0 auto 32px auto;
        text-align: center;
        padding-top: 8px;
    }}
    
    .hero-badge {{
        display: inline-block;
        padding: 4px 12px;
        background-color: {badge_bg};
        border: 1px solid {badge_border};
        border-radius: 9999px;
        font-size: 13px;
        font-weight: 600;
        color: #00D26A;
        margin-bottom: 16px;
    }}
    
    .hero-title {{
        font-size: 38px;
        font-weight: 700;
        line-height: 1.2;
        background: {hero_grad};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 16px;
        text-wrap: balance;
    }}
    
    .hero-subtitle {{
        font-size: 16px;
        color: {text_secondary};
        line-height: 1.5;
        text-wrap: balance;
        margin-bottom: 24px;
    }}

    /* Flat Card Surfaces per B3, B4 */
    .card-surface {{
        background-color: {bg_card};
        border: 1px solid {border_card};
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        color: {text_primary};
        transition: transform 300ms cubic-bezier(0.22, 1, 0.36, 1), border-color 300ms ease;
    }}
    
    .card-surface:hover {{
        border-color: #00D26A;
    }}

    .card-title {{
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 16px;
        color: {text_primary};
    }}

    /* Threat Status Cards (Component States per B9) */
    .threat-card {{
        border-radius: 16px;
        padding: 24px;
        margin-top: 16px;
        margin-bottom: 24px;
        border: 1px solid;
    }}
    
    .threat-normal {{
        background-color: {c_norm_bg};
        border-color: {c_norm_border};
    }}
    
    .threat-ddos {{
        background-color: {c_ddos_bg};
        border-color: {c_ddos_border};
    }}
    
    .threat-portscan {{
        background-color: {c_scan_bg};
        border-color: {c_scan_border};
    }}
    
    .threat-bruteforce {{
        background-color: {c_brute_bg};
        border-color: {c_brute_border};
    }}

    .threat-title {{
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 8px;
    }}
    
    .threat-desc {{
        font-size: 14px;
        line-height: 1.5;
        color: {threat_desc_color};
        margin-bottom: 16px;
    }}

    .action-tag {{
        display: inline-block;
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        background-color: {action_tag_bg};
        color: {action_tag_text};
    }}

    /* Metric Grid Box */
    .metric-box {{
        background-color: {metric_bg};
        border: 1px solid {metric_border};
        border-radius: 10px;
        padding: 12px 16px;
        text-align: center;
    }}
    
    .metric-label {{
        font-size: 12px;
        color: {text_secondary};
        margin-bottom: 4px;
    }}
    
    .metric-value {{
        font-size: 18px;
        font-weight: 600;
        color: {text_primary};
    }}
    
    /* Step Cards in How it Works */
    .step-box {{
        background-color: {step_bg};
        border: 1px solid {step_border};
        padding: 16px;
        border-radius: 12px;
        height: 100%;
    }}
    
    .step-title {{
        font-weight: 600;
        color: {text_primary};
        margin-bottom: 6px;
    }}
    
    .step-desc {{
        font-size: 13px;
        color: {text_secondary};
        line-height: 1.5;
    }}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 5. โหลดโมเดล Machine Learning
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
# 6. SECTION 1: HERO SECTION
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

# แถบทางลัดไปยังหน้าย่อย (Navigation Links)
_link1, _link2 = st.columns(2)
with _link1:
    st.page_link("pages/2_red_vs_blue.py", label="⚔️ สนามจำลอง: ฝ่ายโจมตี vs ฝ่ายป้องกัน (Red vs Blue Team)", icon="⚔️")
with _link2:
    st.page_link("pages/1_why_defense.py", label="🛡️ เหตุผลที่สร้างโปรเจกต์นี้ (มุมมองฝ่ายป้องกันในยุค AI)", icon="🛡️")

# ----------------------------------------------------
# 7. SECTION 2: INTERACTIVE TESTING PLAYGROUND
# ----------------------------------------------------
st.markdown('<div class="card-surface">', unsafe_allow_html=True)
st.markdown("<div class='card-title'>1. ทดลองป้อนข้อมูลหรือเลือกตัวอย่างการโจมตี (Interactive Test)</div>", unsafe_allow_html=True)

# ตัวเลือกรูปแบบการป้อนข้อมูล
input_mode = st.radio(
    "เลือกรูปแบบการป้อนข้อมูล:",
    ["⚡ เลือกจากเหตุการณ์ตัวอย่าง (Presets)", "✍️ กำหนดค่าตัวเลขเองอิสระ (Custom Input)"],
    horizontal=True
)

if input_mode == "⚡ เลือกจากเหตุการณ์ตัวอย่าง (Presets)":
    preset = st.selectbox(
        "เลือกเหตุการณ์ตัวอย่างเพื่อทดสอบอย่างรวดเร็ว:",
        [
            "ทราฟฟิกปกติ (Normal Web Browsing)",
            "การโจมตี DDoS (SYN Flood แพ็กเก็ตสูงในเสี้ยววินาที)",
            "การกวาดสแกนพอร์ต (Port Scan เพื่อหาช่องโหว่)",
            "การสุ่มรหัสผ่าน (SSH Brute Force พอร์ต 22)"
        ]
    )

    if preset.startswith("ทราฟฟิกปกติ"):
        init_dur, init_pkts, init_bytes, init_logins, init_port = 2.4, 42, 17500, 0, 443
    elif preset.startswith("การโจมตี DDoS"):
        init_dur, init_pkts, init_bytes, init_logins, init_port = 0.04, 1850, 74000, 0, 80
    elif preset.startswith("การกวาดสแกนพอร์ต"):
        init_dur, init_pkts, init_bytes, init_logins, init_port = 0.02, 1, 44, 0, 8080
    else:
        init_dur, init_pkts, init_bytes, init_logins, init_port = 9.2, 84, 12600, 21, 22
else:
    # โหมดกำหนดค่าเองอิสระ
    init_dur, init_pkts, init_bytes, init_logins, init_port = 3.0, 50, 20000, 0, 80
    st.info("💡 **โหมดกำหนดค่าอิสระ:** คุณสามารถพิมพ์ตัวเลขในช่องด้านล่างตามที่ต้องการได้เลยครับ หรือเปิดดูคำแนะนำด้านล่างว่ากรอกประมาณไหนถึงจะจำลองแต่ละเหตุการณ์ได้ครับ")

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

# คำแนะนำสำหรับคิดกรอกตัวเลขเอง
with st.expander("📖 คำแนะนำ: วิธีคิดตัวเลขสำหรับกรอกเอง (Custom Input Guide)"):
    st.markdown("""
    คุณสามารถลองพิมพ์เลขตามพฤติกรรมจริงของเครือข่าย เพื่อดูว่าโมเดลจะทำนายถูกต้องหรือไม่:
    * **1. อยากให้โมเดลทำนายเป็น 'ทราฟฟิกปกติ (Normal)':**
      - `duration`: 1.0 ถึง 10.0 วินาที
      - `packets`: 15 ถึง 100 แพ็กเก็ต
      - `failed_logins`: 0 ครั้ง
      - `port`: 80 หรือ 443 (เว็บ) หรือ 53 (DNS)
    * **2. อยากให้โมเดลทำนายเป็น 'การโจมตี DDoS':**
      - `duration`: สั้นมากๆ เช่น 0.01 ถึง 0.1 วินาที
      - `packets`: ถล่มเข้ามาเยอะมาก เช่น 800 ถึง 3,000 แพ็กเก็ต
      - `bytes`: แพ็กเก็ตละประมาณ 40-50 ไบต์
      - `port`: 80 หรือ 443
    * **3. อยากให้โมเดลทำนายเป็น 'การกวาดสแกนพอร์ต (Port Scan)':**
      - `duration`: 0.01 ถึง 0.05 วินาที
      - `packets`: น้อยมากๆ แค่ 1 ถึง 3 แพ็กเก็ตเพื่อหยั่งเชิง
      - `bytes`: 44 ไบต์
      - `port`: สุ่มพอร์ตแปลกๆ เช่น 8080, 21, 23, 1433
    * **4. อยากให้โมเดลทำนายเป็น 'การสุ่มรหัสผ่าน (SSH Brute Force)':**
      - `port`: ต้องเป็นพอร์ต **22** (SSH)
      - `failed_logins`: สูงผิดปกติ เช่น 10 ถึง 30 ครั้ง
      - `duration`: 5.0 ถึง 15.0 วินาที
    """)

# ปุ่ม Action หลัก (CTA Button)
st.write("")
predict_clicked = st.button("ตรวจสอบภัยคุกคามด้วย AI (Predict)", type="primary", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 8. SECTION 3: THREAT CARD COMPONENT
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

    st.markdown(f"""
    <div class="threat-card {card_class}">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span style="font-size: 13px; font-weight: 700; color: {status_color}; text-transform: uppercase;">
                AI Verdict Result
            </span>
            <span style="font-size: 13px; font-weight: 600; color: {status_color}; background-color: rgba(0,0,0,0.06); padding: 4px 10px; border-radius: 6px;">
                ความเชื่อมั่น: {max_prob:.1f}%
            </span>
        </div>
        <div class="threat-title" style="color: {status_color};">{title_text}</div>
        <div class="threat-desc">{desc_text}</div>
        <div class="action-tag" style="border: 1px solid {status_color};">
            💡 {recommend_text}
        </div>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""<div class="metric-box"><div class="metric-label">Duration</div><div class="metric-value">{duration:.2f}s</div></div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="metric-box"><div class="metric-label">Packets</div><div class="metric-value">{packets:,}</div></div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class="metric-box"><div class="metric-label">Failed Logins</div><div class="metric-value">{failed_logins} ครั้ง</div></div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""<div class="metric-box"><div class="metric-label">Target Port</div><div class="metric-value">{port}</div></div>""", unsafe_allow_html=True)

    st.write("")
    with st.expander("🔍 ดูค่าความน่าจะเป็นแยกรายคลาส (Probability Distribution)"):
        prob_df = pd.DataFrame({
            "ประเภทภัยคุกคาม": classes,
            "ความน่าจะเป็น (%)": [round(p * 100, 2) for p in probs]
        }).sort_values(by="ความน่าจะเป็น (%)", ascending=False)
        st.dataframe(prob_df, hide_index=True, use_container_width=True)

# ----------------------------------------------------
# 9. SECTION 4: HOW IT WORKS (3 STEPS)
# ----------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="card-surface">', unsafe_allow_html=True)
st.markdown("<div class='card-title'>2. หลักการทำงานของระบบ (How It Works)</div>", unsafe_allow_html=True)

col_s1, col_s2, col_s3 = st.columns(3)
with col_s1:
    st.markdown("""
    <div class="step-box">
        <div style="color: #00D26A; font-weight: 700; margin-bottom: 6px;">ขั้นตอนที่ 1</div>
        <div class="step-title">รวบรวมทราฟฟิก (Ingest)</div>
        <div class="step-desc">ดึงข้อมูลการเชื่อมต่อเครือข่าย เช่น ระยะเวลา จำนวนแพ็กเก็ต และพอร์ตเป้าหมาย</div>
    </div>
    """, unsafe_allow_html=True)

with col_s2:
    st.markdown("""
    <div class="step-box">
        <div style="color: #00D26A; font-weight: 700; margin-bottom: 6px;">ขั้นตอนที่ 2</div>
        <div class="step-title">ทำนายด้วย AI (Classify)</div>
        <div class="step-desc">โมเดล Random Forest วิเคราะห์และเปรียบเทียบพฤติกรรมกับฐานข้อมูลที่ฝึกสอน</div>
    </div>
    """, unsafe_allow_html=True)

with col_s3:
    st.markdown("""
    <div class="step-box">
        <div style="color: #00D26A; font-weight: 700; margin-bottom: 6px;">ขั้นตอนที่ 3</div>
        <div class="step-title">แจ้งเตือนทันที (Respond)</div>
        <div class="step-desc">แสดงผลลัพธ์ผ่านแดชบอร์ด พร้อมคำแนะนำในการบล็อกหรือจำกัดความเสียหาย</div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 10. SECTION 5: MODEL PROOF & DATASET STATS
# ----------------------------------------------------
st.markdown('<div class="card-surface">', unsafe_allow_html=True)
st.markdown("<div class='card-title'>3. ข้อมูลสถิติของโมเดล (Model Performance & Data)</div>", unsafe_allow_html=True)

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
