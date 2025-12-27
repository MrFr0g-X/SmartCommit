"""
Safety Guardrails for SmartCommit
Implements input validation, hallucination warnings, and safety checks
Phase 3 - AI Governance and Safety
"""

import re
from typing import Tuple, Dict, List, Any
import time
from datetime import datetime
from collections import defaultdict


class SafetyGuardrails:
    """
    Comprehensive safety guardrails for AI-generated commit messages
    Implements validation, hallucination detection, and safety warnings
    """

    def __init__(self):
        """Initialize safety guardrails with thresholds and rate limiters"""
        # Configuration thresholds
        self.MAX_DIFF_SIZE_KB = 100
        self.MAX_DIFF_LINES = 1000
        self.HALLUCINATION_LOW_THRESHOLD = 0.10
        self.HALLUCINATION_MEDIUM_THRESHOLD = 0.20
        self.HALLUCINATION_HIGH_THRESHOLD = 0.35

        # Sensitive patterns (regex)
        self.SENSITIVE_PATTERNS = [
            r'password\s*=\s*[\'"][^\'"]+[\'"]',
            r'api[_-]?key\s*=\s*[\'"][^\'"]+[\'"]',
            r'secret\s*=\s*[\'"][^\'"]+[\'"]',
            r'token\s*=\s*[\'"][^\'"]+[\'"]',
            r'\b\d{16}\b',  # Credit card-like numbers
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Emails
        ]

        # Rate limiting (requests per IP per minute)
        self.RATE_LIMIT_RPM = 60
        self.rate_limit_store = defaultdict(list)

    def validate_input(self, diff: str, ip_address: str = "unknown") -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate input diff for safety and correctness

        Args:
            diff: Git diff string
            ip_address: Client IP address for rate limiting

        Returns:
            Tuple of (is_valid, error_message, metadata)
        """
        metadata = {
            "validation_time": datetime.now().isoformat(),
            "ip_address": ip_address,
            "checks_performed": []
        }

        # Check 1: Rate limiting
        is_allowed, rate_msg = self._check_rate_limit(ip_address)
        metadata["checks_performed"].append("rate_limit")
        if not is_allowed:
            return False, rate_msg, metadata

        # Check 2: Empty diff
        if not diff or diff.strip() == "":
            metadata["checks_performed"].append("empty_check")
            return False, "Error: Diff is empty. Please provide a valid git diff.", metadata

        # Check 3: Size limit
        diff_size_kb = len(diff.encode('utf-8')) / 1024
        metadata["diff_size_kb"] = round(diff_size_kb, 2)
        metadata["checks_performed"].append("size_limit")

        if diff_size_kb > self.MAX_DIFF_SIZE_KB:
            return False, (
                f"Error: Diff size ({diff_size_kb:.2f} KB) exceeds maximum "
                f"allowed size ({self.MAX_DIFF_SIZE_KB} KB). "
                f"Please reduce the diff size or split into multiple commits."
            ), metadata

        # Check 4: Line count
        lines = diff.split('\n')
        line_count = len(lines)
        metadata["line_count"] = line_count
        metadata["checks_performed"].append("line_count")

        if line_count > self.MAX_DIFF_LINES:
            return False, (
                f"Error: Diff has {line_count} lines, exceeding maximum "
                f"of {self.MAX_DIFF_LINES} lines. Consider splitting into smaller commits."
            ), metadata

        # Check 5: Basic diff format validation
        has_diff_markers = any(
            line.startswith(('diff --git', '@@', '---', '+++', '+', '-'))
            for line in lines[:20]  # Check first 20 lines
        )
        metadata["checks_performed"].append("format_validation")

        if not has_diff_markers:
            return False, (
                "Warning: Input does not appear to be a valid git diff. "
                "Expected diff markers (@@, +++, ---, +, -) not found. "
                "Results may be inaccurate."
            ), metadata

        # Check 6: Sensitive data detection
        sensitive_found, sensitive_msg = self._check_sensitive_data(diff)
        metadata["checks_performed"].append("sensitive_data")
        metadata["sensitive_data_detected"] = sensitive_found

        if sensitive_found:
            return False, sensitive_msg, metadata

        # All checks passed
        metadata["checks_performed"].append("all_passed")
        return True, "Input validation passed", metadata

    def _check_rate_limit(self, ip_address: str) -> Tuple[bool, str]:
        """
        Check if IP address has exceeded rate limit

        Args:
            ip_address: Client IP address

        Returns:
            Tuple of (is_allowed, message)
        """
        current_time = time.time()

        # Clean old entries (older than 1 minute)
        self.rate_limit_store[ip_address] = [
            t for t in self.rate_limit_store[ip_address]
            if current_time - t < 60
        ]

        # Check limit
        request_count = len(self.rate_limit_store[ip_address])

        if request_count >= self.RATE_LIMIT_RPM:
            return False, (
                f"Error: Rate limit exceeded. Maximum {self.RATE_LIMIT_RPM} requests "
                f"per minute. Please wait before making more requests."
            )

        # Add current request
        self.rate_limit_store[ip_address].append(current_time)

        return True, f"Rate limit: {request_count + 1}/{self.RATE_LIMIT_RPM} requests this minute"

    def _check_sensitive_data(self, diff: str) -> Tuple[bool, str]:
        """
        Check if diff contains sensitive data patterns

        Args:
            diff: Git diff string

        Returns:
            Tuple of (found, message)
        """
        for pattern in self.SENSITIVE_PATTERNS:
            if re.search(pattern, diff, re.IGNORECASE):
                return True, (
                    "⚠️ Security Warning: Diff appears to contain sensitive data "
                    "(passwords, API keys, tokens, or personal information). "
                    "Please remove sensitive data before processing."
                )

        return False, "No sensitive data detected"

    def assess_hallucination_severity(self, hallucination_rate: float,
                                     hallucination_detected: bool) -> str:
        """
        Assess hallucination severity level

        Args:
            hallucination_rate: Percentage of ungrounded tokens (0-1 scale)
            hallucination_detected: Boolean flag if hallucination was detected

        Returns:
            Severity level: "NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL"
        """
        if not hallucination_detected:
            return "NONE"

        if hallucination_rate < self.HALLUCINATION_LOW_THRESHOLD:
            return "LOW"
        elif hallucination_rate < self.HALLUCINATION_MEDIUM_THRESHOLD:
            return "MEDIUM"
        elif hallucination_rate < self.HALLUCINATION_HIGH_THRESHOLD:
            return "HIGH"
        else:
            return "CRITICAL"

    def generate_safety_warnings(self, hallucination_severity: str,
                                 hallucination_details: Dict[str, Any],
                                 quality_score: float) -> List[str]:
        """
        Generate human-readable safety warnings

        Args:
            hallucination_severity: Severity level
            hallucination_details: Detailed hallucination info
            quality_score: Overall quality score (0-1)

        Returns:
            List of warning messages
        """
        warnings = []

        # Hallucination warnings
        if hallucination_severity == "CRITICAL":
            warnings.append(
                "🚨 CRITICAL: Very high hallucination rate (>35%). "
                "Generated message contains significant ungrounded information. "
                "DO NOT use without thorough manual review."
            )
        elif hallucination_severity == "HIGH":
            warnings.append(
                "⚠️ HIGH: High hallucination rate (20-35%). "
                "Generated message may contain invented function/variable names. "
                "Manual verification strongly recommended."
            )
        elif hallucination_severity == "MEDIUM":
            warnings.append(
                "⚠️ MEDIUM: Moderate hallucination detected (10-20%). "
                "Verify all mentioned functions and files exist in the diff."
            )
        elif hallucination_severity == "LOW":
            warnings.append(
                "ℹ️ LOW: Minor hallucination detected (<10%). "
                "Quick review recommended before committing."
            )

        # Quality score warnings
        if quality_score < 0.20:
            warnings.append(
                "⚠️ Very low quality score (<0.20). "
                "Generated message may not accurately reflect changes. "
                "Consider regenerating or writing manually."
            )
        elif quality_score < 0.35:
            warnings.append(
                "ℹ️ Low quality score (0.20-0.35). "
                "Review carefully and consider improvements."
            )

        # Ungrounded tokens warning
        if hallucination_details.get('ungrounded_tokens'):
            tokens = hallucination_details['ungrounded_tokens']
            if len(tokens) > 0:
                warnings.append(
                    f"⚠️ Ungrounded tokens detected: {', '.join(tokens[:5])}... "
                    f"({len(tokens)} total). Verify these appear in your diff."
                )

        # Human oversight requirement
        if hallucination_severity in ["HIGH", "CRITICAL"] or quality_score < 0.25:
            warnings.append(
                "⚠️ HUMAN OVERSIGHT REQUIRED: This message should not be used "
                "without thorough manual review by a developer familiar with the changes."
            )
        else:
            warnings.append(
                "ℹ️ Human review recommended: While quality is acceptable, "
                "always verify AI-generated commit messages before pushing."
            )

        return warnings

    def get_confidence_level(self, quality_score: float,
                            hallucination_severity: str) -> str:
        """
        Determine overall confidence level for generated message

        Args:
            quality_score: Overall quality score (0-1)
            hallucination_severity: Hallucination severity level

        Returns:
            Confidence level: "VERY_LOW", "LOW", "MEDIUM", "HIGH"
        """
        # Critical hallucination overrides everything
        if hallucination_severity == "CRITICAL":
            return "VERY_LOW"

        # High hallucination limits confidence
        if hallucination_severity == "HIGH":
            return "VERY_LOW" if quality_score < 0.30 else "LOW"

        # Medium hallucination
        if hallucination_severity == "MEDIUM":
            if quality_score >= 0.45:
                return "MEDIUM"
            elif quality_score >= 0.30:
                return "LOW"
            else:
                return "VERY_LOW"

        # Low or no hallucination - quality score determines
        if quality_score >= 0.50:
            return "HIGH"
        elif quality_score >= 0.35:
            return "MEDIUM"
        elif quality_score >= 0.20:
            return "LOW"
        else:
            return "VERY_LOW"

    def sanitize_output(self, commit_message: str) -> str:
        """
        Sanitize output message for safety

        Args:
            commit_message: Generated commit message

        Returns:
            Sanitized message
        """
        # Remove any potential code injection attempts
        sanitized = commit_message.strip()

        # Remove backticks that might interfere with shell
        sanitized = sanitized.replace('`', "'")

        # Remove excessive newlines
        sanitized = re.sub(r'\n{3,}', '\n\n', sanitized)

        # Limit total length
        MAX_MESSAGE_LENGTH = 500
        if len(sanitized) > MAX_MESSAGE_LENGTH:
            sanitized = sanitized[:MAX_MESSAGE_LENGTH] + "... (truncated)"

        return sanitized

    def get_usage_recommendations(self, confidence_level: str,
                                  hallucination_severity: str) -> List[str]:
        """
        Generate usage recommendations based on confidence and hallucination

        Args:
            confidence_level: Confidence level
            hallucination_severity: Hallucination severity

        Returns:
            List of recommendations
        """
        recommendations = []

        if confidence_level == "VERY_LOW":
            recommendations.append(
                "❌ NOT RECOMMENDED FOR USE: Consider writing commit message manually"
            )
            recommendations.append(
                "🔍 If you choose to use: Thoroughly verify every mentioned file, "
                "function, and change against your actual diff"
            )
        elif confidence_level == "LOW":
            recommendations.append(
                "⚠️ USE WITH CAUTION: Extensive manual review required"
            )
            recommendations.append(
                "✓ Verify: All file names, function names, and described changes match your diff"
            )
        elif confidence_level == "MEDIUM":
            recommendations.append(
                "ℹ️ ACCEPTABLE WITH REVIEW: Quick verification recommended"
            )
            recommendations.append(
                "✓ Check: Main changes are accurately described"
            )
        else:  # HIGH
            recommendations.append(
                "✅ GOOD QUALITY: Minor review recommended"
            )
            recommendations.append(
                "✓ Quick check: Verify message accurately summarizes your changes"
            )

        # Add hallucination-specific recommendations
        if hallucination_severity in ["HIGH", "CRITICAL"]:
            recommendations.append(
                "🔍 Hallucination detected: Pay special attention to function/variable names"
            )

        return recommendations
