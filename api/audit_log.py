"""
Audit Logging System for SmartCommit
Tracks all API calls, hallucinations, and safety events
Phase 3 - AI Governance and Compliance
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import csv
from collections import defaultdict


class AuditLogger:
    """
    Comprehensive audit logging for AI-generated commit messages
    Tracks usage patterns, hallucination occurrences, and safety violations
    """

    def __init__(self, log_dir: str = None):
        """
        Initialize audit logger

        Args:
            log_dir: Directory for log files (default: ../logs)
        """
        if log_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            log_dir = os.path.normpath(os.path.join(current_dir, "..", "logs"))

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Initialize log files
        self.api_log_file = self.log_dir / "api_calls.jsonl"
        self.hallucination_log_file = self.log_dir / "hallucinations.jsonl"
        self.safety_log_file = self.log_dir / "safety_violations.jsonl"
        self.metrics_log_file = self.log_dir / "daily_metrics.csv"

        # In-memory statistics for current session
        self.session_stats = {
            "total_requests": 0,
            "total_hallucinations": 0,
            "total_safety_violations": 0,
            "severity_counts": defaultdict(int),
            "confidence_counts": defaultdict(int)
        }

        # Initialize metrics CSV if not exists
        self._initialize_metrics_csv()

    def _initialize_metrics_csv(self):
        """Initialize daily metrics CSV with headers if not exists"""
        if not self.metrics_log_file.exists():
            with open(self.metrics_log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'date',
                    'total_requests',
                    'hallucination_count',
                    'hallucination_rate',
                    'safety_violations',
                    'avg_quality_score',
                    'avg_confidence_level',
                    'critical_severity_count',
                    'high_severity_count',
                    'medium_severity_count',
                    'low_severity_count'
                ])

    def log_api_call(self,
                     endpoint: str,
                     request_data: Dict[str, Any],
                     response_data: Dict[str, Any],
                     ip_address: str = "unknown",
                     latency_ms: int = 0,
                     status_code: int = 200) -> None:
        """
        Log API call details

        Args:
            endpoint: API endpoint name (e.g., /generateCommit)
            request_data: Request payload (sanitized, no sensitive data)
            response_data: Response payload (sanitized)
            ip_address: Client IP address
            latency_ms: Request latency in milliseconds
            status_code: HTTP status code
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "ip_address": ip_address,
            "latency_ms": latency_ms,
            "status_code": status_code,
            "request": {
                "diff_size_kb": len(request_data.get('diff', '')).to_bytes(4, 'big').hex() if request_data.get('diff') else 0,
                "diff_lines": request_data.get('diff', '').count('\n') if request_data.get('diff') else 0,
                "has_reference": 'reference_message' in request_data
            },
            "response": {
                "message_length": len(response_data.get('message', '')),
                "hallucination_severity": response_data.get('hallucination_severity'),
                "confidence_level": response_data.get('confidence_level'),
                "quality_score": response_data.get('quality_metrics', {}).get('quality_score')
            }
        }

        self._write_log(self.api_log_file, log_entry)
        self.session_stats["total_requests"] += 1

        # Update severity and confidence counts
        if response_data.get('hallucination_severity'):
            self.session_stats["severity_counts"][response_data['hallucination_severity']] += 1
        if response_data.get('confidence_level'):
            self.session_stats["confidence_counts"][response_data['confidence_level']] += 1

    def log_hallucination(self,
                         message: str,
                         diff: str,
                         hallucination_details: Dict[str, Any],
                         severity: str,
                         ungrounded_tokens: List[str],
                         hallucination_rate: float) -> None:
        """
        Log hallucination occurrence

        Args:
            message: Generated commit message
            diff: Code diff
            hallucination_details: Detailed hallucination information
            severity: Hallucination severity level
            ungrounded_tokens: List of tokens not found in diff
            hallucination_rate: Percentage of ungrounded tokens
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "severity": severity,
            "hallucination_rate": hallucination_rate,
            "message": message[:200],  # Truncate for privacy
            "diff_snippet": diff[:200],  # Truncate for privacy
            "ungrounded_tokens": ungrounded_tokens[:20],  # First 20
            "ungrounded_count": len(ungrounded_tokens),
            "total_tokens": hallucination_details.get('total_tokens', 0),
            "hallucination_details": {
                "detected": hallucination_details.get('detected'),
                "rate": hallucination_details.get('rate')
            }
        }

        self._write_log(self.hallucination_log_file, log_entry)
        self.session_stats["total_hallucinations"] += 1

    def log_safety_violation(self,
                            violation_type: str,
                            details: str,
                            input_data: Dict[str, Any],
                            ip_address: str = "unknown") -> None:
        """
        Log safety violation (sensitive data, rate limit, etc.)

        Args:
            violation_type: Type of violation (e.g., "sensitive_data", "rate_limit", "size_exceeded")
            details: Detailed violation message
            input_data: Sanitized input that caused violation
            ip_address: Client IP address
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "violation_type": violation_type,
            "details": details,
            "ip_address": ip_address,
            "input_metadata": {
                "diff_size_kb": len(input_data.get('diff', '')) / 1024 if input_data.get('diff') else 0,
                "diff_lines": input_data.get('diff', '').count('\n') if input_data.get('diff') else 0
            }
        }

        self._write_log(self.safety_log_file, log_entry)
        self.session_stats["total_safety_violations"] += 1

    def log_daily_metrics(self,
                         total_requests: int,
                         hallucination_count: int,
                         safety_violations: int,
                         avg_quality_score: float,
                         severity_breakdown: Dict[str, int]) -> None:
        """
        Log daily aggregated metrics

        Args:
            total_requests: Total requests for the day
            hallucination_count: Number of hallucinations detected
            safety_violations: Number of safety violations
            avg_quality_score: Average quality score
            severity_breakdown: Count by severity level
        """
        date = datetime.now().strftime("%Y-%m-%d")
        hallucination_rate = (hallucination_count / total_requests * 100) if total_requests > 0 else 0.0

        with open(self.metrics_log_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                date,
                total_requests,
                hallucination_count,
                f"{hallucination_rate:.2f}",
                safety_violations,
                f"{avg_quality_score:.4f}",
                "N/A",  # avg_confidence_level (computed separately)
                severity_breakdown.get('CRITICAL', 0),
                severity_breakdown.get('HIGH', 0),
                severity_breakdown.get('MEDIUM', 0),
                severity_breakdown.get('LOW', 0)
            ])

    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get current session statistics

        Returns:
            Dictionary with session statistics
        """
        return {
            "total_requests": self.session_stats["total_requests"],
            "total_hallucinations": self.session_stats["total_hallucinations"],
            "hallucination_rate": (
                (self.session_stats["total_hallucinations"] / self.session_stats["total_requests"] * 100)
                if self.session_stats["total_requests"] > 0 else 0.0
            ),
            "total_safety_violations": self.session_stats["total_safety_violations"],
            "severity_counts": dict(self.session_stats["severity_counts"]),
            "confidence_counts": dict(self.session_stats["confidence_counts"])
        }

    def get_recent_logs(self, log_type: str = "api", limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve recent log entries

        Args:
            log_type: Type of log ("api", "hallucination", "safety")
            limit: Maximum number of entries to return

        Returns:
            List of log entries (most recent first)
        """
        log_file_map = {
            "api": self.api_log_file,
            "hallucination": self.hallucination_log_file,
            "safety": self.safety_log_file
        }

        log_file = log_file_map.get(log_type)
        if not log_file or not log_file.exists():
            return []

        logs = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue

        # Return most recent first
        return logs[-limit:][::-1]

    def generate_audit_report(self, days: int = 7) -> Dict[str, Any]:
        """
        Generate audit report for specified number of days

        Args:
            days: Number of days to include in report

        Returns:
            Comprehensive audit report
        """
        # Read daily metrics
        metrics = []
        if self.metrics_log_file.exists():
            with open(self.metrics_log_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                metrics = list(reader)

        # Get recent entries (last N days approximation)
        recent_api_calls = self.get_recent_logs("api", limit=1000)
        recent_hallucinations = self.get_recent_logs("hallucination", limit=500)
        recent_violations = self.get_recent_logs("safety", limit=100)

        return {
            "report_generated": datetime.now().isoformat(),
            "period_days": days,
            "summary": {
                "total_api_calls": len(recent_api_calls),
                "total_hallucinations": len(recent_hallucinations),
                "total_safety_violations": len(recent_violations),
                "hallucination_rate": (
                    (len(recent_hallucinations) / len(recent_api_calls) * 100)
                    if recent_api_calls else 0.0
                )
            },
            "daily_metrics": metrics[-days:] if metrics else [],
            "recent_high_severity": [
                h for h in recent_hallucinations
                if h.get('severity') in ['HIGH', 'CRITICAL']
            ][:10],
            "session_stats": self.get_session_stats()
        }

    def _write_log(self, log_file: Path, entry: Dict[str, Any]) -> None:
        """
        Write log entry to JSONL file

        Args:
            log_file: Path to log file
            entry: Log entry dictionary
        """
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')

    def export_logs_csv(self, output_file: str, log_type: str = "api") -> None:
        """
        Export logs to CSV format

        Args:
            output_file: Output CSV file path
            log_type: Type of log to export
        """
        logs = self.get_recent_logs(log_type, limit=10000)

        if not logs:
            return

        # Extract all possible keys
        all_keys = set()
        for log in logs:
            all_keys.update(self._flatten_dict(log).keys())

        # Write CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
            writer.writeheader()
            for log in logs:
                writer.writerow(self._flatten_dict(log))

    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """Flatten nested dictionary for CSV export"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                items.append((new_key, ', '.join(map(str, v[:10]))))  # First 10 items
            else:
                items.append((new_key, v))
        return dict(items)
