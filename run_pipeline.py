"""
GoHard AI Threat Detection & Incident Decision Support System
Script: run_pipeline.py
One-click orchestrator for the complete Machine Learning Pipeline:
  Step 1: Data Generation & Ingestion
  Step 2: Cleaning & Temporal Splitting
  Step 3: Model Training (Isolation Forest + Random Forest)
  Step 4: Comprehensive Model Evaluation & Metric Persistence
"""

import sys
import os
import argparse
from datetime import datetime

from src.data_generator import generate_security_logs
from src.train import train_models


def main():
    parser = argparse.ArgumentParser(description="Run GoHard AI Threat Engine Pipeline")
    parser.add_argument("--regenerate-data", action="store_true", help="Force regenerate raw logs")
    parser.add_argument("--samples", type=int, default=15000, help="Number of records to generate")
    args = parser.parse_args()

    print("\n" + "="*70)
    print("      GOHARD AI THREAT ENGINE — END-TO-END ML PIPELINE RUNNER       ")
    print("="*70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    raw_data_path = "data/raw/security_logs.csv"
    
    # Step 1: Data Generation
    if args.regenerate_data or not os.path.exists(raw_data_path):
        print(f"\n[STEP 1/4] Generating {args.samples} realistic security logs...")
        generate_security_logs(num_records=args.samples, output_path=raw_data_path)
    else:
        print(f"\n[STEP 1/4] Using existing dataset at {raw_data_path}")

    # Steps 2, 3, 4: Preprocess, Train, Evaluate
    print("\n[STEP 2/4] Preprocessing & Temporal Train-Test Splitting...")
    print("[STEP 3/4] Training Two-Stage Models (Isolation Forest + Classifier)...")
    print("[STEP 4/4] Evaluating Performance & Exporting Benchmark...")
    
    metrics = train_models(raw_data_path=raw_data_path)
    
    print("="*70)
    print("                      PIPELINE EXECUTION COMPLETE                   ")
    print("="*70)
    print(f"[*] Macro F1-Score       : {metrics['macro_f1']:.4f}")
    print(f"[*] Overall Accuracy     : {metrics['overall_accuracy']:.2%}")
    print(f"[*] Attack Recall        : {metrics['attack_detection_recall']:.2%}")
    print(f"[*] False Positive Rate  : {metrics['false_positive_rate']:.2%}")
    print("\nAll model artifacts and reports are successfully saved in `models/`.")
    print("To launch the interactive dashboard, run:")
    print("   streamlit run app/dashboard.py\n")


if __name__ == "__main__":
    main()

