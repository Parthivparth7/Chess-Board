# ML Chess Arena

A responsive, good-looking browser chess game where you play White against a black AI opponent that uses a lightweight machine-learned style evaluation plus minimax with alpha-beta pruning.

## Run

Open `index.html` directly in your browser, or serve with a static server:

```bash
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

## FASTQ RAG Analytics Extension

A blueprint for evolving this project toward a genomics assistant (FASTQ understanding + RAG + analytics reporting) is available in:

- `FASTQ_RAG_ANALYTICS_PLAN.md`


## Genomics FastAPI Backend

A FastAPI orchestration backend is available under `genomics_ai_system/` with endpoint:

- `POST /analyze-fastq`

### Install

```bash
pip install -r requirements.txt
```

### Run

```bash
uvicorn genomics_ai_system.app:app --host 0.0.0.0 --port 8000 --reload
```

### Example cURL request

```bash
curl -X POST "http://127.0.0.1:8000/analyze-fastq" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/sample.fastq.gz"
```

Expected response schema:

```json
{
  "qc_metrics": {},
  "model_results": {},
  "analysis_summary": "",
  "chatbot_response": ""
}
```
