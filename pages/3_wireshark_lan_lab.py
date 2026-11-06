"""
หน้าแล็บจำลอง: การต่อ Notebook 3 เครื่องในวง LAN/Hotspot เดียวกัน,
ดักจับด้วย Wireshark (Display Filter & I/O Graph),
แปลง Log เป็น Feature Vector (Time Window) และวัดผล Imbalanced Data
"""

import os
import json
import joblib
import pandas as pd
import altair as alt
import streamlit as st

st.set_page_config(
    page_title="Wireshark 3-Notebook Lab & Imbalanced ML | บริษัท GoHard",
    page_icon="🦈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

is_dark = st.session_state.get("is_dark", True)

if is_dark:
    bg_app = "#121212"
    bg_card = "#1E1E1E"
    border_card = "#2D2D2D"
    text_primary = "#FFFFFF"
    text_secondary = "#9E9E9E"
    inner_card = "#161616"
    inner_border = "#2A2A2A"
else:
    bg_app = "#F8FAFC"
    bg_card = "#FFFFFF"
    border_card = "#E2E8F0"
    text_primary = "#0F172A"
    text_secondary = "#64748B"
    inner_card = "#F8FAFC"
    inner_border = "#E2E8F0"

st.markdown(f"""
<style>
    .stApp {{
        background-color: {bg_app} !important;
        color: {text_primary} !important;
    }}
    .lab-card {{
        background-color: {bg_card};
        border: 1px solid {border_card};
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 20px;
    }}
    .lab-badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        background: rgba(56, 189, 248, 0.15);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.35);
        margin-bottom: 8px;
    }}
    .topo-box {{
        background-color: {inner_card};
        border: 1px solid {inner_border};
        border-radius: 10px;
        padding: 16px;
        height: 100%;
    }}
    .ws-filter-bar {{
        background-color: #1B2A1E;
        border: 1px solid #00D26A;
        border-radius: 8px;
        padding: 10px 14px;
        font-family: monospace;
        color: #00D26A;
        margin-bottom: 12px;
    }}
</style>
""", unsafe_allow_html=True)

# แถบนำทางกลับหน้าหลัก
nav1, nav2, nav3 = st.columns([1, 1, 1])
with nav1:
    st.page_link("app.py", label="⬅️ กลับหน้าหลัก (Main Dashboard)", icon="🏠")
with nav2:
    st.page_link("pages/2_red_vs_blue.py", label="⚔️ สนามจำลอง Red vs Blue Team", icon="⚔️")
with nav3:
    st.page_link("pages/1_why_defense.py", label="🛡️ เหตุผลที่สร้างโปรเจกต์นี้", icon="🛡️")

st.markdown("""
<div class="lab-card">
    <div class="lab-badge">🦈 WIRESHARK 3-NOTEBOOK LAN LAB — FROM PACKET CAPTURE TO IMBALANCED ML</div>
    <h2 style="margin: 4px 0 8px 0;">การทดลองจริงด้วย Notebook 3 เครื่อง + ดักจับด้วย Wireshark + แปลง Feature Vector</h2>
    <p style="margin: 0; opacity: 0.85;">
        คู่มือปฏิบัติการพร้อมระบบจำลองผลลัพธ์จาก Wireshark (Display Filter &amp; Statistics I/O Graph)
        ไปจนถึงการแปลงเป็น Time Window 1 วินาที และการวัดผลโมเดลบนข้อมูลไม่สมดุล (Imbalanced Data)
    </p>
</div>
""", unsafe_allow_html=True)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB_DIR = os.path.join(ROOT_DIR, "lan_lab")
RAW_CSV = os.path.join(LAB_DIR, "raw_packets.csv")
GT_CSV = os.path.join(LAB_DIR, "attack_ground_truth.csv")
WIN_CSV = os.path.join(LAB_DIR, "window_inspection_with_time.csv")
FEAT_CSV = os.path.join(LAB_DIR, "ddos_feature_vectors.csv")
METRICS_JSON = os.path.join(LAB_DIR, "imbalanced_metrics.json")
MODEL_PKL = os.path.join(LAB_DIR, "ddos_window_model.pkl")

# ----------------------------------------------------
# ขั้นตอนที่ 1: โครงสร้างการทดลองจริงด้วย Notebook 3 เครื่อง
# ----------------------------------------------------
st.markdown("### 1. การตั้งค่า Notebook 3 เครื่องในกลุ่ม (เชื่อมต่อ Wi-Fi / Mobile Hotspot เดียวกัน)")
st.caption("ขั้นตอนที่ 1: เปิด CMD พิมพ์ `ipconfig` บนทั้ง 3 เครื่องเพื่อดูเลข IPv4 แล้วรันคำสั่งตามบทบาทดังนี้")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
    <div class="topo-box" style="border-left: 4px solid #38BDF8;">
        <h4 style="margin-top:0; color:#38BDF8;">🖥️ เครื่องที่ 1: เป้าหมาย (Victim / Web Server)</h4>
        <p><b>IP สมมติ:</b> <code>192.168.1.10</code> (พอร์ต <code>8000</code>)</p>
        <p style="font-size:14px;"><b>หน้าที่:</b> เปิดเว็บจำลองรอรับทราฟฟิก และเปิดโปรแกรม <b>Wireshark</b> (กดปุ่มฉลามสีฟ้า) ดักจับแพ็กเกจตลอดเวลา</p>
    </div>
    """, unsafe_allow_html=True)
    st.code("python lan_lab/machine1_victim_server.py --port 8000", language="bash")

with c2:
    st.markdown("""
    <div class="topo-box" style="border-left: 4px solid #EF4444;">
        <h4 style="margin-top:0; color:#EF4444;">⚡ เครื่องที่ 2: ผู้โจมตี (Attacker — เพื่อนตัวแสบ)</h4>
        <p><b>IP สมมติ:</b> <code>192.168.1.20</code></p>
        <p style="font-size:14px;"><b>หน้าที่:</b> ยิง Request ถล่มเครื่องที่ 1 รัวๆ เป็นรอบๆ พร้อมบันทึก Timestamp เริ่ม-จบลงไฟล์เฉลยอัตโนมัติ</p>
    </div>
    """, unsafe_allow_html=True)
    st.code("python lan_lab/machine3_attacker_ddos.py --target 192.168.1.10 --port 8000", language="bash")

with c3:
    st.markdown("""
    <div class="topo-box" style="border-left: 4px solid #00D26A;">
        <h4 style="margin-top:0; color:#00D26A;">💻 เครื่องที่ 3: ผู้ใช้งานปกติ (Normal User)</h4>
        <p><b>IP สมมติ:</b> <code>192.168.1.30</code></p>
        <p style="font-size:14px;"><b>หน้าที่:</b> เปิดเข้าหน้าเว็บเครื่องที่ 1 ทุกๆ 1-3 วินาที เพื่อให้ใน Wireshark มีทราฟฟิกคนปกติปะปนกับผู้โจมตี</p>
    </div>
    """, unsafe_allow_html=True)
    st.code("python lan_lab/machine2_normal_traffic.py --target 192.168.1.10 --port 8000", language="bash")

st.write("")

# ----------------------------------------------------
# ขั้นตอนที่ 2: จำลองหน้าจอ Wireshark (Display Filter & Statistics -> IO Graph)
# ----------------------------------------------------
st.markdown("### 2. สิ่งที่เห็นในโปรแกรม Wireshark บนเครื่องที่ 1 (Display Filter & I/O Graph)")

if os.path.exists(RAW_CSV) and os.path.exists(WIN_CSV):
    df_raw = pd.read_csv(RAW_CSV, nrows=5000)
    df_win = pd.read_csv(WIN_CSV)

    st.markdown("#### 🔍 ทดลองใช้ Display Filter ของ Wireshark เพื่อกรองดูว่าใครยิงใคร")
    filter_choice = st.radio(
        "เลือกคำสั่ง Display Filter ด้านบนของ Wireshark:",
        [
            "แสดงแพ็กเกจทั้งหมด (ไม่ใส่ Filter)",
            "ip.src == 192.168.1.20  (ดูเฉพาะตอนเพื่อนเครื่องที่ 2 Attacker ยิงถล่มเข้ามา)",
            "ip.src == 192.168.1.30  (ดูเฉพาะตอนเพื่อนเครื่องที่ 3 Normal User ใช้งานปกติ)",
            "tcp.flags.syn == 1      (ดูเฉพาะแพ็กเกจขอเชื่อมต่อ TCP SYN Flood)",
        ],
    )

    if "192.168.1.20" in filter_choice:
        filtered_df = df_raw[df_raw["ip.src"] == "192.168.1.20"]
        active_expr = "ip.src == 192.168.1.20"
    elif "192.168.1.30" in filter_choice:
        filtered_df = df_raw[df_raw["ip.src"] == "192.168.1.30"]
        active_expr = "ip.src == 192.168.1.30"
    elif "tcp.flags.syn" in filter_choice:
        filtered_df = df_raw[df_raw["tcp.flags.syn"] == 1]
        active_expr = "tcp.flags.syn == 1"
    else:
        filtered_df = df_raw
        active_expr = "/* No Display Filter Applied — Showing All Packets */"

    st.markdown(f'<div class="ws-filter-bar">🦈 Wireshark Display Filter: <b>{active_expr}</b> &nbsp;|&nbsp; พบ {len(filtered_df):,} แพ็กเกจ (ในตัวอย่าง 5,000 แรก)</div>', unsafe_allow_html=True)
    st.dataframe(filtered_df.head(12), use_container_width=True, hide_index=True)

    st.markdown("#### 📈 เมนู `Statistics -> I/O Graph` ใน Wireshark (กราฟจำนวนแพ็กเกจต่อวินาที)")
    st.markdown("""
    เมื่อเปิดเมนู **Statistics &rarr; I/O Graph** ใน Wireshark จะเห็นชัดเจนว่า:
    - **ช่วงปกติ (สีเขียว):** แพ็กเกจวิ่งระดับต่ำสม่ำเสมอ (~5 - 25 Packets/Sec)
    - **ช่วงโดนเพื่อนยิงถล่ม (สีแดง):** กราฟกระโดดพุ่งขึ้นเป็นภูเขาชันทันที (150 - 350+ Packets/Sec)
    """)

    df_win["second_index"] = df_win["window_id"] - df_win["window_id"].min()
    df_win["สถานะใน_Wireshark"] = df_win["label"].map({
        0: "ช่วงปกติ (Normal Background Traffic)",
        1: "ช่วงถูกเพื่อนยิงโจมตี (Attack Window — กราฟพุ่งเป็นภูเขา)",
    })

    io_chart = (
        alt.Chart(df_win)
        .mark_area(opacity=0.75, line=True)
        .encode(
            x=alt.X("second_index:Q", title="เวลาใน Wireshark I/O Graph (วินาทีที่ 0 - 1,200)"),
            y=alt.Y("packet_count:Q", title="Packets / Second (จำนวนแพ็กเกจต่อวินาที)"),
            color=alt.Color(
                "สถานะใน_Wireshark:N",
                scale=alt.Scale(
                    domain=[
                        "ช่วงปกติ (Normal Background Traffic)",
                        "ช่วงถูกเพื่อนยิงโจมตี (Attack Window — กราฟพุ่งเป็นภูเขา)",
                    ],
                    range=["#00D26A", "#EF4444"],
                ),
            ),
            tooltip=["second_index", "packet_count", "total_bytes", "syn_ratio", "mean_iat", "สถานะใน_Wireshark"],
        )
        .properties(height=280)
    )
    st.altair_chart(io_chart, use_container_width=True)

# ----------------------------------------------------
# ขั้นตอนที่ 3: การแปลง Log จาก Wireshark เป็น Feature Vector & ทำเฉลย
# ----------------------------------------------------
st.markdown("### 3. การแปลงไฟล์จาก Wireshark เป็น Feature Vector (Time Window 1 วินาที) และการติดเฉลย")

if os.path.exists(GT_CSV) and os.path.exists(FEAT_CSV):
    df_gt = pd.read_csv(GT_CSV)
    df_feat = pd.read_csv(FEAT_CSV)

    col_l, col_r = st.columns([1, 1.3])
    with col_l:
        st.markdown("**🎯 ตารางเวลาที่เครื่องที่ 2 กดยิง (`attack_ground_truth.csv`)**")
        st.dataframe(df_gt, use_container_width=True, hide_index=True)
        st.info("""
        **ทำไมต้องตัด `ip.src`, `ip.dst`, `window_id` ออกก่อนเทรนโมเดล?**
        เพราะถ้าใส่เลข IP `192.168.1.20` ของเพื่อนเข้าไป โมเดลจะจำแค่เลข IP เพื่อน (Data Leakage) พอเปลี่ยนเครื่องยิงใหม่โมเดลจะจับไม่ได้เลย! จึงต้องยุบรวมเป็นสถิติราย 1 วินาทีแทน
        """)

    with col_r:
        st.markdown("**🧮 ตาราง Feature Vector หลังยุบรวมทุกๆ 1 วินาที (`ddos_feature_vectors.csv`)**")
        t1, t2 = st.tabs(["🔴 ช่วงเวลาที่เพื่อนยิงโจมตี (Label = 1)", "🟢 ช่วงเวลาใช้งานปกติ (Label = 0)"])
        with t1:
            st.dataframe(df_feat[df_feat["label"] == 1].head(6), use_container_width=True, hide_index=True)
        with t2:
            st.dataframe(df_feat[df_feat["label"] == 0].head(6), use_container_width=True, hide_index=True)

# ----------------------------------------------------
# ขั้นตอนที่ 4: การวัดผล Imbalanced Data (ตามที่อาจารย์เน้น)
# ----------------------------------------------------
st.markdown("### 4. การจัดการ Imbalanced Data และทำไมห้ามใช้แค่ Accuracy วัดผล")

if os.path.exists(METRICS_JSON):
    with open(METRICS_JSON, "r", encoding="utf-8") as f:
        metrics_data = json.load(f)

    ds = metrics_data["dataset_summary"]
    models_comp = metrics_data["models_comparison"]
    feat_imp = pd.DataFrame(metrics_data["feature_importances"])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("จำนวน Time Windows ทั้งหมด", f"{ds['total_windows']:,} วินาที")
    m2.metric("ช่วงเวลาปกติ (Normal = 0)", f"{ds['normal_windows']:,} วินาที ({ds['imbalance_ratio_normal_pct']}%)")
    m3.metric("ช่วงถูกโจมตี (Attack = 1)", f"{ds['attack_windows']:,} วินาที ({ds['imbalance_ratio_attack_pct']}%)")
    m4.metric("ชุดทดสอบ (Test Set 25%)", f"{ds['test_size']} วินาที (มี Attack 21 วินาที)")

    rows = []
    for m in models_comp:
        cm = m["confusion_matrix"]
        rows.append({
            "โมเดลที่ใช้เปรียบเทียบ": m["model_name"],
            "Accuracy": f"{m['accuracy']:.2%}",
            "Detection Rate (Recall)": f"{m['recall_detection_rate']:.2%}",
            "Precision": f"{m['precision']:.2%}",
            "F1-Score": f"{m['f1_score']:.2%}",
            "PR-AUC": f"{m['pr_auc']:.4f}",
            "จับ DDoS สำเร็จ (TP)": f"{cm['tp']} / {cm['tp'] + cm['fn']} วินาที",
            "หลุดรอด (FN)": f"{cm['fn']} วินาที",
            "เตือนผิดพลาด (FP)": f"{cm['fp']} วินาที",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    col_imp, col_note = st.columns([1.1, 1])
    with col_imp:
        st.markdown("**📊 ความสำคัญของฟีเจอร์ในการจับ DDoS (Feature Importance)**")
        imp_chart = (
            alt.Chart(feat_imp)
            .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4, color="#38BDF8")
            .encode(
                x=alt.X("importance:Q", title="ความสำคัญต่อการตัดสินใจของโมเดล"),
                y=alt.Y("feature:N", sort="-x", title="Feature Vector"),
                tooltip=["feature", "importance"],
            )
            .properties(height=260)
        )
        st.altair_chart(imp_chart, use_container_width=True)

    with col_note:
        st.markdown("**📌 สรุปคำตอบสำหรับอธิบายอาจารย์ตอนพรีเซนต์**")
        st.markdown("""
        1. **จาก Log กลายเป็นตัวเลขเข้า ML ได้อย่างไร?**
           - ดึงข้อมูลดิบจาก Wireshark (`tshark`) แล้วหั่นเป็นหน้าต่างเวลาละ 1 วินาที (Time Window) คำนวณค่าสถิติ เช่น `packet_count`, `mean_iat`, `syn_ratio`, `std_packet_len`
        2. **ทำเฉลย (Ground Truth Label) อย่างไร?**
           - ซิงค์นาฬิกาทั้ง 3 เครื่องให้ตรงกัน เมื่อเครื่องที่ 2 เริ่มยิงจะบันทึก Timestamp เริ่ม-จบ แล้วนำมาทาบกับ `window_id` เพื่อติดป้าย `1 = Attack`, `0 = Normal`
        3. **ทำไมต้องระวัง Imbalanced Data?**
           - ช่วงปกติมีถึง 93% ช่วงโจมตีมีแค่ 7% ถ้าดูแต่ Accuracy โมเดลที่ทายว่าปกติทั้งหมดจะได้ 93% ทันทีแต่จับโจรไม่ได้เลย (`Recall = 0%`) จึงต้องใช้ **Balanced Random Forest (`class_weight='balanced'`)** และวัดผลด้วย **Detection Rate (Recall), Precision, F1-Score และ PR-AUC**
        """)
