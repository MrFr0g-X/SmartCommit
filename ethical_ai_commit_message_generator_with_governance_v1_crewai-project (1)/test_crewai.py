#!/usr/bin/env python
"""Test script for CrewAI multi-agent workflow"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Verify API key is loaded
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file!")

print(f"✓ API Key loaded: {api_key[:10]}...")

# Now import and run the crew
from ethical_ai_commit_message_generator_with_governance.crew import EthicalAiCommitMessageGeneratorWithGovernanceCrew

def main():
    """Run the crew with test inputs"""
    inputs = {
        'max_iterations': '3',
        'quality_threshold': '0.3',
        'diff': '''@@ api/utils.py @@
-def calculate(x):
-    return x
+def calculate_total(x, y):
+    return x + y
'''
    }

    print("\n🚀 Starting CrewAI Multi-Agent Workflow...")
    print(f"Input Diff:\n{inputs['diff']}\n")

    crew = EthicalAiCommitMessageGeneratorWithGovernanceCrew().crew()
    result = crew.kickoff(inputs=inputs)

    print("\n✅ Workflow Complete!")
    print(f"Result: {result}")

    return result

if __name__ == "__main__":
    main()
