# HookLab Phase 3 — Scoring Model Evaluation

Generated: 2026-06-30T16:54:29.640921+00:00

## Dataset

- Training: 16 hooks (8 strong, 8 weak)
- Test: 4 hooks (2 strong, 2 weak)
- Features: 384-dim sentence-transformer embeddings (all-MiniLM-L6-v2)

## Baselines

| Baseline | Accuracy | Precision | Recall |
|----------|----------|-----------|--------|
| majority_class | 50.00% | 0.00% | 0.00% |
| hook_length | 50.00% | 50.00% | 50.00% |

## Models

| Model | Accuracy | Precision | Recall | vs. Best Baseline |
|-------|----------|-----------|--------|-------------------|
| Logistic Regression | 75.00% | 100.00% | 50.00% | +25.00% |
| Gradient Boosting | 75.00% | 100.00% | 50.00% | +25.00% |

## Confusion Matrices

### Logistic Regression

```
              Predicted
              weak  strong
Actual weak      2     0
Actual strong    1     1
```

### Gradient Boosting

```
              Predicted
              weak  strong
Actual weak      2     0
Actual strong    1     1
```

## Test Set Predictions

### Logistic Regression

| Hook Text | True | Predicted | Confidence |
|-----------|------|-----------|------------|
| 100 push-ups, 100 sit-ups, and 100 squats, and a 10 km run. ... | strong | weak (WRONG) | 52.13% |
| if you want to push harder know this your mind quits way bef... | strong | strong (ok) | 57.96% |
| do not neglect the reverse wrist curl if you've never done i... | weak | weak (ok) | 52.54% |
| there we go | weak | weak (ok) | 56.47% |

### Gradient Boosting

| Hook Text | True | Predicted | Confidence |
|-----------|------|-----------|------------|
| 100 push-ups, 100 sit-ups, and 100 squats, and a 10 km run. ... | strong | weak (WRONG) | 69.26% |
| if you want to push harder know this your mind quits way bef... | strong | strong (ok) | 99.03% |
| do not neglect the reverse wrist curl if you've never done i... | weak | weak (ok) | 69.26% |
| there we go | weak | weak (ok) | 69.26% |

## Failure Analysis

| Hook Text | True | Predicted | Confidence | Notes |
|-----------|------|-----------|------------|-------|
| 100 push-ups, 100 sit-ups, and 100 squats, and a 10 km run. ... | strong | weak | 52.13% | Borderline confidence |

## Honest Assessment

- With a very small dataset, these numbers are not statistically meaningful.
- Individual predictions swing accuracy by large percentages.
- At least one model beats the best baseline, but this may not generalize.
- The methodology and infrastructure are the real deliverable at this scale.
- More data (200+ hooks) is needed before drawing conclusions.
