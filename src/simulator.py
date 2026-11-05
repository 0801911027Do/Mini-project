"""
GoHard AI Threat Detection & Incident Decision Support System
Module: src/simulator.py
Real-time Network Traffic and Threat Injection Simulator.
Provides live interactive event feeds for the Streamlit dashboard and testing.
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Generator

from src.inference_engine import AIThreatEngine
from src.decision_engine import calculate_risk_score, get_mitigation_actions


class TrafficSimulator:
    """
    Simulates real-time network flow packets and allows on-demand attack injection.
    """
    def __init__(self, models_dir: str = "models"):
        self.engine = AIThreatEngine(models_dir)
        
    def generate_event(self, event_type: str = "Normal") -> Dict[str, Any]:
        """
        Generates a realistic synthetic network event of the specified type.
        Supports: 'Normal', 'DDoS_SynFlood', 'Port_Scan', 'SSH_BruteForce',
                  'Ransomware_LateralMovement', 'ZeroDay_Exploit'.
        """
        now = datetime.now()
        
        if event_type == "Normal":
            traffic_type = np.random.choice(["web", "dns", "db", "api"], p=[0.5, 0.2, 0.15, 0.15])
            src_ip = f"10.0.1.{np.random.randint(20, 200)}"
            if traffic_type == "web":
                dst_ip = f"{np.random.randint(50, 180)}.{np.random.randint(10, 200)}.14.88"
                dst_port = np.random.choice([80, 443])
                proto = "TCP"
                state = "ESTABLISHED"
                dur = float(np.random.uniform(0.1, 3.0))
                bytes_s = int(np.random.randint(500, 3000))
                bytes_r = int(np.random.randint(1000, 25000))
            elif traffic_type == "dns":
                dst_ip = "10.0.1.1"
                dst_port = 53
                proto = "UDP"
                state = "CLOSED"
                dur = 0.02
                bytes_s = 64
                bytes_r = 128
            elif traffic_type == "db":
                dst_ip = "10.0.1.100"
                dst_port = 3306
                proto = "TCP"
                state = "ESTABLISHED"
                dur = float(np.random.uniform(0.05, 1.0))
                bytes_s = int(np.random.randint(300, 2000))
                bytes_r = int(np.random.randint(800, 12000))
            else:
                dst_ip = "172.16.5.80"
                dst_port = 8080
                proto = "TCP"
                state = "ESTABLISHED"
                dur = 0.15
                bytes_s = 400
                bytes_r = 1500
                
            raw_event = {
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "source_ip": src_ip,
                "destination_ip": dst_ip,
                "source_port": int(np.random.randint(35000, 62000)),
                "destination_port": int(dst_port),
                "protocol": proto,
                "duration_sec": round(dur, 4),
                "bytes_sent": bytes_s,
                "bytes_received": bytes_r,
                "packets_sent": max(1, int(bytes_s / 600)),
                "packets_received": max(1, int(bytes_r / 900)),
                "failed_login_attempts": 0,
                "connection_state": state
            }
            
        elif event_type == "DDoS_SynFlood":
            raw_event = {
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "source_ip": "185.220.101.5",
                "destination_ip": "172.16.5.80",  # Web gateway
                "source_port": int(np.random.randint(1024, 65535)),
                "destination_port": 80,
                "protocol": "TCP",
                "duration_sec": 0.002,
                "bytes_sent": 54,
                "bytes_received": 0,
                "packets_sent": int(np.random.randint(150, 600)),
                "packets_received": 0,
                "failed_login_attempts": 0,
                "connection_state": "SYN_SENT"
            }
            
        elif event_type == "Port_Scan":
            raw_event = {
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "source_ip": "194.26.29.112",
                "destination_ip": "10.0.1.100",  # DB Server
                "source_port": int(np.random.randint(45000, 58000)),
                "destination_port": int(np.random.randint(21, 1024)),
                "protocol": "TCP",
                "duration_sec": 0.015,
                "bytes_sent": 44,
                "bytes_received": 0,
                "packets_sent": 1,
                "packets_received": 0,
                "failed_login_attempts": 0,
                "connection_state": "RESET"
            }
            
        elif event_type == "SSH_BruteForce":
            raw_event = {
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "source_ip": "45.142.214.8",
                "destination_ip": "10.0.1.10",  # Domain Controller
                "source_port": int(np.random.randint(32000, 48000)),
                "destination_port": 22,
                "protocol": "TCP",
                "duration_sec": 4.5,
                "bytes_sent": 5200,
                "bytes_received": 2800,
                "packets_sent": 40,
                "packets_received": 40,
                "failed_login_attempts": int(np.random.randint(12, 35)),
                "connection_state": "CLOSED"
            }
            
        elif event_type == "Ransomware_LateralMovement":
            raw_event = {
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "source_ip": "10.0.1.45",  # Compromised workstation
                "destination_ip": "10.0.1.120",  # File Server
                "source_port": int(np.random.randint(50000, 62000)),
                "destination_port": 445,  # SMB
                "protocol": "TCP",
                "duration_sec": 85.0,
                "bytes_sent": 45000000,  # 45 MB bulk upload
                "bytes_received": 12000000,
                "packets_sent": 5500,
                "packets_received": 3800,
                "failed_login_attempts": 1,
                "connection_state": "ESTABLISHED"
            }
            
        elif event_type == "ZeroDay_Exploit":
            raw_event = {
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "source_ip": "91.240.118.172",
                "destination_ip": "172.16.5.80",
                "source_port": int(np.random.randint(38000, 52000)),
                "destination_port": 8443,
                "protocol": "TCP",
                "duration_sec": 0.25,
                "bytes_sent": 18500,
                "bytes_received": 280,
                "packets_sent": 60,
                "packets_received": 2,
                "failed_login_attempts": 0,
                "connection_state": "ESTABLISHED"
            }
            
        else:
            raise ValueError(f"Unknown event type: {event_type}")

        # Analyze through AI engine
        analysis = self.engine.analyze_event(raw_event)
        
        # Calculate Risk and Mitigations
        risk_data = calculate_risk_score(
            verdict=analysis["verdict"],
            confidence=analysis["confidence"],
            dst_ip=raw_event["destination_ip"],
            anomaly_score=analysis["anomaly_score"]
        )
        mitigations = get_mitigation_actions(
            verdict=analysis["verdict"],
            src_ip=raw_event["source_ip"],
            dst_ip=raw_event["destination_ip"],
            dst_port=raw_event["destination_port"]
        )
        
        # Merge all into comprehensive processed record
        full_record = {
            **raw_event,
            **analysis,
            **risk_data,
            "mitigations": mitigations
        }
        return full_record

