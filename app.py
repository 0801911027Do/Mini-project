"""
แอปพลิเคชัน Streamlit แบบง่าย สำหรับมินิโปรเจกต์ Machine Learning
โค้ดสั้น เข้าใจง่าย อธิบายให้อาจารย์ฟังได้สบายๆ
"""

import streamlit as st
import pandas as pd
import joblib
import os

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ML Mini-Project: Cyber Threat Detection", page_icon="🛡️")

st.title("🛡️ ระบบตรวจจับภัยคุกคามไซเบอร์ (ML Mini-Project)")
st.write("มินิโปรเจกต์จำแนกพฤติกรรมและการโจมตีบนเครือข่ายด้วย Machine Learning (Random Forest)")

# 2. โหลดโมเดลที่เทรนไว้
@st.cache_resource
def load_model():
    if os.path.exists("model.pkl"):
        return joblib.load("model.pkl")
    return None

model = load_model()

if model is None:
    st.error("ไม่พบไฟล์ model.pkl กรุณารันคำสั่ง `python train.py` เพื่อฝึกสอนโมเดลก่อน")
    st.stop()

# 3. เมนูเลือกตัวอย่างข้อมูลจำลอง (Presets)
st.subheader("1. ป้อนข้อมูลเพื่อทดสอบการทำนาย")

preset = st.selectbox(
    "เลือกชุดข้อมูลตัวอย่างอย่างรวดเร็ว (หรือปรับแก้ตัวเลขเองด้านล่าง):",
    [
        "ทราฟฟิกปกติ (Normal Web Traffic)",
        "การโจมตี DDoS (ส่งแพ็กเก็ตขยะจำนวนมาก)",
        "การกวาดสแกนพอร์ต (Port Scan)",
        "การสุ่มรหัสผ่าน (SSH Brute Force)"
    ]
)

# กำหนดค่าเริ่มต้นตาม preset ที่เลือก
if preset == "ทราฟฟิกปกติ (Normal Web Traffic)":
    init_dur, init_pkts, init_bytes, init_logins, init_port = 2.5, 45, 18000, 0, 443
elif preset == "การโจมตี DDoS (ส่งแพ็กเก็ตขยะจำนวนมาก)":
    init_dur, init_pkts, init_bytes, init_logins, init_port = 0.05, 1800, 72000, 0, 80
elif preset == "การกวาดสแกนพอร์ต (Port Scan)":
    init_dur, init_pkts, init_bytes, init_logins, init_port = 0.02, 1, 44, 0, 8080
else: # SSH Brute Force
    init_dur, init_pkts, init_bytes, init_logins, init_port = 8.5, 80, 12000, 18, 22

# ช่องกรอกข้อมูล 2 คอลัมน์
col1, col2 = st.columns(2)
with col1:
    duration = st.number_input("ระยะเวลาเชื่อมต่อ (duration ในวินาที):", min_value=0.0, value=float(init_dur), step=0.1)
    packets = st.number_input("จำนวนแพ็กเก็ต (packets):", min_value=1, value=int(init_pkts), step=10)
    bytes_data = st.number_input("ขนาดข้อมูลรวม (bytes):", min_value=1, value=int(init_bytes), step=500)

with col2:
    failed_logins = st.number_input("จำนวนครั้งที่ล็อกอินผิดพลาด (failed_logins):", min_value=0, value=int(init_logins), step=1)
    port = st.number_input("พอร์ตปลายทาง (destination port):", min_value=1, max_value=65535, value=int(init_port), step=1)

# 4. ปุ่มทำนายผล
st.write("")
if st.button("🔍 ตรวจสอบภัยคุกคาม (Predict)", type="primary"):
    # นำข้อมูลที่ผู้ใช้กรอกมาสร้างเป็น DataFrame
    input_df = pd.DataFrame([{
        "duration": duration,
        "packets": packets,
        "bytes": bytes_data,
        "failed_logins": failed_logins,
        "port": port
    }])

    # ทำนายผลด้วยโมเดล
    prediction = model.predict(input_df)[0]
    probabilities = model.predict_proba(input_df)[0]
    classes = model.classes_

    st.subheader("2. ผลการวิเคราะห์จากโมเดล AI")

    # แสดงผลลัพธ์แยกตามประเภท
    if prediction == "Normal":
        st.success(f"🟢 **ผลลัพธ์: ทราฟฟิกปกติ (Normal Traffic)**")
        st.info("คำแนะนำ: ไม่พบพฤติกรรมน่าสงสัย การเชื่อมต่อปลอดภัย")
    elif prediction == "DDoS":
        st.error(f"🔴 **ผลลัพธ์: ตรวจพบการโจมตีแบบ DDoS (Distributed Denial of Service)**")
        st.warning("คำแนะนำ: มีแพ็กเก็ตพุ่งสูงผิดปกติ ควรเปิด Rate-Limiting หรือบล็อก IP ต้นทาง")
    elif prediction == "PortScan":
        st.warning(f"🟠 **ผลลัพธ์: ตรวจพบการกวาดสแกนพอร์ต (Port Scan)**")
        st.info("คำแนะนำ: ตรวจสอบพอร์ตที่เปิดทิ้งไว้ และปิดบริการที่ไม่จำเป็น")
    elif prediction == "BruteForce":
        st.error(f"🔴 **ผลลัพธ์: ตรวจพบการพยายามสุ่มรหัสผ่าน (Brute Force Attack)**")
        st.warning("คำแนะนำ: พบล็อกอินผิดหลายครั้ง ควรระงับบัญชีชั่วคราวและบังคับใช้รหัสผ่านที่ซับซ้อน")

    # แสดงค่าความน่าจะเป็น (Probability) ในแต่ละคลาส
    st.write("---")
    st.write("**ความมั่นใจของโมเดล (Prediction Confidence):**")
    prob_df = pd.DataFrame({
        "ประเภท": classes,
        "ความน่าจะเป็น (%)": [round(p * 100, 2) for p in probabilities]
    }).sort_values(by="ความน่าจะเป็น (%)", ascending=False)
    
    st.dataframe(prob_df, hide_index=True)

# 5. ข้อมูลสรุปของ Dataset
st.write("---")
with st.expander("📊 ดูข้อมูลตัวอย่างในชุดข้อมูล (Dataset Overview)"):
    if os.path.exists("data.csv"):
        sample_df = pd.read_csv("data.csv")
        st.write("ตัวอย่างข้อมูล 5 แถวแรก:")
        st.dataframe(sample_df.head(), hide_index=True)
        st.write("สัดส่วนข้อมูลแต่ละประเภทในชุดฝึกสอน:")
        st.bar_chart(sample_df["label"].value_counts())
