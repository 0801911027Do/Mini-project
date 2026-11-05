"""
GoHard AI Threat Detection & Incident Decision Support System
Module: src/train.py
Trains the Two-Stage AI Threat Engine:
  - Stage 1: Isolation Forest (Unsupervised Behavioral Anomaly Detection for Zero-Day)
  - Stage 2: Random Forest / Gradient Boosting (Supervised Threat Classification)
Evaluates using Precision, Recall, F1-Score, and False Positive Rate (FPR).
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support

from src.data_generator import generate_security_logs
from src.preprocessor import SecurityPreprocessor


def train_models(
    raw_data_path: str = "data/raw/security_logs.csv",
    models_dir: str = "models",
    processed_dir: str = "data/processed",
    random_seed: int = 42
) -> Dict[str, Any]:
    """
    Executes the complete training and evaluation pipeline.
    """
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    
    # 1. Load or Generate Dataset
    if not os.path.exists(raw_data_path):
        print(f"[*] Raw logs not found at {raw_data_path}. Generating dataset...")
        df_raw = generate_security_logs(output_path=raw_data_path, random_seed=random_seed)
    else:
        print(f"[*] Loading raw security logs from {raw_data_path}...")
        df_raw = pd.read_csv(raw_data_path)
        df_raw["timestamp"] = pd.to_datetime(df_raw["timestamp"])
        
    # 2. Preprocess & Temporal Split
    print("[*] Preprocessing features with temporal splitting...")
    preprocessor = SecurityPreprocessor()
    X_train, y_train, X_test, y_test, train_df, test_df = preprocessor.fit_transform(
        df_raw, temporal_train_ratio=0.75, apply_smote=True
    )
    preprocessor.save(models_dir)
    
    # Save processed subsets for audit
    train_df.to_csv(os.path.join(processed_dir, "train_features.csv"), index=False)
    test_df.to_csv(os.path.join(processed_dir, "test_features.csv"), index=False)
    
    # 3. Stage 1: Train Unsupervised Anomaly Detector (Isolation Forest)
    # Train primarily on normal traffic from the training set
    print("[*] Training Stage 1: Isolation Forest (Zero-Day Anomaly Detection)...")
    normal_idx = preprocessor.class_to_idx["Normal"]
    X_train_normal = X_train[y_train == normal_idx]
    
    iso_forest = IsolationForest(
        n_estimators=150,
        contamination=0.03,
        random_state=random_seed,
        n_jobs=-1
    )
    iso_forest.fit(X_train_normal)
    joblib.dump(iso_forest, os.path.join(models_dir, "anomaly_detector.joblib"))
    print("[+] Stage 1 Isolation Forest model trained and saved.")
    
    # 4. Stage 2: Train Supervised Threat Classifier (Random Forest)
    print("[*] Training Stage 2: Balanced Random Forest Threat Classifier...")
    clf = RandomForestClassifier(
        n_estimators=120,
        max_depth=16,
        class_weight="balanced_subsample",
        random_state=random_seed,
        n_jobs=-1
    )
    clf.fit(X_train, y_train)
    joblib.dump(clf, os.path.join(models_dir, "threat_classifier.joblib"))
    print("[+] Stage 2 Threat Classifier model trained and saved.")
    
    # 5. Model Evaluation on Unseen Temporal Test Set
    print("\n" + "="*60)
    print("           MODEL EVALUATION (TEMPORAL TEST SET)             ")
    print("="*60)
    
    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)
    
    # Overall and per-class metrics
    class_names = preprocessor.class_names
    target_names = [class_names[i] for i in range(len(class_names))]
    all_label_indices = list(range(len(target_names)))
    
    report_dict = classification_report(
        y_test, y_pred, labels=all_label_indices, target_names=target_names, output_dict=True, zero_division=0
    )
    cm = confusion_matrix(y_test, y_pred, labels=all_label_indices)
    
    # Calculate False Positive Rate (FPR) on Normal class: FP / (FP + TN)
    # Class 0 is Normal
    tn = cm[0, 0]
    fp = cm[0, 1:].sum()
    fn = cm[1:, 0].sum()
    tp = cm[1:, 1:].sum()
    
    fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    recall_attack = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    
    # Test Isolation Forest anomaly scores on test set
    iso_scores = -iso_forest.score_samples(X_test)
    # Zero-day detection check
    zeroday_mask = (y_test == preprocessor.class_to_idx.get("ZeroDay_Exploit", -999))
    zeroday_anomaly_mean = float(np.mean(iso_scores[zeroday_mask])) if zeroday_mask.sum() > 0 else 0.0
    normal_anomaly_mean = float(np.mean(iso_scores[y_test == normal_idx]))
    
    eval_results = {
        "macro_f1": round(report_dict["macro avg"]["f1-score"], 4),
        "weighted_f1": round(report_dict["weighted avg"]["f1-score"], 4),
        "overall_accuracy": round(report_dict["accuracy"], 4),
        "false_positive_rate": round(fpr, 4),
        "attack_detection_recall": round(recall_attack, 4),
        "normal_anomaly_score_mean": round(normal_anomaly_mean, 4),
        "zeroday_anomaly_score_mean": round(zeroday_anomaly_mean, 4),
        "confusion_matrix": cm.tolist(),
        "classes": target_names,
        "per_class_report": {
            cls_name: {
                "precision": round(report_dict[cls_name]["precision"], 4),
                "recall": round(report_dict[cls_name]["recall"], 4),
                "f1_score": round(report_dict[cls_name]["f1-score"], 4),
                "support": int(report_dict[cls_name]["support"])
            }
            for cls_name in target_names if cls_name in report_dict
        }
    }
    
    # Save evaluation metrics
    metrics_path = os.path.join(models_dir, "evaluation_metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(eval_results, f, indent=2, ensure_ascii=False)
        
    print(f"Overall Accuracy          : {eval_results['overall_accuracy']:.2%}")
    print(f"Macro F1-Score            : {eval_results['macro_f1']:.4f}")
    print(f"Attack Recall (Sensitivity): {eval_results['attack_detection_recall']:.2%}")
    print(f"False Positive Rate (FPR) : {eval_results['false_positive_rate']:.2%}  <-- Crucial noise reduction!")
    print(f"Zero-Day Anomaly Mean     : {eval_results['zeroday_anomaly_score_mean']:.4f} (Normal: {eval_results['normal_anomaly_score_mean']:.4f})")
    print(f"\n[+] Evaluation metrics saved to {metrics_path}\n")
    
    return eval_results


if __name__ == "__main__":
    train_models()
