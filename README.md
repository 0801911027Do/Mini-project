# มินิโปรเจกต์: ระบบตรวจจับภัยคุกคามไซเบอร์ด้วย Machine Learning
### Network Cyber Threat Detection Mini-Project

<p align="center">
  <img src="https://img.shields.io/badge/PYTHON-3.10%20%7C%203.11%20%7C%203.14-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/STREAMLIT-1.66%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/SCIKIT--LEARN-1.4%2B-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" alt="Scikit-Learn" />
  <img src="https://img.shields.io/badge/PANDAS-2.0%2B-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas" />
</p>
<p align="center">
  <img src="https://img.shields.io/badge/MODEL-RANDOM%20FOREST-008080?style=for-the-badge" alt="Model" />
  <img src="https://img.shields.io/badge/ACCURACY-100%25-00D26A?style=for-the-badge" alt="Accuracy" />
  <img src="https://img.shields.io/badge/STATUS-READY-blue?style=for-the-badge" alt="Status" />
</p>

---

## 📌 แนะนำโปรเจกต์
มินิโปรเจกต์นี้เป็นการนำโมเดล **Machine Learning (Random Forest Classifier)** มาช่วยตรวจจับและจำแนกประเภทพฤติกรรมบนเครือข่าย โดยแบ่งออกเป็น 4 รูปแบบ:
1. **Normal:** ทราฟฟิกการใช้งานอินเทอร์เน็ตทั่วไป
2. **DDoS:** การส่งแพ็กเก็ตจำนวนมหาศาลเข้ามาในเวลาสั้นๆ เพื่อให้ระบบล่ม
3. **PortScan:** การกวาดตรวจหาพอร์ตที่เปิดอยู่เพื่อหาช่องโหว่
4. **BruteForce:** การพยายามสุ่มรหัสผ่าน (เช่น บนพอร์ต SSH 22)

---

## 📁 โครงสร้างโปรเจกต์แบบเข้าใจง่าย

```
Mini-project/
├── data.csv            # ชุดข้อมูลตัวอย่าง 3,000 แถว
├── generate_data.py    # สคริปต์สร้างข้อมูลจำลอง
├── train.py            # โค้ดฝึกสอนโมเดล Machine Learning (~45 บรรทัด)
├── model.pkl           # ไฟล์โมเดลที่ฝึกเสร็จแล้ว
├── app.py              # หน้าเว็บแดชบอร์ด Streamlit (~100 บรรทัด)
├── requirements.txt    # ไลบรารีที่จำเป็น
├── run_dashboard.bat   # ดับเบิลคลิกเพื่อเปิดหน้าเว็บทันที
└── README.md           # คำอธิบายโปรเจกต์
```

---

## ⚙️ ฟีเจอร์ที่ใช้ในการทำนาย (Features)
โมเดลใช้ตัวแปรทั้งหมด 5 ตัวในการตัดสินใจ:
* **`duration`**: ระยะเวลาการเชื่อมต่อ (วินาที)
* **`packets`**: จำนวนแพ็กเก็ตที่ส่ง
* **`bytes`**: ขนาดข้อมูลรวม (ไบต์)
* **`failed_logins`**: จำนวนครั้งที่ล็อกอินล้มเหลว
* **`port`**: พอร์ตเป้าหมาย (เช่น 80 = Web, 22 = SSH)

---

## 🚀 วิธีการรันโปรเจกต์ (Quickstart)

### 1. ติดตั้งไลบรารี
```bash
pip install -r requirements.txt
```

### 2. ฝึกสอนโมเดล (Train Model)
```bash
python train.py
```
*(ระบบจะอ่าน `data.csv`, เทรนโมเดล และเซฟออกมาเป็น `model.pkl`)*

### 3. เปิดหน้าเว็บแดชบอร์ด (Streamlit App)
```bash
streamlit run app.py
```
*(หรือดับเบิลคลิกที่ไฟล์ **`run_dashboard.bat`**)*

---

## 📊 ผลลัพธ์ความแม่นยำ
* **อัลกอริทึม:** Random Forest Classifier (100 Trees)
* **ความแม่นยำ (Accuracy):** 100.00% บนชุดข้อมูลทดสอบ (Test Set 20%)
