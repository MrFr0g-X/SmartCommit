"""
Experiment Runner for SmartCommit Phase 2
Runs batch evaluation on CommitBench dataset samples
"""

import sys
import os

# Add project root to path (works whether run from experiments/ or project/)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Go up one level from experiments/
sys.path.insert(0, project_root)
import json
import pandas as pd
import yaml
from datetime import datetime
from tqdm import tqdm
import logging
import time

from api.model_service import ModelService
from api.evaluate_simple import CommitMessageEvaluator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ExperimentRunner:
    """Run and log experiments on dataset samples"""

    def __init__(self, config_path: str = "../config.yaml"):
        """Initialize experiment runner"""
        # Resolve config path to absolute (works from any directory)
        if not os.path.isabs(config_path):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.normpath(os.path.join(current_dir, config_path))

        # Load config
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Initialize services
        self.model_service = ModelService(config_path)
        self.evaluator = CommitMessageEvaluator()

        # Setup paths
        self.results_dir = self.config['output']['results_dir']
        if not os.path.isabs(self.results_dir):
            current = os.path.dirname(os.path.abspath(__file__))
            self.results_dir = os.path.normpath(os.path.join(current, "..", self.results_dir))
        os.makedirs(self.results_dir, exist_ok=True)

        self.experiment_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info(f"Initialized experiment: {self.experiment_id}")

    def run_experiment(self, dataset_path: str, num_samples: int = None):
        """
        Run full experiment on dataset

        Args:
            dataset_path: Path to CSV file with diff and message columns
            num_samples: Number of samples to process (None = all)

        Returns:
            Results dataframe
        """
        logger.info(f"Loading dataset from {dataset_path}")

        # Load dataset
        df = pd.read_csv(dataset_path)

        if num_samples:
            df = df.head(num_samples)

        logger.info(f"Processing {len(df)} samples")

        results = []
        errors = 0

        # Get delay setting (for rate limiting)
        delay = self.config['experiment'].get('delay_seconds', 0)
        if delay > 0:
            logger.info(f"Rate limiting enabled: {delay}s delay between requests")

        # Process each sample
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing"):
            try:
                # Get diff and reference message
                diff = row['diff']
                reference = row['message']

                # Generate commit message
                gen_result = self.model_service.generate_commit_message(diff)

                if not gen_result['success']:
                    logger.error(f"Generation failed for sample {idx}")
                    errors += 1
                    # Still delay even on failure to respect rate limits
                    if delay > 0:
                        time.sleep(delay)
                    continue

                generated = gen_result['message']

                # Evaluate
                eval_result = self.evaluator.evaluate_message(
                    generated=generated,
                    reference=reference,
                    diff=diff
                )

                # Combine results
                result = {
                    'sample_id': idx,
                    'diff': diff[:200] + '...',  # Truncate for storage
                    'reference_message': reference,
                    'generated_message': generated,
                    'bleu': eval_result['bleu'],
                    'rouge1': eval_result['rouge']['rouge1'],
                    'rouge2': eval_result['rouge']['rouge2'],
                    'rougeL': eval_result['rouge']['rougeL'],
                    'semantic_similarity': eval_result['semantic_similarity'],
                    'hallucination_detected': eval_result['hallucination']['detected'],
                    'hallucination_rate': eval_result['hallucination']['hallucination_rate'],
                    'quality_score': eval_result['quality_score'],
                    'latency_ms': gen_result['latency_ms'],
                    'model': gen_result['model'],
                    'temperature': gen_result['temperature']
                }

                results.append(result)

                # Delay to respect API rate limits
                if delay > 0 and idx < len(df) - 1:  # Don't delay after last sample
                    time.sleep(delay)

            except Exception as e:
                logger.error(f"Error processing sample {idx}: {e}")
                errors += 1
                # Still delay even on error to respect rate limits
                if delay > 0:
                    time.sleep(delay)
                continue

        logger.info(f"Completed with {errors} errors")

        # Convert to dataframe
        results_df = pd.DataFrame(results)

        # Save results
        self._save_results(results_df)

        # Print summary
        self._print_summary(results_df)

        return results_df

    def _save_results(self, results_df: pd.DataFrame):
        """Save experiment results"""
        # Save as CSV
        csv_path = os.path.join(
            self.results_dir,
            f"experiment_{self.experiment_id}.csv"
        )
        results_df.to_csv(csv_path, index=False)
        logger.info(f"Saved results to {csv_path}")

        # Save summary statistics
        summary = {
            'experiment_id': self.experiment_id,
            'timestamp': datetime.now().isoformat(),
            'num_samples': len(results_df),
            'metrics': {
                'mean_bleu': float(results_df['bleu'].mean()),
                'mean_rougeL': float(results_df['rougeL'].mean()),
                'mean_semantic_similarity': float(results_df['semantic_similarity'].mean()),
                'mean_quality_score': float(results_df['quality_score'].mean()),
                'hallucination_rate': float(results_df['hallucination_detected'].sum() / len(results_df)),
                'mean_latency_ms': float(results_df['latency_ms'].mean())
            },
            'config': self.config['model']
        }

        summary_path = os.path.join(
            self.results_dir,
            f"summary_{self.experiment_id}.json"
        )
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Saved summary to {summary_path}")

    def _print_summary(self, results_df: pd.DataFrame):
        """Print experiment summary"""
        print("\n" + "="*80)
        print(f"EXPERIMENT SUMMARY - {self.experiment_id}")
        print("="*80)
        print(f"\nSamples processed: {len(results_df)}")
        print(f"\nMetrics:")
        print(f"  BLEU-4:              {results_df['bleu'].mean():.2f} ± {results_df['bleu'].std():.2f}")
        print(f"  ROUGE-L:             {results_df['rougeL'].mean():.2f} ± {results_df['rougeL'].std():.2f}")
        print(f"  Semantic Similarity: {results_df['semantic_similarity'].mean():.4f} ± {results_df['semantic_similarity'].std():.4f}")
        print(f"  Quality Score:       {results_df['quality_score'].mean():.4f} ± {results_df['quality_score'].std():.4f}")
        print(f"\nHallucination:")
        print(f"  Detected:            {results_df['hallucination_detected'].sum()} / {len(results_df)} ({results_df['hallucination_detected'].sum()/len(results_df)*100:.1f}%)")
        print(f"  Mean rate:           {results_df['hallucination_rate'].mean()*100:.2f}%")
        print(f"\nPerformance:")
        print(f"  Mean latency:        {results_df['latency_ms'].mean():.0f}ms")
        print(f"  Model:               {results_df['model'].iloc[0]}")
        print("="*80 + "\n")


def main():
    """Main experiment runner"""
    # Initialize runner
    runner = ExperimentRunner()

    # Run experiment
    dataset_path = runner.config['experiment']['dataset_path']
    # Make dataset path absolute
    if not os.path.isabs(dataset_path):
        current = os.path.dirname(os.path.abspath(__file__))
        dataset_path = os.path.normpath(os.path.join(current, "..", dataset_path))

    num_samples = runner.config['experiment']['num_samples']

    if not os.path.exists(dataset_path):
        logger.error(f"Dataset not found: {dataset_path}")
        logger.info("Please run data/prepare_dataset.py first")
        return

    results = runner.run_experiment(dataset_path, num_samples)

    logger.info("Experiment complete!")


if __name__ == "__main__":
    main()
