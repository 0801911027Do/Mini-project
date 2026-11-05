# เอกสารส่งมอบโครงการและรายงานวิเคราะห์ปัญหา (Project Handover & Post-Mortem v2)
## ระบบ AI ตรวจจับภัยคุกคามไซเบอร์และสนับสนุนการตัดสินใจเชิงปฏิบัติการ (AI Threat Detection & SOC Support)

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

**ทีมพัฒนา:** GoHard  
**เวอร์ชันเอกสาร:** 2.0 (Official Handoff & Lessons Learned)  
**กรอบเวลาการดำเนินงาน:** เหลือระยะเวลา 2 สัปดาห์ก่อนส่งมอบและนำเสนอผลงาน Mini Project  

---

## 1. ภาพรวมโครงการและขอบเขตงาน (Executive Summary & ML Scope)

### 1.1 วัตถุประสงค์หลัก
พัฒนาระบบปัญญาประดิษฐ์ (AI) เพื่อสนับสนุนการทำงานของศูนย์ปฏิบัติการรักษาความปลอดภัย (SOC) ให้สามารถตรวจจับ จำแนกประเภท และยับยั้งภัยคุกคามทางไซเบอร์ได้แบบเรียลไทม์ พร้อมระบบช่วยวิเคราะห์และเสนอแนวทางแก้ไขเพื่อลดระยะเวลาเฉลี่ยในการกอบกู้ระบบ (MTTR: Mean Time to Respond) และลดอัตราการแจ้งเตือนที่ผิดพลาด (False Positive Rate)

### 1.2 ขอบเขตกระบวนการ Machine Learning (End-to-End ML Pipeline)
โครงการครอบคลุมวงจรการพัฒนาทางวิทยาศาสตร์ข้อมูลและ Machine Learning ทั้งหมด 5 ขั้นตอนหลัก:
1. **Data Collection & Ingestion:** รวบรวมและนำเข้าข้อมูลบันทึกระบบ (Event Logs) และทราฟฟิกเครือข่าย (Network Traffic)
2. **Data Cleaning & Preprocessing:** ล้างข้อมูล จัดการค่าสูญหาย ทำความสะอาด และสกัดคุณลักษณะสำคัญ (Feature Engineering)
3. **Model Development & Training:** คัดเลือก ฝึกฝน และปรับจูนอัลกอริทึม (Supervised / Anomaly Detection)
4. **Evaluation & Verification:** ประเมินประสิทธิภาพโมเดลด้วยเกณฑ์วัดทางสถิติ (Precision, Recall, F1-Score, ROC-AUC)
5. **Dashboard & Actionable Visualization:** ออกแบบหน้าจอแสดงผลสรุปสถานการณ์ความเสี่ยงและปุ่มตัดสินใจสั่งการสำหรับผู้บริหาร/ทีม SOC

---

## 2. รวบรวมจุดผิดพลาด อุปสรรค และแนวทางแก้ไข (Known Issues, Errors & Lessons Learned)

หมวดนี้รวบรวมข้อบกพร่อง ปัญหาเชิงเทคนิคที่พบในระหว่างการทดลองพัฒนาโมเดล และแนวทางปรับปรุงแก้ไขเพื่อเตรียมความพร้อมในการนำเสนอ:

### 2.1 ด้านข้อมูลและการเตรียมข้อมูล (Data & Feature Engineering Issues)

* **จุดผิดพลาดที่ 1: ปัญหาความไม่สมดุลของข้อมูลอย่างรุนแรง (Severe Class Imbalance)**
  * *ปัญหาที่พบ:* ในข้อมูล Network Traffic ปกติ มีปริมาณข้อมูลการโจมตี (Attacks) เพียง 0.5% - 2% ส่งผลให้โมเดลเกิดภาพลวงตาทางความแม่นยำ (Accuracy Paradox) โดยโมเดลทายว่าเป็น "ทราฟฟิกปกติ" ตลอดเวลาแต่ได้ Accuracy สูงถึง 98%
  * *แนวทางแก้ไข:* เลิกใช้ Accuracy เป็นตัววัดหลัก และหันมาใช้ **Precision, Recall, F1-Score (Macro)** พร้อมประยุกต์ใช้เทคนิค **SMOTE** (Synthetic Minority Over-sampling Technique) หรือปรับค่า **Class Weights** ในโมเดลเพื่อให้น้ำหนักความสำคัญกับคลาสที่เป็นภัยคุกคามมากขึ้น

* **จุดผิดพลาดที่ 2: ปัญหาข้อมูลรั่วไหลในมิติของเวลา (Data Leakage in Time-Series Data)**
  * *ปัญหาที่พบ:* การใช้คำสั่งสุ่มแบ่งข้อมูลแบบดั้งเดิม (`train_test_split(shuffle=True)`) ส่งผลให้เหตุการณ์การโจมตีในอนาคตหลุดเข้าไปอยู่ในชุด Train ทำให้โมเดลจำรูปแบบได้เกินจริง แต่เมื่อนำไปทดสอบบนข้อมูลจริงกลับทำนายไม่ได้
  * *แนวทางแก้ไข:* ปรับเปลี่ยนมาใช้ **Time-based Splitting (Temporal Split)** โดยแบ่งช่วงเวลาอดีตสำหรับฝึกฝนโมเดล และช่วงเวลาถัดไปสำหรับการทดสอบ เพื่อสะท้อนสภาพแวดล้อมการทำงานจริง

* **จุดผิดพลาดที่ 3: ปัญหาค่าคุณลักษณะมีความหลากหลายสูงเกินไป (High-Cardinality Categorical Features)**
  * *ปัญหาที่พบ:* การทำ One-Hot Encoding บนฟีเจอร์อย่าง `Source IP`, `Destination Port` หรือ `User-Agent` ทำให้มิติข้อมูลพุ่งสูงจนหน่วยความจำล้น (Curse of Dimensionality)
  * *แนวทางแก้ไข:* จัดกลุ่มข้อมูล (Binning) เช่น แปลง Port ให้เป็นกลุ่มบริการที่รู้จัก (Well-known Ports vs Dynamic Ports) หรือใช้ **Frequency / Target Encoding** แทน

---

### 2.2 ด้านโมเดลและอัลกอริทึม (Model & Evaluation Issues)

* **จุดผิดพลาดที่ 4: อัตราการแจ้งเตือนที่ผิดพลาดสูง (High False Positive Rate - Alert Noise)**
  * *ปัญหาที่พบ:* โมเดลตรวจพบภัยคุกคามได้ดี แต่มักระบุทราฟฟิกที่มีปริมาณสูงชั่วคราว (เช่น การสำรองข้อมูลตอนเที่ยงคืน) เป็นการโจมตี ทำให้เกิดปัญหา Alert Fatigue
  * *แนวทางแก้ไข:* ปรับจูน **Threshold การตัดสินใจ (Decision Threshold Optimization)** ร่วมกับการใช้ **Two-Stage Detection**:
    1. ชั้นแรกใช้ Unsupervised Anomaly Detection (เช่น Isolation Forest) เพื่อจับความผิดปกติเบื้องต้น
    2. ชั้นที่สองใช้ Supervised Classification เพื่อจำแนกประเภทการโจมตีให้ชัดเจน

* **จุดผิดพลาดที่ 5: โมเดลจำกัดเฉพาะรูปแบบการโจมตีเดิม (Overfitting on Known Signatures)**
  * *ปัญหาที่พบ:* โมเดลทำนายการโจมตีแบบเดิมได้สมบูรณ์แบบ แต่ไม่สามารถรับมือกับการโจมตีรูปแบบใหม่ (Zero-day Exploits)
  * *แนวทางแก้ไข:* ผสมผสานโมเดลประเภท **Behavior-based Anomaly Detection** ซึ่งเน้นการเรียนรู้พฤติกรรมปกติของระบบ (Baseline) หากมีพฤติกรรมใดเบี่ยงเบนออกไป ระบบจะส่งสัญญาณเตือนทันทีแม้ไม่มี Signature มาก่อน

* **จุดผิดพลาดที่ 6: ความโปร่งใสของโมเดล (Explainability / Black-box Dilemma)**
  * *ปัญหาที่พบ:* เมื่อโมเดลตัดสินว่ามีภัยคุกคาม ทีม SOC และ CISO ไม่กล้าอนุมัติตัดการเชื่อมต่อ เนื่องจากโมเดลไม่ได้แสดงเหตุผลประกอบ
  * *แนวทางแก้ไข:* นำเทคนิค **Explainable AI (XAI)** เช่น **SHAP Values** หรือ **Feature Importance** มาใช้ระบุว่าฟีเจอร์ใดเป็นสาเหตุหลักที่ทำให้โมเดลตัดสินใจแจ้งเตือน

---

### 2.3 ด้านการนำไปประยุกต์ใช้งานและระบบแสดงผล (System & Dashboard Issues)

* **จุดผิดพลาดที่ 7: ความล่าช้าในการทำนายผล (Inference Latency)**
  * *ปัญหาที่พบ:* โค้ดประมวลผลข้อมูลมีการวนลูปซ้ำซ้อน ทำให้ใช้เวลาทำนายหลายวินาทีต่อแพ็กเก็ต ไม่สามารถตอบโจทย์การทำงานแบบ Real-time ได้
  * *แนวทางแก้ไข:* ปรับปรุงการคำนวณให้เป็นแบบเวกเตอร์ (Vectorized Operations) บน NumPy/Pandas และทดสอบประมวลผลข้อมูลแบบ Micro-batching

* **จุดผิดพลาดที่ 8: แดชบอร์ดแสดงข้อมูลเชิงเทคนิคมากเกินไปจนเข้าใจยาก**
  * *ปัญหาที่พบ:* Dashboard แรกเริ่มแสดงผลเฉพาะตารางตัวเลขและกราฟทางสถิติ ทำให้ผู้บริหารระดับสูงมองไม่เห็นผลกระทบทางธุรกิจ
  * *แนวทางแก้ไข:* ปรับโครงสร้างหน้า Dashboard ให้มี 2 มุมมองหลัก:
    1. **Executive View (สำหรับ CISO):** สรุปคะแนนความเสี่ยงรวม (Risk Score), ระดับความพร้อมของระบบ, และปุ่ม Action สำหรับอนุมัติตัดการเชื่อมต่อ
    2. **SOC Operational View (สำหรับทีมเทคนิค):** เจาะลึก Log รายบรรทัด, IP ต้นทาง-ปลายทาง, และ Attack Storyline

---

## 3. แผนการดำเนินงานช่วงโค้งสุดท้าย (2-Week Sprint Roadmap)

```
[สัปดาห์ที่ 1: ปรับปรุงประสิทธิภาพโมเดล] ──> [สัปดาห์ที่ 2: ระบบเชื่อมโยงและเตรียมนำเสนอ]
```

| สัปดาห์ | กิจกรรมหลัก | ผลลัพธ์ที่คาดหวัง (Milestone Output) |
| :--- | :--- | :--- |
| **Week 1** | • แก้ไขปัญหา Class Imbalance ด้วย SMOTE/Class Weights<br>• ปรับแต่ง Hyperparameters เพื่อลด False Positives<br>• เชื่อมต่อโมเดลเข้ากับ Pipeline อัตโนมัติ | • โมเดลมีค่า F1-Score บนคลาสการโจมตี $\ge 85\%$<br>• False Positive Rate ลดลงอย่างมีนัยสำคัญ |
| **Week 2** | • พัฒนา Dashboard แสดงผล (Streamlit / Gradio / Looker)<br>• จำลองสถานการณ์การโจมตี (Attack Scenario Demo)<br>• จัดทำสไลด์และซ้อมนำเสนอ Mini Project | • ระบบ Interactive Demo ที่กดทดสอบได้จริง<br>• เอกสารสรุปโครงการและสไลด์นำเสนอฉบับสมบูรณ์ |

---

## 4. รายการตรวจสอบสิ่งที่ต้องส่งมอบ (Deliverables Checklist)

- [ ] **Data Pipeline Script:** ชุดคำสั่งสำหรับการทำความสะอาดและแปลงข้อมูลดิบสู่ฟีเจอร์พร้อมป้อนโมเดล
- [ ] **Model Artifacts:** ไฟล์โมเดลที่ผ่านการฝึกฝนแล้ว (เช่น `.pkl`, `.onnx`, หรือ `.joblib`) พร้อมผลการวัดผล Benchmark
- [ ] **Interactive Security Dashboard:** หน้าจอแสดงผลที่แสดงการตรวจจับทราฟฟิกผิดปกติ พร้อมปุ่มจำลองการบล็อก (Containment Simulation)
- [ ] **Project Presentation Deck:** สไลด์สรุปปัญหา, แนวทาง ML, ผลการทดลอง, จุดผิดพลาดที่ได้เรียนรู้ และผลลัพธ์เชิงธุรกิจ
- [ ] **Post-Mortem & Future Roadmap Report:** รายงานสรุปอุปสรรค วิธีแก้ปัญหา และทิศทางการต่อยอดในอนาคต

---

## 5. กระบวนการควบคุมคุณภาพแบบวนซ้ำ (PDCA Continuous Improvement)

โครงการใช้กรอบการทำงานแบบ **PDCA (Plan - Do - Check - Act)** ในการพัฒนาทุกฟีเจอร์:
1. **Plan:** ระบุสมมติฐานและปัญหา เช่น "ลดอัตราแจ้งเตือนผิดพลาดจากทราฟฟิกสำรองข้อมูล"
2. **Do:** ออกแบบกฎการกรองและฝึกโมเดลชั้นที่สอง
3. **Check:** วัดค่า Precision และ Recall บนชุดข้อมูลทดสอบ
4. **Act:** ปรับใช้เวอร์ชันที่ผ่านเกณฑ์ และบันทึกข้อจำกัดเพื่อพัฒนาต่อยอดในรอบถัดไป
