"""
ขั้นตอนที่ 1: แปลงข้อมูลดิบจาก Wireshark (raw_packets.csv) ให้เป็น Feature Vector รายช่วงเวลา (Time Window)
พร้อมติดเฉลย (Data Labeling) จากไฟล์ attack_ground_truth.csv อัตโนมัติ

หากยังไม่มีไฟล์ raw_packets.csv จาก Wireshark จริง สคริปต์จะสร้างชุดข้อมูลจำลองจากวง LAN 3 เครื่อง
(192.168.10.10 = Victim, 192.168.10.20 = Normal User, 192.168.10.30 = Attacker)
ที่มีสัดส่วน Imbalanced Data สมจริง (Normal ~93% : Attack ~7%) เพื่อให้ทดสอบ Pipeline ได้ทันที
"""

import os
import numpy as np
import pandas as pd


LAB_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_PACKETS_CSV = os.path.join(LAB_DIR, "raw_packets.csv")
GROUND_TRUTH_CSV = os.path.join(LAB_DIR, "attack_ground_truth.csv")
WINDOW_INSPECT_CSV = os.path.join(LAB_DIR, "window_inspection_with_time.csv")
FEATURE_VECTORS_CSV = os.path.join(LAB_DIR, "ddos_feature_vectors.csv")


def generate_realistic_wireshark_capture_if_missing():
    """
    สร้างข้อมูลจำลองระดับแพ็กเกจ (Packet-level) เหมือนได้จากคำสั่ง:
    tshark -r capture.pcap -T fields -e frame.time_epoch -e ip.src -e ip.dst
           -e _ws.col.Protocol -e frame.len -e tcp.flags.syn -e tcp.flags.ack
    ครอบคลุมเวลา 1,200 วินาที (20 นาที) โดยมีช่วงยิง DDoS เพียง 3 รอบสั้นๆ (Imbalanced Data ~7% Attack)
    """
    np.random.seed(42)
    base_epoch = 1730912400.0  # ตัวอย่าง Unix Timestamp เริ่มต้นการทดลอง
    total_seconds = 1200       # 1,200 วินาที (1,200 Time Windows)

    # กำหนดช่วงเวลาที่เครื่องที่ 3 (192.168.10.30) ยิง DDoS 3 รอบ (รวม 84 วินาที = 7.0% ของเวลาทั้งหมด)
    attack_windows = [
        (1, "DDoS_SYN_Flood",  base_epoch + 180.0, base_epoch + 208.0),  # รอบที่ 1: 28 วินาที
        (2, "DDoS_HTTP_Flood", base_epoch + 540.0, base_epoch + 568.0),  # รอบที่ 2: 28 วินาที
        (3, "DDoS_SYN_Flood",  base_epoch + 920.0, base_epoch + 948.0),  # รอบที่ 3: 28 วินาที
    ]

    # บันทึกตารางเฉลย attack_ground_truth.csv
    gt_rows = []
    for wid, atype, s_ep, e_ep in attack_windows:
        gt_rows.append({
            "wave_id": wid,
            "attack_type": atype,
            "start_epoch": s_ep,
            "end_epoch": e_ep,
            "duration_sec": int(e_ep - s_ep),
        })
    pd.DataFrame(gt_rows).to_csv(GROUND_TRUTH_CSV, index=False)

    packets = []
    victim_ip = "192.168.1.10"
    attacker_ip = "192.168.1.20"
    normal_ips = ["192.168.1.30", "192.168.1.31"]

    for sec in range(total_seconds):
        cur_sec_epoch = base_epoch + float(sec)

        # ตรวจสอบว่าวินาทีนี้อยู่ในช่วงถูกโจมตีหรือไม่
        active_attack = None
        for _, atype, s_ep, e_ep in attack_windows:
            if s_ep <= cur_sec_epoch < e_ep:
                active_attack = atype
                break

        # 1. ทราฟฟิกปกติจากเครื่องที่ 2 (เกิดขึ้นตลอดเวลาทั้งช่วงปกติและช่วงถูกโจมตี)
        # มีโอกาส 3% ที่ผู้ใช้ปกติโหลดหน้าเว็บหนักๆ หรือดึงไฟล์พร้อมกัน (Flash Crowd / Heavy Burst)
        is_normal_burst = (np.random.rand() < 0.03)
        n_normal_pkts = np.random.randint(45, 115) if is_normal_burst else np.random.randint(4, 26)

        for _ in range(n_normal_pkts):
            pkt_time = cur_sec_epoch + np.random.uniform(0.001, 0.999)
            src_ip = np.random.choice(normal_ips)
            proto = np.random.choice(["HTTP", "TCP", "TLSv1.3", "DNS"], p=[0.35, 0.35, 0.20, 0.10])
            # หากเป็นช่วง Burst ปกติ บางครั้งส่ง TCP/HTTP รัวๆ ขนาดใกล้เคียงกัน
            if is_normal_burst and np.random.rand() < 0.45:
                pkt_len = int(np.random.randint(60, 175))
                syn_flag = 1 if np.random.rand() < 0.42 else 0
            else:
                pkt_len = int(np.random.choice([
                    np.random.randint(54, 180),
                    np.random.randint(250, 850),
                    np.random.randint(1000, 1500),
                ], p=[0.4, 0.3, 0.3]))
                syn_flag = 1 if (proto in ["TCP", "HTTP"] and np.random.rand() < 0.12) else 0
            ack_flag = 1 if syn_flag == 0 and proto != "DNS" else 0
            packets.append([round(pkt_time, 6), src_ip, victim_ip, proto, pkt_len, syn_flag, ack_flag])

        # 2. หากอยู่ในช่วงเวลาโจมตี (Attack Window) เครื่องที่ 3 จะยิงแพ็กเกจถล่มเข้ามา
        if active_attack is not None:
            # วินาทีแรกและวินาทีสุดท้ายของคลื่นโจมตี (Ramp-up / Ramp-down) แพ็กเกจยังไม่หนาแน่นมาก
            is_ramp = (np.random.rand() < 0.22)
            n_attack_pkts = np.random.randint(18, 58) if is_ramp else np.random.randint(110, 320)

            for _ in range(n_attack_pkts):
                pkt_time = cur_sec_epoch + np.random.uniform(0.0001, 0.9999)
                if active_attack == "DDoS_SYN_Flood":
                    proto = "TCP"
                    pkt_len = int(np.random.randint(54, 78)) if not is_ramp else int(np.random.randint(54, 260))
                    syn_flag = 1 if np.random.rand() < (0.50 if is_ramp else 0.85) else 0
                    ack_flag = 1 - syn_flag
                else:
                    proto = "HTTP"
                    pkt_len = int(np.random.randint(110, 210)) if not is_ramp else int(np.random.randint(90, 480))
                    syn_flag = 1 if np.random.rand() < 0.32 else 0
                    ack_flag = 1

                packets.append([round(pkt_time, 6), attacker_ip, victim_ip, proto, pkt_len, syn_flag, ack_flag])

    df_raw = pd.DataFrame(
        packets,
        columns=[
            "frame.time_epoch",
            "ip.src",
            "ip.dst",
            "_ws.col.Protocol",
            "frame.len",
            "tcp.flags.syn",
            "tcp.flags.ack",
        ],
    )
    df_raw = df_raw.sort_values("frame.time_epoch").reset_index(drop=True)
    df_raw.to_csv(RAW_PACKETS_CSV, index=False)
    print(f"[สร้างข้อมูล Wireshark จำลองสำเร็จ] {RAW_PACKETS_CSV} ({len(df_raw):,} แพ็กเกจ)")


def convert_packets_to_time_windows(window_size: float = 1.0):
    """
    แปลงข้อมูลระดับแพ็กเกจ (Packet-level) เป็น Feature Vector ระดับช่วงเวลา (Window-level)
    """
    if not os.path.exists(RAW_PACKETS_CSV) or not os.path.exists(GROUND_TRUTH_CSV):
        generate_realistic_wireshark_capture_if_missing()

    print(f"1. กำลังโหลดข้อมูลดิบจาก Wireshark: {RAW_PACKETS_CSV}")
    df = pd.read_csv(RAW_PACKETS_CSV)
    gt_df = pd.read_csv(GROUND_TRUTH_CSV)

    # แปลงค่าว่างในคอลัมน์ TCP flags ให้เป็น 0
    df["tcp.flags.syn"] = df["tcp.flags.syn"].fillna(0).astype(int)
    df["tcp.flags.ack"] = df["tcp.flags.ack"].fillna(0).astype(int)

    # เรียงลำดับตามเวลา และคำนวณ Inter-Arrival Time (IAT)
    df = df.sort_values("frame.time_epoch").reset_index(drop=True)
    df["iat"] = df["frame.time_epoch"].diff().fillna(0).clip(lower=0)

    # 2. สร้างคอลัมน์สำหรับแบ่ง Time Window (หั่นทุกๆ window_size วินาที)
    df["window_id"] = (df["frame.time_epoch"] // window_size) * window_size

    # 3. ยุบรวมแพ็กเกจในแต่ละ Window ให้กลายเป็น Feature Vector (Aggregation)
    features = (
        df.groupby("window_id")
        .agg(
            packet_count=("frame.len", "count"),
            total_bytes=("frame.len", "sum"),
            mean_packet_len=("frame.len", "mean"),
            std_packet_len=("frame.len", "std"),
            mean_iat=("iat", "mean"),
            syn_count=("tcp.flags.syn", "sum"),
            ack_count=("tcp.flags.ack", "sum"),
            unique_src_ips=("ip.src", "nunique"),
        )
        .reset_index()
    )

    # จัดการค่า NaN (กรณีใน Window นั้นมีแค่ 1 แพ็กเกจ ค่า std จะเป็น NaN)
    features["std_packet_len"] = features["std_packet_len"].fillna(0)

    # สร้างฟีเจอร์สัดส่วน (Ratio)
    features["syn_ratio"] = features["syn_count"] / features["packet_count"]
    features["ack_ratio"] = features["ack_count"] / features["packet_count"]

    # 4. การใส่เฉลย (Data Labeling) ตามช่วงเวลาใน attack_ground_truth.csv
    features["label"] = 0  # 0 = Normal
    features["attack_name"] = "Normal"

    for _, row in gt_df.iterrows():
        s_ep = float(row["start_epoch"])
        e_ep = float(row["end_epoch"])
        atype = str(row["attack_type"])
        mask = (features["window_id"] >= s_ep) & (features["window_id"] < e_ep)
        features.loc[mask, "label"] = 1  # 1 = DDoS Attack
        features.loc[mask, "attack_name"] = atype

    # บันทึกไฟล์ที่มี window_id เก็บไว้สำหรับพล็อตกราฟ Timeline บน Dashboard
    features.to_csv(WINDOW_INSPECT_CSV, index=False)

    # 5. ลบคอลัมน์เวลา (window_id) และชื่อคลาสข้อความออกก่อนนำไปเทรน
    # เพื่อป้องกันไม่ให้โมเดลจำเวลาเกิดเหตุ (ป้องกัน Data Leakage / Overfitting)
    model_dataset = features.drop(columns=["window_id", "attack_name"])
    model_dataset.to_csv(FEATURE_VECTORS_CSV, index=False)

    n_total = len(model_dataset)
    n_attack = int((model_dataset["label"] == 1).sum())
    n_normal = n_total - n_attack
    print("=" * 65)
    print(f"แปลงเป็น Feature Vector สำเร็จ: {FEATURE_VECTORS_CSV}")
    print(f"จำนวน Time Windows ทั้งหมด : {n_total:,} วินาที")
    print(f"  - ช่วงเวลาปกติ (Normal = 0) : {n_normal:,} วินาที ({n_normal / n_total:.1%})")
    print(f"  - ช่วงถูกโจมตี (Attack = 1) : {n_attack:,} วินาที ({n_attack / n_total:.1%}) -> Imbalanced Data!")
    print("=" * 65)
    return model_dataset


if __name__ == "__main__":
    convert_packets_to_time_windows(window_size=1.0)
