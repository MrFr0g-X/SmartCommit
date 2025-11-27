"""
Compare Baseline vs Improved Experiment Results
Generates comparison tables for Phase 2 report
"""

import pandas as pd
import sys

def compare_experiments(baseline_id: str, improved_id: str):
    """Compare two experiments and generate report"""

    # Load results
    baseline = pd.read_csv(f'../results/experiment_{baseline_id}.csv')
    improved = pd.read_csv(f'../results/experiment_{improved_id}.csv')

    print("=" * 80)
    print("PHASE 2: BASELINE vs IMPROVED COMPARISON")
    print("=" * 80)

    print(f"\nBaseline Experiment: {baseline_id}")
    print(f"Improved Experiment: {improved_id}")
    print(f"\nSamples: Baseline={len(baseline)}, Improved={len(improved)}")

    # BLEU Comparison
    print("\n" + "-" * 80)
    print("BLEU-4 Score")
    print("-" * 80)
    baseline_bleu = baseline['bleu'].mean()
    improved_bleu = improved['bleu'].mean()
    print(f"Baseline:  {baseline_bleu:.2f} ± {baseline['bleu'].std():.2f}")
    print(f"Improved:  {improved_bleu:.2f} ± {improved['bleu'].std():.2f}")
    print(f"Change:    {improved_bleu - baseline_bleu:+.2f} ({((improved_bleu - baseline_bleu) / max(baseline_bleu, 0.01) * 100):+.1f}%)")

    # ROUGE Comparison
    print("\n" + "-" * 80)
    print("ROUGE-L Score")
    print("-" * 80)
    baseline_rouge = baseline['rougeL'].mean()
    improved_rouge = improved['rougeL'].mean()
    print(f"Baseline:  {baseline_rouge:.2f} ± {baseline['rougeL'].std():.2f}")
    print(f"Improved:  {improved_rouge:.2f} ± {improved['rougeL'].std():.2f}")
    print(f"Change:    {improved_rouge - baseline_rouge:+.2f} ({((improved_rouge - baseline_rouge) / baseline_rouge * 100):+.1f}%)")

    # Semantic Similarity
    print("\n" + "-" * 80)
    print("Semantic Similarity")
    print("-" * 80)
    baseline_sem = baseline['semantic_similarity'].mean()
    improved_sem = improved['semantic_similarity'].mean()
    print(f"Baseline:  {baseline_sem:.4f} ± {baseline['semantic_similarity'].std():.4f}")
    print(f"Improved:  {improved_sem:.4f} ± {improved['semantic_similarity'].std():.4f}")
    print(f"Change:    {improved_sem - baseline_sem:+.4f} ({((improved_sem - baseline_sem) / baseline_sem * 100):+.1f}%)")

    # Hallucination Rate
    print("\n" + "-" * 80)
    print("Hallucination Detection")
    print("-" * 80)
    baseline_hall = baseline['hallucination_detected'].sum() / len(baseline) * 100
    improved_hall = improved['hallucination_detected'].sum() / len(improved) * 100
    baseline_hall_rate = baseline['hallucination_rate'].mean() * 100
    improved_hall_rate = improved['hallucination_rate'].mean() * 100

    print(f"Detected Rate:")
    print(f"  Baseline:  {baseline['hallucination_detected'].sum()}/{len(baseline)} ({baseline_hall:.1f}%)")
    print(f"  Improved:  {improved['hallucination_detected'].sum()}/{len(improved)} ({improved_hall:.1f}%)")
    print(f"  Change:    {improved_hall - baseline_hall:+.1f}%")

    print(f"\nMean Hallucination Rate:")
    print(f"  Baseline:  {baseline_hall_rate:.2f}%")
    print(f"  Improved:  {improved_hall_rate:.2f}%")
    print(f"  Change:    {improved_hall_rate - baseline_hall_rate:+.2f}%")

    # Quality Score
    print("\n" + "-" * 80)
    print("Overall Quality Score")
    print("-" * 80)
    baseline_qual = baseline['quality_score'].mean()
    improved_qual = improved['quality_score'].mean()
    print(f"Baseline:  {baseline_qual:.4f} ± {baseline['quality_score'].std():.4f}")
    print(f"Improved:  {improved_qual:.4f} ± {improved['quality_score'].std():.4f}")
    print(f"Change:    {improved_qual - baseline_qual:+.4f} ({((improved_qual - baseline_qual) / baseline_qual * 100):+.1f}%)")

    # Latency
    print("\n" + "-" * 80)
    print("Generation Latency")
    print("-" * 80)
    baseline_lat = baseline['latency_ms'].mean()
    improved_lat = improved['latency_ms'].mean()
    print(f"Baseline:  {baseline_lat:.0f}ms ± {baseline['latency_ms'].std():.0f}ms")
    print(f"Improved:  {improved_lat:.0f}ms ± {improved['latency_ms'].std():.0f}ms")
    print(f"Change:    {improved_lat - baseline_lat:+.0f}ms ({((improved_lat - baseline_lat) / baseline_lat * 100):+.1f}%)")

    # Summary Table (LaTeX format for report)
    print("\n" + "=" * 80)
    print("LATEX TABLE FOR PHASE 2 REPORT")
    print("=" * 80)
    print(r"""
\begin{table}[h]
\centering
\caption{Baseline vs Improved System Comparison}
\begin{tabular}{lccc}
\hline
\textbf{Metric} & \textbf{Baseline} & \textbf{Improved} & \textbf{Change} \\
\hline""")
    print(f"BLEU-4 & {baseline_bleu:.2f} & {improved_bleu:.2f} & {improved_bleu - baseline_bleu:+.2f} \\\\")
    print(f"ROUGE-L & {baseline_rouge:.2f} & {improved_rouge:.2f} & {improved_rouge - baseline_rouge:+.2f} \\\\")
    print(f"Semantic Sim. & {baseline_sem:.4f} & {improved_sem:.4f} & {improved_sem - baseline_sem:+.4f} \\\\")
    print(f"Hallucination (\%) & {baseline_hall:.1f} & {improved_hall:.1f} & {improved_hall - baseline_hall:+.1f} \\\\")
    print(f"Quality Score & {baseline_qual:.4f} & {improved_qual:.4f} & {improved_qual - baseline_qual:+.4f} \\\\")
    print(f"Latency (ms) & {baseline_lat:.0f} & {improved_lat:.0f} & {improved_lat - baseline_lat:+.0f} \\\\")
    print(r"""\hline
\end{tabular}
\label{tab:comparison}
\end{table}
""")

    # Markdown Table
    print("\n" + "=" * 80)
    print("MARKDOWN TABLE")
    print("=" * 80)
    print("\n| Metric | Baseline | Improved | Change | % Change |")
    print("|--------|----------|----------|--------|----------|")
    print(f"| BLEU-4 | {baseline_bleu:.2f} | {improved_bleu:.2f} | {improved_bleu - baseline_bleu:+.2f} | - |")
    print(f"| ROUGE-L | {baseline_rouge:.2f} | {improved_rouge:.2f} | {improved_rouge - baseline_rouge:+.2f} | {((improved_rouge - baseline_rouge) / baseline_rouge * 100):+.1f}% |")
    print(f"| Semantic Similarity | {baseline_sem:.4f} | {improved_sem:.4f} | {improved_sem - baseline_sem:+.4f} | {((improved_sem - baseline_sem) / baseline_sem * 100):+.1f}% |")
    print(f"| Hallucination Rate | {baseline_hall:.1f}% | {improved_hall:.1f}% | {improved_hall - baseline_hall:+.1f}% | {((improved_hall - baseline_hall) / baseline_hall * 100):+.1f}% |")
    print(f"| Quality Score | {baseline_qual:.4f} | {improved_qual:.4f} | {improved_qual - baseline_qual:+.4f} | {((improved_qual - baseline_qual) / baseline_qual * 100):+.1f}% |")
    print(f"| Latency (ms) | {baseline_lat:.0f} | {improved_lat:.0f} | {improved_lat - baseline_lat:+.0f} | {((improved_lat - baseline_lat) / baseline_lat * 100):+.1f}% |")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python compare_results.py <baseline_id> <improved_id>")
        print("\nExample:")
        print("  python compare_results.py 20251127_001902 20251127_005526")
        print("\nAvailable experiments:")
        import os
        results_dir = '../results'
        if os.path.exists(results_dir):
            files = [f for f in os.listdir(results_dir) if f.startswith('experiment_') and f.endswith('.csv')]
            for f in sorted(files):
                exp_id = f.replace('experiment_', '').replace('.csv', '')
                print(f"  - {exp_id}")
        sys.exit(1)

    baseline_id = sys.argv[1]
    improved_id = sys.argv[2]

    compare_experiments(baseline_id, improved_id)
