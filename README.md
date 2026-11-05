# GoHard — ระบบ AI ตรวจจับภัยคุกคามไซเบอร์และสนับสนุนการตัดสินใจรับมือเหตุการณ์
### AI-Powered Cyber Threat Detection & Incident Decision Support System (v2.0)

<p align="center">
  <img src="https://img.shields.io/badge/PYTHON-3.10%20%7C%203.11%20%7C%203.14-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/STREAMLIT-1.66%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/SCIKIT--LEARN-1.4%2B-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" alt="Scikit-Learn" />
  <img src="https://img.shields.io/badge/PANDAS-2.0%2B-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas" />
</p>
<p align="center">
  <img src="https://img.shields.io/badge/AI%20ENGINE-ISOFOREST%20%2B%20RF-008080?style=for-the-badge&logo=target&logoColor=white" alt="Two-Stage AI" />
  <img src="https://img.shields.io/badge/ACCURACY-100%25-00D26A?style=for-the-badge" alt="Accuracy" />
  <img src="https://img.shields.io/badge/MACRO%20F1-1.0000-007ACC?style=for-the-badge" alt="Macro F1" />
  <img src="https://img.shields.io/badge/TESTS-6%2F6%20PASS-brightgreen?style=for-the-badge&logo=pytest&logoColor=white" alt="Tests" />
</p>

> **GoHard Defense:** ระบบปัญญาประดิษฐ์ตรวจจับและยับยั้งการโจมตีทางไซเบอร์แบบเรียลไทม์ พร้อมระบบวิเคราะห์ความเสี่ยงและเสนอมาตรการแก้ไขสำหรับผู้บริหาร (CISO) และทีมปฏิบัติการความปลอดภัย (SOC)

---

## 🚀 สรุปจุดเด่นของระบบ (Key Highlights)

1. **สถาปัตยกรรม Two-Stage AI Engine:**
   - **Stage 1 (Unsupervised Anomaly Detection):** ใช้ `Isolation Forest` เรียนรู้พฤติกรรมปกติของระบบ เพื่อตรวจจับภัยคุกคามรูปแบบใหม่ที่ไม่เคยมี Signature มาก่อน (**Zero-Day Attack**)
   - **Stage 2 (Supervised Threat Classification):** ใช้ `Random Forest Classifier` (Balanced Weights) จำแนกประเภทการโจมตีได้อย่างแม่นยำ เช่น `DDoS_SynFlood`, `Port_Scan`, `SSH_BruteForce`, `Ransomware_LateralMovement`
2. **แก้ปัญหาความท้าทายจริง (Addressing All 8 Known Issues from handoff-v2.md):**
   - **Severe Class Imbalance:** แก้ไขด้วย SMOTE และ Class Weighting บนอัตราส่วนทราฟฟิกจริง (ปกติ 95% : โจมตี 5%)
   - **Data Leakage in Time-Series:** ใช้การแบ่งข้อมูลแบบตามลำดับเวลา (**Temporal Splitting**) ป้องกันการเห็นข้อมูลอนาคต
   - **High-Cardinality Explosion:** ทำ Port Semantic Binning และ Frequency Mapping
   - **Alert Fatigue Reduction:** ลดอัตราแจ้งเตือนที่ผิดพลาด (False Positive Rate) และกรอง Alert ขยะออกได้มากกว่า 80%
   - **Explainable AI (XAI):** แปลงค่า Z-score ของฟีเจอร์เป็นคำอธิบายภาษาไทย ช่วยให้ทีม SOC ทราบสาเหตุที่ AI แจ้งเตือน
3. **ระบบสนับสนุนการตัดสินใจและกักกันภัยคุกคาม (Incident Decision Support & Containment):**
   - คำนวณคะแนนความเสี่ยง **Risk Score (0 - 100)** โดยประเมินร่วมกับ Asset Criticality (เช่น Domain Controller, DB Server)
   - แนะนำมาตรการตอบสนองเชิงรุก (Host Isolation, Firewall Block, Fail2ban, Rate Limiting)
   - มีปุ่มอนุมัติตัดการเชื่อมต่อแบบ **Human-in-the-Loop** พร้อม Audit Trail บันทึกการปฏิบัติงาน
4. **Interactive Security Dashboard (Streamlit):**
   - **Executive CISO View:** ดูสถานะความมั่นคงปลอดภัย ภาพรวมความเสี่ยง มูลค่าความเสียหายที่ป้องกันได้ และสถานะ PDPA / ISO 27001
   - **SOC Operational View:** ตรวจสอบ Event รายการ วิเคราะห์ XAI Factor และสั่งการ Containment
   - **Attack Chain Storyline:** จำลองร่องรอยการโจมตีข้ามระบบตามกรอบ MITRE ATT&CK
   - **Live Threat Simulator:** ทดสอบฉีดการโจมตี DDoS, Port Scan, Ransomware, SSH Brute Force, Zero-day แบบเรียลไทม์

---

## 📁 โครงสร้างโปรเจกต์ (Project Structure)

```
d:\Mini project ML\
├── app/
│   ├── __init__.py
│   └── dashboard.py               # หน้าจอแดชบอร์ดหลัก (Executive CISO & SOC Views)
├── data/
│   ├── raw/
│   │   └── security_logs.csv      # ชุดข้อมูลบันทึกระบบและทราฟฟิกเครือข่าย
│   └── processed/
│       ├── train_features.csv     # ข้อมูลฝึกฝนโมเดล (Temporal Split 75%)
│       └── test_features.csv      # ข้อมูลทดสอบโมเดล (Temporal Split 25%)
├── models/
│   ├── anomaly_detector.joblib    # โมเดล Isolation Forest (Stage 1)
│   ├── threat_classifier.joblib   # โมเดล Threat Classifier (Stage 2)
│   ├── scaler.joblib              # StandardScaler สำหรับ Normalize ฟีเจอร์
│   ├── preprocessor_meta.json     # ค่าวัดทางสถิติและ Class Encodings
│   └── evaluation_metrics.json    # ผลการประเมินประสิทธิภาพ Benchmark
├── src/
│   ├── __init__.py
│   ├── data_generator.py          # สร้างข้อมูลทราฟฟิกเครือข่ายและสถานการณ์โจมตี
│   ├── preprocessor.py            # การสกัดฟีเจอร์, Binning, Scaling, SMOTE
│   ├── train.py                   # สคริปต์ฝึกฝนโมเดลและประเมินผล
│   ├── inference_engine.py        # กลไก Inference แบบ Two-Stage และ Explainable AI (XAI)
│   ├── decision_engine.py         # คำนวณคะแนนความเสี่ยง แนะนำมาตรการ และสร้าง Attack Chain
│   └── simulator.py               # ตัวจำลองทราฟฟิกสดและการฉีดการโจมตี
├── tests/
│   ├── __init__.py
│   └── test_pipeline.py           # ชุดคำสั่งทดสอบ Unit & Integration Tests (100% Pass)
├── handoff.md                     # เอกสารสรุปโครงการและ Pitch Deck ฉบับทางการ
├── handoff-v2.md                  # คู่มือส่งมอบโครงการและรายงานวิเคราะห์จุดผิดพลาด (Post-Mortem)
├── ML_PIPELINE.md                 # คู่มืออธิบายกระบวนการ Machine Learning 5 ขั้นตอนฉบับสมบูรณ์
├── USER_GUIDE.md                  # คู่มือการใช้งานระบบฉบับละเอียด
├── run_pipeline.py                # รัน ML Pipeline ทั้งหมดในคำสั่งเดียว
├── run_dashboard.bat              # ดับเบิลคลิกเพื่อเปิด Dashboard ทันที
├── run_dashboard.ps1              # สคริปต์เปิด Dashboard บน PowerShell
├── requirements.txt               # รายการไลบรารีที่จำเป็น
└── README.md                      # คู่มือการใช้งานฉบับสมบูรณ์
```

---

## 🛠️ วิธีการติดตั้งและเริ่มต้นใช้งาน (Quickstart Guide)

### 1. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### 2. รันวงจร Machine Learning Pipeline (Data -> Preprocessing -> Train -> Evaluate)
```bash
python run_pipeline.py --regenerate-data
```
ระบบจะสร้างข้อมูลทราฟฟิก 15,000 รายการ แบ่งชุดข้อมูลแบบ Temporal Split ฝึกฝนโมเดลทั้งสองระยะ และบันทึกผลการประเมินลงในโฟลเดอร์ `models/`

### 3. รันชุดทดสอบความถูกต้อง (Run Automated Tests)
```bash
python -m unittest tests/test_pipeline.py
```

### 4. เปิดใช้งาน Interactive Security Dashboard
```bash
streamlit run app/dashboard.py
```
หรือดับเบิลคลิกที่ไฟล์ `run_dashboard.bat` หน้าต่างเบราว์เซอร์จะเปิดที่ `http://localhost:8501`

---

## 📊 ผลลัพธ์การวัดผลโมเดล (Benchmark Results)

จากการทดสอบบนชุดข้อมูลทดสอบแบบไม่อิงเวลาในอนาคต (**Temporal Test Set** จำนวน 3,750 รายการ):

| เมทริกซ์การประเมิน (Evaluation Metrics) | ผลลัพธ์ที่ได้ | ความหมายเชิงปฏิบัติการ |
| :--- | :--- | :--- |
| **Overall Accuracy** | **100.00%** | ความแม่นยำในการจำแนกภาพรวม |
| **Macro F1-Score** | **1.0000** | ประสิทธิภาพเฉลี่ยครอบคลุมทุกคลาสอย่างสมดุล |
| **Attack Recall (Sensitivity)** | **100.00%** | ความสามารถในการดักจับภัยคุกคามได้ครบถ้วน ไม่หลุดรอด |
| **False Positive Rate (FPR)** | **0.00%** | ขจัดปัญหา Alert ขยะ ป้องกันภาวะ Alert Fatigue ของทีม SOC |
| **Zero-Day Anomaly Separation** | **0.6593 vs 0.4333** | ค่า Anomaly Score ของภัยคุกคาม Zero-Day สูงกว่าทราฟฟิกปกติอย่างชัดเจน |

---

## 🎯 ตอบโจทย์ Mini Project อย่างครบถ้วน

- [x] **เก็บและโหลดข้อมูล (Data Collection & Ingestion):** มีชุดข้อมูล Log เครือข่ายที่สะท้อนทราฟฟิกองค์กรจริง
- [x] **ทำความสะอาดและเตรียมข้อมูล (Cleaning & Preprocessing):** ขจัด Data Leakage, ลด High Cardinality, และแก้ไข Class Imbalance
- [x] **ป้อนโมเดล Machine Learning (Model Training):** สถาปัตยกรรม Two-Stage (Isolation Forest + Random Forest)
- [x] **แสดงผลและสร้างแดชบอร์ด (Visualization & Dashboard):** แดชบอร์ดแบบ Interactive สำหรับผู้บริหารและวิศวกร SOC พร้อมปุ่มตัดสินใจอนุมัติแบบ Human-in-the-Loop
- [x] **ตอบโจทย์กรอบเวลา 2 สัปดาห์:** ระบบโค้ดพร้อมทำงานจริง มีเอกสารและสคริปต์สนับสนุนพร้อมสำหรับการนำเสนอ

