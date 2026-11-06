"""
สคริปต์สำหรับเครื่องที่ 1: เครื่องเป้าหมาย (Victim / Web Server) — IP: 192.168.1.10
หน้าที่:
1. เปิด Web Server รอรับการเชื่อมต่อจากเครื่องเพื่อนในวง Wi-Fi / Hotspot เดียวกัน
2. แสดง IP Address ของเครื่องตัวเองอัตโนมัติ เพื่อให้บอกเพื่อนเครื่องที่ 2 และ 3 ได้ทันที
3. ขณะรันสคริปต์นี้ ให้เปิดโปรแกรม Wireshark คู่กันเพื่อดักจับแพ็กเกจทั้งหมด
"""

import socket
import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "192.168.1.10"


class LabHTTPHandler(SimpleHTTPRequestHandler):
    def log_message(self, format_str, *args):
        now_str = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        client_ip = self.client_address[0]
        print(f"[{now_str}] แพ็กเกจวิ่งเข้าจาก IP: {client_ip:<15} | {format_str % args}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Machine 1: Victim Web Server for Wireshark Capture")
    parser.add_argument("--port", type=int, default=8000, help="พอร์ตสำหรับรัน Web Server (ค่าเริ่มต้น: 8000)")
    args = parser.parse_args()

    my_ip = get_local_ip()
    print("=" * 70)
    print("  🖥️ เครื่องที่ 1: เครื่องเป้าหมาย (Victim / Web Server) พร้อมทำงาน!")
    print("=" * 70)
    print(f"  📌 IP ของเครื่องนี้คือ : {my_ip}  (พอร์ต {args.port})")
    print(f"  📌 URL สำหรับทดสอบ : http://{my_ip}:{args.port}")
    print("-" * 70)
    print("  สิ่งที่ต้องทำต่อ:")
    print("  1. เปิดโปรแกรม Wireshark บนเครื่องนี้ -> เลือก Wi-Fi / LAN -> กดปุ่มฉลามสีฟ้า")
    print(f"  2. บอกเพื่อนเครื่องที่ 2 (Attacker) ให้รัน: python lan_lab/machine3_attacker_ddos.py --target {my_ip} --port {args.port}")
    print(f"  3. บอกเพื่อนเครื่องที่ 3 (Normal)   ให้รัน: python lan_lab/machine2_normal_traffic.py --target {my_ip} --port {args.port}")
    print("=" * 70)

    server = HTTPServer(("0.0.0.0", args.port), LabHTTPHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Victim Server] ปิดเซิร์ฟเวอร์เรียบร้อย")
        server.server_close()
