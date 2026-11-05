"""
GoHard AI Threat Detection & Incident Decision Support System
Module: src/data_generator.py
Generates realistic enterprise network traffic and cybersecurity event logs.
Includes Normal traffic baseline and multi-vector attack scenarios (DDoS, PortScan,
SSH BruteForce, Ransomware Lateral Movement, and novel Zero-day anomalies).
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os


def generate_security_logs(
    num_records: int = 15000,
    attack_ratio: float = 0.05,
    random_seed: int = 42,
    output_path: str = "data/raw/security_logs.csv"
) -> pd.DataFrame:
    """
    Generates time-ordered enterprise network security logs.
    Realistic imbalance: ~95% Normal traffic, ~5% Attacks across 5 attack types.
    """
    np.random.seed(random_seed)
    
    start_time = datetime(2026, 11, 1, 8, 0, 0)
    
    # Internal enterprise subnets and external ranges
    internal_subnets = ["10.0.1.", "10.0.2.", "192.168.10.", "172.16.5."]
    external_ips = [f"{np.random.randint(45, 200)}.{np.random.randint(10, 250)}.{np.random.randint(1, 254)}.{np.random.randint(1, 254)}" for _ in range(50)]
    
    # Critical enterprise assets
    db_server = "10.0.1.100"
    file_server = "10.0.1.120"
    domain_controller = "10.0.1.10"
    web_server = "172.16.5.80"
    
    num_attacks = int(num_records * attack_ratio)
    num_normal = num_records - num_attacks
    
    records = []
    
    # 1. Generate Normal Traffic
    # Generate cumulative timestamps across the entire timeline
    deltas = np.random.exponential(scale=2.0, size=num_normal)
    cum_seconds = np.cumsum(deltas)
    total_timeline_sec = float(cum_seconds[-1])
    
    for i in range(num_normal):
        timestamp = start_time + timedelta(seconds=float(cum_seconds[i]))
        
        traffic_type = np.random.choice(["web_browsing", "dns_query", "db_query", "file_share", "internal_api"], 
                                        p=[0.45, 0.20, 0.15, 0.10, 0.10])
        
        src_ip = f"{np.random.choice(internal_subnets)}{np.random.randint(15, 220)}"
        proto = "TCP"
        state = "ESTABLISHED"
        failed_logins = 0
        
        if traffic_type == "web_browsing":
            dst_ip = np.random.choice(external_ips)
            dst_port = np.random.choice([80, 443], p=[0.2, 0.8])
            duration = np.random.exponential(scale=2.5) + 0.1
            bytes_sent = int(np.random.lognormal(mean=7.0, sigma=1.0))
            bytes_recv = int(np.random.lognormal(mean=9.5, sigma=1.2))
            pkts_sent = max(2, int(bytes_sent / np.random.uniform(200, 800)))
            pkts_recv = max(2, int(bytes_recv / np.random.uniform(400, 1400)))
            
        elif traffic_type == "dns_query":
            dst_ip = "10.0.1.1"  # Internal DNS resolver
            dst_port = 53
            proto = "UDP"
            duration = np.random.uniform(0.01, 0.1)
            bytes_sent = np.random.randint(40, 120)
            bytes_recv = np.random.randint(60, 400)
            pkts_sent = 1
            pkts_recv = 1
            state = "CLOSED"
            
        elif traffic_type == "db_query":
            dst_ip = db_server
            dst_port = np.random.choice([3306, 5432])
            duration = np.random.exponential(scale=1.2) + 0.05
            bytes_sent = int(np.random.lognormal(mean=6.5, sigma=0.8))
            bytes_recv = int(np.random.lognormal(mean=8.5, sigma=1.0))
            pkts_sent = max(3, int(bytes_sent / 500))
            pkts_recv = max(5, int(bytes_recv / 600))
            
        elif traffic_type == "file_share":
            dst_ip = file_server
            dst_port = 445
            duration = np.random.exponential(scale=15.0) + 0.5
            bytes_sent = int(np.random.lognormal(mean=8.0, sigma=1.5))
            bytes_recv = int(np.random.lognormal(mean=9.0, sigma=1.5))
            pkts_sent = max(5, int(bytes_sent / 1000))
            pkts_recv = max(5, int(bytes_recv / 1000))
            
        else:  # internal API
            dst_ip = web_server
            dst_port = 8080
            duration = np.random.exponential(scale=0.8) + 0.02
            bytes_sent = np.random.randint(200, 2000)
            bytes_recv = np.random.randint(500, 15000)
            pkts_sent = max(2, int(bytes_sent / 300))
            pkts_recv = max(3, int(bytes_recv / 500))
            
        src_port = np.random.randint(30000, 65000)
        
        records.append({
            "timestamp": timestamp,
            "source_ip": src_ip,
            "destination_ip": dst_ip,
            "source_port": src_port,
            "destination_port": dst_port,
            "protocol": proto,
            "duration_sec": round(duration, 4),
            "bytes_sent": max(10, bytes_sent),
            "bytes_received": max(10, bytes_recv),
            "packets_sent": max(1, pkts_sent),
            "packets_received": max(1, pkts_recv),
            "failed_login_attempts": failed_logins,
            "connection_state": state,
            "threat_label": "Normal",
            "is_attack": 0
        })

    # 2. Generate Attack Scenarios across multiple time waves
    attack_types = ["DDoS_SynFlood", "Port_Scan", "SSH_BruteForce", "Ransomware_LateralMovement", "ZeroDay_Exploit"]
    attack_counts = {
        "DDoS_SynFlood": int(num_attacks * 0.35),
        "Port_Scan": int(num_attacks * 0.25),
        "SSH_BruteForce": int(num_attacks * 0.20),
        "Ransomware_LateralMovement": int(num_attacks * 0.12),
        "ZeroDay_Exploit": num_attacks - (int(num_attacks * 0.35) + int(num_attacks * 0.25) + int(num_attacks * 0.20) + int(num_attacks * 0.12))
    }
    
    # Calculate total duration of normal traffic to spread attacks across whole timeline
    max_time_sec = total_timeline_sec
    
    attack_records = []
    
    # 2a. DDoS SYN Flood (Multiple waves across timeline)
    attacker_ip_ddos = "185.220.101.5"
    for _ in range(attack_counts["DDoS_SynFlood"]):
        # Spread in 3 distinct waves (early, mid, late)
        wave_offset = np.random.choice([0.15, 0.50, 0.85]) * max_time_sec
        ts = start_time + timedelta(seconds=wave_offset + np.random.uniform(-300, 300))
        attack_records.append({
            "timestamp": ts,
            "source_ip": attacker_ip_ddos,
            "destination_ip": web_server,
            "source_port": np.random.randint(1024, 65535),
            "destination_port": 80,
            "protocol": "TCP",
            "duration_sec": round(np.random.uniform(0.001, 0.05), 4),
            "bytes_sent": np.random.randint(40, 64),
            "bytes_received": 0,
            "packets_sent": np.random.randint(50, 400),
            "packets_received": 0,
            "failed_login_attempts": 0,
            "connection_state": "SYN_SENT",
            "threat_label": "DDoS_SynFlood",
            "is_attack": 1
        })
        
    # 2b. Port Scan (Periodic reconnaissance sweeps)
    scanner_ip = "194.26.29.112"
    scan_target = db_server
    scanned_ports = np.random.choice(range(1, 1024), size=attack_counts["Port_Scan"], replace=True)
    for port in scanned_ports:
        wave_offset = np.random.choice([0.10, 0.40, 0.78]) * max_time_sec
        ts = start_time + timedelta(seconds=wave_offset + np.random.uniform(-400, 400))
        attack_records.append({
            "timestamp": ts,
            "source_ip": scanner_ip,
            "destination_ip": scan_target,
            "source_port": np.random.randint(40000, 60000),
            "destination_port": int(port),
            "protocol": "TCP",
            "duration_sec": round(np.random.uniform(0.005, 0.08), 4),
            "bytes_sent": 44,
            "bytes_received": 0,
            "packets_sent": 1,
            "packets_received": np.random.choice([0, 1], p=[0.7, 0.3]),
            "failed_login_attempts": 0,
            "connection_state": "RESET",
            "threat_label": "Port_Scan",
            "is_attack": 1
        })
        
    # 2c. SSH Brute Force (Targeting domain controller & servers across time)
    brute_ip = "45.142.214.8"
    for _ in range(attack_counts["SSH_BruteForce"]):
        wave_offset = np.random.choice([0.25, 0.60, 0.82]) * max_time_sec
        ts = start_time + timedelta(seconds=wave_offset + np.random.uniform(-500, 500))
        failed_attempts = np.random.randint(5, 35)
        attack_records.append({
            "timestamp": ts,
            "source_ip": brute_ip,
            "destination_ip": domain_controller,
            "source_port": np.random.randint(30000, 60000),
            "destination_port": 22,
            "protocol": "TCP",
            "duration_sec": round(np.random.uniform(1.5, 8.0), 4),
            "bytes_sent": np.random.randint(1500, 8000),
            "bytes_received": np.random.randint(800, 4000),
            "packets_sent": failed_attempts * 2,
            "packets_received": failed_attempts * 2,
            "failed_login_attempts": failed_attempts,
            "connection_state": "CLOSED",
            "threat_label": "SSH_BruteForce",
            "is_attack": 1
        })
        
    # 2d. Ransomware Lateral Movement
    compromised_host = "10.0.1.45"
    for _ in range(attack_counts["Ransomware_LateralMovement"]):
        wave_offset = np.random.choice([0.30, 0.70, 0.90]) * max_time_sec
        ts = start_time + timedelta(seconds=wave_offset + np.random.uniform(-600, 600))
        target = np.random.choice([file_server, db_server, domain_controller])
        port = np.random.choice([445, 3389])
        attack_records.append({
            "timestamp": ts,
            "source_ip": compromised_host,
            "destination_ip": target,
            "source_port": np.random.randint(49152, 65535),
            "destination_port": port,
            "protocol": "TCP",
            "duration_sec": round(np.random.uniform(25.0, 120.0), 4),
            "bytes_sent": int(np.random.lognormal(mean=12.5, sigma=1.0)),  # Massive internal upload
            "bytes_received": int(np.random.lognormal(mean=11.0, sigma=1.0)),
            "packets_sent": np.random.randint(1500, 8000),
            "packets_received": np.random.randint(1200, 6000),
            "failed_login_attempts": np.random.choice([0, 1, 2], p=[0.7, 0.2, 0.1]),
            "connection_state": "ESTABLISHED",
            "threat_label": "Ransomware_LateralMovement",
            "is_attack": 1
        })
        
    # 2e. Zero-Day Exploit (Novel anomaly)
    zeroday_attacker = "91.240.118.172"
    for _ in range(attack_counts["ZeroDay_Exploit"]):
        wave_offset = np.random.choice([0.35, 0.65, 0.92]) * max_time_sec
        ts = start_time + timedelta(seconds=wave_offset + np.random.uniform(-400, 400))
        attack_records.append({
            "timestamp": ts,
            "source_ip": zeroday_attacker,
            "destination_ip": web_server,
            "source_port": np.random.randint(35000, 55000),
            "destination_port": 8443,  # unusual admin API port
            "protocol": "TCP",
            "duration_sec": round(np.random.uniform(0.08, 0.6), 4),
            "bytes_sent": np.random.randint(8500, 25000),  # unusual payload size
            "bytes_received": np.random.randint(150, 400),
            "packets_sent": np.random.randint(25, 80),
            "packets_received": 2,
            "failed_login_attempts": 0,
            "connection_state": "ESTABLISHED",
            "threat_label": "ZeroDay_Exploit",
            "is_attack": 1
        })

    # Combine and sort by timestamp to preserve temporal integrity
    all_records = records + attack_records
    df = pd.DataFrame(all_records)
    df.sort_values(by="timestamp", inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    # Save to disk
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[+] Security logs generated: {len(df)} records saved to {output_path}")
    print(f"    - Normal: {(df['is_attack'] == 0).sum()} ({(df['is_attack'] == 0).mean():.1%})")
    print(f"    - Attack: {(df['is_attack'] == 1).sum()} ({(df['is_attack'] == 1).mean():.1%})")
    print("    - Attack breakdown:\n", df[df['is_attack'] == 1]['threat_label'].value_counts().to_string())
    
    return df


if __name__ == "__main__":
    generate_security_logs()
