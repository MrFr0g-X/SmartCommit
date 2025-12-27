# SmartCommit - Phase 3 Final Submission Package

**Course:** SW403 - AI in Modern Software Engineering (Fall 2025)
**Phase:** 3 - Production Implementation & Final Deployment
**Submission Date:** December 27, 2025

**Team Members:**
- Hothifa Hamdan (202201792) - Project Lead, Backend Integration
- Jilan Ismail (202201997) - Evaluation & Metrics Specialist
- Youssef Mahmoud (202202048) - Frontend & UI Specialist
- Mariam Zakary (202202092) - Testing & Audit Systems Specialist

**Institution:** University of Science and Technology at Zewail City

---

## 📦 Submission Contents

This package contains the complete Phase 3 submission for SmartCommit, including:

1. **Final Report** (8-page IEEE format paper)
2. **Complete Source Code** (2,500+ lines across 7 modules)
3. **Dataset & Experimental Results** (170 samples, 2 experiments)
4. **Test Suite** (32 tests with 100% coverage)
5. **Documentation** (API docs, user guides, technical specifications)
6. **Configuration Files** (deployment-ready setup)

---

## 📂 Directory Structure

```
Phase3_Submission/
│
├── SmartCommit_Phase3_Final_Report.pdf    # Main deliverable: 8-page IEEE paper
│
├── code/                                   # Complete source code
│   ├── api/                               # FastAPI backend (7 modules)
│   │   ├── main.py                       # 5 API endpoints with safety integration
│   │   ├── model_service.py              # Gemini 2.0 Flash API wrapper
│   │   ├── evaluate_simple.py            # Multi-metric evaluation
│   │   ├── safety.py                     # Phase 3: SafetyGuardrails (389 lines)
│   │   ├── audit_log.py                  # Phase 3: AuditLogger (346 lines)
│   │   └── git_interface.py              # GitPython diff extraction
│   ├── ui/                                # Streamlit frontend
│   │   └── app.py                        # iOS 26 Liquid Glass UI
│   ├── prompts/                           # Prompt engineering templates
│   │   ├── commit_generation.txt         # Baseline prompt
│   │   └── commit_generation_improved.txt # Phase 2 improved prompt
│   ├── config.yaml                        # System configuration
│   ├── requirements.txt                   # Python dependencies
│   └── .env.example                      # API key template
│
├── data/                                  # Dataset
│   ├── commitbench_samples.csv           # 170 synthetic samples
│   └── prepare_dataset.py                # Dataset generation script
│
├── results/                               # Experimental results
│   ├── experiment_20251127_001902.csv    # Baseline experiment (detailed)
│   ├── summary_20251127_001902.json      # Baseline statistics
│   ├── experiment_20251127_005526.csv    # Improved experiment (detailed)
│   ├── summary_20251127_005526.json      # Improved statistics
│   ├── hallucination_analysis.csv        # Error analysis
│   └── plots/                             # Metric visualizations
│       ├── bleu_distribution.png
│       ├── rouge_distribution.png
│       ├── semantic_similarity.png
│       └── hallucination_rate.png
│
├── tests/                                 # Test suite
│   └── test_phase3.py                    # 32 tests, 100% coverage
│
├── docs/                                  # Documentation
│   ├── Phase3_Report_IEEE.tex            # LaTeX source
│   ├── EVALUATION_METRICS_GUIDE.md       # Metrics explanation
│   ├── TESTING_GUIDE.md                  # Testing documentation
│   └── UI_DESIGN_GUIDE.md                # UI/UX documentation
│
└── README.md                              # Main project README

```

---

## 🎯 Key Deliverables

### 1. Final Research Paper (8 pages, IEEE format)

**File:** `SmartCommit_Phase3_Final_Report.pdf`

**Sections:**
- Abstract & Keywords
- Introduction (context, objectives, achievements)
- System Architecture (7 components, data flow)
- Phase 2 Experimental Results (baseline vs improved)
- Phase 3 Implementation (safety guardrails, audit logging)
- Testing & Validation (32 tests, 100% coverage)
- Results & Analysis (performance, safety metrics)
- Related Work & Discussion
- Future Work & Conclusions
- References (6 academic papers)

**Key Statistics:**
- BLEU-4: 0.00 (zero-shot baseline)
- ROUGE-L: 47.90 ± 19.31
- Semantic Similarity: 0.2952 ± 0.1075 (+65.4% improvement)
- Hallucination Rate: 42.4% (-35.3% reduction)
- Test Coverage: 100% (32/32 passing)
- Performance Overhead: <2% (<10ms per request)

### 2. Complete Source Code (2,500+ lines)

**Key Modules:**

**Phase 3 Safety Modules:**
- `api/safety.py` (389 lines) - 6-layer validation, 5 severity levels, 4 confidence tiers
- `api/audit_log.py` (346 lines) - JSONL logging, CSV metrics, audit reports

**Core System:**
- `api/main.py` - 5 REST endpoints with Pydantic validation
- `api/model_service.py` - Gemini API integration with rate limiting
- `api/evaluate_simple.py` - BLEU/ROUGE/semantic/hallucination evaluation
- `ui/app.py` - Modern Streamlit interface

**Configuration:**
- `config.yaml` - Centralized system settings
- `requirements.txt` - All Python dependencies
- `.env.example` - API key template

### 3. Dataset & Experimental Results

**Dataset:**
- `commitbench_samples.csv` - 170 synthetic samples
- Format: id, diff, message, type (bug_fix/feature/refactoring), language (python)
- Generated using `prepare_dataset.py` with realistic patterns

**Experiment Results:**
- **Baseline (20251127_001902):** Temperature 0.3, basic prompt
- **Improved (20251127_005526):** Temperature 0.1, few-shot prompt
- Detailed CSV files with per-sample metrics
- JSON summaries with aggregate statistics
- Hallucination analysis CSV (72 samples, 2 error categories)
- 4 metric distribution plots (PNG format)

### 4. Test Suite (100% Coverage)

**File:** `tests/test_phase3.py` (32 tests, 7 suites)

**Test Categories:**
1. Input Validation (6 tests) - Empty, size, lines, format, sensitive data, rate limiting
2. Hallucination Severity (5 tests) - NONE, LOW, MEDIUM, HIGH, CRITICAL
3. Confidence Levels (5 tests) - VERY_LOW, LOW, MEDIUM, HIGH
4. Safety Warnings (3 tests) - Warning generation, blocking behavior
5. Usage Recommendations (4 tests) - Context-specific guidance
6. Audit Logging (5 tests) - Request logging, metrics, stats, reports
7. Output Sanitization (3 tests) - Backticks, length, special chars

**Coverage:** 100% for `api/safety.py` and `api/audit_log.py`

### 5. Documentation

- **EVALUATION_METRICS_GUIDE.md** - BLEU, ROUGE, semantic similarity, hallucination detection
- **TESTING_GUIDE.md** - Test suite structure, running tests, coverage metrics
- **UI_DESIGN_GUIDE.md** - iOS 26 Liquid Glass design, accessibility, implementation
- **README.md** - Project overview, quick start, installation, usage

---

## 🚀 How to Run

### Prerequisites

```bash
# Python 3.9+
python --version

# Install dependencies
pip install -r code/requirements.txt
```

### Setup

```bash
# 1. Set API key
cp code/.env.example code/.env
# Edit .env and add: GOOGLE_API_KEY=your_key_here

# 2. Test the system
cd tests
python test_phase3.py
# Expected: 32/32 tests passing
```

### Running the API Backend

```bash
cd code
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# API will be available at: http://localhost:8000
# Interactive docs: http://localhost:8000/docs
```

### Running the UI Frontend

```bash
cd code
streamlit run ui/app.py

# UI will open in browser: http://localhost:8501
```

### Running Experiments

```bash
cd code
python experiments/run_experiments.py

# Results will be saved in: results/experiment_<timestamp>.csv
# Edit config.yaml to change num_samples for quick tests
```

---

## 📊 Phase 3 Achievements

### Safety Guardrails Module (389 lines)

**6-Layer Input Validation:**
1. Rate limiting (60 RPM per IP)
2. Empty input detection
3. Size validation (100KB max)
4. Line count validation (1,000 lines max)
5. Diff format verification
6. Sensitive data detection (API keys, passwords, tokens, emails, credit cards, SSH keys)

**5-Level Hallucination Severity:**
- NONE: <5% ungrounded tokens
- LOW: 5-15% ungrounded tokens (acceptable)
- MEDIUM: 15-30% ungrounded tokens (review recommended)
- HIGH: 30-50% ungrounded tokens (blocked)
- CRITICAL: >50% ungrounded tokens (blocked)

**4-Level Confidence Assessment:**
- HIGH: Quality score ≥ 0.7 (auto-commit safe)
- MEDIUM: Quality score 0.4-0.7 (review recommended)
- LOW: Quality score 0.2-0.4 (manual review required)
- VERY_LOW: Quality score < 0.2 (blocked)

### Audit Logging Module (346 lines)

**Features:**
- Tamper-evident JSONL logging (append-only, one JSON per line)
- CSV metrics aggregation (daily exports)
- Real-time session statistics
- Comprehensive audit reports
- Privacy preservation (no sensitive data logged)

**Logged Data:**
- Request metadata (timestamp, request_id, endpoint, IP)
- Diff characteristics (size, line count)
- Generation results (message length, quality score)
- Safety assessment (hallucination detected, severity, confidence)
- Performance metrics (execution time in milliseconds)

### Test Coverage (100%)

- **Total Tests:** 32
- **Passing:** 32 (100%)
- **Code Coverage:** 100% for Phase 3 modules
- **Performance:** <2% overhead, <10ms per request

---

## 🔬 Research Contributions

1. **First comprehensive evaluation of zero-shot LLMs for commit message generation** with detailed hallucination analysis

2. **Demonstration that prompt engineering achieves +65.4% semantic improvement** without fine-tuning

3. **Novel safety-first architecture for AI software tools** establishing blueprint for responsible AI deployment

4. **Open-source implementation** enabling reproducible research and practical deployment

---

## 📈 Performance Metrics

### Phase 2 Improvement Results

| Metric | Baseline | Improved | Change |
|--------|----------|----------|--------|
| BLEU-4 | 0.00 | 0.00 | - |
| ROUGE-L | 46.62 ± 21.89 | 47.90 ± 19.31 | +2.8% |
| Semantic Similarity | 0.1785 ± 0.1150 | 0.2952 ± 0.1075 | **+65.4%** |
| Hallucination Rate | 77.6% (132/170) | 42.4% (72/170) | **-35.3%** |
| Quality Score | 0.2158 ± 0.1235 | 0.2899 ± 0.1091 | **+34.4%** |
| Mean Latency | 690ms | 639ms | -7.5% |

### Phase 3 Production Metrics

| Metric | Value |
|--------|-------|
| Safety Code | 1,735 lines (SafetyGuardrails + AuditLogger + Tests) |
| Test Coverage | 100% (32/32 tests) |
| Performance Overhead | <2% (<10ms per request) |
| Input Validation Layers | 6 |
| Hallucination Severity Levels | 5 |
| Confidence Tiers | 4 |
| API Endpoints | 5 |

---

## 🎓 Academic Integrity Declaration

This project was completed by the SmartCommit team as part of SW403 coursework. All team members contributed to different aspects:

- **Hothifa Hamdan:** Project lead, backend integration, safety guardrails implementation
- **Jilan Ismail:** Evaluation metrics, experimental design, hallucination analysis
- **Youssef Mahmoud:** UI/UX design, frontend implementation, accessibility features
- **Mariam Zakary:** Test suite development, audit logging, quality assurance

All AI tools used (including Claude, ChatGPT, GitHub Copilot) are disclosed in the final report. Individual contributions are tracked via Git commit history.

---

## 📝 Grading Rubric Alignment

### Technical Implementation (40%)
✅ Complete system with 7 integrated modules
✅ 2,500+ lines of production code
✅ Phase 3 safety modules (1,735 lines)
✅ 100% test coverage (32 tests)

### Experimental Evaluation (30%)
✅ 170-sample synthetic dataset
✅ Baseline vs improved comparison
✅ Statistical analysis with visualizations
✅ Hallucination analysis (2 error categories)

### Documentation & Reporting (20%)
✅ 8-page IEEE format paper
✅ Complete API documentation
✅ User guides and technical specs
✅ Reproducible setup instructions

### Innovation & Research Quality (10%)
✅ Novel safety-first architecture
✅ Comprehensive hallucination detection
✅ First zero-shot LLM evaluation for commit messages
✅ Open-source contribution

---

## 📧 Contact Information

For questions about this submission:

- **Email:** s-hothifa.mohamed@zewailcity.edu.eg
- **GitHub:** https://github.com/MrFr0g-X/SmartCommit
- **Course:** SW403 - AI in Modern Software Engineering
- **Instructor:** [Course Instructor Name]

---

## 📄 License

This project is submitted for academic evaluation. Code and documentation are available for educational purposes only.

---

**Submission Prepared:** December 27, 2025
**Final Submission Package Version:** 1.0
