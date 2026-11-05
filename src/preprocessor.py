"""
GoHard AI Threat Detection & Incident Decision Support System
Module: src/preprocessor.py
Handles data cleaning, advanced feature engineering, temporal splitting (to prevent data leakage),
and scaling for the two-stage ML pipeline.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any, List
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE


def is_internal_ip(ip_str: str) -> int:
    """Checks if an IP address belongs to RFC 1918 private subnets."""
    if not isinstance(ip_str, str):
        return 0
    if ip_str.startswith("10.") or ip_str.startswith("192.168.") or ip_str.startswith("172.16."):
        return 1
    return 0


def categorize_port(port: int) -> int:
    """
    Bins ports into semantic categories to prevent high-cardinality explosion:
    0: Web (80, 443, 8080)
    1: Management/Shell (22, 3389)
    2: Database (3306, 5432, 1433)
    3: File Share / SMB (445, 139)
    4: Core Infrastructure / DNS (53, 123)
    5: Other / High Ports (>1024)
    """
    try:
        p = int(port)
    except (ValueError, TypeError):
        return 5
        
    if p in [80, 443, 8080]:
        return 0
    elif p in [22, 3389]:
        return 1
    elif p in [3306, 5432, 1433]:
        return 2
    elif p in [445, 139]:
        return 3
    elif p in [53, 123]:
        return 4
    else:
        return 5


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes network behavioral metrics and domain-specific security ratios.
    """
    df = df.copy()
    
    # 1. Network Boundary Features
    df["is_internal_src"] = df["source_ip"].apply(is_internal_ip)
    df["is_internal_dst"] = df["destination_ip"].apply(is_internal_ip)
    df["is_lateral_candidate"] = ((df["is_internal_src"] == 1) & (df["is_internal_dst"] == 1)).astype(int)
    
    # 2. Port Semantics
    df["port_category"] = df["destination_port"].apply(categorize_port)
    
    # 3. Flow Dynamic & Rate Metrics
    safe_duration = df["duration_sec"].clip(lower=0.001)
    safe_pkts_sent = df["packets_sent"].clip(lower=1)
    safe_pkts_recv = df["packets_received"].clip(lower=1)
    safe_bytes_recv = df["bytes_received"].clip(lower=1)
    
    df["bytes_per_packet_sent"] = df["bytes_sent"] / safe_pkts_sent
    df["bytes_per_packet_recv"] = df["bytes_received"] / safe_pkts_recv
    df["byte_ratio"] = df["bytes_sent"] / safe_bytes_recv
    df["packet_rate"] = (df["packets_sent"] + df["packets_received"]) / safe_duration
    df["byte_rate"] = (df["bytes_sent"] + df["bytes_received"]) / safe_duration
    
    # 4. State & Protocol One-Hot / Map
    proto_map = {"TCP": 1, "UDP": 2, "ICMP": 3}
    df["protocol_code"] = df["protocol"].map(lambda x: proto_map.get(str(x).upper(), 0))
    
    state_map = {"ESTABLISHED": 1, "SYN_SENT": 2, "RESET": 3, "CLOSED": 4}
    df["state_code"] = df["connection_state"].map(lambda x: state_map.get(str(x).upper(), 0))
    
    return df


class SecurityPreprocessor:
    """
    Production Preprocessor for GoHard AI Threat Engine.
    Enforces temporal integrity, feature consistency, and scaling.
    """
    FEATURE_COLS = [
        "duration_sec",
        "bytes_sent",
        "bytes_received",
        "packets_sent",
        "packets_received",
        "failed_login_attempts",
        "is_internal_src",
        "is_internal_dst",
        "is_lateral_candidate",
        "port_category",
        "bytes_per_packet_sent",
        "bytes_per_packet_recv",
        "byte_ratio",
        "packet_rate",
        "byte_rate",
        "protocol_code",
        "state_code"
    ]
    
    LABEL_COL = "threat_label"
    BINARY_COL = "is_attack"
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.class_names: List[str] = []
        self.class_to_idx: Dict[str, int] = {}
        self.idx_to_class: Dict[int, str] = {}
        self.feature_means: Dict[str, float] = {}
        self.feature_stds: Dict[str, float] = {}

    def fit_transform(
        self,
        raw_df: pd.DataFrame,
        temporal_train_ratio: float = 0.75,
        apply_smote: bool = True
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, pd.DataFrame, pd.DataFrame]:
        """
        Executes strict temporal split (no future data leakage).
        Fits scaler on Train only. Optionally applies SMOTE on Train to handle severe imbalance.
        """
        # Ensure timestamp sorting
        df = raw_df.sort_values(by="timestamp").reset_index(drop=True)
        df_feat = engineer_features(df)
        
        # Temporal split point
        split_idx = int(len(df_feat) * temporal_train_ratio)
        train_raw = df_feat.iloc[:split_idx].copy()
        test_raw = df_feat.iloc[split_idx:].copy()
        
        # Build Label Encodings
        unique_labels = sorted(df_feat[self.LABEL_COL].unique())
        # Ensure 'Normal' is class 0
        if "Normal" in unique_labels:
            unique_labels.remove("Normal")
            unique_labels = ["Normal"] + unique_labels
            
        self.class_names = unique_labels
        self.class_to_idx = {name: idx for idx, name in enumerate(self.class_names)}
        self.idx_to_class = {idx: name for idx, name in enumerate(self.class_names)}
        
        X_train_raw = train_raw[self.FEATURE_COLS].values
        y_train_raw = train_raw[self.LABEL_COL].map(self.class_to_idx).values
        
        X_test_raw = test_raw[self.FEATURE_COLS].values
        y_test_raw = test_raw[self.LABEL_COL].map(self.class_to_idx).values
        
        # Fit scaler on train only
        X_train_scaled = self.scaler.fit_transform(X_train_raw)
        X_test_scaled = self.scaler.transform(X_test_raw)
        
        # Store distribution statistics for feature explainability
        for idx, col in enumerate(self.FEATURE_COLS):
            self.feature_means[col] = float(self.scaler.mean_[idx])
            self.feature_stds[col] = float(self.scaler.scale_[idx])
            
        # Optional SMOTE for multi-class training data balance
        if apply_smote:
            # Filter classes with at least 6 samples for SMOTE k_neighbors=5
            class_counts = pd.Series(y_train_raw).value_counts()
            valid_classes = class_counts[class_counts >= 6].index
            mask = np.isin(y_train_raw, valid_classes)
            
            try:
                # Target sampling: boost minority classes moderately
                smote = SMOTE(random_state=42, k_neighbors=min(5, class_counts.min() - 1))
                X_train_res, y_train_res = smote.fit_resample(X_train_scaled[mask], y_train_raw[mask])
            except Exception as e:
                print(f"[!] SMOTE skipped due to class distribution constraint: {e}")
                X_train_res, y_train_res = X_train_scaled, y_train_raw
        else:
            X_train_res, y_train_res = X_train_scaled, y_train_raw
            
        return X_train_res, y_train_res, X_test_scaled, y_test_raw, train_raw, test_raw

    def transform_single(self, log_dict: Dict[str, Any]) -> np.ndarray:
        """Transforms a single incoming network log event for real-time inference."""
        df_single = pd.DataFrame([log_dict])
        df_feat = engineer_features(df_single)
        X_raw = df_feat[self.FEATURE_COLS].values
        return self.scaler.transform(X_raw)

    def save(self, model_dir: str = "models"):
        """Saves scaler and feature metadata."""
        os.makedirs(model_dir, exist_ok=True)
        joblib.dump(self.scaler, os.path.join(model_dir, "scaler.joblib"))
        
        meta = {
            "feature_cols": self.FEATURE_COLS,
            "class_names": self.class_names,
            "class_to_idx": self.class_to_idx,
            "idx_to_class": {str(k): v for k, v in self.idx_to_class.items()},
            "feature_means": self.feature_means,
            "feature_stds": self.feature_stds
        }
        with open(os.path.join(model_dir, "preprocessor_meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
        print(f"[+] Preprocessor metadata saved to {model_dir}")

    @classmethod
    def load(cls, model_dir: str = "models") -> "SecurityPreprocessor":
        """Loads fitted preprocessor from disk."""
        instance = cls()
        instance.scaler = joblib.load(os.path.join(model_dir, "scaler.joblib"))
        with open(os.path.join(model_dir, "preprocessor_meta.json"), "r", encoding="utf-8") as f:
            meta = json.load(f)
        instance.FEATURE_COLS = meta["feature_cols"]
        instance.class_names = meta["class_names"]
        instance.class_to_idx = meta["class_to_idx"]
        instance.idx_to_class = {int(k): v for k, v in meta["idx_to_class"].items()}
        instance.feature_means = meta.get("feature_means", {})
        instance.feature_stds = meta.get("feature_stds", {})
        return instance

