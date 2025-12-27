"""
Comprehensive Phase 3 Testing Script
Tests all safety guardrails, audit logging, and API enhancements
"""

import sys
import os

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from api.safety import SafetyGuardrails
from api.audit_log import AuditLogger
import json

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_test_header(test_name):
    """Print formatted test header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}TEST: {test_name}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.RESET}\n")

def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.RESET} {message}")

def print_failure(message):
    """Print failure message"""
    print(f"{Colors.RED}[FAILURE]{Colors.RESET} {message}")

def print_info(message):
    """Print info message"""
    print(f"{Colors.YELLOW}[INFO]{Colors.RESET} {message}")

def test_safety_guardrails_input_validation():
    """Test 1: SafetyGuardrails input validation"""
    print_test_header("SafetyGuardrails - Input Validation")

    safety = SafetyGuardrails()
    tests_passed = 0
    tests_total = 6

    # Test 1.1: Empty diff
    print_info("Test 1.1: Empty diff validation")
    valid, msg, metadata = safety.validate_input("", "test_ip")
    if not valid and "empty" in msg.lower():
        print_success("Empty diff correctly rejected")
        tests_passed += 1
    else:
        print_failure(f"Empty diff not rejected: {msg}")

    # Test 1.2: Valid diff
    print_info("Test 1.2: Valid diff acceptance")
    valid_diff = """diff --git a/file.py b/file.py
@@ -1,1 +1,1 @@
-old line
+new line"""
    valid, msg, metadata = safety.validate_input(valid_diff, "test_ip_2")
    if valid:
        print_success(f"Valid diff accepted: {metadata.get('checks_performed', [])}")
        tests_passed += 1
    else:
        print_failure(f"Valid diff rejected: {msg}")

    # Test 1.3: Oversized diff (>100KB)
    print_info("Test 1.3: Oversized diff rejection")
    large_diff = "diff --git a/file.py b/file.py\n" + "x" * 110000  # >100KB
    valid, msg, metadata = safety.validate_input(large_diff, "test_ip_3")
    if not valid and "size" in msg.lower():
        print_success(f"Oversized diff rejected: {metadata.get('diff_size_kb')} KB")
        tests_passed += 1
    else:
        print_failure(f"Oversized diff not rejected: {msg}")

    # Test 1.4: Too many lines (>1000)
    print_info("Test 1.4: Too many lines rejection")
    many_lines_diff = "diff --git a/file.py b/file.py\n" + "\n".join([f"+line {i}" for i in range(1100)])
    valid, msg, metadata = safety.validate_input(many_lines_diff, "test_ip_4")
    if not valid and "lines" in msg.lower():
        print_success(f"Many-line diff rejected: {metadata.get('line_count')} lines")
        tests_passed += 1
    else:
        print_failure(f"Many-line diff not rejected: {msg}")

    # Test 1.5: Invalid diff format
    print_info("Test 1.5: Invalid diff format warning")
    invalid_format = "This is not a diff at all, just plain text"
    valid, msg, metadata = safety.validate_input(invalid_format, "test_ip_5")
    if not valid and "diff" in msg.lower():
        print_success("Invalid format detected")
        tests_passed += 1
    else:
        print_failure(f"Invalid format not detected: {msg}")

    # Test 1.6: Sensitive data detection
    print_info("Test 1.6: Sensitive data detection")
    sensitive_diff = """diff --git a/config.py b/config.py
@@ -1,0 +1,1 @@
+API_KEY = "sk-1234567890abcdef"
"""
    valid, msg, metadata = safety.validate_input(sensitive_diff, "test_ip_6")
    if not valid and "sensitive" in msg.lower():
        print_success("Sensitive data (API key) detected and rejected")
        tests_passed += 1
    else:
        print_failure(f"Sensitive data not detected: {msg}")

    print(f"\n{Colors.BOLD}Input Validation: {tests_passed}/{tests_total} tests passed{Colors.RESET}")
    return tests_passed == tests_total

def test_safety_guardrails_hallucination_severity():
    """Test 2: Hallucination severity assessment"""
    print_test_header("SafetyGuardrails - Hallucination Severity")

    safety = SafetyGuardrails()
    tests_passed = 0
    tests_total = 5

    # Test 2.1: No hallucination
    print_info("Test 2.1: No hallucination (rate=0.0)")
    severity = safety.assess_hallucination_severity(0.0, False)
    if severity == "NONE":
        print_success(f"Severity correctly assessed as {severity}")
        tests_passed += 1
    else:
        print_failure(f"Expected NONE, got {severity}")

    # Test 2.2: Low hallucination (5%)
    print_info("Test 2.2: Low hallucination (rate=0.05)")
    severity = safety.assess_hallucination_severity(0.05, True)
    if severity == "LOW":
        print_success(f"Severity correctly assessed as {severity}")
        tests_passed += 1
    else:
        print_failure(f"Expected LOW, got {severity}")

    # Test 2.3: Medium hallucination (15%)
    print_info("Test 2.3: Medium hallucination (rate=0.15)")
    severity = safety.assess_hallucination_severity(0.15, True)
    if severity == "MEDIUM":
        print_success(f"Severity correctly assessed as {severity}")
        tests_passed += 1
    else:
        print_failure(f"Expected MEDIUM, got {severity}")

    # Test 2.4: High hallucination (28%)
    print_info("Test 2.4: High hallucination (rate=0.28)")
    severity = safety.assess_hallucination_severity(0.28, True)
    if severity == "HIGH":
        print_success(f"Severity correctly assessed as {severity}")
        tests_passed += 1
    else:
        print_failure(f"Expected HIGH, got {severity}")

    # Test 2.5: Critical hallucination (40%)
    print_info("Test 2.5: Critical hallucination (rate=0.40)")
    severity = safety.assess_hallucination_severity(0.40, True)
    if severity == "CRITICAL":
        print_success(f"Severity correctly assessed as {severity}")
        tests_passed += 1
    else:
        print_failure(f"Expected CRITICAL, got {severity}")

    print(f"\n{Colors.BOLD}Hallucination Severity: {tests_passed}/{tests_total} tests passed{Colors.RESET}")
    return tests_passed == tests_total

def test_safety_guardrails_confidence_levels():
    """Test 3: Confidence level calculation"""
    print_test_header("SafetyGuardrails - Confidence Levels")

    safety = SafetyGuardrails()
    tests_passed = 0
    tests_total = 5

    # Test 3.1: High quality, no hallucination
    print_info("Test 3.1: High quality (0.55) + NONE hallucination")
    confidence = safety.get_confidence_level(0.55, "NONE")
    if confidence == "HIGH":
        print_success(f"Confidence: {confidence}")
        tests_passed += 1
    else:
        print_failure(f"Expected HIGH, got {confidence}")

    # Test 3.2: Medium quality, low hallucination
    print_info("Test 3.2: Medium quality (0.40) + LOW hallucination")
    confidence = safety.get_confidence_level(0.40, "LOW")
    if confidence == "MEDIUM":
        print_success(f"Confidence: {confidence}")
        tests_passed += 1
    else:
        print_failure(f"Expected MEDIUM, got {confidence}")

    # Test 3.3: Low quality, medium hallucination
    print_info("Test 3.3: Low quality (0.25) + MEDIUM hallucination")
    confidence = safety.get_confidence_level(0.25, "MEDIUM")
    if confidence == "VERY_LOW":  # Quality <0.30 + MEDIUM = VERY_LOW (correct behavior)
        print_success(f"Confidence: {confidence} (correct: low quality overrides)")
        tests_passed += 1
    else:
        print_failure(f"Expected VERY_LOW, got {confidence}")

    # Test 3.4: Any quality, critical hallucination
    print_info("Test 3.4: Any quality (0.60) + CRITICAL hallucination")
    confidence = safety.get_confidence_level(0.60, "CRITICAL")
    if confidence == "VERY_LOW":
        print_success(f"Confidence: {confidence} (critical overrides)")
        tests_passed += 1
    else:
        print_failure(f"Expected VERY_LOW, got {confidence}")

    # Test 3.5: Low quality, high hallucination
    print_info("Test 3.5: Low quality (0.20) + HIGH hallucination")
    confidence = safety.get_confidence_level(0.20, "HIGH")
    if confidence == "VERY_LOW":
        print_success(f"Confidence: {confidence}")
        tests_passed += 1
    else:
        print_failure(f"Expected VERY_LOW, got {confidence}")

    print(f"\n{Colors.BOLD}Confidence Levels: {tests_passed}/{tests_total} tests passed{Colors.RESET}")
    return tests_passed == tests_total

def test_safety_guardrails_warnings():
    """Test 4: Safety warning generation"""
    print_test_header("SafetyGuardrails - Safety Warnings")

    safety = SafetyGuardrails()
    tests_passed = 0
    tests_total = 3

    # Test 4.1: Critical severity warnings
    print_info("Test 4.1: Critical severity warnings")
    warnings = safety.generate_safety_warnings(
        "CRITICAL",
        {"ungrounded_tokens": ["fake_func", "invented_var"], "rate": 0.40},
        0.15
    )
    if any("CRITICAL" in w for w in warnings) and any("HUMAN OVERSIGHT" in w for w in warnings):
        print_success(f"Generated {len(warnings)} warnings including CRITICAL and oversight")
        tests_passed += 1
    else:
        print_failure(f"Missing expected warnings: {warnings}")

    # Test 4.2: Low severity with good quality
    print_info("Test 4.2: Low severity with good quality")
    warnings = safety.generate_safety_warnings(
        "LOW",
        {"ungrounded_tokens": ["minor"], "rate": 0.05},
        0.55
    )
    if any("LOW" in w for w in warnings) and not any("CRITICAL" in w for w in warnings):
        print_success(f"Generated appropriate warnings for LOW severity")
        tests_passed += 1
    else:
        print_failure(f"Inappropriate warnings: {warnings}")

    # Test 4.3: Very low quality score
    print_info("Test 4.3: Very low quality score (0.15)")
    warnings = safety.generate_safety_warnings(
        "NONE",
        {"ungrounded_tokens": [], "rate": 0.0},
        0.15
    )
    if any("quality" in w.lower() for w in warnings):
        print_success("Quality score warning generated")
        tests_passed += 1
    else:
        print_failure(f"Quality warning missing: {warnings}")

    print(f"\n{Colors.BOLD}Safety Warnings: {tests_passed}/{tests_total} tests passed{Colors.RESET}")
    return tests_passed == tests_total

def test_safety_guardrails_recommendations():
    """Test 5: Usage recommendations"""
    print_test_header("SafetyGuardrails - Usage Recommendations")

    safety = SafetyGuardrails()
    tests_passed = 0
    tests_total = 4

    # Test 5.1: VERY_LOW confidence
    print_info("Test 5.1: VERY_LOW confidence recommendations")
    recs = safety.get_usage_recommendations("VERY_LOW", "CRITICAL")
    if any("NOT RECOMMENDED" in r for r in recs):
        print_success(f"Recommendation: NOT RECOMMENDED FOR USE")
        tests_passed += 1
    else:
        print_failure(f"Missing strong warning: {recs}")

    # Test 5.2: LOW confidence
    print_info("Test 5.2: LOW confidence recommendations")
    recs = safety.get_usage_recommendations("LOW", "MEDIUM")
    if any("CAUTION" in r for r in recs):
        print_success("Recommendation: USE WITH CAUTION")
        tests_passed += 1
    else:
        print_failure(f"Missing caution: {recs}")

    # Test 5.3: MEDIUM confidence
    print_info("Test 5.3: MEDIUM confidence recommendations")
    recs = safety.get_usage_recommendations("MEDIUM", "LOW")
    if any("ACCEPTABLE" in r for r in recs):
        print_success("Recommendation: ACCEPTABLE WITH REVIEW")
        tests_passed += 1
    else:
        print_failure(f"Missing acceptable: {recs}")

    # Test 5.4: HIGH confidence
    print_info("Test 5.4: HIGH confidence recommendations")
    recs = safety.get_usage_recommendations("HIGH", "NONE")
    if any("GOOD QUALITY" in r for r in recs):
        print_success("Recommendation: GOOD QUALITY")
        tests_passed += 1
    else:
        print_failure(f"Missing good quality: {recs}")

    print(f"\n{Colors.BOLD}Usage Recommendations: {tests_passed}/{tests_total} tests passed{Colors.RESET}")
    return tests_passed == tests_total

def test_audit_logger():
    """Test 6: AuditLogger functionality"""
    print_test_header("AuditLogger - Logging & Retrieval")

    # Create test logs directory
    test_log_dir = os.path.join(current_dir, "test_logs")
    os.makedirs(test_log_dir, exist_ok=True)

    audit = AuditLogger(log_dir=test_log_dir)
    tests_passed = 0
    tests_total = 5

    # Test 6.1: Log API call
    print_info("Test 6.1: Log API call")
    audit.log_api_call(
        endpoint="/generateCommit",
        request_data={"diff": "test diff"},
        response_data={"message": "test message", "hallucination_severity": "LOW", "confidence_level": "MEDIUM", "quality_metrics": {"quality_score": 0.45}},
        ip_address="192.168.1.1",
        latency_ms=500,
        status_code=200
    )
    api_logs = audit.get_recent_logs("api", limit=1)
    if len(api_logs) > 0 and api_logs[0]["endpoint"] == "/generateCommit":
        print_success(f"API call logged: {api_logs[0]['timestamp']}")
        tests_passed += 1
    else:
        print_failure("API call not logged correctly")

    # Test 6.2: Log hallucination
    print_info("Test 6.2: Log hallucination")
    audit.log_hallucination(
        message="Test commit message with hallucinated content",
        diff="diff --git a/file.py",
        hallucination_details={"detected": True, "rate": 0.25},
        severity="HIGH",
        ungrounded_tokens=["fake_function", "invented_variable"],
        hallucination_rate=0.25
    )
    hall_logs = audit.get_recent_logs("hallucination", limit=1)
    if len(hall_logs) > 0 and hall_logs[0]["severity"] == "HIGH":
        print_success(f"Hallucination logged: severity={hall_logs[0]['severity']}, rate={hall_logs[0]['hallucination_rate']}")
        tests_passed += 1
    else:
        print_failure("Hallucination not logged correctly")

    # Test 6.3: Log safety violation
    print_info("Test 6.3: Log safety violation")
    audit.log_safety_violation(
        violation_type="sensitive_data",
        details="API key detected in diff",
        input_data={"diff": "API_KEY=sk-123"},
        ip_address="192.168.1.2"
    )
    safety_logs = audit.get_recent_logs("safety", limit=1)
    if len(safety_logs) > 0 and safety_logs[0]["violation_type"] == "sensitive_data":
        print_success(f"Safety violation logged: {safety_logs[0]['violation_type']}")
        tests_passed += 1
    else:
        print_failure("Safety violation not logged correctly")

    # Test 6.4: Session statistics
    print_info("Test 6.4: Session statistics")
    stats = audit.get_session_stats()
    if stats["total_requests"] >= 1 and stats["total_hallucinations"] >= 1 and stats["total_safety_violations"] >= 1:
        print_success(f"Session stats: {stats['total_requests']} requests, {stats['total_hallucinations']} hallucinations, {stats['total_safety_violations']} violations")
        tests_passed += 1
    else:
        print_failure(f"Session stats incorrect: {stats}")

    # Test 6.5: Audit report generation
    print_info("Test 6.5: Audit report generation")
    report = audit.generate_audit_report(days=7)
    if "summary" in report and report["summary"]["total_api_calls"] >= 1:
        print_success(f"Audit report generated: {report['summary']['total_api_calls']} total calls")
        tests_passed += 1
    else:
        print_failure(f"Audit report incomplete: {report}")

    # Cleanup test logs
    import shutil
    shutil.rmtree(test_log_dir)

    print(f"\n{Colors.BOLD}Audit Logger: {tests_passed}/{tests_total} tests passed{Colors.RESET}")
    return tests_passed == tests_total

def test_output_sanitization():
    """Test 7: Output sanitization"""
    print_test_header("SafetyGuardrails - Output Sanitization")

    safety = SafetyGuardrails()
    tests_passed = 0
    tests_total = 3

    # Test 7.1: Backtick removal
    print_info("Test 7.1: Backtick removal")
    sanitized = safety.sanitize_output("Fix bug in `calculate_total` function")
    if "`" not in sanitized and "'" in sanitized:
        print_success(f"Backticks removed: {sanitized}")
        tests_passed += 1
    else:
        print_failure(f"Backticks not removed: {sanitized}")

    # Test 7.2: Excessive newline removal
    print_info("Test 7.2: Excessive newline removal")
    sanitized = safety.sanitize_output("Line 1\n\n\n\n\nLine 2")
    newline_count = sanitized.count("\n\n")
    if newline_count == 1:
        print_success(f"Excessive newlines removed: {newline_count} double newlines remaining")
        tests_passed += 1
    else:
        print_failure(f"Newlines not cleaned: {newline_count} double newlines")

    # Test 7.3: Length truncation (>500 chars)
    print_info("Test 7.3: Length truncation")
    long_message = "x" * 600
    sanitized = safety.sanitize_output(long_message)
    if len(sanitized) <= 520 and "(truncated)" in sanitized:  # 500 + "... (truncated)"
        print_success(f"Long message truncated: {len(sanitized)} chars")
        tests_passed += 1
    else:
        print_failure(f"Message not truncated: {len(sanitized)} chars")

    print(f"\n{Colors.BOLD}Output Sanitization: {tests_passed}/{tests_total} tests passed{Colors.RESET}")
    return tests_passed == tests_total


def test_multi_agent_workflow():
    """
    Test Suite 8: Multi-Agent Workflow (BONUS)
    Tests the ethically governed multi-agent system with Generator, Validator, and Refiner agents
    """
    print_test_header("Multi-Agent Workflow (BONUS)")

    from api.multi_agent import (
        MultiAgentOrchestrator, GovernanceController,
        GeneratorAgent, ValidatorAgent, RefinerAgent,
        generate_with_multi_agent
    )

    tests_passed = 0
    tests_total = 8

    # Test 1: Multi-agent workflow completes successfully
    test_num = 1
    print_info("Test 8.1: Multi-agent workflow completion")
    try:
        diff = "@@ file.py @@\n-old_value = 1\n+new_value = 2"
        result = generate_with_multi_agent(diff)

        if (result and "message" in result and "governance" in result and
            "agent_trail" in result and len(result["agent_trail"]) >= 2):
            tests_passed += 1
            print_success("Multi-agent workflow completed")
        else:
            print_failure("Multi-agent workflow incomplete")
    except Exception as e:
        print_failure(f"Multi-agent workflow failed: {e}")

    # Test 2: Governance controller validation
    test_num += 1
    print_info("Test 8.2: Governance controller input validation")
    try:
        governance = GovernanceController()
        input_data = {"diff": "@@ file.py @@\n-old\n+new"}

        safety_check = governance.validate_agent_input("GeneratorAgent", input_data)

        if safety_check and safety_check.get("passed") == True:
            tests_passed += 1
            print_success("Governance validation working")
        else:
            print_failure("Governance validation failed")
    except Exception as e:
        print_failure(f"Governance validation error: {e}")

    # Test 3: Generator Agent execution
    test_num += 1
    print_info("Test 8.3: Generator Agent produces message")
    try:
        governance = GovernanceController()
        generator = GeneratorAgent(governance)

        diff = "@@ utils.py @@\n-def old_func():\n+def new_func():"
        gen_result = generator.execute(diff)

        if (gen_result and "message" in gen_result and "reasoning" in gen_result and
            len(gen_result["message"]) > 0):
            tests_passed += 1
            print_success(f"Generator produced: '{gen_result['message'][:50]}...'")
        else:
            print_failure("Generator failed to produce message")
    except Exception as e:
        print_failure(f"Generator Agent error: {e}")

    # Test 4: Validator Agent execution
    test_num += 1
    print_info("Test 8.4: Validator Agent assesses quality")
    try:
        governance = GovernanceController()
        validator = ValidatorAgent(governance)

        message = "Update function name"
        diff = "@@ utils.py @@\n-def old_func():\n+def new_func():"

        val_result = validator.execute(message, diff)

        if (val_result and "is_valid" in val_result and "feedback" in val_result and
            "metrics" in val_result):
            tests_passed += 1
            print_success(f"Validator assessed: valid={val_result['is_valid']}")
        else:
            print_failure("Validator failed to assess")
    except Exception as e:
        print_failure(f"Validator Agent error: {e}")

    # Test 5: Refiner Agent execution
    test_num += 1
    print_info("Test 8.5: Refiner Agent improves message")
    try:
        governance = GovernanceController()
        refiner = RefinerAgent(governance)

        message = "fix"  # Too short
        feedback = {
            "is_valid": False,
            "issues": ["Message too short (< 10 chars)"],
            "suggestions": ["Expand message to include what was changed"]
        }
        diff = "@@ file.py @@\n-old\n+new"

        ref_result = refiner.execute(message, feedback, diff)

        if (ref_result and "refined_message" in ref_result and
            len(ref_result["refined_message"]) > len(message)):
            tests_passed += 1
            print_success(f"Refiner improved: '{message}' -> '{ref_result['refined_message']}'")
        else:
            print_failure("Refiner failed to improve message")
    except Exception as e:
        print_failure(f"Refiner Agent error: {e}")

    # Test 6: Governance transparency report
    test_num += 1
    print_info("Test 8.6: Governance transparency reporting")
    try:
        diff = "@@ test.py @@\n-print('old')\n+print('new')"
        result = generate_with_multi_agent(diff)

        transparency_report = result["governance"].get("transparency_report", {})

        if (transparency_report and "decision_chain" in transparency_report and
            "governance_compliance" in transparency_report):
            tests_passed += 1
            print_success("Transparency report generated")
        else:
            print_failure("Transparency report incomplete")
    except Exception as e:
        print_failure(f"Transparency reporting error: {e}")

    # Test 7: Agent accountability trail
    test_num += 1
    print_info("Test 8.7: Agent accountability trail logging")
    try:
        diff = "@@ code.py @@\n-value = 1\n+value = 2"
        result = generate_with_multi_agent(diff)

        agent_trail = result.get("agent_trail", [])

        if len(agent_trail) >= 2:  # At least Generator + Validator
            has_reasoning = all("reasoning" in decision for decision in agent_trail)
            has_execution_time = all("execution_time_ms" in decision for decision in agent_trail)

            if has_reasoning and has_execution_time:
                tests_passed += 1
                print_success(f"Accountability trail: {len(agent_trail)} agent decisions logged")
            else:
                print_failure("Accountability trail incomplete")
        else:
            print_failure("Accountability trail too short")
    except Exception as e:
        print_failure(f"Accountability trail error: {e}")

    # Test 8: Explainability - Each agent provides reasoning
    test_num += 1
    print_info("Test 8.8: Agent explainability (reasoning provided)")
    try:
        diff = "@@ main.py @@\n-# TODO: implement\n+def process():\n+    return True"
        result = generate_with_multi_agent(diff)

        agent_trail = result.get("agent_trail", [])

        if agent_trail:
            all_have_reasoning = all(
                decision.get("reasoning") and len(decision["reasoning"]) > 10
                for decision in agent_trail
            )

            if all_have_reasoning:
                tests_passed += 1
                print_success("All agents provided reasoning")
            else:
                print_failure("Some agents missing reasoning")
        else:
            print_failure("No agent trail found")
    except Exception as e:
        print_failure(f"Explainability check error: {e}")

    print(f"\n{Colors.BOLD}Multi-Agent Workflow: {tests_passed}/{tests_total} tests passed{Colors.RESET}")
    return tests_passed == tests_total


def main():
    """Run all Phase 3 tests including BONUS Multi-Agent Workflow"""
    print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}   SMARTCOMMIT PHASE 3 + BONUS COMPREHENSIVE TEST SUITE{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")

    results = []

    # Run all tests
    results.append(("Input Validation", test_safety_guardrails_input_validation()))
    results.append(("Hallucination Severity", test_safety_guardrails_hallucination_severity()))
    results.append(("Confidence Levels", test_safety_guardrails_confidence_levels()))
    results.append(("Safety Warnings", test_safety_guardrails_warnings()))
    results.append(("Usage Recommendations", test_safety_guardrails_recommendations()))
    results.append(("Audit Logger", test_audit_logger()))
    results.append(("Output Sanitization", test_output_sanitization()))
    results.append(("Multi-Agent Workflow (BONUS)", test_multi_agent_workflow()))

    # Print summary
    print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}TEST SUMMARY{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for test_name, passed in results:
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if passed else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"{status} - {test_name}")

    print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
    if passed_count == total_count:
        print(f"{Colors.GREEN}{Colors.BOLD}ALL TESTS PASSED ({passed_count}/{total_count}){Colors.RESET}")
        print(f"{Colors.GREEN}{Colors.BOLD}Phase 3 implementation is PRODUCTION READY{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}TESTS PASSED: {passed_count}/{total_count}{Colors.RESET}")
        print(f"{Colors.YELLOW}{Colors.BOLD}Phase 3 implementation needs fixes{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")

    return passed_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
