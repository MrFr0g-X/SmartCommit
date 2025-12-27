#!/usr/bin/env python
import sys
from ethical_ai_commit_message_generator_with_governance.crew import EthicalAiCommitMessageGeneratorWithGovernanceCrew

# This main file is intended to be a way for your to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
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
    EthicalAiCommitMessageGeneratorWithGovernanceCrew().crew().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'max_iterations': 'sample_value',
        'quality_threshold': 'sample_value',
        'diff': 'sample_value'
    }
    try:
        EthicalAiCommitMessageGeneratorWithGovernanceCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        EthicalAiCommitMessageGeneratorWithGovernanceCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'max_iterations': 'sample_value',
        'quality_threshold': 'sample_value',
        'diff': 'sample_value'
    }
    try:
        EthicalAiCommitMessageGeneratorWithGovernanceCrew().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: main.py <command> [<args>]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "run":
        run()
    elif command == "train":
        train()
    elif command == "replay":
        replay()
    elif command == "test":
        test()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
