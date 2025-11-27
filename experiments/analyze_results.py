"""
Results Analysis Script
Analyzes experimental results and generates tables/plots for Phase 2 report
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict
import json

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 11


class ResultsAnalyzer:
    """Analyze experimental results"""

    def __init__(self, results_path: str):
        """Load results from CSV"""
        self.results_df = pd.read_csv(results_path)
        self.experiment_id = os.path.basename(results_path).replace('experiment_', '').replace('.csv', '')

        print(f"Loaded {len(self.results_df)} results from {results_path}")

    def generate_metric_summary_table(self) -> pd.DataFrame:
        """Generate summary statistics table"""
        metrics = ['bleu', 'rougeL', 'semantic_similarity', 'quality_score']

        summary = []
        for metric in metrics:
            values = self.results_df[metric]
            summary.append({
                'Metric': metric.replace('_', ' ').title(),
                'Mean': f"{values.mean():.3f}",
                'Std': f"{values.std():.3f}",
                'Min': f"{values.min():.3f}",
                'Max': f"{values.max():.3f}",
                'Median': f"{values.median():.3f}"
            })

        summary_df = pd.DataFrame(summary)
        print("\n" + "="*80)
        print("METRIC SUMMARY TABLE")
        print("="*80)
        print(summary_df.to_string(index=False))
        print("="*80 + "\n")

        return summary_df

    def analyze_hallucinations(self) -> Dict:
        """Analyze hallucination patterns"""
        total = len(self.results_df)
        detected = self.results_df['hallucination_detected'].sum()
        rate = detected / total

        mean_hall_rate = self.results_df['hallucination_rate'].mean()

        print("\n" + "="*80)
        print("HALLUCINATION ANALYSIS")
        print("="*80)
        print(f"Total samples:           {total}")
        print(f"Hallucinations detected: {detected} ({rate*100:.1f}%)")
        print(f"Mean hallucination rate: {mean_hall_rate*100:.2f}%")
        print("="*80 + "\n")

        return {
            'total_samples': total,
            'hallucinations_detected': int(detected),
            'detection_percentage': rate,
            'mean_hallucination_rate': mean_hall_rate
        }

    def categorize_errors(self) -> pd.DataFrame:
        """Categorize errors based on metrics"""
        def categorize(row):
            if row['bleu'] < 5:
                return "Very Low BLEU"
            elif row['hallucination_detected']:
                return "Hallucination"
            elif row['semantic_similarity'] < 0.5:
                return "Low Semantic Sim"
            elif row['quality_score'] < 0.5:
                return "Low Quality"
            else:
                return "Acceptable"

        self.results_df['error_category'] = self.results_df.apply(categorize, axis=1)

        category_counts = self.results_df['error_category'].value_counts()

        print("\n" + "="*80)
        print("ERROR CATEGORIZATION")
        print("="*80)
        for category, count in category_counts.items():
            percentage = count / len(self.results_df) * 100
            print(f"{category:20s}: {count:4d} ({percentage:5.1f}%)")
        print("="*80 + "\n")

        return category_counts

    def get_failure_examples(self, n: int = 10) -> pd.DataFrame:
        """Get worst performing examples for analysis"""
        # Sort by quality score
        failures = self.results_df.nsmallest(n, 'quality_score')

        examples = failures[['sample_id', 'reference_message', 'generated_message',
                            'bleu', 'hallucination_detected', 'quality_score']]

        print("\n" + "="*80)
        print(f"TOP {n} FAILURE EXAMPLES")
        print("="*80)
        for idx, row in examples.iterrows():
            print(f"\nSample {row['sample_id']}:")
            print(f"  Reference:  {row['reference_message'][:80]}...")
            print(f"  Generated:  {row['generated_message'][:80]}...")
            print(f"  BLEU: {row['bleu']:.2f} | Hallucination: {row['hallucination_detected']} | Quality: {row['quality_score']:.3f}")
        print("="*80 + "\n")

        return examples

    def get_success_examples(self, n: int = 10) -> pd.DataFrame:
        """Get best performing examples"""
        successes = self.results_df.nlargest(n, 'quality_score')

        examples = successes[['sample_id', 'reference_message', 'generated_message',
                             'bleu', 'semantic_similarity', 'quality_score']]

        print("\n" + "="*80)
        print(f"TOP {n} SUCCESS EXAMPLES")
        print("="*80)
        for idx, row in examples.iterrows():
            print(f"\nSample {row['sample_id']}:")
            print(f"  Reference:  {row['reference_message'][:80]}...")
            print(f"  Generated:  {row['generated_message'][:80]}...")
            print(f"  BLEU: {row['bleu']:.2f} | Semantic: {row['semantic_similarity']:.3f} | Quality: {row['quality_score']:.3f}")
        print("="*80 + "\n")

        return examples

    def plot_metric_distributions(self, save_path: str = None):
        """Plot distributions of evaluation metrics"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        metrics = [
            ('bleu', 'BLEU-4 Score'),
            ('rougeL', 'ROUGE-L Score'),
            ('semantic_similarity', 'Semantic Similarity'),
            ('quality_score', 'Quality Score')
        ]

        for ax, (metric, title) in zip(axes.flat, metrics):
            data = self.results_df[metric]

            ax.hist(data, bins=30, edgecolor='black', alpha=0.7)
            ax.axvline(data.mean(), color='red', linestyle='--', label=f'Mean: {data.mean():.2f}')
            ax.set_xlabel(title)
            ax.set_ylabel('Frequency')
            ax.set_title(f'Distribution of {title}')
            ax.legend()
            ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved distribution plot to {save_path}")

        plt.show()

    def plot_hallucination_analysis(self, save_path: str = None):
        """Plot hallucination detection results"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Pie chart of detection
        detected = self.results_df['hallucination_detected'].value_counts()
        colors = ['#4CAF50', '#f44336']
        ax1.pie(detected, labels=['No Hallucination', 'Hallucination Detected'],
               autopct='%1.1f%%', colors=colors, startangle=90)
        ax1.set_title('Hallucination Detection Rate')

        # Histogram of hallucination rates
        hall_rates = self.results_df['hallucination_rate'] * 100
        ax2.hist(hall_rates, bins=30, edgecolor='black', alpha=0.7)
        ax2.axvline(15, color='red', linestyle='--', label='15% Threshold')
        ax2.set_xlabel('Hallucination Rate (%)')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Distribution of Hallucination Rates')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved hallucination plot to {save_path}")

        plt.show()

    def generate_comparison_table(self) -> pd.DataFrame:
        """Generate table comparing our results to baselines"""
        our_results = {
            'Model': 'SmartCommit (Gemini 2.0)',
            'BLEU-4': f"{self.results_df['bleu'].mean():.2f}",
            'ROUGE-L': f"{self.results_df['rougeL'].mean():.2f}",
            'Hallucination Rate': f"{self.results_df['hallucination_detected'].mean()*100:.1f}%",
            'Quality Score': f"{self.results_df['quality_score'].mean():.3f}"
        }

        # Baselines from Phase 1 literature review
        baselines = [
            {'Model': 'CodeT5 (Wang 2021)', 'BLEU-4': '18-19', 'ROUGE-L': '44-47', 'Hallucination Rate': 'N/A', 'Quality Score': 'N/A'},
            {'Model': 'CommitBERT (Jung 2021)', 'BLEU-4': '11-14', 'ROUGE-L': 'N/A', 'Hallucination Rate': 'N/A', 'Quality Score': 'N/A'},
            {'Model': 'Baseline (Liu 2025)', 'BLEU-4': 'N/A', 'ROUGE-L': 'N/A', 'Hallucination Rate': '20%', 'Quality Score': 'N/A'},
            our_results
        ]

        comparison_df = pd.DataFrame(baselines)

        print("\n" + "="*80)
        print("COMPARISON WITH BASELINES")
        print("="*80)
        print(comparison_df.to_string(index=False))
        print("="*80 + "\n")

        return comparison_df


def main():
    """Run analysis on latest results"""
    results_dir = "../results"

    # Find latest experiment
    files = [f for f in os.listdir(results_dir) if f.startswith('experiment_') and f.endswith('.csv')]

    if not files:
        print("No experiment results found in ../results/")
        return

    latest_file = sorted(files)[-1]
    results_path = os.path.join(results_dir, latest_file)

    print(f"Analyzing: {latest_file}\n")

    # Initialize analyzer
    analyzer = ResultsAnalyzer(results_path)

    # Run all analyses
    analyzer.generate_metric_summary_table()
    analyzer.analyze_hallucinations()
    analyzer.categorize_errors()
    analyzer.get_failure_examples(10)
    analyzer.get_success_examples(10)

    # Generate plots
    plots_dir = os.path.join(results_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)

    analyzer.plot_metric_distributions(
        save_path=os.path.join(plots_dir, f"metrics_distribution_{analyzer.experiment_id}.png")
    )

    analyzer.plot_hallucination_analysis(
        save_path=os.path.join(plots_dir, f"hallucination_analysis_{analyzer.experiment_id}.png")
    )

    # Generate comparison table
    analyzer.generate_comparison_table()


if __name__ == "__main__":
    main()
