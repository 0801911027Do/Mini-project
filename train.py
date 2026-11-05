"""
โค้ดเทรนโมเดล Machine Learning แบบง่าย สำหรับมินิโปรเจกต์
ใช้ขั้นตอนมาตรฐาน 5 ขั้นตอน:
1. โหลดข้อมูล (Load Data)
2. แยกฟีเจอร์และคลาสเป้าหมาย (Features & Target)
3. แบ่งชุดข้อมูล Train / Test (Train/Test Split)
4. ฝึกสอนโมเดล (Train Model ด้วย Random Forest)
5. ประเมินผลและบันทึกโมเดล (Evaluate & Save Model)
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

# ----------------------------------------------------
# 1. โหลดข้อมูล
# ----------------------------------------------------
print("1. กำลังโหลดข้อมูลจาก data.csv...")
df = pd.read_csv("data.csv")

# ----------------------------------------------------
# 2. กำหนด Features (X) และ Target (y)
# ----------------------------------------------------
features = ["duration", "packets", "bytes", "failed_logins", "port"]
X = df[features]
y = df["label"]

# ----------------------------------------------------
# 3. แบ่งข้อมูลเป็น Train 80% และ Test 20%
# ----------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ----------------------------------------------------
# 4. ฝึกสอนโมเดล (ใช้ Random Forest เข้าใจง่ายและแม่นยำ)
# ----------------------------------------------------
print("2. กำลังฝึกสอนโมเดล Random Forest...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# ----------------------------------------------------
# 5. ทดสอบและวัดผลความแม่นยำ
# ----------------------------------------------------
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)

print("\n" + "="*40)
print(f"ผลการทดสอบโมเดล: ความแม่นยำ (Accuracy) = {acc:.2%}")
print("="*40)
print(classification_report(y_test, y_pred))

# ----------------------------------------------------
# 6. บันทึกโมเดลเก็บไว้ใช้งานบนเว็บแอป
# ----------------------------------------------------
joblib.dump(model, "model.pkl")
print("บันทึกโมเดลเรียบร้อยแล้ว: model.pkl")
