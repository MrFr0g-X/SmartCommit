"""
Hallucination Analysis Table Generator
Creates structured table of hallucination examples for Phase 2 report
"""

import sys
sys.path.append('..')

import pandas as pd
import os
from typing import List, Dict


def load_latest_results() -> pd.DataFrame:
    """Load latest experiment results"""
    results_dir = "../results"
    files = [f for f in os.listdir(results_dir) if f.startswith('experiment_') and f.endswith('.csv')]

    if not files:
        raise FileNotFoundError("No experiment results found. Run run_experiments.py first.")

    latest_file = sorted(files)[-1]
    results_path = os.path.join(results_dir, latest_file)

    print(f"Loading results from: {latest_file}")
    return pd.read_csv(results_path)


def categorize_error(row) -> str:
    """Categorize error type based on metrics"""
    if row['hallucination_detected']:
        return "Hallucination"
    elif row['bleu'] < 5:
        return "Very Low BLEU"
    elif row['semantic_similarity'] < 0.5:
        return "Semantic Mismatch"
    elif row['quality_score'] < 0.5:
        return "Low Quality"
    else:
        return "Acceptable"


def create_hallucination_table(df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    """
    Create structured hallucination analysis table

    Args:
        df: Results dataframe
        n: Number of examples to include

    Returns:
        Formatted table
    """
    # Filter for diverse examples
    hallucinations = df[df['hallucination_detected'] == True]
    non_hallucinations = df[df['hallucination_detected'] == False]

    # Get worst hallucination cases
    hall_examples = hallucinations.nsmallest(n//2, 'quality_score')

    # Get some false positives (low quality but no hallucination)
    low_quality = non_hallucinations.nsmallest(n//2, 'quality_score')

    # Combine
    examples = pd.concat([hall_examples, low_quality]).head(n)

    # Create structured table
    table_data = []

    for idx, row in examples.iterrows():
        # Truncate for readability
        diff_snippet = row['diff'][:100].replace('\n', ' ') + '...'
        ref_msg = row['reference_message'][:60] + '...' if len(row['reference_message']) > 60 else row['reference_message']
        gen_msg = row['generated_message'][:60] + '...' if len(row['generated_message']) > 60 else row['generated_message']

        # Determine error type
        error_type = categorize_error(row)

        # Hallucination status
        hall_status = "Yes" if row['hallucination_detected'] else "No"

        # Root cause hypothesis
        if row['hallucination_detected'] and row['hallucination_rate'] > 0.2:
            root_cause = "High rate of ungrounded tokens"
        elif row['bleu'] < 5:
            root_cause = "Misunderstood diff context"
        elif row['semantic_similarity'] < 0.5:
            root_cause = "Incorrect interpretation"
        else:
            root_cause = "Minor semantic deviation"

        table_data.append({
            'ID': row['sample_id'],
            'Diff (snippet)': diff_snippet,
            'Expected': ref_msg,
            'Generated': gen_msg,
            'Error Type': error_type,
            'Hallucination?': hall_status,
            'BLEU': f"{row['bleu']:.1f}",
            'Quality': f"{row['quality_score']:.2f}",
            'Root Cause': root_cause
        })

    return pd.DataFrame(table_data)


def print_latex_table(df: pd.DataFrame):
    """Print LaTeX formatted table for IEEE paper"""
    print("\n" + "="*100)
    print("LATEX TABLE FOR PHASE 2 REPORT")
    print("="*100)
    print()

    print("\\begin{table*}[t]")
    print("\\centering")
    print("\\caption{Hallucination and Error Analysis Examples}")
    print("\\label{tab:hallucination_analysis}")
    print("\\small")
    print("\\begin{tabular}{|p{0.8cm}|p{3cm}|p{3cm}|p{2cm}|c|c|p{3cm}|}")
    print("\\hline")
    print("\\textbf{ID} & \\textbf{Expected} & \\textbf{Generated} & \\textbf{Error Type} & \\textbf{Hall?} & \\textbf{BLEU} & \\textbf{Root Cause} \\\\")
    print("\\hline")

    for _, row in df.head(10).iterrows():  # First 10 for paper
        # Escape special characters for LaTeX
        expected = row['Expected'].replace('_', '\\_').replace('&', '\\&')
        generated = row['Generated'].replace('_', '\\_').replace('&', '\\&')
        error_type = row['Error Type']
        hall = row['Hallucination?']
        bleu = row['BLEU']
        root = row['Root Cause']

        print(f"{row['ID']} & {expected} & {generated} & {error_type} & {hall} & {bleu} & {root} \\\\")
        print("\\hline")

    print("\\end{tabular}")
    print("\\end{table*}")
    print()
    print("="*100 + "\n")


def print_markdown_table(df: pd.DataFrame):
    """Print Markdown formatted table"""
    print("\n" + "="*100)
    print("MARKDOWN TABLE")
    print("="*100)
    print()
    print(df.to_markdown(index=False))
    print()
    print("="*100 + "\n")


def analyze_error_distribution(df: pd.DataFrame):
    """Analyze distribution of error types"""
    df['error_category'] = df.apply(categorize_error, axis=1)

    print("\n" + "="*80)
    print("ERROR DISTRIBUTION ANALYSIS")
    print("="*80)

    category_counts = df['error_category'].value_counts()
    total = len(df)

    for category, count in category_counts.items():
        percentage = count / total * 100
        print(f"{category:25s}: {count:4d} ({percentage:5.1f}%)")

    print("="*80 + "\n")


def main():
    """Generate hallucination analysis table"""
    # Load results
    df = load_latest_results()

    print(f"\nLoaded {len(df)} results")
    print(f"Hallucinations detected: {df['hallucination_detected'].sum()} ({df['hallucination_detected'].sum()/len(df)*100:.1f}%)\n")

    # Analyze error distribution
    analyze_error_distribution(df)

    # Create hallucination table
    table = create_hallucination_table(df, n=15)

    # Print in different formats
    print_markdown_table(table)
    print_latex_table(table)

    # Save as CSV
    output_path = "../results/hallucination_analysis.csv"
    table.to_csv(output_path, index=False)
    print(f"✅ Saved table to: {output_path}")


if __name__ == "__main__":
    main()
