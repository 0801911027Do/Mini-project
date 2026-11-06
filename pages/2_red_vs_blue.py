"""
หน้าจำลอง: ฝ่ายโจมตี (Red Team) vs ฝ่ายป้องกัน (Blue Team)
ระบบสาธิตการทำงานร่วมกันระหว่างการโจมตีและการป้องกันแบบ Interactive
สำหรับใช้แสดงใน Mini Project: มีทั้ง 2 ฝั่งในหน้าเดียว
"""

import streamlit as st
import time
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="โจมตี vs ป้องกัน (Red vs Blue Team) | Mini-Project",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------------------------------
# 1. จัดการธีม (มืด / สว่าง) เชื่อมกับหน้าหลัก
# ----------------------------------------------------
is_dark = st.session_state.get("is_dark", True)

if is_dark:
    bg_app = "#121212"
    bg_card = "#1E1E1E"
    border_card = "#2D2D2D"
    text_primary = "#FFFFFF"
    text_secondary = "#9E9E9E"
    inner_card = "#161616"
    inner_border = "#2A2A2A"
    hero_grad = "linear-gradient(180deg, #FFFFFF 0%, #9B9B9B 100%)"
    terminal_bg = "#0B0F19"
    terminal_text = "#38BDF8"
else:
    bg_app = "#F8FAFC"
    bg_card = "#FFFFFF"
    border_card = "#E2E8F0"
    text_primary = "#0F172A"
    text_secondary = "#64748B"
    inner_card = "#F8FAFC"
    inner_border = "#E2E8F0"
    hero_grad = "linear-gradient(180deg, #000000 0%, #666666 100%)"
    terminal_bg = "#1E293B"
    terminal_text = "#38BDF8"

# ----------------------------------------------------
# 2. Dynamic CSS
# ----------------------------------------------------
st.markdown(f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">

<style>
    .stApp, .stApp p, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp button, .stApp input {{
        font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }}
    .stApp {{
        background-color: {bg_app} !important;
        color: {text_primary} !important;
    }}
    [data-testid="stIconMaterial"],
    [data-testid*="stIcon"],
    [data-testid="stExpanderToggleIcon"],
    [data-testid="stExpander"] summary span:first-child {{
        font-family: "Material Symbols Rounded" !important;
        font-feature-settings: 'liga' 1 !important;
        display: inline-flex !important;
        overflow: hidden !important;
    }}
    .hero-container {{
        max-width: 760px;
        margin: 0 auto 28px auto;
        text-align: center;
    }}
    .hero-badge {{
        display: inline-block;
        padding: 4px 12px;
        background-color: {inner_card};
        border: 1px solid {inner_border};
        border-radius: 9999px;
        font-size: 13px;
        font-weight: 600;
        color: #00D26A;
        margin-bottom: 12px;
    }}
    .hero-title {{
        font-size: 36px;
        font-weight: 700;
        line-height: 1.25;
        background: {hero_grad};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 12px;
    }}
    .hero-desc {{
        font-size: 15px;
        color: {text_secondary};
        line-height: 1.6;
    }}
    .team-card {{
        background-color: {bg_card};
        border: 1px solid {border_card};
        border-radius: 14px;
        padding: 20px;
        height: 100%;
        margin-bottom: 20px;
    }}
    .terminal-box {{
        background-color: {terminal_bg};
        border-radius: 10px;
        padding: 16px;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        color: #E2E8F0;
        line-height: 1.6;
        border: 1px solid #334155;
        max-height: 280px;
        overflow-y: auto;
    }}
    .metric-badge {{
        display: inline-block;
        padding: 6px 12px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 13px;
    }}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 3. Header & Navigation Back
# ----------------------------------------------------
if st.button("⬅️ กลับไปยังหน้าตรวจจับหลัก (Main Dashboard)", key="back_to_main"):
    st.switch_page("app.py")

st.markdown("""
<div class="hero-container">
    <div class="hero-badge">⚔️ RED TEAM VS BLUE TEAM SIMULATOR</div>
    <div class="hero-title">สนามจำลอง: ฝ่ายโจมตี vs ฝ่ายป้องกัน</div>
    <div class="hero-desc">
        เรียนรู้และนำเสนอระบบไซเบอร์ซีเคียวริตี้แบบครบวงจร: จำลองการโจมตี (Red Team) 
        และดูกลไกการสกัดกั้นอัตโนมัติของฝ่ายป้องกัน (Blue Team) บนหน้าจอเดียวกันแบบ Interactive
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 4. Interactive Arena: Red Team vs Blue Team
# ----------------------------------------------------
col_red, col_blue = st.columns(2)

# --- ฝ่ายโจมตี (RED TEAM) ---
with col_red:
    st.markdown("""
    <div class="team-card" style="border-top: 4px solid #EF4444;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
            <h3 style="margin: 0; color: #EF4444; font-size: 20px;">🔴 ฝ่ายโจมตี (Red Team)</h3>
            <span style="background: rgba(239,68,68,0.15); color: #EF4444; padding: 2px 10px; border-radius: 9999px; font-size: 12px; font-weight: 700;">ATTACKER</span>
        </div>
        <p style="font-size: 13px; color: grey; margin-bottom: 16px;">เลือกประเภทและรูปแบบอาวุธที่ใช้ในการโจมตีเซิร์ฟเวอร์เป้าหมาย</p>
    </div>
    """, unsafe_allow_html=True)
    
    attack_type = st.selectbox(
        "เลือกรูปแบบการโจมตี:",
        [
            "💥 Distributed Denial of Service (DDoS)",
            "🔍 Port Scanning (แอบแสกนพอร์ตหาช่องโหว่)",
            "🔑 Brute Force Attack (สุ่มรหัสผ่านรัวๆ)"
        ],
        key="sim_attack_type"
    )
    
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        if "DDoS" in attack_type:
            attack_rate = st.select_slider("ปริมาณทราฟฟิก (Packets/sec):", options=["5,000", "20,000", "100,000 (รุนแรงสุด)"], value="20,000")
            target_port = 80
        elif "Port" in attack_type:
            scan_speed = st.select_slider("ความเร็วในการแสกน:", options=["ช้า (Stealth)", "ปานกลาง (Normal)", "เร็วมาก (Aggressive)"], value="เร็วมาก (Aggressive)")
            target_port = 22
        else:
            attempts = st.select_slider("จำนวนครั้งที่พยายามเดารหัส:", options=["10 ครั้ง", "50 ครั้ง", "500 ครั้ง/นาที"], value="50 ครั้ง")
            target_port = 22
            
    with col_a2:
        attacker_ip = st.text_input("IP ผู้โจมตี (Attacker Source):", value="185.220.101.5", disabled=True)
        target_ip = st.text_input("IP เป้าหมาย (Target Server):", value="192.168.1.10 (Bank Gateway)", disabled=True)

# --- ฝ่ายป้องกัน (BLUE TEAM) ---
with col_blue:
    st.markdown("""
    <div class="team-card" style="border-top: 4px solid #00D26A;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
            <h3 style="margin: 0; color: #00D26A; font-size: 20px;">🛡️ ฝ่ายป้องกัน (Blue Team)</h3>
            <span style="background: rgba(0,210,106,0.15); color: #00D26A; padding: 2px 10px; border-radius: 9999px; font-size: 12px; font-weight: 700;">DEFENDER</span>
        </div>
        <p style="font-size: 13px; color: grey; margin-bottom: 16px;">ระบบป้องกันอัตโนมัติด้วย AI Detection + Active Mitigation</p>
    </div>
    """, unsafe_allow_html=True)
    
    defense_enabled = st.toggle(
        "🛡️ เปิดใช้งานระบบป้องกันอัตโนมัติ (Active Defense Enabled)",
        value=True,
        help="หากเปิดใช้งาน: AI จะวิเคราะห์แพ็กเก็ตและสั่ง Firewall/IPS บล็อกการโจมตีทันที",
        key="toggle_defense_active"
    )
    
    st.markdown("**กลไกการป้องกันที่เตรียมไว้ตามประเภทภัย:**")
    if "DDoS" in attack_type:
        st.info("🔹 **กลยุทธ์ป้องกัน DDoS:** เปิดระบบ **Rate Limiting + SYN Cookie Drop** เพื่อทิ้งทราฟฟิกขยะที่ขอบเครือข่าย ป้องกันไม่ให้แบนด์วิดท์เซิร์ฟเวอร์เต็ม")
    elif "Port" in attack_type:
        st.info("🔹 **กลยุทธ์ป้องกัน PortScan:** เปิดระบบ **Dynamic Blackhole + Honeypot Decoy** ปิดไม่ให้มองเห็นพอร์ตจริง และล่อลวงผู้ไม่หวังดีไปยังพอร์ตกับดัก")
    else:
        st.info("🔹 **กลยุทธ์ป้องกัน Brute Force:** เปิดระบบ **Fail2ban Auto-Block + Step-Up MFA Challenge** สั่งแบน IP ทันทีหลังล็อกอินพลาด 3 ครั้ง พร้อมบังคับยืนยันตัวตน 2 ชั้น")

# ----------------------------------------------------
# 5. ปุ่มเริ่มการจำลอง (Launch Simulation Button)
# ----------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
with btn_col2:
    start_sim = st.button("⚡ ยิงการโจมตีและประเมินผลระบบป้องกัน (Launch Simulation)", type="primary", use_container_width=True)

# ----------------------------------------------------
# 6. ผลลัพธ์การจำลอง (Simulation Output)
# ----------------------------------------------------
if start_sim:
    st.markdown("<hr style='margin: 30px 0;'>", unsafe_allow_html=True)
    
    with st.spinner("กำลังจำลองการส่งข้อมูลเครือข่ายและวิเคราะห์การป้องกัน..."):
        time.sleep(0.8) # จำลองเวลาประมวลผลให้สมจริง
        
    st.markdown("### 📊 ผลลัพธ์สถานการณ์จำลอง (Simulation Results)")
    
    res_col1, res_col2 = st.columns(2)
    
    if not defense_enabled:
        # กรณีปิดระบบป้องกัน (UNPROTECTED)
        with res_col1:
            st.markdown(f"""
            <div style="background-color: rgba(239, 68, 68, 0.1); border: 2px solid #EF4444; border-radius: 12px; padding: 20px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span style="font-size: 18px; font-weight: 700; color: #EF4444;">🚨 เซิร์ฟเวอร์ถูกเจาะ / ล่ม (BREACHED / OVERLOADED)</span>
                    <span class="metric-badge" style="background: #EF4444; color: white;">STATUS: DOWN</span>
                </div>
                <p style="margin-top: 10px; font-size: 14px; color: {text_primary};">
                    เนื่องจาก <b>ปิดระบบป้องกัน</b> การโจมตีทั้งหมดจึงทะลวงเข้าสู่ Core Server โดยตรง ไม่มีเครื่องมือใดคัดกรอง
                </p>
                <ul style="font-size: 13px; color: {text_secondary}; line-height: 1.8;">
                    <li>❌ <b>การโจมตีสำเร็จ:</b> 100% ของแพ็กเก็ตพุ่งชนเซิร์ฟเวอร์</li>
                    <li>❌ <b>ผลกระทบ:</b> ผู้ใช้งานทั่วไปไม่สามารถทำธุรกรรมการเงินได้</li>
                    <li>❌ <b>ความเสียหาย:</b> เกิด Service Downtime และความน่าเชื่อถือลดลงทันที</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Metric Card Server โดนถล่ม
            st.markdown("<br>", unsafe_allow_html=True)
            m1, m2, m3 = st.columns(3)
            m1.metric("Server CPU Load", "98%", "วิกฤต (Overheat)", delta_color="inverse")
            m2.metric("Latency (Ping)", "4,820 ms", "+4,800 ms", delta_color="inverse")
            m3.metric("Blocked Packets", "0 แถว", "-100% ป้องกันไม่ได้", delta_color="inverse")
            
        with res_col2:
            st.markdown("<b>บันทึกเหตุการณ์เซิร์ฟเวอร์ (Server Logs):</b>", unsafe_allow_html=True)
            if "DDoS" in attack_type:
                log_content = f"""[CRITICAL] High volume SYN Flood detected from {attacker_ip}
[WARNING] Bandwidth consumption exceeded 99.4% threshold!
[ERROR] HTTP Connection pool exhausted (Max 10,000 active clients)
[FAILURE] Service NGINX exited with code 137 (Out Of Memory)
[RESULT] Server Unreachable. Customer transactions failed!"""
            elif "Port" in attack_type:
                log_content = f"""[INFO] TCP SYN scan probing port 21 (FTP)... OPEN
[INFO] TCP SYN scan probing port 22 (SSH)... OPEN
[INFO] TCP SYN scan probing port 80 (HTTP)... OPEN
[INFO] TCP SYN scan probing port 3389 (RDP)... OPEN
[ALERT] Attacker {attacker_ip} mapped 14 internal open ports!
[RESULT] Attack surface mapped successfully. Ready for exploit."""
            else:
                log_content = f"""[AUTH] User 'admin' password attempt 1: FAILED
[AUTH] User 'admin' password attempt 2: FAILED
[AUTH] User 'admin' password attempt 3: FAILED
...
[AUTH] User 'admin' password attempt 48: SUCCESS! (Weak password found)
[ALERT] Remote shell session established for {attacker_ip}
[RESULT] Database credentials leaked to external server!"""
            st.markdown(f'<div class="terminal-box">{log_content}</div>', unsafe_allow_html=True)

    else:
        # กรณีเปิดระบบป้องกัน (PROTECTED)
        with res_col1:
            st.markdown(f"""
            <div style="background-color: rgba(0, 210, 106, 0.1); border: 2px solid #00D26A; border-radius: 12px; padding: 20px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span style="font-size: 18px; font-weight: 700; color: #00D26A;">🛡️ สกัดกั้นสำเร็จ 100% (ATTACK NEUTRALIZED)</span>
                    <span class="metric-badge" style="background: #00D26A; color: black;">STATUS: HEALTHY</span>
                </div>
                <p style="margin-top: 10px; font-size: 14px; color: {text_primary};">
                    ระบบป้องกันอัตโนมัติทำงานร่วมกับโมเดล <b>Machine Learning</b> ตรวจจับแพ็กเก็ตผิดปกติและสร้างกฎบล็อกแบบทันที
                </p>
                <ul style="font-size: 13px; color: {text_secondary}; line-height: 1.8;">
                    <li>✅ <b>AI ตรวจจับ:</b> ระบุลักษณะภัยคุกคามได้ภายในเวลา 0.002 วินาที</li>
                    <li>✅ <b>การตอบโต้:</b> ทราฟฟิกของผู้โจมตีถูก Drop ทิ้งที่ระดับ Firewall</li>
                    <li>✅ <b>ความพร้อมใช้งาน:</b> ลูกค้าทั่วไปใช้งานระบบได้ต่อเนื่องตามปกติ (Zero Downtime)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Metric Card Server ปลอดภัย
            st.markdown("<br>", unsafe_allow_html=True)
            m1, m2, m3 = st.columns(3)
            m1.metric("Server CPU Load", "12%", "ปกติเสถียร", delta_color="normal")
            m2.metric("Latency (Ping)", "18 ms", "เร็วปกติ", delta_color="normal")
            m3.metric("Blocked Packets", "99.9%", "+ปลอดภัย", delta_color="normal")
            
        with res_col2:
            st.markdown("<b>บันทึกการตอบโต้ของฝ่ายป้องกัน (Blue Team Incident Response Log):</b>", unsafe_allow_html=True)
            if "DDoS" in attack_type:
                log_content = f"""[AI-INSPECT] Packet anomaly detected on interface eth0 (Source: {attacker_ip})
[AI-CLASSIFY] Match: DDoS Traffic Wave (Confidence: 99.8%)
[DEFENSE-ACTION] Rate limiter triggered: Dropped 49,850 invalid SYN packets
[FIREWALL] Created temporary IP-Drop rule: iptables -A INPUT -s {attacker_ip} -j DROP
[STATUS] Server latency stable at 18ms. 0 dropped legitimate user packets."""
            elif "Port" in attack_type:
                log_content = f"""[AI-INSPECT] Rapid SYN sequence across multiple ports detected from {attacker_ip}
[AI-CLASSIFY] Match: PortScan Reconnaissance (Confidence: 99.9%)
[DEFENSE-ACTION] Activating Stealth Firewall & Honeypot Redirection
[FIREWALL] Sending RST packet to real ports; Diverted {attacker_ip} to Honeypot port 8080
[STATUS] Attacker captured in sandbox container. Real system architecture concealed."""
            else:
                log_content = f"""[AI-INSPECT] Repeated authentication failures for user 'admin' from {attacker_ip}
[AI-CLASSIFY] Match: BruteForce Attack (Confidence: 100.0%)
[DEFENSE-ACTION] Triggered Fail2ban rule: Threshold 3 reached.
[DEFENSE-ACTION] IP {attacker_ip} blacklisted for 24 hours.
[DEFENSE-ACTION] Step-up MFA challenge forced for account 'admin'."""
            st.markdown(f'<div class="terminal-box" style="border-color: #00D26A;">{log_content}</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# 7. พิมพ์เขียววิธีการสร้างระบบป้องกันจริง (Practical Defense Blueprint)
# ----------------------------------------------------
st.markdown("<br><hr style='margin: 30px 0;'>", unsafe_allow_html=True)
st.markdown("""
<div style="background-color: {bg_card}; border: 1px solid {border_card}; border-radius: 14px; padding: 24px;">
    <h3 style="margin-top: 0; color: #00D26A; font-size: 22px;">🛠️ สรุป: วิธีสร้างระบบป้องกันภัยไซเบอร์สำหรับโปรเจกต์ (3 สเต็ปปฏิบัติจริง)</h3>
    <p style="font-size: 14px; color: {text_secondary}; line-height: 1.6;">
        ถ้าต้องนำเสนอใน Mini Project ว่า <b>"เราจะสร้างระบบป้องกันขึ้นมาจริงๆ ได้อย่างไร"</b> 
        คำตอบคือการรวม 3 เลเยอร์นี้เข้าด้วยกัน:
    </p>
</div>
""".format(bg_card=bg_card, border_card=border_card, text_secondary=text_secondary), unsafe_allow_html=True)

step1, step2, step3 = st.columns(3)

with step1:
    st.markdown(f"""
    <div style="background: {inner_card}; border: 1px solid {inner_border}; padding: 18px; border-radius: 12px; height: 100%;">
        <div style="font-weight: 700; color: #00D26A; font-size: 14px; margin-bottom: 6px;">เลเยอร์ที่ 1: ตรวจจับ (Detection)</div>
        <div style="font-weight: 600; color: {text_primary}; margin-bottom: 8px;">ใช้ AI ที่เราฝึกสอนไว้</div>
        <div style="font-size: 13px; color: {text_secondary}; line-height: 1.5;">
            นำโมเดล <code>Random Forest</code> ที่เทรนไว้ มาดักจับค่าเครือข่ายแบบ Real-time เพื่อแยกแยะว่าแพ็กเก็ตที่เข้ามาเป็นคนทั่วไป หรือเป็นผู้ไม่หวังดี
        </div>
    </div>
    """, unsafe_allow_html=True)

with step2:
    st.markdown(f"""
    <div style="background: {inner_card}; border: 1px solid {inner_border}; padding: 18px; border-radius: 12px; height: 100%;">
        <div style="font-weight: 700; color: #00D26A; font-size: 14px; margin-bottom: 6px;">เลเยอร์ที่ 2: ตอบโต้ (Automated Action)</div>
        <div style="font-weight: 600; color: {text_primary}; margin-bottom: 8px;">ส่งคำสั่งไปยัง Firewall / WAF</div>
        <div style="font-size: 13px; color: {text_secondary}; line-height: 1.5;">
            เมื่อ AI ตรวจพบการโจมตี สคริปต์จะสั่งคำสั่งระบบอัตโนมัติทันที เช่น <code>iptables DROP</code>, สั่งแบน IP ผ่าน Fail2ban, หรือเปิด Cloudflare Under Attack Mode
        </div>
    </div>
    """, unsafe_allow_html=True)

with step3:
    st.markdown(f"""
    <div style="background: {inner_card}; border: 1px solid {inner_border}; padding: 18px; border-radius: 12px; height: 100%;">
        <div style="font-weight: 700; color: #00D26A; font-size: 14px; margin-bottom: 6px;">เลเยอร์ที่ 3: บันทึกและแจ้งเตือน (Audit)</div>
        <div style="font-weight: 600; color: {text_primary}; margin-bottom: 8px;">แสดงผลบน Dashboard</div>
        <div style="font-size: 13px; color: {text_secondary}; line-height: 1.5;">
            บันทึก Log ลงในระบบและแจ้งเตือนวิศวกรระบบ (SOC Team) ผ่านหน้าจอแดชบอร์ด เพื่อให้เห็นสถิติภัยคุกคามแบบเรียลไทม์
        </div>
    </div>
    """, unsafe_allow_html=True)

# โค้ดตัวอย่างการเขียนสคริปต์ป้องกันจริง
with st.expander("💻 ดูตัวอย่างโค้ด Python สำหรับสั่ง Firewall ป้องกันอัตโนมัติ (Python Defense Automation Code)"):
    st.code("""# ตัวอย่างโค้ด: เมื่อโมเดล AI ตรวจพบการโจมตี จะสั่ง Firewall บล็อก IP อัตโนมัติทันที
import subprocess

def automated_defense_action(predicted_threat, attacker_ip):
    \"\"\"
    ฟังก์ชันตอบโต้อัตโนมัติ (Automated Incident Response)
    \"\"\"
    if predicted_threat == "Normal":
        print(f"[ALLOW] ทราฟฟิกจาก {attacker_ip} ปลอดภัย อนุญาตให้ผ่านได้")
        return
        
    print(f"[ALERT] ตรวจพบภัยคุกคาม: {predicted_threat} จาก {attacker_ip}!")
    
    if predicted_threat == "DDoS":
        # คำสั่งสกัดกั้น DDoS: บล็อก IP ทันทีที่ระดับ Kernel Firewall
        print(f"[ACTION] รันคำสั่ง: iptables -A INPUT -s {attacker_ip} -j DROP")
        # subprocess.run(["iptables", "-A", "INPUT", "-s", attacker_ip, "-j", "DROP"])
        
    elif predicted_threat == "PortScan":
        # คำสั่งสกัดกั้น PortScan: สั่งซ่อนพอร์ตและปิดการตอบสนอง
        print(f"[ACTION] ปิดการตอบสนองพอร์ต ICMP/TCP RST สำหรับ IP {attacker_ip}")
        
    elif predicted_threat == "BruteForce":
        # คำสั่งสกัดกั้น Brute Force: สั่งบล็อกชั่วคราวและบังคับ MFA
        print(f"[ACTION] รันคำสั่ง Fail2ban: fail2ban-client set sshd banip {attacker_ip}")
        print(f"[ACTION] บังคับเปิดระบบ MFA สำหรับผู้ใช้ที่กำลังล็อกอิน")

# ทดสอบรันฟังก์ชันเมื่อ AI ทำนายผลออกมา
automated_defense_action("DDoS", "185.220.101.5")
""", language="python")

st.markdown("<br><div style='text-align: center; color: grey; font-size: 13px;'>Cyber Threat Detection & Mitigation Mini-Project • Red Team vs Blue Team Arena</div>", unsafe_allow_html=True)

