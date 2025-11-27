# SmartCommit - AI Coding Agent Instructions

## Project Overview
SmartCommit is an academic research prototype (SW403 course, Phase 2) that generates commit messages using Google Gemini 2.0 Flash and evaluates quality through BLEU, ROUGE, semantic similarity, and hallucination detection. The system follows Liu et al. 2025's methodology for detecting fabricated information in AI-generated messages.

**Tech Stack**: FastAPI backend, Streamlit UI with iOS 26 Liquid Glass design, Google Gemini API, sentence transformers, NLTK

## Critical Architecture Patterns

### Path Resolution Strategy
All modules use **dynamic absolute path resolution** to work from any directory:
```python
# Standard pattern in api/, experiments/, ui/
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)
config_path = os.path.normpath(os.path.join(current_dir, "../config.yaml"))
```
The `config.yaml` at project root drives all paths. Services resolve relative paths (e.g., `prompts/commit_generation_improved.txt`) to absolute using `self.project_root`. **Never use relative imports without this pattern.**

### Service Initialization Chain
1. `config.yaml` loads first (defines model params, prompt paths, thresholds)
2. `ModelService(config_path)` initializes Gemini with config settings and loads prompt template
3. `CommitMessageEvaluator()` is stateless but needs NLTK data (auto-downloads stopwords/punkt)
4. All services must handle `project_root` resolution for Windows paths (`os.path.normpath`)

### Two Evaluation Modules Pattern
- `api/evaluate.py`: Full evaluator with BERTScore (requires transformers, heavy dependencies)
- `api/evaluate_simple.py`: Lightweight version without TensorFlow/Keras (BLEU, ROUGE, hallucination only)
- **Experiments use `evaluate_simple`** to avoid Keras 3.x compatibility issues with TensorFlow
- Set `TF_ENABLE_ONEDNN_OPTS=0` and `TRANSFORMERS_NO_TF=1` when running experiments (see `run_experiment_quick.bat`)

## Developer Workflows

### Running Experiments (Primary Workflow)
```powershell
# From project root
.\run_experiment_quick.bat

# Or manually from experiments/
cd experiments
python run_experiments.py  # Processes data/commitbench_samples.csv
python analyze_results.py  # Generates tables/plots in results/
```
**Key**: Experiments run from `experiments/` but import from project root via `sys.path.insert(0, project_root)`. Results save to `results/experiment_YYYYMMDD_HHMMSS.csv` with summary JSON.

### API Development
```powershell
# Terminal 1: Backend (must run from api/)
cd api
python main.py  # Uvicorn auto-starts on port 8000

# Terminal 2: Frontend (must run from ui/)
cd ui
streamlit run app.py --server.port 8501
```
**Never run FastAPI from project root** - ModelService expects `config.yaml` at `../config.yaml` relative to `api/`.

### First-Time Setup
```powershell
python setup.py  # Creates .env, installs deps, verifies Python 3.8+
# Edit .env and add: GOOGLE_API_KEY=your_key_here
```

## Project-Specific Conventions

### Prompt Engineering Pattern
Prompts live in `prompts/` as `.txt` files with structured format:
- **Imperative mood enforcement**: "Fix bug" not "Fixed bug"
- **Grounding rules**: "ONLY mention changes visible in the diff"
- **Few-shot examples**: Each prompt includes 3+ diff→message pairs
- Active prompt: `commit_generation_improved.txt` (configured in `config.yaml`)
- **Prompt versioning**: Keep old prompts (`commit_generation.txt`, `commit_generation_aggressive.txt`) for A/B testing

### Hallucination Detection Logic
Located in evaluators' `detect_hallucination()` method:
1. Tokenize commit message, remove stopwords
2. Check each token against diff text (case-insensitive)
3. Allow `self.allowed_technical_terms` (bug, refactor, etc.) without appearing in diff
4. Flag if >10% tokens are ungrounded (threshold in `config.yaml`)
5. Return `{detected: bool, rate: float, ungrounded_tokens: list}`

**Critical**: When modifying hallucination detection, update BOTH `evaluate.py` and `evaluate_simple.py` identically.

### Configuration-Driven Design
`config.yaml` controls:
- **Model params**: `temperature: 0.1` (reduced for determinism), `top_p`, `top_k`, `max_output_tokens`
- **Experiment settings**: `num_samples`, `delay_seconds: 7` (for 10 RPM rate limit), `batch_size`
- **Prompt selection**: `prompts.generation` points to active template
- **Hallucination threshold**: `evaluation.hallucination_threshold: 0.10`

**Always modify config, not hardcoded values** when tuning experiments.

### iOS 26 Liquid Glass UI Specs
Implemented in `ui/app.py` with custom CSS:
- **Blur**: `backdrop-filter: blur(20px)` with `-webkit-` prefix
- **Glass cards**: `rgba(255,255,255,0.1)` backgrounds, `rgba(255,255,255,0.3)` borders, 16px border-radius
- **Typography**: Inter font (fallback to SF Pro), 17px base size, no uppercase
- **Performance**: Never animate blur directly (causes lag), use opacity/transform only
- **Accessibility**: Provide high-contrast toggle, reduced-motion support, 44×44px touch targets

## Integration Points

### Gemini API Integration (`api/model_service.py`)
- Uses `google-generativeai` SDK with `genai.GenerativeModel`
- Prompt template has `{diff}` placeholder filled via `.format(diff=diff)`
- Logs every request/response to `logs/` if `config.logging.enabled: true`
- Returns dict: `{message: str, model: str, latency_ms: int, timestamp: str}`
- Handle `genai.exceptions.ResourceExhausted` for rate limits (10 RPM free tier)

### Dataset Format (`data/commitbench_samples.csv`)
Columns: `diff`, `message` (human reference), optional `repo`, `commit_id`
- Preprocessing in `data/prepare_dataset.py` filters trivial commits, limits diff length (50-5000 chars)
- Synthetic generation fallback if real dataset missing
- **Never mix repos** between train/val/test splits

### Results Analysis Pipeline
1. Experiments save to `results/experiment_*.csv` with columns: `diff`, `reference`, `generated`, `bleu`, `rougeL`, `semantic_similarity`, `hallucination_detected`, `hallucination_rate`, `quality_score`
2. `analyze_results.py` generates summary tables, hallucination analysis, metric distributions
3. `compare_results.py <baseline_id> <improved_id>` compares two experiments with LaTeX/Markdown tables
4. `create_hallucination_table.py` extracts worst hallucination cases with root cause analysis
5. Plots save to `results/plots/` (metric histograms, correlation matrices)
6. Summary JSON includes mean/std/min/max for each metric

**Analysis Script Usage**:
```powershell
cd experiments
python analyze_results.py  # Analyzes latest experiment
python compare_results.py 20251127_001902 20251127_005526  # Baseline vs improved
python create_hallucination_table.py  # Generates error analysis table
```

## Common Pitfalls

### Path Issues
❌ `FileNotFoundError: config.yaml` when running from wrong directory
✅ Always resolve paths absolutely using `os.path.abspath(__file__)` pattern

### Dependency Conflicts
❌ Keras 3.x incompatible with TensorFlow when loading BERTScore
✅ Use `evaluate_simple.py` for experiments, set `TRANSFORMERS_NO_TF=1`

### Rate Limiting
❌ Google API rejects requests if >10 RPM (free tier)
✅ `config.experiment.delay_seconds: 7` enforced in `run_experiments.py` batch loop

### Hallucination False Positives
❌ Flagging valid technical terms like "refactor" as hallucinations
✅ Maintain `allowed_technical_terms` set in evaluators, expand as needed

### BLEU Score Challenges
❌ Expecting high BLEU scores with synthetic dataset (observed: 0.00)
✅ BLEU requires exact n-gram matches; synthetic data has high variance. Focus on ROUGE-L and semantic similarity instead
- **Phase 2 Results**: BLEU-4 = 0.00 across all experiments (synthetic dataset limitation)
- **Better metrics**: ROUGE-L (47.90), Semantic Similarity (0.2952 improved from 0.1785)

### Dataset Quality Impact
❌ Using `data/commitbench_samples.csv` without understanding it's synthetic
✅ Current dataset generated by `data/prepare_dataset.py` with randomized patterns
- Real improvements: Hallucination rate reduced from 77.6% → 42.4% (35.3% improvement)
- Quality score improved 34.4% (0.2158 → 0.2899)

## Experimental Results Insights (Phase 2)

### Baseline vs Improved Performance
Running `compare_results.py` shows quantified improvements from prompt engineering:
- **Hallucination reduction**: 77.6% → 42.4% (35.3% decrease) via stricter grounding rules
- **Semantic similarity**: 0.1785 → 0.2952 (+65.4%) from few-shot examples in prompt
- **ROUGE-L**: 46.62 → 47.90 (+2.8%) marginal improvement
- **Latency improvement**: 690ms → 639ms (-7.5%) from reduced temperature
- **BLEU-4**: Remains 0.00 due to synthetic dataset high variance

### Error Pattern Analysis
`create_hallucination_table.py` categorizes failures:
1. **Hallucination errors (42.4%)**: "High rate of ungrounded tokens"
   - Model mentions functions/variables not in diff (e.g., `_simplified_item_process`)
   - Fix: Expand `allowed_technical_terms` cautiously, improve prompt grounding
2. **Context misunderstanding (57.6%)**: "Misunderstood diff context"
   - Model describes wrong operation (e.g., "return True" when actual change differs)
   - Fix: Add more contextual examples to prompt template

### Analysis Workflow for Debugging
```powershell
# 1. Run experiment
.\run_experiment_quick.bat

# 2. Analyze latest results
cd experiments
python analyze_results.py  # Check overall metrics

# 3. Compare with baseline
python compare_results.py 20251127_001902 20251127_005526

# 4. Deep-dive hallucinations
python create_hallucination_table.py  # Get LaTeX table for report
```

## Key Files Reference
- **Core services**: `api/main.py` (FastAPI endpoints), `api/model_service.py` (Gemini wrapper), `api/evaluate_simple.py` (metrics)
- **Experiments**: `experiments/run_experiments.py` (batch runner), `experiments/analyze_results.py` (results processing), `experiments/compare_results.py` (baseline comparison), `experiments/create_hallucination_table.py` (error analysis)
- **Config**: `config.yaml` (single source of truth), `prompts/commit_generation_improved.txt` (active prompt)
- **Setup**: `setup.py` (first-time install), `run_experiment_quick.bat` (Windows quick launcher)
- **Results**: `results/experiment_YYYYMMDD_HHMMSS.csv` (raw data), `results/hallucination_analysis.csv` (error table), `results/plots/*.png` (visualizations)
