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

Uploads a FASTQ file and executes the pipeline stages sequentially:

1. Upload FASTQ file
2. Run preprocessing
3. Run QC analysis
4. Run model analytics
5. Generate analysis report
6. Send report to chatbot interface
7. Return response JSON

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

## Example cURL request

```bash
curl -X POST "http://127.0.0.1:8000/analyze-fastq" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/sample.fastq.gz"
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
