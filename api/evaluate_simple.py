"""
Simplified Evaluation Module - No TensorFlow/Keras dependencies
Implements BLEU, ROUGE, and hallucination detection only
"""

import re
import logging
from typing import Dict, List
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
from collections import Counter
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CommitMessageEvaluator:
    """Simplified evaluator for commit message quality"""

    def __init__(self):
        """Initialize evaluation metrics"""
        logger.info("Initializing simplified evaluator...")

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
        """Comprehensive evaluation of generated commit message"""
        results = {}

        # BLEU score
        bleu_score = self.compute_bleu(generated, reference)
        results['bleu'] = bleu_score

        # ROUGE scores
        rouge_scores = self.compute_rouge(generated, reference)
        results['rouge'] = rouge_scores

        # Semantic similarity (simplified - word overlap)
        semantic_sim = self.compute_word_overlap(generated, reference)
        results['semantic_similarity'] = semantic_sim

        # Hallucination detection
        hallucination_results = self.detect_hallucination(generated, diff)
        results['hallucination'] = hallucination_results

        # Overall quality score
        quality_score = self._compute_quality_score(results)
        results['quality_score'] = quality_score

        return results

    def compute_bleu(self, generated: str, reference: str) -> float:
        """Compute BLEU-4 score manually"""
        try:
            gen_tokens = word_tokenize(generated.lower())
            ref_tokens = word_tokenize(reference.lower())

            if len(gen_tokens) == 0:
                return 0.0

            # Calculate precision for n-grams (1 to 4)
            precisions = []
            for n in range(1, 5):
                gen_ngrams = self._get_ngrams(gen_tokens, n)
                ref_ngrams = self._get_ngrams(ref_tokens, n)

                if len(gen_ngrams) == 0:
                    precisions.append(0)
                    continue

                matches = sum((gen_ngrams & ref_ngrams).values())
                total = sum(gen_ngrams.values())

                precisions.append(matches / total if total > 0 else 0)

            # Geometric mean of precisions
            if all(p > 0 for p in precisions):
                geo_mean = math.exp(sum(math.log(p) for p in precisions) / 4)
            else:
                geo_mean = 0.0

            # Brevity penalty
            if len(gen_tokens) >= len(ref_tokens):
                bp = 1.0
            else:
                bp = math.exp(1 - len(ref_tokens) / len(gen_tokens))

            bleu = bp * geo_mean * 100  # Convert to 0-100 scale
            return round(bleu, 2)

        except Exception as e:
            logger.error(f"Error computing BLEU: {e}")
            return 0.0

    def compute_rouge(self, generated: str, reference: str) -> Dict:
        """Compute ROUGE scores manually"""
        try:
            gen_tokens = word_tokenize(generated.lower())
            ref_tokens = word_tokenize(reference.lower())

            # ROUGE-1 (unigram overlap)
            rouge1 = self._rouge_n(gen_tokens, ref_tokens, 1)

            # ROUGE-2 (bigram overlap)
            rouge2 = self._rouge_n(gen_tokens, ref_tokens, 2)

            # ROUGE-L (longest common subsequence)
            rougeL = self._rouge_l(gen_tokens, ref_tokens)

            return {
                'rouge1': round(rouge1 * 100, 2),
                'rouge2': round(rouge2 * 100, 2),
                'rougeL': round(rougeL * 100, 2)
            }
        except Exception as e:
            logger.error(f"Error computing ROUGE: {e}")
            return {'rouge1': 0.0, 'rouge2': 0.0, 'rougeL': 0.0}

    def compute_word_overlap(self, generated: str, reference: str) -> float:
        """Compute simple word overlap as semantic similarity proxy"""
        try:
            gen_words = set(word_tokenize(generated.lower()))
            ref_words = set(word_tokenize(reference.lower()))

            # Remove stopwords
            gen_words = gen_words - self.stopwords
            ref_words = ref_words - self.stopwords

            if len(gen_words) == 0 or len(ref_words) == 0:
                return 0.0

            # Jaccard similarity
            intersection = len(gen_words & ref_words)
            union = len(gen_words | ref_words)

            return round(intersection / union, 4) if union > 0 else 0.0

        except Exception as e:
            logger.error(f"Error computing semantic similarity: {e}")
            return 0.0

    def detect_hallucination(self, message: str, diff: str) -> Dict:
        """Detect potential hallucinations in commit message"""
        message_tokens = self._extract_meaningful_tokens(message)
        diff_tokens = self._extract_diff_tokens(diff)

        ungrounded_tokens = []
        total_checked = 0

        for token in message_tokens:
            if token.lower() in self.allowed_technical_terms:
                continue

            total_checked += 1

            if not any(token.lower() in diff_token.lower() for diff_token in diff_tokens):
                ungrounded_tokens.append(token)

        if total_checked == 0:
            hallucination_rate = 0.0
        else:
            hallucination_rate = len(ungrounded_tokens) / total_checked

        return {
            'detected': hallucination_rate > 0.10,  # Stricter threshold (was 0.15)
            'hallucination_rate': round(hallucination_rate, 4),
            'ungrounded_tokens': ungrounded_tokens,
            'total_tokens_checked': total_checked
        }

    def _get_ngrams(self, tokens: List[str], n: int) -> Counter:
        """Get n-grams from token list"""
        ngrams = []
        for i in range(len(tokens) - n + 1):
            ngrams.append(tuple(tokens[i:i+n]))
        return Counter(ngrams)

    def _rouge_n(self, gen_tokens: List[str], ref_tokens: List[str], n: int) -> float:
        """Compute ROUGE-N score"""
        gen_ngrams = self._get_ngrams(gen_tokens, n)
        ref_ngrams = self._get_ngrams(ref_tokens, n)

        if sum(ref_ngrams.values()) == 0:
            return 0.0

        matches = sum((gen_ngrams & ref_ngrams).values())
        total_ref = sum(ref_ngrams.values())

        return matches / total_ref if total_ref > 0 else 0.0

    def _rouge_l(self, gen_tokens: List[str], ref_tokens: List[str]) -> float:
        """Compute ROUGE-L score (longest common subsequence)"""
        lcs_length = self._lcs(gen_tokens, ref_tokens)

        if len(ref_tokens) == 0:
            return 0.0

        return lcs_length / len(ref_tokens)

    def _lcs(self, seq1: List[str], seq2: List[str]) -> int:
        """Compute longest common subsequence length"""
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])

        return dp[m][n]

    def _extract_meaningful_tokens(self, text: str) -> List[str]:
        """Extract meaningful tokens from text"""
        tokens = word_tokenize(text.lower())
        meaningful = [
            token for token in tokens
            if token.isalnum() and
            token not in self.stopwords and
            len(token) > 2
        ]
        return meaningful

    def _extract_diff_tokens(self, diff: str) -> List[str]:
        """Extract all tokens from diff"""
        diff_clean = re.sub(r'^[+-]', '', diff, flags=re.MULTILINE)
        diff_clean = re.sub(r'diff --git.*?\n', '', diff_clean)
        diff_clean = re.sub(r'index.*?\n', '', diff_clean)
        diff_clean = re.sub(r'@@.*?@@', '', diff_clean)

        tokens = word_tokenize(diff_clean.lower())
        return tokens

    def _compute_quality_score(self, results: Dict) -> float:
        """Compute overall quality score"""
        bleu = results['bleu'] / 100
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
