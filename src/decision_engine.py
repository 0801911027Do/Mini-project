"""
GoHard AI Threat Detection & Incident Decision Support System
Module: src/decision_engine.py
Incident Decision Support System:
  - Risk Scoring (0 to 100) combining threat type, confidence, and asset criticality
  - Automated Mitigation Action Calculator (Containment & Response)
  - Attack Chain Reconstruction (Multi-Stage Cyber Attack Storyline)
"""

from typing import Dict, Any, List
from datetime import datetime


# Asset Criticality Directory
CRITICAL_ASSETS = {
    "10.0.1.10": {"name": "Domain Controller (AD DS)", "tier": 1, "criticality_multiplier": 1.35},
    "10.0.1.100": {"name": "Production Database Server", "tier": 1, "criticality_multiplier": 1.30},
    "10.0.1.120": {"name": "Central File Server (Storage)", "tier": 2, "criticality_multiplier": 1.25},
    "172.16.5.80": {"name": "Public Web Application Gateway", "tier": 2, "criticality_multiplier": 1.15},
}

# Base Threat Severity Matrix
THREAT_SEVERITY_WEIGHTS = {
    "Ransomware_LateralMovement": 95,
    "ZeroDay_Exploit": 90,
    "DDoS_SynFlood": 85,
    "SSH_BruteForce": 75,
    "Port_Scan": 55,
    "Normal": 5
}


def calculate_risk_score(verdict: str, confidence: float, dst_ip: str, anomaly_score: float = 0.0) -> Dict[str, Any]:
    """
    Computes holistic enterprise risk score (0 - 100) and severity category.
    """
    base_weight = THREAT_SEVERITY_WEIGHTS.get(verdict, 50)
    
    # Asset Context
    asset_info = CRITICAL_ASSETS.get(dst_ip, {"name": "Standard Endpoint / Server", "tier": 3, "criticality_multiplier": 1.0})
    multiplier = asset_info["criticality_multiplier"]
    
    # Combine threat weight, model confidence, and asset multiplier
    if verdict == "Normal":
        raw_score = 5 * (1.0 + anomaly_score * 0.5)
    else:
        raw_score = (base_weight * confidence * 0.75) + (anomaly_score * 25)
        raw_score *= multiplier
        
    final_score = int(min(100, max(0, round(raw_score))))
    
    # Severity classification
    if final_score >= 85:
        severity = "CRITICAL"
        color = "#FF2B2B"  # Red
    elif final_score >= 70:
        severity = "HIGH"
        color = "#FF7A00"  # Orange
    elif final_score >= 40:
        severity = "MEDIUM"
        color = "#FFA800"  # Amber
    else:
        severity = "LOW"
        color = "#00D26A"  # Green
        
    return {
        "risk_score": final_score,
        "severity": severity,
        "severity_color": color,
        "target_asset_name": asset_info["name"],
        "asset_tier": asset_info["tier"]
    }


def get_mitigation_actions(verdict: str, src_ip: str, dst_ip: str, dst_port: int) -> List[Dict[str, str]]:
    """
    Returns prioritized automated & recommended countermeasures for SOC/CISO approval.
    """
    if verdict == "Ransomware_LateralMovement":
        return [
            {
                "action_id": "ACT_ISOLATE_HOST",
                "title": f"สั่งกักกันเครื่องแม่ข่าย {src_ip} ทันที (Host Isolation)",
                "description": "ตัดการเชื่อมต่อเครือข่ายของโฮสต์ต้นทางผ่าน EDR/Firewall ทันที เพื่อสกัดกั้นการแพร่ระบาดของ Ransomware สู่โฮสต์อื่น",
                "type": "CONTAINMENT",
                "risk_reduction": "95%",
                "auto_executable": True
            },
            {
                "action_id": "ACT_BLOCK_SMB",
                "title": f"ระงับทราฟฟิก SMB/RDP ระหว่างเครื่องภายในบนพอร์ต {dst_port}",
                "description": "บล็อกการเข้าถึง File Share ชั่วคราว และกระตุ้นระบบ Snapshot Backup เพื่อปกป้องไฟล์สำคัญ",
                "type": "PREVENTION",
                "risk_reduction": "85%",
                "auto_executable": True
            }
        ]
    elif verdict == "DDoS_SynFlood":
        return [
            {
                "action_id": "ACT_BLOCK_IP_PERIMETER",
                "title": f"บล็อก IP ผู้โจมตี {src_ip} ที่ Ingress Firewall",
                "description": "เพิ่ม Blacklist Rule บน Edge Router/Firewall เพื่อหยุดแพ็กเก็ตขยะตั้งแต่ขอบเขตเครือข่าย",
                "type": "CONTAINMENT",
                "risk_reduction": "90%",
                "auto_executable": True
            },
            {
                "action_id": "ACT_RATE_LIMIT",
                "title": f"เปิดใช้งาน SYN Flood Protection / Rate-Limiting พอร์ต {dst_port}",
                "description": "จำกัดอัตราการเชื่อมต่อใหม่ไม่ให้เกิน 100 SYN/วินาที เพื่อรักษาความต่อเนื่องของบริการ",
                "type": "RATE_LIMIT",
                "risk_reduction": "75%",
                "auto_executable": True
            }
        ]
    elif verdict == "SSH_BruteForce":
        return [
            {
                "action_id": "ACT_FAIL2BAN",
                "title": f"บล็อก IP {src_ip} ชั่วคราว 24 ชั่วโมง (Fail2ban Enforcement)",
                "description": "ระงับการเชื่อมต่อจากที่อยู่นี้เนื่องจากล็อกอินล้มเหลวเกินเกณฑ์ความปลอดภัย",
                "type": "ACCESS_CONTROL",
                "risk_reduction": "90%",
                "auto_executable": True
            },
            {
                "action_id": "ACT_FORCE_MFA",
                "title": f"บังคับใช้ MFA และรีเซ็ตรหัสผ่านบัญชีบนโฮสต์ {dst_ip}",
                "description": "สั่งตัด Session เก่าทั้งหมด และแจ้งเตือนผู้ดูแลระบบเพื่อรีเซ็ต Credential",
                "type": "IDENTITY",
                "risk_reduction": "80%",
                "auto_executable": False
            }
        ]
    elif verdict == "ZeroDay_Exploit":
        return [
            {
                "action_id": "ACT_SANDBOX_QUARANTINE",
                "title": f"กักกันเซสชันที่ผิดปกติจาก {src_ip} เข้าสู่ Sandbox Inspection",
                "description": "เบี่ยงเบนทราฟฟิกไปวิเคราะห์เชิงลึกด้วยระบบตรวจจับพฤติกรรม และบันทึก Full Packet Capture (PCAP)",
                "type": "DEEP_ANALYSIS",
                "risk_reduction": "85%",
                "auto_executable": True
            },
            {
                "action_id": "ACT_MICROSEGMENT",
                "title": f"บังคับใช้ Micro-segmentation ชั่วคราวรอบโฮสต์เป้าหมาย {dst_ip}",
                "description": "จำกัดการเข้าถึงเฉพาะพอร์ตที่จำเป็นอย่างยิ่งยวด จนกว่าทีม Tier-3 SOC จะยืนยันความปลอดภัย",
                "type": "CONTAINMENT",
                "risk_reduction": "80%",
                "auto_executable": False
            }
        ]
    elif verdict == "Port_Scan":
        return [
            {
                "action_id": "ACT_DROP_RECON",
                "title": f"ปฏิเสธทราฟฟิก (Drop Traffic) จาก IP ผู้สแกน {src_ip}",
                "description": "ปิดกั้นการสอดแนมโครงสร้างเครือข่าย ป้องกันไม่ให้แฮกเกอร์ค้นพบพอร์ตบริการที่มีช่องโหว่",
                "type": "DEFENSE",
                "risk_reduction": "70%",
                "auto_executable": True
            }
        ]
    else:
        return [
            {
                "action_id": "ACT_NO_ACTION",
                "title": "ทราฟฟิกปกติ — บันทึก Log เข้าระบบตรวจสอบตามมาตรฐาน",
                "description": "ไม่พบพฤติกรรมเสี่ยงภัยคุกคาม ระบบยังคงเฝ้าระวังอย่างต่อเนื่อง",
                "type": "MONITORING",
                "risk_reduction": "0%",
                "auto_executable": True
            }
        ]


def reconstruct_attack_chain(event_logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Aggregates disparate security events into chronological multi-stage attack storylines.
    Maps to Cyber Kill Chain / MITRE ATT&CK stages.
    """
    storylines = []
    # Filter only attacks
    attacks = [e for e in event_logs if e.get("verdict") not in ["Normal", None]]
    
    # Group by attacker source IP or target asset
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for ev in attacks:
        key = ev.get("source_ip", "UNKNOWN")
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(ev)
        
    for src_ip, events in grouped.items():
        stages = []
        for ev in sorted(events, key=lambda x: str(x.get("timestamp", ""))):
            v = ev.get("verdict")
            if v == "Port_Scan":
                stage_name = "1. การสอดแนมและสำรวจเครือข่าย (Reconnaissance)"
                mitre_tactic = "TA0043: Reconnaissance"
            elif v == "SSH_BruteForce":
                stage_name = "2. การพยายามเข้าถึงระบบโดยมิชอบ (Credential Access)"
                mitre_tactic = "TA0006: Credential Access"
            elif v == "ZeroDay_Exploit":
                stage_name = "3. การเจาะผ่านช่องโหว่แบบใหม่ (Initial Exploitation)"
                mitre_tactic = "TA0001: Initial Access"
            elif v == "Ransomware_LateralMovement":
                stage_name = "4. การแพร่กระจายและเข้ารหัสข้อมูล (Lateral Movement & Impact)"
                mitre_tactic = "TA0008: Lateral Movement / TA0040: Impact"
            elif v == "DDoS_SynFlood":
                stage_name = "5. การโจมตีให้ระบบหยุดทำงาน (Denial of Service)"
                mitre_tactic = "TA0040: Impact"
            else:
                stage_name = "ตรวจพบกิจกรรมผิดปกติ (Suspicious Activity)"
                mitre_tactic = "TA0000: General"
                
            stages.append({
                "timestamp": str(ev.get("timestamp", "")),
                "stage": stage_name,
                "mitre_tactic": mitre_tactic,
                "target": f"{ev.get('destination_ip')}:{ev.get('destination_port')}",
                "confidence": ev.get("confidence", 0.0),
                "risk_score": ev.get("risk_score", 0)
            })
            
        storylines.append({
            "attacker_ip": src_ip,
            "total_events": len(stages),
            "max_risk": max([s["risk_score"] for s in stages]) if stages else 0,
            "timeline": stages
        })
        
    storylines.sort(key=lambda s: s["max_risk"], reverse=True)
    return storylines

