import pandas as pd
import argparse
import os
import sys

# Add parent directory to path so we can import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from ai_engine import AIEngine
from feature_builder import FeatureBuilder
from anomaly_interpreter import AnomalyInterpreter
from feedback_manager import FeedbackManager
from report_generator import ReportGenerator
from time_alignment import TimeAlignment
from Ai_correlation_analyzer import CorrelationAnalyzer


def main(input_file="frequency_validations.csv"):
    """ Main AI analysis pipeline     
    Args:
        input_file: Path to frequency_validations.csv (should be in outputs/) """
    # Change to parent directory (project root)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    print(f"📂 Working directory: {os.getcwd()}")
    
    # Resolve input file path
    if not os.path.exists(input_file):
        # Try looking in outputs directory
        alt_path = os.path.join("outputs", input_file)
        if os.path.exists(alt_path):
            input_file = alt_path
        else:
            print(f"❌ Error: {input_file} not found")
            return

    print(f"📖 Loading data from: {input_file}")
    
    # Step 1: Load Data
    # The CSV contains both event data (SBX, DOCOM, HL7) and waveform data (Waveform_AM, Waveform_PM)
    # We filter to only event data for AI analysis
    # -------------------------------------------------
    df = pd.read_csv(input_file)

    # Filter to only event streams (skip waveform data and empty rows)
    event_streams = ["SBX", "DOCOM", "HL7"]
    df = df[df["stream"].isin(event_streams)].reset_index(drop=True)
    df = df.dropna(how="all")  # Remove completely empty rows

    # Convert numeric columns to proper types
    numeric_cols = ["count", "expected_gap", "max_gap", "avg_gap", "p90_gap", "p95_gap", "jitter"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Step 1.5: Load Correlation Data (optional)
    # -------------------------------------------------
    corr_result = None
    correlation_path = os.path.join("outputs", "correlation_table.csv")
    if os.path.exists(correlation_path):
        print(f"📖 Loading correlation data from: {correlation_path}")
        try:
            corr_df = pd.read_csv(correlation_path)
            
            # Time Alignment
            alignment = TimeAlignment()
            corr_df, align_info = alignment.apply_alignment(corr_df)
            print(f"✅ Alignment Info: {align_info}")
            
            # Correlation Analysis
            corr_analyzer = CorrelationAnalyzer()
            corr_result = corr_analyzer.analyze(corr_df)
            print(f"✅ Correlation analysis complete")
        except Exception as e:
            print(f"⚠️  Error in correlation analysis: {e}")
            corr_result = None
    else:
        print(f"ℹ️  No correlation data found, using frequency features only")

    # Step 2: Feature Engineering ✅
    # -------------------------------------------------
    builder = FeatureBuilder()
    freq_features = builder.build_all_features(freq_df=df)
    
    # Merge with correlation features if available
    if corr_result is not None:
        try:
            corr_features = builder.build_correlation_features(corr_result)
            features = builder.merge_features(freq_features, corr_features)
            print(f"✅ Merged frequency and correlation features")
        except Exception as e:
            print(f"⚠️  Error merging features: {e}")
            features = freq_features
    else:
        features = freq_features

    print(f"✅ Features Shape: {features.shape}")
    features.to_csv("debug_features.csv", index=False)

    # Step 3: AI Detection ✅
    # -------------------------------------------------
    engine = AIEngine(contamination=0.1)
    ai_results = engine.fit_predict(features)

    df = pd.concat([df, features, ai_results], axis=1)


    # Step 4: Interpretation ✅
    # -------------------------------------------------
    interpreter = AnomalyInterpreter()
    interpretation = interpreter.interpret(df)

    df = pd.concat([df, interpretation], axis=1)

    print(f"✅ Anomalies Detected: {(df['anomaly_flag'] == -1).sum()}")
    
    # Step 5: Feedback Manager ✅
    # -------------------------------------------------
    feedback = FeedbackManager()
    df = feedback.apply_feedback(df)


    # Step 6: Report Generation ✅
    # -------------------------------------------------
    reporter = ReportGenerator()
    report_text = reporter.generate_all(df)

    # Save report to file
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    summary_file = os.path.join(output_dir, "AI_summary.txt")
    
    with open(summary_file, "w") as f:
        f.write(report_text)
    
    print(report_text)
    print(f"\n✅ Analysis complete!")
    print(f"📄 Report saved to: {summary_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Engine - Log Analysis Pipeline")
    parser.add_argument(
        "--input",
        type=str,
        default="frequency_validations.csv",
        help="Path to frequency_validations.csv (default: frequency_validations.csv)"
    )
    
    args = parser.parse_args()
    main(input_file=args.input)