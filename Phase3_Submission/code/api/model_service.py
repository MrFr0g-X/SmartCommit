"""
Model Service - Handles AI model integration for commit message generation
Uses Google Gemini API with configurable parameters
"""

import os
import logging
from datetime import datetime
from typing import Dict, Optional
import google.generativeai as genai
from dotenv import load_dotenv
import yaml

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelService:
    """Service for generating commit messages using AI models"""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize model service with configuration"""
        # Find project root (where config.yaml is)
        if not os.path.isabs(config_path):
            # Get absolute path relative to this file's location (api/)
            current = os.path.dirname(os.path.abspath(__file__))
            # Resolve config path from api/ directory
            config_path = os.path.normpath(os.path.join(current, config_path))

        self.project_root = os.path.dirname(os.path.abspath(config_path))

        # Load config
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Get API key
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        # Configure Gemini
        genai.configure(api_key=api_key)

        # Load model config
        model_config = self.config['model']
        self.model_name = model_config['primary']
        self.temperature = model_config['temperature']
        self.top_p = model_config['top_p']
        self.top_k = model_config['top_k']
        self.max_tokens = model_config['max_output_tokens']

        # Initialize model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=genai.GenerationConfig(
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
                max_output_tokens=self.max_tokens,
                candidate_count=1
            )
        )

        # Load prompt template
        prompt_path = self.config['prompts']['generation']
        if not os.path.isabs(prompt_path):
            prompt_path = os.path.join(self.project_root, prompt_path)
        with open(prompt_path, 'r') as f:
            self.prompt_template = f.read()

        # Setup logging
        self.log_enabled = self.config['logging']['enabled']
        self.log_dir = self.config['logging']['log_dir']
        if not os.path.isabs(self.log_dir):
            self.log_dir = os.path.join(self.project_root, self.log_dir)
        os.makedirs(self.log_dir, exist_ok=True)

        logger.info(f"ModelService initialized with {self.model_name}")

    def generate_commit_message(self, diff: str) -> Dict:
        """
        Generate commit message from code diff

        Args:
            diff: Git diff string

        Returns:
            Dictionary with message, metadata, and logging info
        """
        try:
            # Format prompt
            prompt = self.prompt_template.format(diff=diff)

            # Call API
            start_time = datetime.now()
            response = self.model.generate_content(prompt)
            end_time = datetime.now()

            # Extract message
            message = response.text.strip()

            # Calculate token usage (approximate)
            input_tokens = len(prompt.split())  # rough estimate
            output_tokens = len(message.split())

            # Prepare result
            result = {
                'message': message,
                'model': self.model_name,
                'temperature': self.temperature,
                'latency_ms': int((end_time - start_time).total_seconds() * 1000),
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'timestamp': start_time.isoformat(),
                'success': True
            }

            # Log if enabled
            if self.log_enabled:
                self._log_generation(prompt, message, result)

            return result

        except Exception as e:
            logger.error(f"Error generating commit message: {e}")
            return {
                'message': None,
                'error': str(e),
                'success': False,
                'timestamp': datetime.now().isoformat()
            }

    def _log_generation(self, prompt: str, response: str, metadata: Dict):
        """Log prompt and response to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(self.log_dir, f"generation_{timestamp}.log")

        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write(f"TIMESTAMP: {metadata['timestamp']}\n")
            f.write(f"MODEL: {metadata['model']}\n")
            f.write(f"TEMPERATURE: {metadata['temperature']}\n")
            f.write(f"LATENCY: {metadata['latency_ms']}ms\n")
            f.write("="*80 + "\n\n")
            f.write("PROMPT:\n")
            f.write(prompt)
            f.write("\n\n" + "="*80 + "\n\n")
            f.write("RESPONSE:\n")
            f.write(response)
            f.write("\n\n" + "="*80 + "\n")

    def batch_generate(self, diffs: list) -> list:
        """Generate commit messages for multiple diffs"""
        results = []
        for i, diff in enumerate(diffs):
            logger.info(f"Processing diff {i+1}/{len(diffs)}")
            result = self.generate_commit_message(diff)
            results.append(result)
        return results


# For testing
if __name__ == "__main__":
    # Test with sample diff
    sample_diff = """diff --git a/src/utils.py b/src/utils.py
index 1234567..abcdefg 100644
--- a/src/utils.py
+++ b/src/utils.py
@@ -10,7 +10,7 @@ def calculate_total(items):
     total = 0
     for item in items:
-        total += item.price
+        total += item.price * item.quantity
     return total
"""

    service = ModelService()
    result = service.generate_commit_message(sample_diff)
    print(f"Generated message: {result['message']}")
    print(f"Latency: {result['latency_ms']}ms")
