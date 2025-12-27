"""
Evaluation Module - Implements metrics for commit message quality assessment
Includes BLEU, ROUGE, BERTScore, semantic similarity, and hallucination detection
"""

import re
import logging
from typing import Dict, List, Tuple
import numpy as np
import evaluate as hf_evaluate  # Rename to avoid circular import
from sentence_transformers import SentenceTransformer, util
import nltk

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CommitMessageEvaluator:
    """Evaluator for commit message quality"""

    def __init__(self):
        """Initialize evaluation metrics"""
        logger.info("Initializing evaluator...")

        # Load metrics using renamed import
        self.bleu = hf_evaluate.load("bleu")
        self.rouge = hf_evaluate.load("rouge")

        # Load sentence transformer for semantic similarity
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Stopwords for hallucination detection
        self.stopwords = set(stopwords.words('english'))

        # Common programming terms that don't need to appear in diff
        self.allowed_technical_terms = {
            'fix', 'bug', 'issue', 'error', 'refactor', 'update', 'add',
            'remove', 'delete', 'implement', 'feature', 'change', 'modify',
            'improve', 'optimize', 'clean', 'rename', 'move', 'merge',
            'function', 'method', 'class', 'variable', 'parameter', 'return',
            'import', 'export', 'test', 'tests', 'testing', 'code', 'file'
        }

        logger.info("Evaluator initialized successfully")

    def evaluate_message(self, generated: str, reference: str, diff: str) -> Dict:
        """
        Comprehensive evaluation of generated commit message

        Args:
            generated: AI-generated commit message
            reference: Human-written reference message
            diff: Code diff used for generation

        Returns:
            Dictionary with all evaluation metrics
        """
        results = {}

        # BLEU score
        bleu_score = self.compute_bleu(generated, reference)
        results['bleu'] = bleu_score

        # ROUGE scores
        rouge_scores = self.compute_rouge(generated, reference)
        results['rouge'] = rouge_scores

        # Semantic similarity
        semantic_sim = self.compute_semantic_similarity(generated, reference)
        results['semantic_similarity'] = semantic_sim

        # Hallucination detection
        hallucination_results = self.detect_hallucination(generated, diff)
        results['hallucination'] = hallucination_results

        # Overall quality score (weighted combination)
        quality_score = self._compute_quality_score(results)
        results['quality_score'] = quality_score

        return results

    def compute_bleu(self, generated: str, reference: str) -> float:
        """Compute BLEU-4 score"""
        try:
            result = self.bleu.compute(
                predictions=[generated],
                references=[reference]
            )
            # Convert to 0-100 scale to match paper reporting
            return round(result['bleu'] * 100, 2)
        except Exception as e:
            logger.error(f"Error computing BLEU: {e}")
            return 0.0

    def compute_rouge(self, generated: str, reference: str) -> Dict:
        """Compute ROUGE scores"""
        try:
            result = self.rouge.compute(
                predictions=[generated],
                references=[reference]
            )
            # Convert to 0-100 scale and extract relevant scores
            return {
                'rouge1': round(result['rouge1'] * 100, 2),
                'rouge2': round(result['rouge2'] * 100, 2),
                'rougeL': round(result['rougeL'] * 100, 2)
            }
        except Exception as e:
            logger.error(f"Error computing ROUGE: {e}")
            return {'rouge1': 0.0, 'rouge2': 0.0, 'rougeL': 0.0}

    def compute_semantic_similarity(self, generated: str, reference: str) -> float:
        """Compute cosine similarity between sentence embeddings"""
        try:
            # Encode sentences
            embedding1 = self.sentence_model.encode(generated, convert_to_tensor=True)
            embedding2 = self.sentence_model.encode(reference, convert_to_tensor=True)

            # Compute cosine similarity
            similarity = util.cos_sim(embedding1, embedding2)
            return round(float(similarity[0][0]), 4)
        except Exception as e:
            logger.error(f"Error computing semantic similarity: {e}")
            return 0.0

    def detect_hallucination(self, message: str, diff: str) -> Dict:
        """
        Detect potential hallucinations in commit message
        Based on Liu et al. 2025 methodology
        """
        # Tokenize and clean message
        message_tokens = self._extract_meaningful_tokens(message)

        # Extract tokens from diff
        diff_tokens = self._extract_diff_tokens(diff)

        # Check which message tokens are grounded in diff
        ungrounded_tokens = []
        total_checked = 0

        for token in message_tokens:
            # Skip allowed technical terms
            if token.lower() in self.allowed_technical_terms:
                continue

            total_checked += 1

            # Check if token appears in diff (case-insensitive)
            if not any(token.lower() in diff_token.lower() for diff_token in diff_tokens):
                ungrounded_tokens.append(token)

        # Calculate hallucination rate
        if total_checked == 0:
            hallucination_rate = 0.0
        else:
            hallucination_rate = len(ungrounded_tokens) / total_checked

        return {
            'detected': hallucination_rate > 0.15,  # 15% threshold
            'hallucination_rate': round(hallucination_rate, 4),
            'ungrounded_tokens': ungrounded_tokens,
            'total_tokens_checked': total_checked
        }

    def _extract_meaningful_tokens(self, text: str) -> List[str]:
        """Extract meaningful tokens from text (no stopwords, punctuation)"""
        # Tokenize
        tokens = word_tokenize(text.lower())

        # Filter stopwords and short tokens
        meaningful = [
            token for token in tokens
            if token.isalnum() and
            token not in self.stopwords and
            len(token) > 2
        ]

        return meaningful

    def _extract_diff_tokens(self, diff: str) -> List[str]:
        """Extract all tokens from diff"""
        # Remove diff markers
        diff_clean = re.sub(r'^[+-]', '', diff, flags=re.MULTILINE)
        diff_clean = re.sub(r'diff --git.*?\n', '', diff_clean)
        diff_clean = re.sub(r'index.*?\n', '', diff_clean)
        diff_clean = re.sub(r'@@.*?@@', '', diff_clean)

        # Tokenize
        tokens = word_tokenize(diff_clean.lower())

        return tokens

    def _compute_quality_score(self, results: Dict) -> float:
        """
        Compute overall quality score from individual metrics
        Weighted combination: BLEU(30%), ROUGE-L(30%), Semantic(30%), NoHallucination(10%)
        """
        bleu = results['bleu'] / 100  # normalize to 0-1
        rougeL = results['rouge']['rougeL'] / 100
        semantic = results['semantic_similarity']
        hallucination_penalty = 0.0 if results['hallucination']['detected'] else 0.1

        quality = (0.3 * bleu) + (0.3 * rougeL) + (0.3 * semantic) + hallucination_penalty

        return round(quality, 4)

    def batch_evaluate(self, predictions: List[str], references: List[str],
                      diffs: List[str]) -> List[Dict]:
        """Evaluate multiple message pairs"""
        results = []
        for pred, ref, diff in zip(predictions, references, diffs):
            result = self.evaluate_message(pred, ref, diff)
            results.append(result)
        return results


# For testing
if __name__ == "__main__":
    evaluator = CommitMessageEvaluator()

    # Test case
    generated = "Fix multiplication bug in calculate_total"
    reference = "Fix bug in calculate_total by adding quantity multiplication"
    diff = """--- a/utils.py
+++ b/utils.py
@@ -10,7 +10,7 @@ def calculate_total(items):
-        total += item.price
+        total += item.price * item.quantity
"""

    results = evaluator.evaluate_message(generated, reference, diff)

    print("Evaluation Results:")
    print(f"BLEU: {results['bleu']}")
    print(f"ROUGE-L: {results['rouge']['rougeL']}")
    print(f"Semantic Similarity: {results['semantic_similarity']}")
    print(f"Hallucination Detected: {results['hallucination']['detected']}")
    print(f"Quality Score: {results['quality_score']}")
