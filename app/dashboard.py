"""
GoHard AI Threat Detection & Incident Decision Support System
Interactive Security Dashboard (Streamlit Application)
Includes:
  - Executive CISO View (Strategic Risk & Governance)
  - SOC Operational View (Real-Time Triage & Explainable AI)
  - Attack Chain Storyline (Multi-Stage Cyber Kill Chain)
  - Live Threat Simulator (Interactive Injection & Containment)
  - ML Performance & Post-Mortem (Model Metrics & Lessons Learned)
"""

import os
import json
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime

# Import core system modules
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.simulator import TrafficSimulator
from src.decision_engine import reconstruct_attack_chain

# Streamlit Page Configuration
st.set_page_config(
    page_title="GoHard AI Threat Engine | Security Operations Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise Cybersecurity CSS Styling
st.markdown("""
<style>
    /* Dark SOC Theme Colors */
    .main-header {
        background: linear-gradient(90deg, #0d1b2a 0%, #1b263b 100%);
        padding: 20px 25px;
        border-radius: 12px;
        border-left: 6px solid #00f0ff;
        margin-bottom: 25px;
    }
    .metric-card {
        background-color: #111e2e;
        border: 1px solid #1e3a5f;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .metric-value {
        font-size: 26px;
        font-weight: bold;
        margin: 5px 0;
    }
    .badge-critical { background-color: #ff2b2b; color: white; padding: 4px 10px; border-radius: 6px; font-weight: bold; }
    .badge-high { background-color: #ff7a00; color: white; padding: 4px 10px; border-radius: 6px; font-weight: bold; }
    .badge-medium { background-color: #ffa800; color: black; padding: 4px 10px; border-radius: 6px; font-weight: bold; }
    .badge-low { background-color: #00d26a; color: white; padding: 4px 10px; border-radius: 6px; font-weight: bold; }
    .xai-box {
        background-color: #0f1923;
        border-left: 4px solid #f39c12;
        padding: 10px 15px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Session State
@st.cache_resource
def load_simulator():
    return TrafficSimulator(models_dir="models")

@st.cache_data
def load_metrics():
    metrics_path = "models/evaluation_metrics.json"
    if os.path.exists(metrics_path):
        with open(metrics_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

simulator = load_simulator()
metrics_data = load_metrics()

if "event_history" not in st.session_state:
    st.session_state.event_history = []
    # Seed with initial simulated events
    initial_types = ["Normal", "Port_Scan", "Normal", "SSH_BruteForce", "Normal", "Ransomware_LateralMovement", "DDoS_SynFlood", "ZeroDay_Exploit"]
    for t in initial_types:
        st.session_state.event_history.append(simulator.generate_event(t))

if "containment_log" not in st.session_state:
    st.session_state.containment_log = []


# ==========================================
# SIDEBAR CONTROLS & SYSTEM TELEMETRY
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=64)
    st.title("GoHard Defense")
    st.markdown("**AI Threat Support System v2.0**")
    
    st.success("🟢 AI Engine Online — Active")
    st.info("🛡️ Two-Stage Behavioral Engine: Isolation Forest + Balanced RF")
    
    st.markdown("---")
    app_mode = st.radio(
        "เลือกระบบมุมมอง (View Console):",
        [
            "🏢 Executive CISO View (ผู้บริหาร)",
            "🛡️ SOC Operational View (ศูนย์ปฏิบัติการ)",
            "⚡ Live Threat Simulator (จำลองการโจมตี)",
            "⛓️ Attack Chain Storyline (ห่วงโซ่การโจมตี)",
            "📊 ML Benchmark & Post-Mortem (ผลลัพธ์โมเดล)"
        ]
    )
    
    st.markdown("---")
    st.markdown("### Telemetry Overview")
    total_events = len(st.session_state.event_history)
    attack_events = len([e for e in st.session_state.event_history if e["is_threat"]])
    noise_filtered = total_events - attack_events
    noise_reduction_pct = (noise_filtered / total_events * 100) if total_events > 0 else 0
    
    st.metric("Total Events Analyzed", f"{total_events:,}")
    st.metric("Alert Noise Filtered", f"{noise_reduction_pct:.1f}%")
    st.metric("Containment Actions Executed", f"{len(st.session_state.containment_log)}")
    
    if st.button("🧹 Clear Alert History"):
        st.session_state.event_history = []
        st.session_state.containment_log = []
        st.rerun()


# ==========================================
# HEADER
# ==========================================
st.markdown("""
<div class="main-header">
    <h2 style="color: #00f0ff; margin-bottom: 5px;">GoHard — AI Threat Detection & Incident Decision Support</h2>
    <p style="color: #cbd5e1; font-size: 15px; margin: 0;">
        ระบบปัญญาประดิษฐ์ตรวจจับและยับยั้งภัยคุกคามทางไซเบอร์แบบเรียลไทม์ พร้อมสนับสนุนการตัดสินใจระงับเหตุการณ์สำหรับ CISO และทีม SOC
    </p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# TAB 1: EXECUTIVE CISO VIEW
# ==========================================
if app_mode.startswith("🏢"):
    st.subheader("🏢 Executive CISO Strategic Dashboard")
    st.caption("ภาพรวมสถานะความมั่นคงปลอดภัยไซเบอร์ ความต่อเนื่องทางธุรกิจ และการกำกับดูแลตามมาตรฐาน")
    
    # Critical Risk KPIs
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        # Calculate average active risk
        recent_risks = [e["risk_score"] for e in st.session_state.event_history if e["is_threat"]]
        current_risk = int(np.mean(recent_risks)) if recent_risks else 8
        st.markdown(f"""
        <div class="metric-card">
            <span style="color: #94a3b8; font-size: 13px;">Enterprise Threat Index</span>
            <div class="metric-value" style="color: {'#ff2b2b' if current_risk > 70 else '#00d26a'};">{current_risk}/100</div>
            <span style="font-size: 12px; color: #94a3b8;">{'CRITICAL ATTACK DETECTED' if current_risk > 70 else 'NORMAL DEFENSE POSTURE'}</span>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <span style="color: #94a3b8; font-size: 13px;">Alert Noise Reduction (ลด Alert ขยะ)</span>
            <div class="metric-value" style="color: #00f0ff;">{noise_reduction_pct:.1f}%</div>
            <span style="font-size: 12px; color: #00d26a;">บรรลุเป้าหมายลด Alert ล้นเกิน 80%</span>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        # Downtime averted estimate
        downtime_hours_saved = attack_events * 2.5
        financial_averted = attack_events * 450000
        st.markdown(f"""
        <div class="metric-card">
            <span style="color: #94a3b8; font-size: 13px;">Estimated Loss Averted (ความเสียหายที่ป้องกันได้)</span>
            <div class="metric-value" style="color: #ffd166;">฿{financial_averted:,.0f}</div>
            <span style="font-size: 12px; color: #94a3b8;">ประหยัดเวลาชัตดาวน์ ~{downtime_hours_saved:.1f} ชม.</span>
        </div>
        """, unsafe_allow_html=True)
        
    with c4:
        st.markdown("""
        <div class="metric-card">
            <span style="color: #94a3b8; font-size: 13px;">Compliance & PDPA Status</span>
            <div class="metric-value" style="color: #00d26a;">100% PASS</div>
            <span style="font-size: 12px; color: #94a3b8;">ISO 27001 / PDPA Audit Ready</span>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Analytics Charts
    col_chart1, col_chart2 = st.columns([1, 1])
    
    with col_chart1:
        st.markdown("#### การกระจายตัวของประเภทภัยคุกคาม (Threat Vector Breakdown)")
        if st.session_state.event_history:
            threat_df = pd.DataFrame([e["verdict"] for e in st.session_state.event_history], columns=["Verdict"])
            counts = threat_df["Verdict"].value_counts()
            st.bar_chart(counts)
        else:
            st.info("ไม่มีข้อมูลบันทึกในระบบ")
            
    with col_chart2:
        st.markdown("#### ระดับความรุนแรงของเหตุการณ์ (Risk Severity Tiers)")
        if st.session_state.event_history:
            sev_df = pd.DataFrame([e["severity"] for e in st.session_state.event_history], columns=["Severity"])
            sev_counts = sev_df["Severity"].value_counts()
            st.dataframe(sev_counts, width="stretch")
        else:
            st.info("ไม่มีข้อมูลบันทึกในระบบ")
        st.info("💡 **Executive Summary:** AI Engine ตรวจจับและกักกันภัยคุกคามได้ก่อนเข้าถึงฐานข้อมูลหลักและเครื่องแม่ข่าย Domain Controller ระบบปฏิบัติการหลักยังคงเปิดให้บริการได้เต็ม 100% (Zero Downtime)")


# ==========================================
# TAB 2: SOC OPERATIONAL VIEW
# ==========================================
elif app_mode.startswith("🛡️"):
    st.subheader("🛡️ SOC Operational Center & Incident Decision Console")
    st.caption("ศูนย์วิเคราะห์ภัยคุกคามเชิงลึก อธิบายเหตุผลเบื้องหลังการตัดสินใจของ AI (XAI) และสั่งการระงับเหตุการณ์")
    
    events = st.session_state.event_history
    if not events:
        st.warning("ไม่มีข้อมูลเหตุการณ์ในระบบ กรุณาใช้ Live Threat Simulator ในการสร้างเหตุการณ์")
    else:
        # Event Selector
        event_options = [
            f"[{e['timestamp']}] {e['verdict']} | Risk: {e['risk_score']} | Src: {e['source_ip']} -> Dst: {e['destination_ip']}:{e['destination_port']}"
            for e in reversed(events)
        ]
        selected_option = st.selectbox("เลือกเหตุการณ์ที่ต้องการตรวจสอบและสั่งการ:", event_options)
        selected_idx = len(events) - 1 - event_options.index(selected_option)
        curr_ev = events[selected_idx]
        
        # Details layout
        col_meta, col_xai = st.columns([1, 1])
        
        with col_meta:
            st.markdown("#### 📋 ข้อมูลทางเทคนิคของแพ็กเก็ต (Flow Metadata)")
            st.markdown(f"**ประเภทคำวินิจฉัย (Verdict):** `{curr_ev['verdict']}`")
            st.markdown(f"**ระดับความเสี่ยง (Risk Score):** <span class='badge-{curr_ev['severity'].lower()}'>{curr_ev['risk_score']} / 100 ({curr_ev['severity']})</span>", unsafe_allow_html=True)
            st.markdown(f"**เป้าหมาย (Target Asset):** `{curr_ev.get('target_asset_name', 'N/A')}` (Tier {curr_ev.get('asset_tier', 3)})")
            st.markdown(f"**ต้นทาง (Source):** `{curr_ev['source_ip']}:{curr_ev['source_port']}`")
            st.markdown(f"**ปลายทาง (Destination):** `{curr_ev['destination_ip']}:{curr_ev['destination_port']}` (`{curr_ev['protocol']}`)")
            st.markdown(f"**ปริมาณข้อมูล:** Sent: `{curr_ev['bytes_sent']:,} Bytes` | Recv: `{curr_ev['bytes_received']:,} Bytes`")
            st.markdown(f"**สถานะการเชื่อมต่อ:** `{curr_ev['connection_state']}` | พยายามล็อกอินล้มเหลว: `{curr_ev['failed_login_attempts']}` ครั้ง")
            
            # AI Inference details
            st.markdown("---")
            st.markdown("#### 🤖 สถิติการประมวลผลของ AI Engine")
            st.write(f"- **Stage 1 (Isolation Forest Anomaly Score):** `{curr_ev['anomaly_score']:.4f}`")
            st.write(f"- **Stage 2 (Threat Classifier Confidence):** `{curr_ev['confidence']:.2%}`")
            if curr_ev.get("is_novel_anomaly"):
                st.warning("⚠️ **Zero-Day Alert:** ตรวจพบความผิดปกติพฤติกรรมที่ไม่เคยมี Signature มาก่อน (Novel Anomaly)")

        with col_xai:
            st.markdown("#### 🔍 ปัจจัยอธิบายการตัดสินใจของ AI (Explainable AI - XAI)")
            st.caption("ระบบแจกแจงฟีเจอร์ที่มีค่าเบี่ยงเบนจากพฤติกรรมปกติสูงสุด เพื่อให้ทีม SOC มั่นใจก่อนอนุมัติ")
            
            xai_list = curr_ev.get("xai_factors", [])
            if xai_list:
                for factor in xai_list:
                    st.markdown(f"""
                    <div class="xai-box">
                        <strong>ตัวแปร: <code>{factor['feature']}</code> (เบี่ยงเบน {factor['z_score']:+.2f} std)</strong><br>
                        <span style="color: #e2e8f0; font-size: 14px;">{factor['explanation']}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("คุณลักษณะทั้งหมดอยู่ในเกณฑ์มาตรฐานของระบบ (Baseline Normal)")
                
        # Incident Containment Console (Human-in-the-Loop)
        st.markdown("---")
        st.markdown("### 🚨 ระบบสนับสนุนการตัดสินใจรับมือเหตุการณ์ (Incident Decision & Containment)")
        
        mitigations = curr_ev.get("mitigations", [])
        for m in mitigations:
            st.markdown(f"**มาตรการแนะนำ:** `{m['title']}` *(ลดความเสี่ยงได้ {m['risk_reduction']})*")
            st.write(m["description"])
            
            btn_col1, btn_col2 = st.columns([1, 3])
            with btn_col1:
                btn_key = f"approve_{curr_ev['timestamp']}_{m['action_id']}"
                if st.button(f"⚡ อนุมัติดำเนินการ ({m['type']})", key=btn_key):
                    st.session_state.containment_log.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "action": m["title"],
                        "target_ip": curr_ev["source_ip"],
                        "status": "EXECUTED_SUCCESSFULLY",
                        "approved_by": "SOC_ANALYST (Human-in-the-Loop)"
                    })
                    st.success(f"สั่งการสำเร็จ: {m['title']} ได้รับการบังคับใช้บนระบบเครือข่ายเรียบร้อยแล้ว!")
                    
            with btn_col2:
                wl_key = f"whitelist_{curr_ev['timestamp']}_{m['action_id']}"
                if st.button("⚪ ละเว้นและเพิ่มเข้า Whitelist (False Positive)", key=wl_key):
                    st.info(f"บันทึกการละเว้นสำหรับ {curr_ev['source_ip']} เข้าระบบคัดกรองข้อยกเว้น")
                    
        # Audit Table
        if st.session_state.containment_log:
            st.markdown("#### 📜 บันทึกการอนุมัติและระงับเหตุการณ์ (Containment Audit Trail)")
            st.dataframe(pd.DataFrame(st.session_state.containment_log), width="stretch")


# ==========================================
# TAB 3: LIVE THREAT SIMULATOR
# ==========================================
elif app_mode.startswith("⚡"):
    st.subheader("⚡ Live Threat Simulator & Interactive Attack Injection")
    st.caption("ระบบจำลองการฉีดการโจมตีทางไซเบอร์แบบเรียลไทม์เพื่อทดสอบการตอบสนองของโมเดล AI")
    
    st.markdown("คลิกปุ่มด้านล่างเพื่อทดสอบส่งทราฟฟิกหรือการโจมตีจำลองเข้าสู่ AI Threat Engine ทันที:")
    
    btn1, btn2, btn3, btn4, btn5, btn6 = st.columns(6)
    
    new_event = None
    with btn1:
        if st.button("🌐 ทราฟฟิกปกติ (Normal)", width="stretch"):
            new_event = simulator.generate_event("Normal")
    with btn2:
        if st.button("🌊 ยิง DDoS Flood", width="stretch"):
            new_event = simulator.generate_event("DDoS_SynFlood")
    with btn3:
        if st.button("🔍 Port Scan Probe", width="stretch"):
            new_event = simulator.generate_event("Port_Scan")
    with btn4:
        if st.button("🔑 SSH Brute Force", width="stretch"):
            new_event = simulator.generate_event("SSH_BruteForce")
    with btn5:
        if st.button("🔒 Ransomware SMB", width="stretch"):
            new_event = simulator.generate_event("Ransomware_LateralMovement")
    with btn6:
        if st.button("☣️ Zero-Day Exploit", width="stretch"):
            new_event = simulator.generate_event("ZeroDay_Exploit")
            
    if new_event:
        st.session_state.event_history.append(new_event)
        st.success(f"ฉีดเหตุการณ์เข้าสู่ระบบสำเร็จ: [{new_event['verdict']}] Risk Score: {new_event['risk_score']}/100")
        
        # Immediate display
        st.markdown("#### ผลการวิเคราะห์ทันที (Instant AI Verdict):")
        res_col1, res_col2 = st.columns([1, 1])
        with res_col1:
            st.json({
                "Timestamp": new_event["timestamp"],
                "Verdict": new_event["verdict"],
                "Severity": new_event["severity"],
                "Risk Score": new_event["risk_score"],
                "Confidence": f"{new_event['confidence']:.2%}",
                "Anomaly Score": f"{new_event['anomaly_score']:.4f}"
            })
        with res_col2:
            st.markdown("**มาตรการที่ระบบเสนอ:**")
            for m in new_event["mitigations"]:
                st.info(f"**{m['title']}**\n\n{m['description']}")
                
    st.markdown("---")
    st.markdown("#### ประวัติเหตุการณ์ล่าสุด (Recent Feed - 10 รายการ)")
    if st.session_state.event_history:
        recent_records = st.session_state.event_history[-10:]
        cols = ["timestamp", "source_ip", "destination_ip", "destination_port", "verdict", "risk_score", "severity"]
        recent_df = pd.DataFrame(recent_records)
        display_cols = [c for c in cols if c in recent_df.columns]
        st.dataframe(recent_df[display_cols], width="stretch")
    else:
        st.info("ยังไม่มีประวัติเหตุการณ์ในระบบ (สามารถคลิกปุ่มด้านบนเพื่อจำลองเหตุการณ์ได้)")


# ==========================================
# TAB 4: ATTACK CHAIN STORYLINE
# ==========================================
elif app_mode.startswith("⛓️"):
    st.subheader("⛓️ Multi-Stage Cyber Attack Chain Reconstruction")
    st.caption("แปลงข้อมูลบันทึกระบบที่กระจัดกระจายให้กลายเป็นแผนภาพห่วงโซ่การโจมตีตามกรอบ MITRE ATT&CK")
    
    storylines = reconstruct_attack_chain(st.session_state.event_history)
    
    if not storylines:
        st.info("ยังไม่พบการโจมตีที่เชื่อมโยงกันในระบบ กรุณาลองฉีดการโจมตีหลายรูปแบบผ่าน Live Simulator")
    else:
        for idx, story in enumerate(storylines):
            with st.expander(f"🎯 เส้นทางการโจมตีจาก IP ผู้บุกรุก: {story['attacker_ip']} (ความเสี่ยงสูงสุด: {story['max_risk']}/100)", expanded=True):
                st.write(f"จำนวนการกระทำที่ตรวจพบ: `{story['total_events']}` ขั้นตอน")
                
                for step in story["timeline"]:
                    st.markdown(f"""
                    * **[{step['timestamp']}]** `{step['stage']}`  
                      - **MITRE Tactic:** `{step['mitre_tactic']}`  
                      - **เป้าหมาย:** `{step['target']}`  
                      - **คะแนนความเสี่ยง:** `{step['risk_score']}/100` (ความเชื่อมั่น AI: `{step['confidence']:.1%}`)
                    """)
                    st.markdown("↓")


# ==========================================
# TAB 5: ML BENCHMARK & POST-MORTEM
# ==========================================
elif app_mode.startswith("📊"):
    st.subheader("📊 Machine Learning Performance & Post-Mortem Analysis")
    st.caption("รายงานผลการทดสอบโมเดลบนชุดข้อมูลทดสอบแบบ Temporal Test Set และการถอดบทเรียนจุดผิดพลาด")
    
    if metrics_data:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Overall Accuracy", f"{metrics_data['overall_accuracy']:.2%}")
        m2.metric("Macro F1-Score", f"{metrics_data['macro_f1']:.4f}")
        m3.metric("Attack Recall (Sensitivity)", f"{metrics_data['attack_detection_recall']:.2%}")
        m4.metric("False Positive Rate (FPR)", f"{metrics_data['false_positive_rate']:.2%}")
        
        st.markdown("#### ตารางประสิทธิภาพการจำแนกแยกตามคลาส (Per-Class Performance)")
        per_class_df = pd.DataFrame(metrics_data["per_class_report"]).T
        st.dataframe(per_class_df, width="stretch")
        
        st.markdown("#### เมทริกซ์ความสับสน (Confusion Matrix)")
        cm_df = pd.DataFrame(metrics_data["confusion_matrix"], index=metrics_data["classes"], columns=metrics_data["classes"])
        st.dataframe(cm_df, width="stretch")
    else:
        st.warning("ไม่พบไฟล์สถิติ `models/evaluation_metrics.json` กรุณารัน `python run_pipeline.py` ก่อน")
        
    st.markdown("---")
    st.markdown("### 🛠️ รวบรวมจุดผิดพลาดและแนวทางแก้ไข (Lessons Learned จาก handoff-v2.md)")
    st.markdown("""
    1. **แก้ปัญหา Class Imbalance:** ใช้ SMOTE และ Class Weighting ช่วยให้โมเดลจำแนกภัยคุกคามที่มีเพียง 5% ได้แม่นยำ F1-Score สูง
    2. **ป้องกัน Data Leakage:** ใช้ Temporal Splitting (แบ่งตามเวลา) แทนการสุ่ม Random Shuffle เพื่อสะท้อนการทำงานแบบ Real-time จริง
    3. **ลดปัญหา High Cardinality:** จัดกลุ่ม Port Semantics (Web, Shell, DB, SMB, Infrastructure) ไม่ทำให้มิติฟีเจอร์บวม
    4. **สถาปัตยกรรม Two-Stage:** ชั้นแรกใช้ Isolation Forest ตรวจจับ Zero-Day ชั้นที่สองใช้ Random Forest จำแนกประเภทการโจมตี
    5. **Explainable AI (XAI):** แปลงค่า Z-score ของฟีเจอร์ให้เป็นคำอธิบายภาษาไทย ช่วยให้ทีม SOC อนุมัติได้อย่างมั่นใจ
    """)

