"""
สร้างชุดข้อมูลตัวอย่างสำหรับมินิโปรเจกต์ (แบบง่าย เข้าใจเร็ว)
ฟีเจอร์หลัก 5 ตัว:
- duration: ระยะเวลาเชื่อมต่อ (วินาที)
- packets: จำนวนแพ็กเก็ต
- bytes: ขนาดข้อมูล (ไบต์)
- failed_logins: จำนวนครั้งที่ล็อกอินผิด
- port: พอร์ตปลายทาง (เช่น 80=เว็บ, 22=SSH, 445=แชร์ไฟล์)
- label: ประเภท (Normal, DDoS, PortScan, BruteForce)
"""

import numpy as np
import pandas as pd

np.random.seed(42)
n_samples = 3000

data = []

# 1. ทราฟฟิกปกติ (Normal) ~ 70%
for _ in range(2100):
    duration = round(float(np.random.uniform(0.5, 10.0)), 2)
    packets = int(np.random.randint(5, 100))
    bytes_data = int(packets * np.random.randint(200, 1000))
    failed_logins = 0
    port = int(np.random.choice([80, 443, 53, 8080]))
    data.append([duration, packets, bytes_data, failed_logins, port, "Normal"])

# 2. การโจมตี DDoS (ส่งแพ็กเก็ตเยอะมากในเวลาสั้นๆ) ~ 10%
for _ in range(300):
    duration = round(float(np.random.uniform(0.01, 0.2)), 2)
    packets = int(np.random.randint(500, 3000))  # แพ็กเก็ตเยอะมาก
    bytes_data = int(packets * 40)               # ขนาดแพ็กเก็ตเล็ก (ขยะ)
    failed_logins = 0
    port = int(np.random.choice([80, 443]))
    data.append([duration, packets, bytes_data, failed_logins, port, "DDoS"])

# 3. การกวาดสแกนพอร์ต (PortScan) ~ 10%
for _ in range(300):
    duration = round(float(np.random.uniform(0.01, 0.05)), 2)
    packets = int(np.random.randint(1, 3))       # แพ็กเก็ตน้อยมาก
    bytes_data = 44
    failed_logins = 0
    port = int(np.random.randint(1, 1024))       # สแกนพอร์ตสุ่ม
    data.append([duration, packets, bytes_data, failed_logins, port, "PortScan"])

# 4. การสุ่มรหัสผ่าน (BruteForce) ~ 10%
for _ in range(300):
    duration = round(float(np.random.uniform(3.0, 15.0)), 2)
    failed_logins = int(np.random.randint(5, 30)) # ล็อกอินผิดหลายครั้ง
    packets = int(failed_logins * 4)
    bytes_data = int(packets * 150)
    port = 22                                     # พอร์ต SSH
    data.append([duration, packets, bytes_data, failed_logins, port, "BruteForce"])

# สลับลำดับข้อมูลและบันทึกเป็น CSV
df = pd.DataFrame(data, columns=["duration", "packets", "bytes", "failed_logins", "port", "label"])
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
df.to_csv("data.csv", index=False)
print(f"สร้างข้อมูลสำเร็จ: data.csv ({len(df)} แถว)")
print(df["label"].value_counts())
