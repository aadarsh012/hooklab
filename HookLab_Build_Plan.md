# HookLab — Build Plan

A short-form hook and script pre-flight analyzer. The goal is a portfolio-grade AI project that demonstrates RAG, agent orchestration, applied ML on embeddings, and a real evaluation harness, built and run on free tiers so it costs effectively nothing.

---

## Guiding principles

**Build a walking skeleton first.** Before going deep on any single layer, get a dumb version of the whole pipeline working end to end on 20 hand-collected hooks: input goes in, embedding happens, retrieval returns something, an LLM says something, output comes out. You then deepen each layer in place. This keeps you from spending a week perfecting a retriever you can't yet see working inside the full system.

**The eval harness is the headline, not an afterthought.** What separates this from a wrapper is proof it works. Every later phase feeds the eval. The README is written around the numbers, not the features.

**One niche only.** Pick a single content lane, namely fitness, finance, study-tips, cooking, or tech, and collect, train, and evaluate entirely within it. A focused corpus is what makes retrieval and the classifier sharp. Breadth is a stretch goal, never a v1 goal.

**Assumed setup:** Python backend with a thin Streamlit demo layer, solo builder, roughly 10 to 15 hours per week. The plan spans about 6 weeks at that pace and compresses cleanly if you have more time.

---

## Tech stack, all free

| Layer | Choice | Cost |
|---|---|---|
| Embeddings | sentence-transformers, run locally | Free |
| Vector store | Chroma or FAISS, local | Free |
| Generation | Gemini Flash free tier, Groq Llama as fallback | Free |
| Classifier | scikit-learn, logistic regression or gradient boosting | Free |
| Orchestration | LangGraph | Free |
| Structured outputs | Pydantic | Free |
| Demo UI | Streamlit | Free |
| Local fallback LLM | Ollama | Free |

Set up API keys for both Gemini and Groq on day one so a rate-limit error on one silently falls back to the other.

---

## Repo structure

```
hooklab/
  data/                 raw and cleaned hook corpus
  ingestion/            collection and cleaning scripts
  embeddings/           embedding + vector store code
  scoring/              classifier training + inference
  agents/               LangGraph pipeline, personas, rewriter
  eval/                 test sets, metrics, reports
  app/                  Streamlit demo
  notebooks/            exploration, kept tidy
  README.md             written around the eval results
```

---

## Phase 0 — Setup and scope. ~2 days

**Goal:** environment ready, niche chosen, skeleton mindset locked.

- [ ] Pick the single niche. Decide it now, do not revisit.
- [ ] Create the repo, virtual environment, and the folder structure above.
- [ ] Register Gemini and Groq keys, store them in a `.env`, confirm a hello-world call to each.
- [ ] Define the controllable scoring dimensions you will judge a hook on, namely specificity, curiosity gap, clarity of payoff, and concreteness. Write them down as the spec everything else refers to.

**Deliverable:** a repo that makes one successful call to each LLM provider.

---

## Phase 1 — Data collection. ~1 week

This is the hardest and most important phase. The quality of everything downstream is capped here.

- [ ] Collect 200 to 400 short-form video openers in your niche. The opener is the first one or two sentences, namely the hook itself, not the whole script.
- [ ] For each, capture an engagement signal you can use as a label. View count alone is noisy, so prefer a ratio where you can get it, namely likes-to-views or saves-to-views, which better reflects whether the hook landed.
- [ ] Clean into a structured file, namely one row per hook with text, niche, and the engagement metric.
- [ ] Build a binary or three-bucket label from the metric, namely "strong" versus "weak" by splitting on the median or terciles within your niche.
- [ ] Hold out 20 percent as a test set immediately and do not touch it again until evaluation.

**Honest risk:** collection is tedious and the terms of each platform matter. Budget for manual collection if scraping is blocked. 200 clean, well-labeled hooks beat 2,000 messy ones.

**Deliverable:** a clean, labeled, train-test-split corpus in one niche.

**Walking-skeleton checkpoint:** by the end of this phase, wire the crudest possible end-to-end path, namely embed 20 hooks, retrieve the nearest one to a query, and have Gemini say one sentence about it. Ugly is fine. The point is the pipe runs.

---

## Phase 2 — Embeddings and retrieval. ~4 days

**Goal:** the RAG layer.

- [ ] Embed the full corpus locally with sentence-transformers.
- [ ] Load embeddings into Chroma or FAISS.
- [ ] Build a retrieval function, namely given a new hook, return the k most similar hooks from the corpus with their labels and metrics.
- [ ] Sanity-check retrieval quality by eye on ten queries. Does it return genuinely similar hooks?

**Deliverable:** `retrieve(hook) -> top-k similar labeled hooks`.

**What you learn:** embeddings, vector stores, semantic retrieval.

---

## Phase 3 — The scoring model. ~1 week

This is the ML differentiator that lifts the project above a wrapper. Do not skip it or replace it with an LLM guess.

- [ ] Use the embeddings from Phase 2 as features. Train a scikit-learn classifier, namely logistic regression first, then try gradient boosting, to predict the strong-versus-weak label.
- [ ] Establish a baseline to beat, namely a trivial predictor such as always-predict-majority-class, and a simple one such as hook length. Your model must beat these or you report that honestly.
- [ ] Evaluate on the held-out test set with accuracy, precision, recall, and a confusion matrix.
- [ ] Inspect failures. Which hooks does it misjudge, and why? Write this down, it becomes README gold.

**Deliverable:** `predict_strength(hook) -> score + confidence`, plus a metrics report versus baselines.

**What you learn:** applied ML on embeddings, baselines, honest evaluation, error analysis.

---

## Phase 4 — The agent pipeline. ~1 week

**Goal:** the LangGraph system that turns scores into useful, readable feedback.

- [ ] Define Pydantic schemas for every structured output, namely the score breakdown, the persona reactions, and the rewrite pairs.
- [ ] Build the graph with these nodes: a **scorer** node that combines the Phase 3 model output with an LLM critique on the controllable dimensions, a **synthetic-viewer panel** of three persona agents who each react in-character from a niche-specific viewpoint, and an **A/B rewriter** that proposes two improved variants and explains what each changes.
- [ ] Ground the personas and the rewriter with retrieved examples from Phase 2 so feedback references real comparable hooks rather than floating opinion.
- [ ] Add LLM response caching so repeated runs cost nothing and run fast.

**Deliverable:** `analyze(hook) -> {score, dimension breakdown, three persona reactions, two rewrites}`.

**What you learn:** LangGraph orchestration, multi-agent design, structured outputs, grounding, caching.

---

## Phase 5 — The eval harness. ~5 days, can overlap Phase 4

**Goal:** the proof. This is what makes the project credible.

- [ ] On the held-out test set, compare your system's predicted strength against the real engagement labels. Report the numbers plainly.
- [ ] Show the lift over the baselines from Phase 3.
- [ ] Evaluate the rewriter qualitatively, namely take 20 weak hooks, generate rewrites, and check whether a blind judgment prefers the rewrite. You can use an LLM-as-judge here, but disclose that you did.
- [ ] Write an honest failure section, namely where the system is wrong, where it is overconfident, and what you would fix with more data.

**Deliverable:** an `eval/REPORT.md` with tables, a predicted-versus-actual chart, and a candid limitations section.

**What you learn:** held-out evaluation, predicted-versus-actual analysis, LLM-as-judge, intellectual honesty, which reviewers notice.

---

## Phase 6 — Demo and portfolio polish. ~5 days

**Goal:** make it runnable and legible to a stranger in two minutes.

- [ ] Build a Streamlit app, namely paste a hook, see the score, the dimension breakdown, the persona reactions, and the two rewrites.
- [ ] Write the README around the eval results, not the features. Lead with what the system does, then the numbers proving it works, then the architecture, then the honest limitations.
- [ ] Add a short architecture diagram and a 60-second screen recording.
- [ ] Clean the repo, add setup instructions, pin dependencies.

**Deliverable:** a public repo a recruiter can run, plus a README that opens with evidence.

---

## Timeline at a glance

| Week | Focus | Milestone |
|---|---|---|
| 1 | Phase 0 + start Phase 1 | Keys working, niche chosen, collection underway |
| 2 | Finish Phase 1 + Phase 2 | Labeled corpus, retrieval working, skeleton runs end to end |
| 3 | Phase 3 | Trained classifier beating baselines, metrics report |
| 4 | Phase 4 | Full LangGraph pipeline producing structured feedback |
| 5 | Phase 5 | Eval report with predicted-versus-actual and failure analysis |
| 6 | Phase 6 | Streamlit demo, eval-first README, repo polished |

---

## Sequencing and risk notes

- **Critical path runs through data.** If Phase 1 slips, everything slips. Start collecting on day one, in parallel with setup.
- **The walking skeleton de-risks integration.** Get the ugly end-to-end path running by end of week 2 so no layer is built blind.
- **Phases 4 and 5 can overlap.** Build the eval as you build the agents, not after.
- **Cut frontend before you cut eval.** If time runs short, ship a notebook demo and keep the eval harness intact. The eval is the resume value, the UI is gravy.

---

## What this demonstrates on a resume

RAG and semantic retrieval, agent orchestration with LangGraph, applied ML on embeddings with baselines, structured LLM outputs, a real evaluation methodology with predicted-versus-actual and honest failure analysis, and cost-aware engineering on free infrastructure. The last two are rare in portfolio projects and are exactly what separates an engineer who measures from one who only demos.
