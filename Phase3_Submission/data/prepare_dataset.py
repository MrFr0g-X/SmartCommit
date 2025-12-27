"""
Dataset Preparation Script
Prepares CommitBench samples for experimentation
"""

import pandas as pd
import numpy as np
import os
import re
import random
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatasetPreparator:
    """Prepare and clean CommitBench dataset"""

    def __init__(self):
        """Initialize preparator"""
        self.min_diff_length = 50
        self.max_diff_length = 5000
        self.min_message_length = 10

    def load_commitbench(self, path: str) -> pd.DataFrame:
        """Load CommitBench dataset from CSV/JSON"""
        if os.path.exists(path):
            logger.info(f"Loading existing dataset from {path}")
            return pd.read_csv(path)
        else:
            logger.warning(f"CommitBench file not found, generating synthetic samples")
            return self._generate_synthetic_samples()

    def _generate_synthetic_samples(self, n: int = 500) -> pd.DataFrame:
        """Generate diverse synthetic commit message samples"""
        logger.info(f"Generating {n} synthetic samples...")

        samples = []

        # File names
        files = ['utils.py', 'models.py', 'api.py', 'services.py', 'handlers.py',
                'validators.py', 'controllers.py', 'database.py', 'config.py', 'auth.py']

        # Function names
        functions = ['process_data', 'calculate_total', 'validate_input', 'fetch_results',
                    'handle_request', 'save_record', 'update_status', 'delete_item',
                    'format_output', 'parse_config', 'authenticate_user', 'send_email']

        # Class names
        classes = ['DataProcessor', 'Calculator', 'Validator', 'APIClient',
                  'RequestHandler', 'DatabaseManager', 'ConfigLoader', 'AuthService']

        # Variables
        variables = ['result', 'data', 'response', 'status', 'config', 'user', 'item']

        for i in range(n):
            sample_type = ['bug_fix', 'feature_add', 'refactor'][i % 3]

            file = random.choice(files)
            func = random.choice(functions)
            cls = random.choice(classes)
            var1 = random.choice(variables)
            var2 = random.choice(variables)

            if sample_type == 'bug_fix':
                old_val = random.choice(['None', 'False', '0', 'null', 'empty'])
                new_val = random.choice(['value', 'True', '1', 'data', 'result'])

                diff = f"""diff --git a/src/{file} b/src/{file}
index {random.randint(1000000, 9999999)}..{random.randint(1000000, 9999999)} 100644
--- a/src/{file}
+++ b/src/{file}
@@ -{random.randint(10, 50)},{random.randint(5, 15)} +{random.randint(10, 50)},{random.randint(5, 15)} @@ def {func}({var1}, {var2}=None):
     # Process the input
-    {var1} = {old_val}
+    {var1} = {new_val}
     return {var1}
"""

                issues = ['null pointer', 'division by zero', 'missing validation',
                         'incorrect calculation', 'undefined variable']
                issue = random.choice(issues)
                message = f"Fix {issue} in {func}"

            elif sample_type == 'feature_add':
                new_func = random.choice(functions)
                params = f"{var1}, {var2}"

                diff = f"""diff --git a/src/{file} b/src/{file}
index {random.randint(1000000, 9999999)}..{random.randint(1000000, 9999999)} 100644
--- a/src/{file}
+++ b/src/{file}
@@ -{random.randint(20, 60)},{random.randint(5, 15)} +{random.randint(20, 60)},{random.randint(5, 20)} @@ class {cls}:
     def {func}(self):
         pass

+    def {new_func}(self, {params}):
+        \"\"\"Process {var1} and return {var2}\"\"\"
+        {var2} = self._compute_{var1}({var1})
+        return {var2}
+
"""

                features = ['validation', 'caching', 'error handling', 'logging',
                           'statistics', 'filtering', 'sorting', 'formatting']
                feature = random.choice(features)
                message = f"Add {feature} to {cls}"

            else:  # refactor
                old_impl = f"{var1} = {var2}.method1()\n    {var2} = process({var1})"
                new_impl = f"{var1} = self._simplified_{var2}_process({var2})"

                diff = f"""diff --git a/src/{file} b/src/{file}
index {random.randint(1000000, 9999999)}..{random.randint(1000000, 9999999)} 100644
--- a/src/{file}
+++ b/src/{file}
@@ -{random.randint(10, 50)},{random.randint(10, 20)} +{random.randint(10, 50)},{random.randint(8, 15)} @@ def {func}():
-    {old_impl}
+    {new_impl}
     return {var1}
"""

                reasons = ['better readability', 'improved performance', 'simplified logic',
                          'reduced complexity', 'better maintainability']
                reason = random.choice(reasons)
                message = f"Refactor {func} for {reason}"

            samples.append({
                'id': i,
                'diff': diff.strip(),
                'message': message,
                'type': sample_type,
                'language': 'python'
            })

        df = pd.DataFrame(samples)
        logger.info(f"Generated {len(df)} synthetic samples")
        return df

    def clean_and_filter(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and filter dataset"""
        logger.info(f"Initial dataset size: {len(df)}")

        df = df.dropna(subset=['diff', 'message'])
        logger.info(f"After removing nulls: {len(df)}")

        df['diff_length'] = df['diff'].str.len()
        df = df[
            (df['diff_length'] >= self.min_diff_length) &
            (df['diff_length'] <= self.max_diff_length)
        ]
        logger.info(f"After length filtering: {len(df)}")

        df['message_length'] = df['message'].str.len()
        df = df[df['message_length'] >= self.min_message_length]
        logger.info(f"After message filtering: {len(df)}")

        df = df.drop_duplicates(subset=['message'])
        logger.info(f"After deduplication: {len(df)}")

        df['message'] = df['message'].str.strip()
        df['message'] = df['message'].str.replace(r'\s+', ' ', regex=True)

        df = df.drop(columns=['diff_length', 'message_length'], errors='ignore')

        logger.info(f"Final dataset size: {len(df)}")
        return df

    def stratified_sample(self, df: pd.DataFrame, n: int, by: str = None) -> pd.DataFrame:
        """Sample dataset with stratification"""
        if by and by in df.columns:
            sampled = df.groupby(by, group_keys=False).apply(
                lambda x: x.sample(min(len(x), n // df[by].nunique()), random_state=42),
                include_groups=False
            )
            logger.info(f"Stratified sampling by {by}: {len(sampled)} samples")
        else:
            sampled = df.sample(min(n, len(df)), random_state=42)
            logger.info(f"Random sampling: {len(sampled)} samples")

        return sampled.reset_index(drop=True)

    def save_dataset(self, df: pd.DataFrame, output_path: str):
        """Save processed dataset"""
        df.to_csv(output_path, index=False)
        logger.info(f"Saved dataset to {output_path}")

        print("\n" + "="*80)
        print("DATASET SUMMARY")
        print("="*80)
        print(f"Total samples: {len(df)}")

        if 'type' in df.columns:
            print("\nSamples by type:")
            print(df['type'].value_counts())

        if 'language' in df.columns:
            print("\nSamples by language:")
            print(df['language'].value_counts())

        print("\nMessage statistics:")
        print(f"  Mean length: {df['message'].str.len().mean():.1f} chars")
        print(f"  Min length:  {df['message'].str.len().min()} chars")
        print(f"  Max length:  {df['message'].str.len().max()} chars")

        print("\nDiff statistics:")
        print(f"  Mean length: {df['diff'].str.len().mean():.1f} chars")
        print(f"  Min length:  {df['diff'].str.len().min()} chars")
        print(f"  Max length:  {df['diff'].str.len().max()} chars")
        print("="*80 + "\n")


def main():
    """Main dataset preparation workflow"""
    preparator = DatasetPreparator()

    commitbench_path = "commitbench_raw.csv"
    df = preparator.load_commitbench(commitbench_path)

    df = preparator.clean_and_filter(df)

    df_sampled = preparator.stratified_sample(df, n=500, by='type')

    output_path = "commitbench_samples.csv"
    preparator.save_dataset(df_sampled, output_path)

    print(f"\nDataset ready for experiments: {output_path}")
    print(f"Run experiments with: python ../experiments/run_experiments.py")


if __name__ == "__main__":
    main()
