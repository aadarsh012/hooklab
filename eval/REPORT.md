# HookLab Phase 3 — Scoring Model Evaluation

Generated: 2026-07-08T17:35:54.215929+00:00

## Dataset

- Training: 170 hooks (85 strong, 85 weak)
- Test: 43 hooks (21 strong, 22 weak)
- Features: 384-dim sentence-transformer embeddings (all-MiniLM-L6-v2)

## Baselines

| Baseline | Accuracy | Precision | Recall |
|----------|----------|-----------|--------|
| majority_class | 51.16% | 0.00% | 0.00% |
| hook_length | 76.74% | 78.95% | 71.43% |

## Models

| Model | Accuracy | Precision | Recall | vs. Best Baseline |
|-------|----------|-----------|--------|-------------------|
| Logistic Regression | 53.49% | 52.63% | 47.62% | -23.26% |
| Gradient Boosting | 62.79% | 64.71% | 52.38% | -13.95% |

## Confusion Matrices

### Logistic Regression

```
              Predicted
              weak  strong
Actual weak     13     9
Actual strong   11    10
```

### Gradient Boosting

```
              Predicted
              weak  strong
Actual weak     16     6
Actual strong   10    11
```

## Test Set Predictions

### Logistic Regression

| Hook Text | True | Predicted | Confidence |
|-----------|------|-----------|------------|
| Fitness Advice for Beginners Ft. Saket Gokhale #shorts | strong | strong (ok) | 50.83% |
| Top three abs exercises. #youtubeshorts #shortvideo #shortsv... | weak | weak (ok) | 67.43% |
| 4 Home Exercises That Will Help You Lose Belly Fat, Tighten ... | strong | weak (WRONG) | 65.36% |
| ULTIMATE At Home Chest Workout - NO Equipment Upper, Lower, ... | weak | weak (ok) | 70.82% |
| Chest workout at home (beginner level)✅ | strong | weak (WRONG) | 58.11% |
| being short make losing weight feel 10x harder 😭 #fitness #w... | weak | strong (WRONG) | 57.98% |
| At Home Bodyweight AB WORKOUT! (No Equipment Needed) | strong | weak (WRONG) | 65.47% |
| 100 push-ups, 100 sit-ups, and 100 squats, and a 10 km run. ... | strong | weak (WRONG) | 54.54% |
| COMPLETE Shoulder Workout: From BEGINNER to ADVANCED for MAX... | weak | weak (ok) | 64.65% |
| 4 Dumbbell Moves For Sculpted Shoulders #travel #shorts #gre... | strong | weak (WRONG) | 62.87% |
| If you want to start going to the gym… | strong | strong (ok) | 72.06% |
| How To Do Push Ups Beginners in Telugu #pushups #gym #motiva... | weak | weak (ok) | 57.59% |
| FIRST DAY AT GYM? 🫵🏽 | strong | strong (ok) | 72.30% |
| Complete Abs Workout | Upper + Lower + Obliques (12x3 Sets) ... | weak | weak (ok) | 64.70% |
| Every gym girl can relate 🤌🏻 #gym #gymmotivation #gymhumor #... | weak | strong (WRONG) | 66.22% |
| Average conversation between gym girls😂#gym #gymgirl #gymhum... | weak | strong (WRONG) | 66.92% |
| Want to have Slim Body? 🙌🏻🧍🏻‍♀️#aesthetic #exercise #trendin... | strong | weak (WRONG) | 55.08% |
| Learn the correct posture of butterfly machine chest trainin... | weak | weak (ok) | 58.50% |
| How To Start In The Gym For Beginners | strong | strong (ok) | 68.03% |
| Posture correction exercises | weak | weak (ok) | 67.16% |
| 5 Minutes Quick Workout for Beginners | strong | strong (ok) | 54.28% |
| Trick for fitness video creator #shorts #fitness #tips | strong | weak (WRONG) | 58.08% |
| Quick abs and mobility workout 🔥#africa #bodybuilding #abs #... | weak | weak (ok) | 67.58% |
| पेट और कमर साइज कम#yoga#waistslim#weightloss#petkm#waistwork... | weak | weak (ok) | 51.74% |
| Full body Homeworkout 💪…. #homeworkout #shorts #shortvideo #... | strong | weak (WRONG) | 53.36% |
| No gym, no problem! 3 Exercises To Grow Your Back | strong | weak (WRONG) | 51.47% |
| Chest In Days At Home | strong | strong (ok) | 50.26% |
| Gym anxiety? Watch this🙌🏼 | strong | strong (ok) | 76.94% |
| Phases of a Gymbro’s outfits | strong | strong (ok) | 69.04% |
| Body kaise banaye at home workout #fitnesstips #motivation #... | weak | weak (ok) | 63.12% |
| ❌ Lat Pulldown Mistakes You Need to 🛑 STOP DOING! | strong | strong (ok) | 64.77% |
| Full body workout tips#gym#shorts#trending#motivation #r2xfi... | weak | weak (ok) | 59.94% |
| Discipline and Consistency #bodybuilding #fitness #shorts | strong | strong (ok) | 52.04% |
| PUSH UPS FOR BEGINNERS #shorts | strong | weak (WRONG) | 55.48% |
| How to Grow Chest Fast with Incline Chest Press | Best Chest... | weak | strong (WRONG) | 50.39% |
| Desperado sitting in a old Monte Carlo. | weak | strong (WRONG) | 51.41% |
| Every Lifter will relate #bodybuilding #fitness #shorts | weak | strong (WRONG) | 59.68% |
| Best home workout for chest , triceps and biceps no equipmen... | weak | weak (ok) | 67.48% |
| World hardest Muscle Up😳 #calisthenics #muscleup #shorts #gy... | weak | strong (WRONG) | 57.71% |
| Romanreigns attitude workout for motivation #fitness #gymmot... | weak | strong (WRONG) | 51.06% |
| Do it every single day.. 💪#workout #pushups #challenges #mot... | strong | weak (WRONG) | 53.40% |
| Reduce breast fat #breastfat #fatloss #workout #exercise #yo... | weak | weak (ok) | 60.56% |
| just don’t stop… trust the process! 🥰 #fitness #weightloss #... | weak | strong (WRONG) | 62.94% |

### Gradient Boosting

| Hook Text | True | Predicted | Confidence |
|-----------|------|-----------|------------|
| Fitness Advice for Beginners Ft. Saket Gokhale #shorts | strong | strong (ok) | 62.16% |
| Top three abs exercises. #youtubeshorts #shortvideo #shortsv... | weak | weak (ok) | 90.52% |
| 4 Home Exercises That Will Help You Lose Belly Fat, Tighten ... | strong | weak (WRONG) | 79.11% |
| ULTIMATE At Home Chest Workout - NO Equipment Upper, Lower, ... | weak | weak (ok) | 95.08% |
| Chest workout at home (beginner level)✅ | strong | weak (WRONG) | 60.12% |
| being short make losing weight feel 10x harder 😭 #fitness #w... | weak | strong (WRONG) | 74.56% |
| At Home Bodyweight AB WORKOUT! (No Equipment Needed) | strong | weak (WRONG) | 80.18% |
| 100 push-ups, 100 sit-ups, and 100 squats, and a 10 km run. ... | strong | weak (WRONG) | 65.26% |
| COMPLETE Shoulder Workout: From BEGINNER to ADVANCED for MAX... | weak | weak (ok) | 98.87% |
| 4 Dumbbell Moves For Sculpted Shoulders #travel #shorts #gre... | strong | weak (WRONG) | 92.05% |
| If you want to start going to the gym… | strong | strong (ok) | 97.17% |
| How To Do Push Ups Beginners in Telugu #pushups #gym #motiva... | weak | weak (ok) | 57.95% |
| FIRST DAY AT GYM? 🫵🏽 | strong | strong (ok) | 97.49% |
| Complete Abs Workout | Upper + Lower + Obliques (12x3 Sets) ... | weak | weak (ok) | 90.36% |
| Every gym girl can relate 🤌🏻 #gym #gymmotivation #gymhumor #... | weak | strong (WRONG) | 92.35% |
| Average conversation between gym girls😂#gym #gymgirl #gymhum... | weak | strong (WRONG) | 88.91% |
| Want to have Slim Body? 🙌🏻🧍🏻‍♀️#aesthetic #exercise #trendin... | strong | weak (WRONG) | 59.50% |
| Learn the correct posture of butterfly machine chest trainin... | weak | weak (ok) | 69.35% |
| How To Start In The Gym For Beginners | strong | strong (ok) | 94.39% |
| Posture correction exercises | weak | weak (ok) | 57.75% |
| 5 Minutes Quick Workout for Beginners | strong | strong (ok) | 71.00% |
| Trick for fitness video creator #shorts #fitness #tips | strong | weak (WRONG) | 52.29% |
| Quick abs and mobility workout 🔥#africa #bodybuilding #abs #... | weak | weak (ok) | 91.17% |
| पेट और कमर साइज कम#yoga#waistslim#weightloss#petkm#waistwork... | weak | weak (ok) | 79.03% |
| Full body Homeworkout 💪…. #homeworkout #shorts #shortvideo #... | strong | weak (WRONG) | 62.46% |
| No gym, no problem! 3 Exercises To Grow Your Back | strong | strong (ok) | 53.39% |
| Chest In Days At Home | strong | strong (ok) | 50.58% |
| Gym anxiety? Watch this🙌🏼 | strong | strong (ok) | 96.64% |
| Phases of a Gymbro’s outfits | strong | strong (ok) | 60.81% |
| Body kaise banaye at home workout #fitnesstips #motivation #... | weak | weak (ok) | 72.91% |
| ❌ Lat Pulldown Mistakes You Need to 🛑 STOP DOING! | strong | strong (ok) | 94.37% |
| Full body workout tips#gym#shorts#trending#motivation #r2xfi... | weak | weak (ok) | 71.42% |
| Discipline and Consistency #bodybuilding #fitness #shorts | strong | strong (ok) | 92.17% |
| PUSH UPS FOR BEGINNERS #shorts | strong | weak (WRONG) | 55.58% |
| How to Grow Chest Fast with Incline Chest Press | Best Chest... | weak | weak (ok) | 62.64% |
| Desperado sitting in a old Monte Carlo. | weak | weak (ok) | 61.96% |
| Every Lifter will relate #bodybuilding #fitness #shorts | weak | weak (ok) | 51.62% |
| Best home workout for chest , triceps and biceps no equipmen... | weak | weak (ok) | 96.40% |
| World hardest Muscle Up😳 #calisthenics #muscleup #shorts #gy... | weak | strong (WRONG) | 92.60% |
| Romanreigns attitude workout for motivation #fitness #gymmot... | weak | strong (WRONG) | 89.08% |
| Do it every single day.. 💪#workout #pushups #challenges #mot... | strong | weak (WRONG) | 79.52% |
| Reduce breast fat #breastfat #fatloss #workout #exercise #yo... | weak | weak (ok) | 81.00% |
| just don’t stop… trust the process! 🥰 #fitness #weightloss #... | weak | strong (WRONG) | 60.16% |

## Failure Analysis

| Hook Text | True | Predicted | Confidence | Notes |
|-----------|------|-----------|------------|-------|
| 4 Home Exercises That Will Help You Lose Belly Fat, Tighten ... | strong | weak | 79.11% | Moderate confidence wrong prediction |
| Chest workout at home (beginner level)✅ | strong | weak | 60.12% | Moderate confidence wrong prediction |
| being short make losing weight feel 10x harder 😭 #fitness #w... | weak | strong | 74.56% | Moderate confidence wrong prediction |
| At Home Bodyweight AB WORKOUT! (No Equipment Needed) | strong | weak | 80.18% | High confidence wrong prediction |
| 100 push-ups, 100 sit-ups, and 100 squats, and a 10 km run. ... | strong | weak | 65.26% | Moderate confidence wrong prediction |
| 4 Dumbbell Moves For Sculpted Shoulders #travel #shorts #gre... | strong | weak | 92.05% | High confidence wrong prediction |
| Every gym girl can relate 🤌🏻 #gym #gymmotivation #gymhumor #... | weak | strong | 92.35% | High confidence wrong prediction |
| Average conversation between gym girls😂#gym #gymgirl #gymhum... | weak | strong | 88.91% | High confidence wrong prediction |
| Want to have Slim Body? 🙌🏻🧍🏻‍♀️#aesthetic #exercise #trendin... | strong | weak | 59.50% | Borderline confidence |
| Trick for fitness video creator #shorts #fitness #tips | strong | weak | 52.29% | Borderline confidence |
| Full body Homeworkout 💪…. #homeworkout #shorts #shortvideo #... | strong | weak | 62.46% | Moderate confidence wrong prediction |
| PUSH UPS FOR BEGINNERS #shorts | strong | weak | 55.58% | Borderline confidence |
| World hardest Muscle Up😳 #calisthenics #muscleup #shorts #gy... | weak | strong | 92.60% | High confidence wrong prediction |
| Romanreigns attitude workout for motivation #fitness #gymmot... | weak | strong | 89.08% | High confidence wrong prediction |
| Do it every single day.. 💪#workout #pushups #challenges #mot... | strong | weak | 79.52% | Moderate confidence wrong prediction |
| just don’t stop… trust the process! 🥰 #fitness #weightloss #... | weak | strong | 60.16% | Moderate confidence wrong prediction |

## Honest Assessment

- With a very small dataset, these numbers are not statistically meaningful.
- Individual predictions swing accuracy by large percentages.
- No model beats the best baseline. This is reported honestly.
- The methodology and infrastructure are the real deliverable at this scale.
- More data (200+ hooks) is needed before drawing conclusions.
