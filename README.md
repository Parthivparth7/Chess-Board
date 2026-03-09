# Genomics AI System

A FastAPI backend for **genetic data science workflows** that orchestrates FASTQ processing and analytics pipelines, then returns structured outputs suitable for reporting and chatbot delivery.

## Project Focus

This repository is now documented as a **pure genomics project**:

- FASTQ upload and orchestration
- Preprocessing and QC stage execution
- Model analytics stage execution
- Analysis report generation
- Chatbot response delivery

## API

### `POST /analyze-fastq`

Uploads a local FASTQ file and executes the pipeline stages sequentially:

1. Upload FASTQ file
2. Run preprocessing
3. Run QC analysis
4. Run model analytics
5. Generate analysis report
6. Send report to chatbot interface
7. Return response JSON


### `POST /analyze-fastq-url`

Fetches a FASTQ file from a direct HTTP/HTTPS URL (public source), then runs the same pipeline.

Request body:

```json
{
  "fastq_url": "https://.../sample.fastq.gz",
  "filename": "sample.fastq.gz"
}
```

### `POST /analyze-fastq-ena`

Fetches a real FASTQ dataset from the **ENA authentic public database** using run accession metadata, then runs the same pipeline.

Request body:

```json
{
  "run_accession": "SRR390728"
}
```

### Response format

```json
{
  "qc_metrics": {},
  "model_results": {},
  "analysis_summary": "",
  "chatbot_response": ""
}
```

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
uvicorn genomics_ai_system.app:app --host 0.0.0.0 --port 8000 --reload
```


## Example cURL requests

### 1) Upload local FASTQ

```bash
curl -X POST "http://127.0.0.1:8000/analyze-fastq" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/sample.fastq.gz"
```

### 2) Analyze by direct FASTQ URL

```bash
curl -X POST "http://127.0.0.1:8000/analyze-fastq-url" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"fastq_url":"https://example.org/sample.fastq.gz"}'
```

### 3) Analyze from ENA run accession (authentic database)

```bash
curl -X POST "http://127.0.0.1:8000/analyze-fastq-ena" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"run_accession":"SRR390728"}'
```

## Code structure

```text
genomics_ai_system/
  app.py
  pipeline/
    preprocessing.py
    model_building.py
    report_generation.py
    analysis_report.py
  rag/
    vector_store.py
    retriever.py
  chatbot/
    chatbot_engine.py
    chatbot_interface.py
  routers/
    api_router.py
  services/
    pipeline_service.py
```

## Notes

- Existing domain modules are orchestrated without modifying their internal logic.
- Stage execution time is logged for each pipeline step.


## Built-in default analytics (works immediately)

This repository now includes default implementations for:

- `run_preprocessing`
- `run_qc_analysis`
- `run_model_analytics`
- `generate_analysis_report`
- `send_to_chatbot`

So your API can return analysis JSON immediately, even before plugging in advanced external modules.

To test quickly, send any small FASTQ file to `/analyze-fastq` or use ENA accession endpoint `/analyze-fastq-ena`.
