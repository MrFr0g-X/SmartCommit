"""
FastAPI Backend for SmartCommit
Main API endpoints for commit message generation and quality checking
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
import logging
import yaml
import os

from .model_service import ModelService
from .evaluate_simple import CommitMessageEvaluator  # Use lightweight evaluator
from .git_interface import GitInterface
from .safety import SafetyGuardrails
from .audit_log import AuditLogger

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SmartCommit API",
    description="AI-based commit message generator and quality checker",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load configuration (from parent directory)
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.normpath(os.path.join(current_dir, "..", "config.yaml"))
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Initialize services (pass config_path to ModelService)
model_service = ModelService(config_path=config_path)
evaluator = CommitMessageEvaluator()
git_interface = GitInterface()
safety_guardrails = SafetyGuardrails()
audit_logger = AuditLogger()  # Phase 3: Audit logging


# Request/Response Models
class GenerateRequest(BaseModel):
    diff: str = Field(..., description="Git diff string")
    temperature: Optional[float] = Field(None, description="Override default temperature")


class GenerateResponse(BaseModel):
    message: str
    model: str
    latency_ms: int
    timestamp: str
    # Safety & Quality Information (Phase 3)
    hallucination_severity: str  # NONE, LOW, MEDIUM, HIGH, CRITICAL
    confidence_level: str  # VERY_LOW, LOW, MEDIUM, HIGH
    safety_warnings: List[str]
    usage_recommendations: List[str]
    quality_metrics: Optional[Dict] = None  # BLEU, ROUGE, semantic, hallucination details


class CheckQualityRequest(BaseModel):
    diff: str = Field(..., description="Git diff string")
    commit_message: str = Field(..., description="Commit message to evaluate")
    reference_message: Optional[str] = Field(None, description="Reference message for comparison")


class CheckQualityResponse(BaseModel):
    bleu: float
    rouge: Dict
    semantic_similarity: float
    hallucination: Dict
    quality_score: float
    feedback: List[str]
    # Safety & Governance (Phase 3)
    hallucination_severity: str  # NONE, LOW, MEDIUM, HIGH, CRITICAL
    confidence_level: str  # VERY_LOW, LOW, MEDIUM, HIGH
    safety_warnings: List[str]
    usage_recommendations: List[str]


class HealthResponse(BaseModel):
    status: str
    model: str
    version: str


# API Endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model": model_service.model_name,
        "version": "0.1.0"
    }


@app.post("/generateCommit", response_model=GenerateResponse)
async def generate_commit(request: GenerateRequest):
    """
    Generate commit message from code diff with comprehensive safety checks

    Args:
        request: Contains diff and optional parameters

    Returns:
        Generated commit message with safety & quality metadata (Phase 3 enhanced)
    """
    try:
        logger.info("Received generate request")

        # Phase 3: Input validation using SafetyGuardrails
        is_valid, validation_msg, validation_metadata = safety_guardrails.validate_input(
            diff=request.diff,
            ip_address="unknown"  # In production, extract from request headers
        )

        if not is_valid:
            logger.warning(f"Input validation failed: {validation_msg}")
            # Phase 3: Log safety violation
            audit_logger.log_safety_violation(
                violation_type="input_validation_failed",
                details=validation_msg,
                input_data={"diff": request.diff},
                ip_address="unknown"
            )
            raise HTTPException(status_code=400, detail=validation_msg)

        logger.info(f"Input validation passed: {validation_metadata.get('checks_performed', [])}")

        # Generate message
        result = model_service.generate_commit_message(request.diff)

        if not result['success']:
            raise HTTPException(
                status_code=500,
                detail=f"Generation failed: {result.get('error', 'Unknown error')}"
            )

        generated_message = result['message']
        logger.info(f"Generated message: {generated_message[:50]}...")

        # Phase 3: Automatic quality evaluation
        eval_results = evaluator.evaluate_message(
            generated=generated_message,
            reference=generated_message,  # Self-comparison for hallucination detection
            diff=request.diff
        )

        # Phase 3: Assess hallucination severity
        hallucination_rate = eval_results['hallucination'].get('rate', 0.0)
        hallucination_detected = eval_results['hallucination']['detected']

        hallucination_severity = safety_guardrails.assess_hallucination_severity(
            hallucination_rate=hallucination_rate,
            hallucination_detected=hallucination_detected
        )

        # Phase 3: Generate safety warnings
        safety_warnings = safety_guardrails.generate_safety_warnings(
            hallucination_severity=hallucination_severity,
            hallucination_details=eval_results['hallucination'],
            quality_score=eval_results['quality_score']
        )

        # Phase 3: Calculate confidence level
        confidence_level = safety_guardrails.get_confidence_level(
            quality_score=eval_results['quality_score'],
            hallucination_severity=hallucination_severity
        )

        # Phase 3: Get usage recommendations
        usage_recommendations = safety_guardrails.get_usage_recommendations(
            confidence_level=confidence_level,
            hallucination_severity=hallucination_severity
        )

        # Phase 3: Sanitize output
        sanitized_message = safety_guardrails.sanitize_output(generated_message)

        logger.info(f"Safety assessment - Severity: {hallucination_severity}, Confidence: {confidence_level}")

        # Phase 3: Log hallucination if detected
        if hallucination_detected:
            audit_logger.log_hallucination(
                message=sanitized_message,
                diff=request.diff,
                hallucination_details=eval_results['hallucination'],
                severity=hallucination_severity,
                ungrounded_tokens=eval_results['hallucination'].get('ungrounded_tokens', []),
                hallucination_rate=hallucination_rate
            )

        # Prepare response
        response_data = {
            "message": sanitized_message,
            "model": result['model'],
            "latency_ms": result['latency_ms'],
            "timestamp": result['timestamp'],
            # Phase 3: Safety & Quality Information
            "hallucination_severity": hallucination_severity,
            "confidence_level": confidence_level,
            "safety_warnings": safety_warnings,
            "usage_recommendations": usage_recommendations,
            "quality_metrics": {
                "bleu": eval_results.get('bleu'),
                "rouge_l": eval_results['rouge'].get('rouge_l')
                    if 'rouge_l' in eval_results['rouge'] else eval_results['rouge'].get('rougeL', 0.0),
                "semantic_similarity": eval_results.get('semantic_similarity'),
                "quality_score": eval_results.get('quality_score'),
                "hallucination_rate": hallucination_rate,
                "ungrounded_tokens": eval_results['hallucination'].get('ungrounded_tokens', [])[:10]  # First 10
            }
        }

        # Phase 3: Log API call
        audit_logger.log_api_call(
            endpoint="/generateCommit",
            request_data={"diff": request.diff},
            response_data=response_data,
            ip_address="unknown",
            latency_ms=result['latency_ms'],
            status_code=200
        )

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in generate_commit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/checkCommit", response_model=CheckQualityResponse)
async def check_commit(request: CheckQualityRequest):
    """
    Evaluate commit message quality with comprehensive safety assessment

    Args:
        request: Contains diff, message, and optional reference

    Returns:
        Quality metrics, feedback, and safety assessment (Phase 3 enhanced)
    """
    try:
        logger.info("Received quality check request")

        # Phase 3: Input validation using SafetyGuardrails
        is_valid, validation_msg, validation_metadata = safety_guardrails.validate_input(
            diff=request.diff,
            ip_address="unknown"
        )

        if not is_valid:
            logger.warning(f"Input validation failed: {validation_msg}")
            # Phase 3: Log safety violation
            audit_logger.log_safety_violation(
                violation_type="input_validation_failed",
                details=validation_msg,
                input_data={"diff": request.diff},
                ip_address="unknown"
            )
            raise HTTPException(status_code=400, detail=validation_msg)

        # Validate commit message
        if not request.commit_message or len(request.commit_message.strip()) == 0:
            raise HTTPException(status_code=400, detail="Commit message cannot be empty")

        # If no reference provided, use self-comparison for hallucination detection
        if not request.reference_message:
            reference = request.commit_message  # Self-comparison
            logger.info("No reference provided, using self-comparison for hallucination detection")
        else:
            reference = request.reference_message

        # Evaluate
        results = evaluator.evaluate_message(
            generated=request.commit_message,
            reference=reference,
            diff=request.diff
        )

        # Phase 3: Assess hallucination severity
        hallucination_rate = results['hallucination'].get('rate', 0.0)
        hallucination_detected = results['hallucination']['detected']

        hallucination_severity = safety_guardrails.assess_hallucination_severity(
            hallucination_rate=hallucination_rate,
            hallucination_detected=hallucination_detected
        )

        # Phase 3: Generate safety warnings
        safety_warnings = safety_guardrails.generate_safety_warnings(
            hallucination_severity=hallucination_severity,
            hallucination_details=results['hallucination'],
            quality_score=results['quality_score']
        )

        # Phase 3: Calculate confidence level
        confidence_level = safety_guardrails.get_confidence_level(
            quality_score=results['quality_score'],
            hallucination_severity=hallucination_severity
        )

        # Phase 3: Get usage recommendations
        usage_recommendations = safety_guardrails.get_usage_recommendations(
            confidence_level=confidence_level,
            hallucination_severity=hallucination_severity
        )

        # Generate feedback (legacy system + new safety warnings)
        feedback = _generate_feedback(results, safety_warnings)

        logger.info(f"Quality check - Severity: {hallucination_severity}, Confidence: {confidence_level}")

        # Phase 3: Log hallucination if detected
        if hallucination_detected:
            audit_logger.log_hallucination(
                message=request.commit_message,
                diff=request.diff,
                hallucination_details=results['hallucination'],
                severity=hallucination_severity,
                ungrounded_tokens=results['hallucination'].get('ungrounded_tokens', []),
                hallucination_rate=hallucination_rate
            )

        # Prepare response
        response_data = {
            "bleu": results['bleu'],
            "rouge": results['rouge'],
            "semantic_similarity": results['semantic_similarity'],
            "hallucination": results['hallucination'],
            "quality_score": results['quality_score'],
            "feedback": feedback,
            # Phase 3: Safety & Governance
            "hallucination_severity": hallucination_severity,
            "confidence_level": confidence_level,
            "safety_warnings": safety_warnings,
            "usage_recommendations": usage_recommendations
        }

        # Phase 3: Log API call
        audit_logger.log_api_call(
            endpoint="/checkCommit",
            request_data={"diff": request.diff, "reference_message": request.reference_message},
            response_data=response_data,
            ip_address="unknown",
            latency_ms=0,  # Not tracked for check endpoint
            status_code=200
        )

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in check_commit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/listChanges")
async def list_changes():
    """
    List changed files in current repository

    Returns:
        List of changed files
    """
    try:
        files = git_interface.get_changed_files()
        return {
            "changed_files": files,
            "count": len(files)
        }
    except Exception as e:
        logger.error(f"Error listing changes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history/{count}")
async def get_history(count: int = 10):
    """
    Get commit history

    Args:
        count: Number of commits to retrieve (max 100)

    Returns:
        List of commits with messages and diffs
    """
    try:
        if count > 100:
            count = 100

        commits = git_interface.get_commit_history(max_count=count)
        return {
            "commits": commits,
            "count": len(commits)
        }
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/audit/stats")
async def get_audit_stats():
    """
    Get audit statistics (Phase 3 - Governance & Transparency)

    Returns:
        Current session statistics and audit metrics
    """
    try:
        stats = audit_logger.get_session_stats()
        return {
            "status": "success",
            "session_stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting audit stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/audit/report")
async def get_audit_report(days: int = 7):
    """
    Generate comprehensive audit report (Phase 3 - Governance)

    Args:
        days: Number of days to include in report (default: 7)

    Returns:
        Detailed audit report with hallucination trends and safety metrics
    """
    try:
        if days > 30:
            days = 30  # Limit to 30 days

        report = audit_logger.generate_audit_report(days=days)
        return {
            "status": "success",
            "report": report
        }
    except Exception as e:
        logger.error(f"Error generating audit report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _generate_feedback(results: Dict, safety_warnings: List[str] = None) -> List[str]:
    """
    Generate human-readable feedback from evaluation results
    Phase 3: Integrates safety warnings from SafetyGuardrails
    """
    feedback = []

    # Phase 3: Prioritize safety warnings at the top
    if safety_warnings:
        feedback.extend(safety_warnings)
        feedback.append("")  # Separator

    # BLEU feedback
    if results['bleu'] > 15:
        feedback.append("✓ Good lexical similarity with reference")
    else:
        feedback.append("⚠ Low BLEU score - message differs significantly from reference")

    # Semantic similarity feedback
    if results['semantic_similarity'] > 0.7:
        feedback.append("✓ Semantically similar to reference")
    elif results['semantic_similarity'] > 0.5:
        feedback.append("⚠ Moderate semantic similarity")
    else:
        feedback.append("✗ Low semantic similarity")

    # Hallucination feedback (legacy - now enhanced by SafetyGuardrails)
    if results['hallucination']['detected']:
        tokens = results['hallucination']['ungrounded_tokens'][:5]  # Show first 5
        feedback.append(f"⚠ Potential hallucination detected: {', '.join(tokens)}")
    else:
        feedback.append("✓ No hallucinations detected")

    # Quality score feedback
    if results['quality_score'] > 0.7:
        feedback.append("✓ High overall quality")
    elif results['quality_score'] > 0.5:
        feedback.append("⚠ Acceptable quality")
    else:
        feedback.append("✗ Low quality - consider regenerating")

    return feedback


# Run server
if __name__ == "__main__":
    import uvicorn

    host = config['api']['host']
    port = config['api']['port']
    reload = config['api']['reload']

    logger.info(f"Starting SmartCommit API on {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=reload)
