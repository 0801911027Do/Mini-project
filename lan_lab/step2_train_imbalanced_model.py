"""
ขั้นตอนที่ 2: เทรนโมเดล Machine Learning และวัดผลสำหรับข้อมูลไม่สมดุล (Imbalanced Data)
ตอบโจทย์ที่อาจารย์เน้น:
1. ทำไมข้อมูล Network Attack ถึงไม่ Balance (ช่วงเวลาปกติ > 90%, ช่วงเวลาถูกโจมตี < 10%)
2. ทำไมห้ามวัดผลด้วย Accuracy เพียงอย่างเดียว (Accuracy Paradox)
3. การใช้ class_weight='balanced' และการวัดผลด้วย Detection Rate (Recall), Precision, F1-Score, PR-AUC และ Confusion Matrix
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    average_precision_score,
    roc_auc_score,
)

from step1_wireshark_to_features import (
    FEATURE_VECTORS_CSV,
    convert_packets_to_time_windows,
)

LAB_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(LAB_DIR, "ddos_window_model.pkl")
METRICS_PATH = os.path.join(LAB_DIR, "imbalanced_metrics.json")

FEATURE_COLS = [
    "packet_count",
    "total_bytes",
    "mean_packet_len",
    "std_packet_len",
    "mean_iat",
    "syn_count",
    "ack_count",
    "syn_ratio",
    "ack_ratio",
    "unique_src_ips",
]


def evaluate_model(name: str, y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray) -> dict:
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = [int(x) for x in cm.ravel()]
    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))  # Detection Rate
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    pr_auc = float(average_precision_score(y_true, y_prob))
    roc_auc = float(roc_auc_score(y_true, y_prob))
    fpr = float(fp / max(1, (fp + tn)))  # False Alarm Rate

    return {
        "model_name": name,
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall_detection_rate": round(rec, 4),
        "f1_score": round(f1, 4),
        "pr_auc": round(pr_auc, 4),
        "roc_auc": round(roc_auc, 4),
        "false_alarm_rate": round(fpr, 4),
        "confusion_matrix": {"tn": tn, "fp": fp, "fn": fn, "tp": tp},
    }


def train_and_evaluate_imbalanced():
    if not os.path.exists(FEATURE_VECTORS_CSV):
        convert_packets_to_time_windows(window_size=1.0)

    df = pd.read_csv(FEATURE_VECTORS_CSV)
    X = df[FEATURE_COLS]
    y = df["label"].values

    # แบ่ง Train 75% / Test 25% โดยใช้ stratify=y เพื่อรักษาสัดส่วน Imbalanced (93% : 7%) ให้เหมือนจริงทั้งคู่
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    results = []

    # 1. Dummy Classifier (ทายว่า "ปกติ" ตลอดเวลา เพื่อพิสูจน์ Accuracy Paradox)
    dummy = DummyClassifier(strategy="most_frequent")
    dummy.fit(X_train, y_train)
    y_pred_dummy = dummy.predict(X_test)
    y_prob_dummy = dummy.predict_proba(X_test)[:, 1]
    results.append(
        evaluate_model(
            "1. Naive Baseline (ทายว่า Normal ทั้งหมด)",
            y_test,
            y_pred_dummy,
            y_prob_dummy,
        )
    )

    # 2. Standard Logistic Regression (ไม่ได้ถ่วงน้ำหนัก Imbalanced Class)
    lr_unbalanced = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(C=0.05, random_state=42)),
    ])
    lr_unbalanced.fit(X_train, y_train)
    y_pred_lr = lr_unbalanced.predict(X_test)
    y_prob_lr = lr_unbalanced.predict_proba(X_test)[:, 1]
    results.append(
        evaluate_model(
            "2. Unbalanced Logistic Regression (ไม่แก้ Imbalance)",
            y_test,
            y_pred_lr,
            y_prob_lr,
        )
    )

    # 3. Balanced Random Forest (ใช้ class_weight='balanced_subsample' แก้ปัญหา Imbalanced Data)
    rf_balanced = RandomForestClassifier(
        n_estimators=150,
        max_depth=8,
        class_weight="balanced_subsample",
        random_state=42,
    )
    rf_balanced.fit(X_train, y_train)
    y_pred_rf = rf_balanced.predict(X_test)
    y_prob_rf = rf_balanced.predict_proba(X_test)[:, 1]
    rf_metrics = evaluate_model(
        "3. Balanced Random Forest (class_weight='balanced')",
        y_test,
        y_pred_rf,
        y_prob_rf,
    )
    results.append(rf_metrics)

    # คำนวณความสำคัญของแต่ละ Feature (Feature Importance)
    importances = [
        {"feature": col, "importance": round(float(imp), 4)}
        for col, imp in zip(FEATURE_COLS, rf_balanced.feature_importances_)
    ]
    importances.sort(key=lambda x: x["importance"], reverse=True)

    summary = {
        "dataset_summary": {
            "total_windows": int(len(df)),
            "normal_windows": int((y == 0).sum()),
            "attack_windows": int((y == 1).sum()),
            "imbalance_ratio_normal_pct": round(float((y == 0).mean() * 100), 2),
            "imbalance_ratio_attack_pct": round(float((y == 1).mean() * 100), 2),
            "train_size": int(len(X_train)),
            "test_size": int(len(X_test)),
        },
        "models_comparison": results,
        "feature_importances": importances,
    }

    joblib.dump(rf_balanced, MODEL_PATH)
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 75)
    print("สรุปผลการทดลองแก้ปัญหา Imbalanced Data (Test Set = 300 วินาที)")
    print("=" * 75)
    for m in results:
        cm = m["confusion_matrix"]
        print(f"\n📌 {m['model_name']}")
        print(f"   - Accuracy               : {m['accuracy']:.2%}  <-- (ระวัง! ทาย Normal หมดก็ได้ 93%)")
        print(f"   - Detection Rate (Recall): {m['recall_detection_rate']:.2%}  <-- (จับ DDoS เจอกี่ % ของที่ยิงจริง)")
        print(f"   - Precision              : {m['precision']:.2%}  <-- (เมื่อแจ้งเตือน แม่นยำแค่ไหน)")
        print(f"   - F1-Score               : {m['f1_score']:.2%}  <-- (ค่าเฉลี่ยสมดุลระหว่าง Precision & Recall)")
        print(f"   - PR-AUC                 : {m['pr_auc']:.4f}  <-- (Metric มาตรฐานสูงสุดสำหรับ Imbalanced Data)")
        print(f"   - Confusion Matrix       : TP={cm['tp']}, FP={cm['fp']}, FN={cm['fn']}, TN={cm['tn']}")

    print("\nบันทึกโมเดลสำเร็จ:", MODEL_PATH)
    print("บันทึกรายงานผลสำเร็จ:", METRICS_PATH)
    return summary


if __name__ == "__main__":
    train_and_evaluate_imbalanced()
