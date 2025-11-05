# Evaluation System Tests

Comprehensive test suite for the 3-rubric evaluation system (30 metrics total).

## Test Structure

```
tests/
├── fixtures/               # Mock data for testing
│   ├── mock_turns.jsonl           # Conversation turns
│   ├── mock_session_split.json    # Session boundaries
│   ├── mock_context.json          # Context analysis
│   ├── mock_keywords.json         # Extracted keywords
│   ├── mock_graph.json            # Graph layout
│   ├── mock_golden_annotations.json  # Ground truth
│   └── mock_embeddings.json       # Sentence embeddings
│
├── test_utils.py          # Test utilities and fixtures
├── test_context_rubric.py # Context Rubric tests (10 metrics)
├── test_layout_rubric.py  # Layout Rubric tests (10 metrics)
├── test_comprehensive_rubric.py  # Comprehensive Rubric tests (10 metrics)
└── test_integration.py    # Integration tests (all 3 rubrics)
```

## Test Coverage

### Context Rubric (10 metrics)
1. Main path coherence - Semantic coherence of main conversation flow
2. Branch detection recall - Side branch identification accuracy
3. Side-main connection accuracy - Branch point accuracy
4. Session boundary F1 - Topic transition detection
5. Summary-path consistency - Summary alignment with path
6. Topic transition stability - Transition smoothness
7. Edge direction error rate - Flow direction clarity
8. Duplicate branch rate - Redundancy detection
9. Latency - Processing time
10. Parsing stability - JSON validation

### Layout Rubric (10 metrics)
1. Depth balance - Tree depth distribution entropy
2. Branching balance - Children count uniformity
3. Edge crossing minimization - Line intersection count
4. Centrality distribution balance - PageRank variance
5. Cluster cohesion - Modularity score
6. Edge length variance - Edge length consistency
7. Label readability - Node overlap detection
8. Node density - Optimal spacing
9. Color contrast - Visual distinction
10. Interaction responsiveness - Render time

### Comprehensive Rubric (10 metrics)
1. Structural score - Weighted sum of context + layout
2. Content coverage - Keyword coverage rate
3. Off-topic penalty - Irrelevant node detection
4. Format compliance - Schema validation
5. Parsing success rate - 5-stage pipeline success
6. User preference alignment - User ratings (most important!)
7. Reproducibility - Deterministic execution
8. Processing time score - Pipeline speed
9. Stability - Error rate
10. API cost penalty - Token usage cost

## Running Tests

### Run all tests
```bash
pytest tests/ -v
```

### Run specific test file
```bash
pytest tests/test_context_rubric.py -v
pytest tests/test_layout_rubric.py -v
pytest tests/test_comprehensive_rubric.py -v
pytest tests/test_integration.py -v
```

### Run integration tests only
```bash
pytest tests/test_integration.py::TestFullPipelineEvaluation::test_complete_3_rubric_evaluation -v -s
```

### Run with coverage
```bash
pytest tests/ --cov=agents/evaluate --cov-report=html
```

## Test Fixtures

All test fixtures are JSON files containing mock data that matches the schema definitions in `configs/schema/`.

- **mock_turns.jsonl**: 10-turn conversation about React Hooks
- **mock_session_split.json**: 3 detected sessions
- **mock_context.json**: 2 main paths + 1 side branch
- **mock_keywords.json**: Keywords per path with scores
- **mock_graph.json**: 6 nodes, 5 edges, hierarchical layout
- **mock_golden_annotations.json**: Ground truth for comparison
- **mock_embeddings.json**: 384-dim embeddings for 10 turns

## Expected Test Results

All tests should pass with:
- ✓ Unit tests: Each metric function returns valid scores in [0, 1]
- ✓ Integration tests: All 3 rubrics evaluate successfully
- ✓ Overall score: Weighted average of 30 metrics

## Mock Data Flow

```
Conversation (10 turns)
    ↓
Session Split (3 sessions)
    ↓
Context Analysis (2 main paths, 1 side branch)
    ↓
Keywords (8 keywords across paths)
    ↓
Graph Layout (6 nodes, 5 edges)
    ↓
Evaluation (30 metrics)
```

## Key Testing Principles

1. **No API calls**: All tests use mock data, no OpenAI API required
2. **Deterministic**: Same input always produces same output
3. **Fast**: Complete test suite runs in < 10 seconds
4. **Comprehensive**: Tests cover edge cases, errors, custom weights
5. **Realistic**: Mock data reflects actual pipeline output structure

## Troubleshooting

### ImportError: No module named 'numpy'
```bash
pip install numpy
```

### ImportError: No module named 'pytest'
```bash
pip install pytest
```

### Tests fail due to missing dependencies
```bash
pip install -r requirements.txt
```

## Test Development Guidelines

When adding new metrics:
1. Add unit tests in appropriate rubric test file
2. Add integration test case
3. Update mock fixtures if needed
4. Document metric in this README
5. Verify all tests pass

## Contact

For questions about the evaluation system or tests, refer to:
- Main README: `/README.md`
- Research justification: `/docs/RESEARCH_JUSTIFICATION.md`
- Schema definitions: `/configs/schema/`
