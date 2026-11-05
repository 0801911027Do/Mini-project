"""
GoHard AI Threat Detection & Incident Decision Support System
Module: tests/test_pipeline.py
Unit and Integration Tests for ML Pipeline, Inference Engine, and Decision Engine.
"""

import os
import unittest
import numpy as np
import pandas as pd

from src.data_generator import generate_security_logs
from src.preprocessor import SecurityPreprocessor, is_internal_ip, categorize_port
from src.inference_engine import AIThreatEngine
from src.decision_engine import calculate_risk_score, get_mitigation_actions, reconstruct_attack_chain
from src.simulator import TrafficSimulator


class TestGoHardThreatSystem(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.models_dir = "models"
        cls.engine = AIThreatEngine(models_dir=cls.models_dir)
        cls.simulator = TrafficSimulator(models_dir=cls.models_dir)

    def test_ip_categorization(self):
        """Tests internal IP identification."""
        self.assertEqual(is_internal_ip("10.0.1.5"), 1)
        self.assertEqual(is_internal_ip("192.168.1.1"), 1)
        self.assertEqual(is_internal_ip("172.16.0.2"), 1)
        self.assertEqual(is_internal_ip("8.8.8.8"), 0)
        self.assertEqual(is_internal_ip("185.220.101.5"), 0)

    def test_port_categorization(self):
        """Tests semantic port binning."""
        self.assertEqual(categorize_port(80), 0)    # Web
        self.assertEqual(categorize_port(443), 0)   # Web
        self.assertEqual(categorize_port(22), 1)    # Shell/Admin
        self.assertEqual(categorize_port(3306), 2)  # DB
        self.assertEqual(categorize_port(445), 3)   # SMB
        self.assertEqual(categorize_port(53), 4)    # DNS
        self.assertEqual(categorize_port(49152), 5) # High/dynamic

    def test_risk_scoring(self):
        """Tests risk score calculation across asset tiers and threat types."""
        # Critical Ransomware on Domain Controller
        res_crit = calculate_risk_score("Ransomware_LateralMovement", 0.95, "10.0.1.10", 0.8)
        self.assertGreaterEqual(res_crit["risk_score"], 80)
        self.assertEqual(res_crit["severity"], "CRITICAL")
        
        # Normal traffic on standard endpoint
        res_norm = calculate_risk_score("Normal", 0.99, "192.168.1.50", 0.1)
        self.assertLess(res_norm["risk_score"], 30)
        self.assertEqual(res_norm["severity"], "LOW")

    def test_mitigation_actions(self):
        """Tests mitigation action generation for ransomware and DDoS."""
        mit_ransom = get_mitigation_actions("Ransomware_LateralMovement", "10.0.1.45", "10.0.1.120", 445)
        self.assertTrue(len(mit_ransom) >= 1)
        self.assertEqual(mit_ransom[0]["action_id"], "ACT_ISOLATE_HOST")

        mit_ddos = get_mitigation_actions("DDoS_SynFlood", "185.220.101.5", "172.16.5.80", 80)
        self.assertTrue(len(mit_ddos) >= 1)
        self.assertEqual(mit_ddos[0]["action_id"], "ACT_BLOCK_IP_PERIMETER")

    def test_simulator_and_inference(self):
        """Tests simulator event generation and full AI inference pipeline."""
        event_types = ["Normal", "DDoS_SynFlood", "Port_Scan", "SSH_BruteForce", "Ransomware_LateralMovement", "ZeroDay_Exploit"]
        
        for etype in event_types:
            event = self.simulator.generate_event(etype)
            self.assertIn("verdict", event)
            self.assertIn("risk_score", event)
            self.assertIn("confidence", event)
            self.assertIn("mitigations", event)
            self.assertIn("xai_factors", event)
            self.assertTrue(0 <= event["risk_score"] <= 100)

    def test_attack_chain_reconstruction(self):
        """Tests grouping of attack events into multi-stage kill chains."""
        mock_events = [
            {"timestamp": "2026-11-01 10:00:00", "source_ip": "194.26.29.112", "destination_ip": "10.0.1.10", "destination_port": 80, "verdict": "Port_Scan", "risk_score": 55, "confidence": 0.9},
            {"timestamp": "2026-11-01 10:15:00", "source_ip": "194.26.29.112", "destination_ip": "10.0.1.10", "destination_port": 22, "verdict": "SSH_BruteForce", "risk_score": 75, "confidence": 0.95},
        ]
        storylines = reconstruct_attack_chain(mock_events)
        self.assertEqual(len(storylines), 1)
        self.assertEqual(storylines[0]["attacker_ip"], "194.26.29.112")
        self.assertEqual(len(storylines[0]["timeline"]), 2)


if __name__ == "__main__":
    unittest.main()

