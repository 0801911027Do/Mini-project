"""
GoHard AI Threat Detection & Incident Decision Support System
Module: src/inference_engine.py
Real-time Two-Stage Inference Engine with Explainable AI (XAI) feature attribution.
Combines Unsupervised Anomaly Detection (Zero-day) with Supervised Threat Classification.
"""

import os
import joblib
import numpy as np
from typing import Dict, Any, List, Tuple
from src.preprocessor import SecurityPreprocessor


class AIThreatEngine:
    """
    Two-Stage Real-Time Cyber Threat Inference Engine.
    """
    ANOMALY_THRESHOLD = 0.58  # Normalized threshold for zero-day behavioral alert
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = models_dir
        self.preprocessor = SecurityPreprocessor.load(models_dir)
        self.anomaly_detector = joblib.load(os.path.join(models_dir, "anomaly_detector.joblib"))
        self.threat_classifier = joblib.load(os.path.join(models_dir, "threat_classifier.joblib"))
        
    def analyze_event(self, log_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a single network event through the two-stage AI pipeline.
        Returns prediction, confidence, anomaly score, and XAI feature attributions.
        """
        # Feature transformation
        X_scaled = self.preprocessor.transform_single(log_dict)
        
        # Stage 1: Unsupervised Anomaly Scoring (Isolation Forest)
        # Raw score: lower means more anomalous. Invert and scale to ~[0, 1]
        raw_anomaly = -self.anomaly_detector.score_samples(X_scaled)[0]
        # Normalize into 0.0 - 1.0 range (typical score range is 0.35 to 0.85)
        normalized_anomaly = float(np.clip((raw_anomaly - 0.35) / 0.40, 0.0, 1.0))
        
        # Stage 2: Supervised Multi-Class Threat Prediction
        probs = self.threat_classifier.predict_proba(X_scaled)[0]
        pred_idx = int(np.argmax(probs))
        pred_class = self.preprocessor.idx_to_class[pred_idx]
        confidence = float(probs[pred_idx])
        
        # Two-Stage Decision Fusion
        verdict = pred_class
        is_novel_anomaly = False
        
        if pred_class == "Normal" and normalized_anomaly >= self.ANOMALY_THRESHOLD:
            verdict = "ZeroDay_Exploit"
            is_novel_anomaly = True
            confidence = normalized_anomaly
        elif pred_class != "Normal":
            # Confidence is high from supervised classifier
            pass
            
        is_threat = (verdict != "Normal")
        
        # Explainable AI (XAI): Find top deviating features from normal baseline
        xai_factors = self._explain_prediction(X_scaled[0], log_dict)
        
        return {
            "verdict": verdict,
            "is_threat": is_threat,
            "is_novel_anomaly": is_novel_anomaly,
            "confidence": round(confidence, 4),
            "anomaly_score": round(normalized_anomaly, 4),
            "stage1_anomaly": bool(normalized_anomaly >= self.ANOMALY_THRESHOLD),
            "stage2_classification": pred_class,
            "class_probabilities": {
                self.preprocessor.idx_to_class[i]: round(float(probs[i]), 4)
                for i in range(len(probs))
            },
            "xai_factors": xai_factors
        }

    def _explain_prediction(self, x_scaled: np.ndarray, raw_log: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Computes Explainable AI feature importance factors based on standard score deviations.
        Answers: 'Why did the AI flag this event?'
        """
        deviations = []
        for i, col in enumerate(self.preprocessor.FEATURE_COLS):
            val = x_scaled[i]
            abs_dev = abs(val)
            if abs_dev >= 1.5:  # Significant deviation (> 1.5 standard deviations from mean)
                deviations.append({
                    "feature": col,
                    "z_score": round(float(val), 2),
                    "significance": "HIGH" if abs_dev >= 3.0 else "MEDIUM",
                    "explanation": self._get_feature_explanation(col, val, raw_log)
                })
                
        # Sort by highest absolute z-score deviation
        deviations.sort(key=lambda d: abs(d["z_score"]), reverse=True)
        return deviations[:4]  # Return top 4 most impactful factors

    def _get_feature_explanation(self, feature: str, z_score: float, raw_log: Dict[str, Any]) -> str:
        """Translates technical feature z-score into plain SOC analyst explanation."""
        if feature == "failed_login_attempts":
            count = raw_log.get("failed_login_attempts", 0)
            return f"พบการพยายามล็อกอินล้มเหลวผิดปกติจำนวน {count} ครั้ง (Authentication Spike)"
        elif feature == "packet_rate":
            return f"อัตราการส่งแพ็กเก็ตสูงผิดปกติ ({z_score:+.1f} std) สอดคล้องกับพฤติกรรม DoS/Flood"
        elif feature == "byte_rate":
            return f"ปริมาณการรับส่งข้อมูลต่อวินาทีพุ่งสูงผิดปกติ ({z_score:+.1f} std)"
        elif feature == "is_lateral_candidate" and z_score > 0:
            return "การเชื่อมต่อเกิดขึ้นระหว่างโฮสต์ภายในกับโฮสต์ภายใน (เสี่ยงต่อการแพร่กระจาย Ransomware / Lateral Movement)"
        elif feature == "byte_ratio" and z_score > 0:
            return "สัดส่วนการส่งข้อมูลออก (Upload Ratio) สูงกว่าการรับข้อมูลอย่างมีนัยสำคัญ (เสี่ยงต่อ Data Exfiltration)"
        elif feature == "duration_sec" and z_score < -1.0:
            return "ระยะเวลาการเชื่อมต่อสั้นมากผิดปกติ (Micro-burst / Port Probe)"
        elif feature == "state_code":
            return f"สถานะการเชื่อมต่อผิดปกติ ({raw_log.get('connection_state', 'UNKNOWN')})"
        else:
            return f"ค่าตัวแปร {feature} เบี่ยงเบนจากพฤติกรรมปกติของระบบ ({z_score:+.1f} std)"

