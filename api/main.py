"""
FastAPI Backend for SmartCommit
Main API endpoints for commit message generation and quality checking
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import logging
import yaml
import os

from model_service import ModelService
from evaluate_simple import CommitMessageEvaluator  # Use lightweight evaluator
from git_interface import GitInterface

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


# Request/Response Models
class GenerateRequest(BaseModel):
    diff: str = Field(..., description="Git diff string")
    temperature: Optional[float] = Field(None, description="Override default temperature")


class GenerateResponse(BaseModel):
    message: str
    model: str
    latency_ms: int
    timestamp: str


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
    Generate commit message from code diff

    Args:
        request: Contains diff and optional parameters

    Returns:
        Generated commit message with metadata
    """
    try:
        logger.info("Received generate request")

        # Validate diff
        if not request.diff or len(request.diff.strip()) == 0:
            raise HTTPException(status_code=400, detail="Diff cannot be empty")

        # Check diff size
        if len(request.diff) > 50000:  # ~50KB limit
            logger.warning("Large diff detected, truncating...")
            request.diff = request.diff[:50000] + "\n... (truncated)"

        # Generate message
        result = model_service.generate_commit_message(request.diff)

        if not result['success']:
            raise HTTPException(
                status_code=500,
                detail=f"Generation failed: {result.get('error', 'Unknown error')}"
            )

        logger.info(f"Generated message: {result['message'][:50]}...")

        return {
            "message": result['message'],
            "model": result['model'],
            "latency_ms": result['latency_ms'],
            "timestamp": result['timestamp']
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in generate_commit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/checkCommit", response_model=CheckQualityResponse)
async def check_commit(request: CheckQualityRequest):
    """
    Evaluate commit message quality

    Args:
        request: Contains diff, message, and optional reference

    Returns:
        Quality metrics and feedback
    """
    try:
        logger.info("Received quality check request")

        # Validate inputs
        if not request.diff or not request.commit_message:
            raise HTTPException(status_code=400, detail="Diff and message are required")

        # If no reference provided, generate one for comparison
        if not request.reference_message:
            # Use a simple heuristic or skip BLEU/ROUGE
            reference = request.commit_message  # Self-comparison
            logger.info("No reference provided, using self-comparison")
        else:
            reference = request.reference_message

        # Evaluate
        results = evaluator.evaluate_message(
            generated=request.commit_message,
            reference=reference,
            diff=request.diff
        )

        # Generate feedback
        feedback = _generate_feedback(results)

        return {
            "bleu": results['bleu'],
            "rouge": results['rouge'],
            "semantic_similarity": results['semantic_similarity'],
            "hallucination": results['hallucination'],
            "quality_score": results['quality_score'],
            "feedback": feedback
        }

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


def _generate_feedback(results: Dict) -> List[str]:
    """Generate human-readable feedback from evaluation results"""
    feedback = []

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

    # Hallucination feedback
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
