# คู่มืออธิบายกระบวนการ Machine Learning Pipeline 5 ขั้นตอน
## สถาปัตยกรรมและการทำงานของระบบ GoHard AI Threat Detection & Incident Decision Support (v2.0)

> เอกสารฉบับนี้จัดทำขึ้นเพื่ออธิบายรายละเอียดเชิงลึกของกระบวนการ Machine Learning ทั้ง 5 ขั้นตอน ภาษาเครื่อง อัลกอริทึม และเทคนิคทางวิทยาศาสตร์ข้อมูลที่ใช้ในโครงการ สำหรับใช้อ้างอิงและนำเสนอผลงาน

---

## 🗺️ แผนผังกระบวนการทำงานภาพรวม (End-to-End ML Pipeline Architecture)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   GOHARD AI THREAT ENGINE PIPELINE                                     │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
       │
       ▼
[01. เก็บข้อมูล (Data Collection)]
       │ • 15,000 Network Events (ทราฟฟิกองค์กรเสมือนจริงตามมาตรฐาน CICIDS2017)
       │ • 95% ทราฟฟิกปกติ (14,250 รายการ) : 5% การโจมตี 5 เวกเตอร์ (750 รายการ)
       │ • Time-Series ต่อเนื่อง 12 ชั่วโมง กระจายคลื่นการโจมตี (Attack Waves)
       ▼
[02. โหลดข้อมูล (Data Ingestion)]
       │ • โหลดไฟล์ CSV เข้าสู่ระบบด้วย Pandas DataFrame
       │ • จัดเรียงลำดับเวลา (Temporal Sorting) และตรวจสอบความสมบูรณ์ของ Schema
       ▼
[03. ทำความสะอาดและแปลงข้อมูล (Data Cleaning & Feature Engineering)]
       │ • Temporal Splitting (75% Train : 25% Test) ป้องกัน Data Leakage จากอนาคต
       │ • Semantic Port Binning ลดมิติข้อมูลพอร์ต (แก้ปัญหา High Cardinality)
       │ • สกัดฟีเจอร์ความปลอดภัย: is_lateral_candidate, packet_rate, byte_rate, byte_ratio
       │ • จัดการ Class Imbalance ด้วย SMOTE (Synthetic Minority Over-sampling Technique)
       │ • ปรับสเกลตัวเลขด้วย StandardScaler (Mean=0, Std=1)
       ▼
[04. ป้อนโมเดล AI (Model Training & Two-Stage AI Engine)]
       │ • Stage 1: Isolation Forest (Unsupervised) ──> ตรวจจับ Zero-Day Anomaly
       │ • Stage 2: Balanced Random Forest (Supervised) ──> จำแนกประเภทการโจมตี
       │ • Explainable AI (XAI) คำนวณ Z-score แจกแจงเหตุผลให้ทีม SOC เป็นภาษาไทย
       │ • Risk Scoring Engine (0-100) คำนวณความเสี่ยงร่วมกับ Asset Criticality
       ▼
[05. แสดงผลและ Visualize (Visualization & Incident Decision Support)]
       │ • 🏢 Executive CISO View (Enterprise Risk Index, มูลค่าที่ป้องกันได้, PDPA/ISO)
       │ • 🛡️ SOC Operational View (Real-time Flow, XAI Card, ปุ่ม Human-in-the-Loop)
       │ • ⚡ Live Threat Simulator (ปุ่มทดสอบยิงการโจมตีสด 6 รูปแบบ)
       │ • ⛓️ Attack Chain Storyline (จำลองห่วงโซ่การโจมตีตาม MITRE ATT&CK)
       │ • 📊 ML Benchmark (Confusion Matrix, Precision, Recall, F1-Score 100%)
```

---

## 1. ขั้นตอนที่ 1: เก็บข้อมูลยังไง? (Data Collection & Generation)

* **ไฟล์ต้นทาง:** `src/data_generator.py` $\rightarrow$ บันทึกลง `data/raw/security_logs.csv`
* **ภาษาและเครื่องมือที่ใช้:** Python, NumPy, Pandas, Datetime
* **หลักการทำงานเชิงเทคนิค:**
  1. จำลองข้อมูลบันทึกระบบและทราฟฟิกเครือข่ายระดับองค์กร (NetFlow / Syslog) จำนวน **15,000 เรคคอร์ด** ตามโครงสร้างข้อมูลสากล **CICIDS2017 / Zeek / Suricata**
  2. **สัดส่วนข้อมูลเพื่อสะท้อนโลกความเป็นจริง:**
     * **ทราฟฟิกปกติ (Normal) 95% (14,250 รายการ):** การใช้งานระบบงานทั่วไป เช่น Web Browsing (HTTP/HTTPS พอร์ต 80/443), DNS Query (UDP พอร์ต 53), Database Query (MySQL/PostgreSQL พอร์ต 3306/5432), และ Internal REST API (พอร์ต 8080)
     * **ทราฟฟิกการโจมตี (Attacks) 5% (750 รายการ):** ครอบคลุม 5 เวกเตอร์สำคัญ:
       - `DDoS_SynFlood` (35% ของภัยคุกคาม): ส่งแพ็กเก็ต SYN รัวๆ สู่ Web Server โดยไม่รอรับข้อมูล อัตราแพ็กเก็ตพุ่งสูงผิดปกติ
       - `Port_Scan` (25% ของภัยคุกคาม): ผู้โจมตีกวาดสแกนพอร์ต 1 ถึง 1024 อย่างรวดเร็ว เพื่อสำรวจหาบริการที่มีช่องโหว่
       - `SSH_BruteForce` (20% ของภัยคุกคาม): พยายามสุ่มรหัสผ่านเข้า Domain Controller บนพอร์ต 22 ซ้ำๆ หลายสิบครั้ง
       - `Ransomware_LateralMovement` (12% ของภัยคุกคาม): โฮสต์ภายในที่ติดมัลแวร์แอบส่งไฟล์ข้อมูลขนาดใหญ่หลายสิบเมกะไบต์ผ่าน SMB (พอร์ต 445) ไปยัง File Server เพื่อแพร่กระจายและเข้ารหัสข้อมูล
       - `ZeroDay_Exploit` (8% ของภัยคุกคาม): การโจมตีพฤติกรรมรูปแบบใหม่ที่ไม่เคยมี Signature มาก่อน ผ่านพอร์ตไม่พึงประสงค์ (8443) และมีขนาด Payload ที่ผิดธรรมชาติ
  3. **มิติเวลา (Time Series):** ใช้การแจกแจงแบบ Cumulative Exponential เพื่อให้มี Timestamp เรียงลำดับตามเวลาจริงตลอด 12 ชั่วโมง พร้อมกระจายคลื่นการโจมตี (Attack Waves) ทั้งช่วงต้น กลาง และปลายของไทม์ไลน์

---

## 2. ขั้นตอนที่ 2: โหลดข้อมูลยังไง? (Data Ingestion)

* **ไฟล์ต้นทาง:** `run_pipeline.py`, `src/train.py`
* **ภาษาและเครื่องมือที่ใช้:** Python, Pandas (`pd.read_csv`), OS Path module
* **หลักการทำงานเชิงเทคนิค:**
  1. อ่านไฟล์ดิบ `data/raw/security_logs.csv` เข้าสู่หน่วยความจำในรูปแบบ Pandas DataFrame
  2. ตรวจสอบความถูกต้องของ Schema ทั้ง 14 คอลัมน์พื้นฐาน:
     - ข้อมูลระบุตัวตน: `source_ip`, `destination_ip`, `source_port`, `destination_port`
     - ข้อมูลโปรโตคอลและสถานะ: `protocol`, `connection_state`
     - ข้อมูลเชิงปริมาณ: `duration_sec`, `bytes_sent`, `bytes_received`, `packets_sent`, `packets_received`, `failed_login_attempts`
     - เฉลยสำหรับวัดผล: `threat_label`, `is_attack`
  3. แปลงคอลัมน์ `timestamp` เป็นประเภท `pd.to_datetime` และจัดเรียงข้อมูลตามเวลาอย่างเข้มงวด

---

## 3. ขั้นตอนที่ 3: ทำความสะอาดและแปลงข้อมูลยังไง? (Data Cleaning & Feature Engineering)

* **ไฟล์ต้นทาง:** `src/preprocessor.py`
* **ภาษาและเครื่องมือที่ใช้:** Python, Scikit-learn (`StandardScaler`), Imbalanced-learn (`SMOTE`), NumPy
* **หลักการทำงานเชิงเทคนิค:**
  1. **การป้องกันข้อมูลรั่วไหลข้ามเวลา (Temporal Splitting):**
     * ห้ามใช้การสุ่มแบบ `train_test_split(shuffle=True)` เพราะจะทำให้ข้อมูลในอนาคตรั่วไหลไปอยู่ในชุด Train (**Data Leakage**)
     * โครงการนี้แบ่งข้อมูลแบบ **75% แรกตามลำดับเวลาสำหรับ Train** และ **25% หลังสุดสำหรับ Test** เพื่อให้จำลองการนำโมเดลไปตรวจจับเหตุการณ์ในโลกจริง
  2. **การลดมิติข้อมูลพอร์ต (Semantic Port Binning):**
     * การทำ One-Hot Encoding บนพอร์ตที่มีเป็นพันๆ พอร์ตจะทำให้เกิดปัญหา *Curse of Dimensionality*
     * จึงจัดกลุ่มพอร์ตตามฟังก์ชันการทำงาน:
       - `0`: Web Traffic (80, 443, 8080)
       - `1`: Shell / Remote Admin (22, 3389)
       - `2`: Database (3306, 5432, 1433)
       - `3`: File Share / SMB (445, 139)
       - `4`: Core Infrastructure / DNS (53, 123)
       - `5`: High Dynamic Ports (>1024)
  3. **การสกัดฟีเจอร์พฤติกรรมความปลอดภัย (Cybersecurity Feature Engineering):**
     * วิเคราะห์ขอบเขตเครือข่าย: แปลง IP เป็น Boolean (`is_internal_src`, `is_internal_dst`) และคำนวณ `is_lateral_candidate` (เมื่อภายในคุยกับภายใน เพื่อดักจับ Ransomware)
     * คำนวณอัตราความเร็วและสัดส่วน:
       $$\text{byte\_ratio} = \frac{\text{bytes\_sent}}{\max(1, \text{bytes\_received})}$$
       $$\text{packet\_rate} = \frac{\text{packets\_sent} + \text{packets\_received}}{\max(0.001, \text{duration\_sec})}$$
       $$\text{byte\_rate} = \frac{\text{bytes\_sent} + \text{bytes\_received}}{\max(0.001, \text{duration\_sec})}$$
  4. **การแปลงข้อมูลตัวอักษรเป็นรหัสตัวเลข (Categorical Encoding):**
     * `protocol`: TCP=1, UDP=2, ICMP=3
     * `connection_state`: ESTABLISHED=1, SYN_SENT=2, RESET=3, CLOSED=4
  5. **การจัดการความไม่สมดุลของข้อมูล (Class Imbalance Management):**
     * ใช้ **SMOTE** (Synthetic Minority Over-sampling Technique) เพิ่มตัวอย่างทราฟฟิกการโจมตีในชุด Train ด้วยการสุ่มสร้างตัวอย่างใหม่ระหว่างเพื่อนบ้านที่ใกล้ที่สุด ($k$-nearest neighbors)
  6. **การปรับสเกลตัวแปร (Feature Scaling):**
     * ใช้ **`StandardScaler`** ปรับฟีเจอร์ทั้งหมดให้อยู่ในรูป $Z$-Score ($\text{Mean} = 0, \text{Std} = 1$) โดย `fit` บนชุด Train เท่านั้น แล้วนำค่าสถิติไป `transform` บนชุด Test

---

## 4. ขั้นตอนที่ 4: ป้อนโมเดล ภาษาเครื่องและอัลกอริทึมที่ใช้ยังไง? (Model Architecture)

* **ไฟล์ต้นทาง:** `src/train.py`, `src/inference_engine.py`, `src/decision_engine.py`
* **ภาษาและเครื่องมือที่ใช้:** Python 3.14, Scikit-learn, Joblib
* **สถาปัตยกรรม Two-Stage AI Engine:**

### 4.1 Stage 1: Unsupervised Anomaly Detection — `Isolation Forest`
* **ภาษาเครื่อง/อัลกอริทึม:** ไม่ใช้เฉลย (Unsupervised) ทำงานโดยสร้างชุดต้นไม้ Binary Trees แบบสุ่มตัดแบ่งมิติข้อมูล
* **หน้าที่หลัก:** ตรวจจับภัยคุกคามแบบ **Zero-Day Attack** ที่ไม่เคยมี Signature ในฐานข้อมูล
* **หลักการ:** ข้อมูลปกติจะเกาะกลุ่มหนาแน่นและต้องใช้จำนวนการตัดแบ่งหลายครั้งกว่าจะแยกตัวได้ แต่ข้อมูลที่ผิดปกติ (Anomaly) จะกระเด็นอยู่นอกกลุ่มและถูกตัดแยก (Isolate) ได้ในกิ่งที่สั้น
* **ผลลัพธ์:** คำนวณออกมาเป็น **Anomaly Score (0.0 - 1.0)** หากเกินค่า Threshold (0.58) ระบบจะส่งสัญญาณเตือน Zero-Day ทันที

### 4.2 Stage 2: Supervised Threat Classification — `Balanced Random Forest`
* **ภาษาเครื่อง/อัลกอริทึม:** การเรียนรู้แบบมีผู้สอน (Supervised Ensemble Learning) ใช้ Decision Trees 120 ต้น
* **หน้าที่หลัก:** จำแนกประเภทภัยคุกคามที่ชัดเจน (`Normal`, `DDoS_SynFlood`, `Port_Scan`, `SSH_BruteForce`, `Ransomware_LateralMovement`)
* **การตั้งค่าเฉพาะทาง:** กำหนด `class_weight="balanced_subsample"` เพื่อปรับน้ำหนักการคำนวณ Loss ให้ความสำคัญกับคลาสที่มีจำนวนน้อยเท่าเทียมกับคลาสปกติ

### 4.3 ระบบอธิบายผลการตัดสินใจ (Explainable AI - XAI)
* เพื่อแก้ปัญหา "กล่องดำ" (Black-Box AI) ระบบดึงค่า $Z$-Score ของฟีเจอร์ที่มีค่าเบี่ยงเบนจากพฤติกรรมปกติเกิน $1.5$ ถึง $3.0$ เท่า แล้วแปลงเป็นภาษาไทยอธิบายให้วิศวกร SOC เข้าใจ เช่น:
  * *"พบการพยายามล็อกอินล้มเหลวผิดปกติ 28 ครั้ง (+7.4 std) สอดคล้องกับพฤติกรรม Brute Force"*
  * *"ปริมาณการส่งข้อมูลออก (Upload Ratio) สูงกว่าการรับข้อมูลอย่างมีนัยสำคัญ สอดคล้องกับพฤติกรรม Data Exfiltration"*

### 4.4 ระบบคำนวณคะแนนความเสี่ยงและการตัดสินใจ (Decision Engine)
* คำนวณ **Enterprise Risk Score (0 - 100)** โดยประเมินร่วมกับความสำคัญของเครื่องเป้าหมาย (Asset Criticality Multiplier):
  * Domain Controller: ตัวคูณ $1.35$ (Tier 1 Asset)
  * Production Database Server: ตัวคูณ $1.30$ (Tier 1 Asset)
  * File Server: ตัวคูณ $1.25$ (Tier 2 Asset)
* เสนอมาตรการแก้ไขแบบเจาะจง (เช่น Host Isolation สำหรับ Ransomware, Ingress Block สำหรับ DDoS)

---

## 5. ขั้นตอนที่ 5: แสดงผลและ Visualize ยังไงบ้าง? (Visualization & Dashboard)

* **ไฟล์ต้นทาง:** `app/dashboard.py`
* **ภาษาและเครื่องมือที่ใช้:** Python, Streamlit (v1.66), Altair, Custom HTML/CSS
* **มิติการแสดงผล 5 รูปแบบ:**

| มุมมองการแสดงผล | กลุ่มผู้ใช้เป้าหมาย | องค์ประกอบและกราฟที่แสดงผล |
| :--- | :--- | :--- |
| **🏢 Executive CISO View** | ผู้บริหารระดับสูง (CISO) | • **Enterprise Threat Index (0-100):** ดัชนีความเสี่ยงรวมขององค์กร<br>• **Alert Noise Reduction (%):** อัตราลด Alert ขยะ (>80%) ขจัดปัญหา Alert Fatigue<br>• **Loss Averted (฿):** มูลค่าความเสียหายที่ป้องกันได้ และชั่วโมง Downtime ที่ลดลง<br>• **Threat Breakdown:** แผนภูมิแท่งแจกแจงสัดส่วนประเภทการโจมตี |
| **🛡️ SOC Operational View** | วิศวกรความปลอดภัย (SOC) | • **Real-Time Packet Flow:** ตารางตรวจสอบข้อมูลแพ็กเก็ตรายบรรทัด<br>• **XAI Factor Cards:** กล่องสีส้มอธิบายตัวแปรที่ผิดปกติเบื้องหลังการตัดสินใจของ AI<br>• **Human-in-the-Loop Console:** ปุ่มกด **"⚡ อนุมัติดำเนินการ (CONTAINMENT)"** สั่งตัดการเชื่อมต่อทันที พร้อมลงบันทึกใน **Containment Audit Trail** |
| **⚡ Live Threat Simulator** | ผู้ชมการสาธิต / ผู้ทดสอบ | • ปุ่มกด 6 ปุ่มสำหรับจำลองการโจมตีสด (`Normal`, `DDoS`, `Port Scan`, `SSH Brute Force`, `Ransomware`, `Zero-Day`)<br>• แสดงผลการทำนายและมาตรการแก้ไขในเสี้ยววินาที |
| **⛓️ Attack Chain Storyline** | นิติวิทยาศาสตร์ไซเบอร์ (Forensics) | • รวมข้อมูล Log ที่กระจัดกระจายและเรียงลำดับเวลาออกมาเป็นสตอรี่ตามกรอบสากล **MITRE ATT&CK**: $\text{Reconnaissance} \rightarrow \text{Credential Access} \rightarrow \text{Lateral Movement}$ |
| **📊 ML Benchmark** | คณะกรรมการ / อาจารย์ผู้ตรวจ | • ตาราง **Confusion Matrix** แบบ Interactive<br>• ตารางเปรียบเทียบ Per-Class Metrics (Precision, Recall, F1-Score)<br>• สรุปบทเรียน 8 ประเด็นความท้าทายที่แก้ไขได้สำเร็จ |

---

## 🛠️ ตารางสรุป Technology Stack ทั้งโครงการ

| หมวดหมู่ | เทคโนโลยี / ภาษา / ไลบรารี | หน้าที่ในระบบ |
| :--- | :--- | :--- |
| **ภาษาหลัก** | Python 3.14 | ภาษาหลักที่ใช้ประมวลผลทั้งระบบ |
| **การจัดการข้อมูล** | Pandas, NumPy | โครงสร้างข้อมูลตาราง และการคำนวณแบบ Vectorized |
| **Machine Learning** | Scikit-learn | อัลกอริทึม Isolation Forest, Random Forest, StandardScaler |
| **Imbalance Handling** | Imbalanced-learn (SMOTE) | สร้างข้อมูลตัวอย่างคลาสส่วนน้อยในชุด Train |
| **Model Persistence** | Joblib | บันทึกและโหลดโมเดล (.joblib) แบบ Binary |
| **การแสดงผลแดชบอร์ด** | Streamlit, Altair | สร้างเว็บแอปพลิเคชัน Interactive และกราฟแสดงผล |
| **การทดสอบระบบ** | Unittest (Python Standard) | ชุดทดสอบความถูกต้องอัตโนมัติ (6 Tests Passing 100%) |
| **การควบคุมเวอร์ชัน** | Git, GitHub | จัดเก็บซอร์สโค้ดและควบคุมเวอร์ชันของโครงการ |
