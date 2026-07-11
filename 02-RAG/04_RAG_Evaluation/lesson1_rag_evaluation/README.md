# Lesson 1 · RAG Evaluation

**Time:** 19:00 · 60 minutes  
**Module:** PHASE 3: RAG  
**Instructor:** Liangjun Song

---

## Learning Objectives

By the end of this lesson, students will be able to:

1. Explain **why evaluation is the missing link** in most RAG pipelines and what breaks without it.
2. Name and define the **four core RAG metrics**: Context Precision, Context Recall, Faithfulness, and Answer Relevancy.
3. Manually calculate each metric on a toy example to build intuition before using a framework.
4. Use the **RAGAS framework** to run automated evaluation on a sample dataset with DeepSeek as the judge LLM.
5. Read a RAGAS score report and identify which component of the RAG pipeline needs the most attention.

---

## Time Allocation

| Segment                        | Duration | Notes                                      |
|--------------------------------|----------|--------------------------------------------|
| Introduction & framing         | 5 min    | Why we care; course context                |
| Why evaluate RAG?              | 10 min   | Failure modes, the "vibes" trap            |
| Four core metrics overview     | 20 min   | One slide + code example per metric        |
| RAGAS framework quickstart     | 15 min   | Live demo: `02_ragas_quickstart.py`        |
| Diagnostic reading & wrap-up   | 10 min   | Interpreting scores, next steps            |

---

## Files

| File                       | Description                                                                 |
|----------------------------|-----------------------------------------------------------------------------|
| `slides.md`                | Marp slide source — 35 slides covering all segments above                  |
| `01_basic_rag_eval.py`     | Pure-Python manual metric calculation; no API key required for the logic    |
| `02_ragas_quickstart.py`   | RAGAS pipeline with DeepSeek judge LLM; requires `.env` with API key        |
| `talk-deck/`               | Exported HTML/PDF slides ready for presentation without VS Code              |

---

## How to Run the Demos

```bash
# Make sure you are in the lesson directory
cd lesson1_rag_evaluation

# Activate the virtual environment (from repo root)
source ../.venv/bin/activate

# Demo 1 — manual metrics (self-contained, prints results to stdout)
python 01_basic_rag_eval.py

# Demo 2 — RAGAS quickstart (requires OPENAI_API_KEY in ../.env)
python 02_ragas_quickstart.py
```

Expected output for Demo 2:

```
Evaluating... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:12
{'context_precision': 0.82, 'context_recall': 0.74,
 'faithfulness': 0.91, 'answer_relevancy': 0.88}
```

---

## Common Pitfalls

| Pitfall                              | What Happens                                     | Fix                                                    |
|--------------------------------------|--------------------------------------------------|--------------------------------------------------------|
| No reference answers in dataset      | RAGAS raises `KeyError: 'ground_truth'`          | Always include a `ground_truth` column in your dataset |
| Using the same LLM as judge and gen  | Self-evaluation bias inflates faithfulness       | Use a separate judge model or provider                 |
| Evaluating on the training corpus    | Metrics look great, real users complain          | Hold out an evaluation set before ingesting docs       |
| Ignoring per-question scores         | Aggregate scores hide individual failures        | Always inspect the per-row DataFrame, not just means   |
| Short retrieved chunks               | Context Recall collapses even with good retriever| Tune chunk size and overlap before evaluating          |
