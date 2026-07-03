# HookLab — Evaluation Report

Generated: 2026-07-03T17:55:09.410853+00:00

## Dataset

- Test set: 43 hooks
- Distribution: 21 strong, 22 weak
- Features: 384-dim sentence-transformer embeddings (all-MiniLM-L6-v2)

## ML Classifier Performance

| Metric | Value |
|--------|-------|
| Accuracy | 62.79% |
| Precision | 64.71% |
| Recall | 52.38% |
| F1 Score | 57.89% |
| Correct | 27/43 |

### Confusion Matrix

```
              Predicted
              weak  strong
Actual weak     16     6
Actual strong   10    11
```

## Predicted vs Actual

### Per-Label Breakdown

| True Label | Count | Accuracy | Mean Confidence |
|------------|-------|----------|-----------------|
| strong | 21 | 52.38% | 74.11% |
| weak | 22 | 72.73% | 78.44% |

### Overconfident Wrong Predictions (confidence >80% but incorrect)

| Hook Text | True | Predicted | Confidence |
|-----------|------|-----------|------------|
| At Home Bodyweight AB WORKOUT! (No Equipment Needed) | strong | weak | 80.18% |
| 4 Dumbbell Moves For Sculpted Shoulders #travel #shorts #gre... | strong | weak | 92.05% |
| Every gym girl can relate 🤌🏻 #gym #gymmotivation #gymhumor #... | weak | strong | 92.35% |
| Average conversation between gym girls😂#gym #gymgirl #gymhum... | weak | strong | 88.91% |
| World hardest Muscle Up😳 #calisthenics #muscleup #shorts #gy... | weak | strong | 92.60% |
| Romanreigns attitude workout for motivation #fitness #gymmot... | weak | strong | 89.08% |

### Underconfident Correct Predictions (confidence <60% but correct)

| Hook Text | True | Predicted | Confidence |
|-----------|------|-----------|------------|
| How To Do Push Ups Beginners in Telugu #pushups #gym #motiva... | weak | weak | 57.95% |
| Posture correction exercises | weak | weak | 57.75% |
| No gym, no problem! 3 Exercises To Grow Your Back | strong | strong | 53.39% |
| Chest In Days At Home | strong | strong | 50.58% |
| Every Lifter will relate #bodybuilding #fitness #shorts | weak | weak | 51.62% |

## Rewriter Evaluation

Rewriter evaluation was skipped.

## Failure Analysis

16 out of 43 hooks were misclassified.

### High-Confidence Failures (confidence >70%)

These are the most concerning — the model is confident but wrong:

- "4 Home Exercises That Will Help You Lose Belly Fat, Tighten Your Core,..." — true: strong, predicted: weak (79%)
- "being short make losing weight feel 10x harder 😭 #fitness #workoutmoti..." — true: weak, predicted: strong (75%)
- "At Home Bodyweight AB WORKOUT! (No Equipment Needed)" — true: strong, predicted: weak (80%)
- "4 Dumbbell Moves For Sculpted Shoulders #travel #shorts #greece #worko..." — true: strong, predicted: weak (92%)
- "Every gym girl can relate 🤌🏻 #gym #gymmotivation #gymhumor #gymmemes #..." — true: weak, predicted: strong (92%)
- "Average conversation between gym girls😂#gym #gymgirl #gymhumor #gymmot..." — true: weak, predicted: strong (89%)
- "World hardest Muscle Up😳 #calisthenics #muscleup #shorts #gym" — true: weak, predicted: strong (93%)
- "Romanreigns attitude workout for motivation #fitness #gymmotivation #g..." — true: weak, predicted: strong (89%)
- "Do it every single day.. 💪#workout #pushups #challenges #motivationalv..." — true: strong, predicted: weak (80%)

### Borderline Failures (7 hooks with confidence <=70%)

These are understandable — the model was unsure:

- "Chest workout at home (beginner level)✅" — true: strong, predicted: weak (60%)
- "100 push-ups, 100 sit-ups, and 100 squats, and a 10 km run. Do it ever..." — true: strong, predicted: weak (65%)
- "Want to have Slim Body? 🙌🏻🧍🏻‍♀️#aesthetic #exercise #trending #shorts ..." — true: strong, predicted: weak (60%)
- "Trick for fitness video creator #shorts #fitness #tips" — true: strong, predicted: weak (52%)
- "Full body Homeworkout 💪…. #homeworkout #shorts #shortvideo #workout" — true: strong, predicted: weak (62%)
- "PUSH UPS FOR BEGINNERS #shorts" — true: strong, predicted: weak (56%)
- "just don’t stop… trust the process! 🥰 #fitness #weightloss #transforma..." — true: weak, predicted: strong (60%)

## Honest Limitations

- **Small dataset:** 213 total hooks is far below the 400 target. Results are directional, not statistically significant.
- **Classifier underperforms baseline:** The ML model does not beat the simple hook_length baseline. This suggests embeddings alone may not capture what makes a hook strong — or the dataset is too small for the model to learn meaningful patterns.
- **LLM-as-judge is not ground truth:** The rewriter evaluation uses an LLM to judge quality. This is disclosed and should be validated with human evaluation in future work.
- **Dimension scores are LLM-generated:** The 4 dimension scores (specificity, curiosity gap, clarity of payoff, concreteness) come from an LLM, not from human annotators. There is no ground truth for these.
- **Single niche:** All data is from fitness. Generalization to other content verticals is unknown.
- **What would help:** 500+ hooks with human-annotated dimension scores, A/B test data from real content performance, and multi-niche expansion.
