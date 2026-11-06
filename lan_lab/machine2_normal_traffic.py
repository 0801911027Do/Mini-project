"""
สคริปต์สำหรับเครื่องที่ 2: Normal User (IP: 192.168.10.20)
หน้าที่: จำลองพฤติกรรมผู้ใช้งานปกติในวง LAN ส่ง HTTP Request ไปยังเครื่อง Victim (192.168.10.10)
ด้วยจังหวะเวลาสุ่ม (0.5 - 3.5 วินาที) และขนาดคำขอที่หลากหลาย เพื่อให้ Wireshark ดักจับเป็นคลาส Normal (0)
"""

import time
import random
import argparse
import urllib.request
import urllib.error
from datetime import datetime


def run_normal_traffic(target_ip: str, port: int, duration_sec: int):
    base_url = f"http://{target_ip}:{port}"
    endpoints = [
        "/",
        "/index.html",
        "/about.html",
        "/assets/logo.png",
        "/api/status?user=normal_client",
        "/docs/manual.pdf",
    ]

    print("=" * 65)
    print(f"[Normal User] เริ่มจำลองผู้ใช้งานปกติไปยัง {base_url}")
    print(f"[Normal User] ระยะเวลาทำงาน: {duration_sec} วินาที (กด Ctrl+C เพื่อหยุด)")
    print("=" * 65)

    start_ts = time.time()
    req_count = 0

    try:
        while (time.time() - start_ts) < duration_sec:
            path = random.choice(endpoints)
            url = f"{base_url}{path}"
            now_str = datetime.now().strftime("%H:%M:%S.%f")[:-3]

            try:
                req = urllib.request.Request(
                    url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) NormalClient/1.0",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    },
                )
                with urllib.request.urlopen(req, timeout=2.0) as resp:
                    _ = resp.read(512)
                    req_count += 1
                    print(f"[{now_str}] GET {path:<28} -> HTTP {resp.status} (Total: {req_count})")
            except Exception as exc:
                req_count += 1
                print(f"[{now_str}] GET {path:<28} -> Sent ({type(exc).__name__})")

            # หน่วงเวลาสุ่มเหมือนมนุษย์ใช้งานจริง (ทำให้ Inter-Arrival Time หรือ IAT มีค่าสูงและกระจายตัว)
            sleep_time = random.uniform(0.5, 3.0)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n[Normal User] หยุดการทำงานโดยผู้ใช้")

    print("=" * 65)
    print(f"[Normal User] เสร็จสิ้นการจำลอง ส่งคำขอปกติทั้งหมด {req_count} รายการ")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Normal User Traffic Generator for 3-Machine LAN Lab")
    parser.add_argument("--target", default="192.168.1.10", help="IP ของเครื่องที่ 1 (Victim)")
    parser.add_argument("--port", type=int, default=8000, help="พอร์ตของ Web Server บนเครื่องที่ 1")
    parser.add_argument("--duration", type=int, default=600, help="ระยะเวลารันทั้งหมด (วินาที)")
    args = parser.parse_args()

    run_normal_traffic(args.target, args.port, args.duration)
