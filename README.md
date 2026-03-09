# DNA Sequence Analysis AI System

Production-ready **Agentic Genomic AI Platform** for FASTQ ingestion, QC, feature extraction, ML prediction, RAG retrieval, report generation, and chatbot explanation.

## Project Name
**DNA Sequence Analysis AI Backend**

## Key Capabilities
- FASTQ genomic data ingestion
- Sequence preprocessing and quality control
- Feature extraction (k-mer + nucleotide distribution)
- ML prediction and risk scoring
- Analysis report generation
- RAG retrieval over genomic knowledge base
- Multi-agent chatbot explanation
- FastAPI endpoints for analysis and chat

## Agentic Pipeline
Data Agent → QC Agent → Feature Agent → ML Agent → Report Agent → Knowledge Retrieval Agent → Chatbot Agent

## New Modular Architecture

```text
agentic_genomic_ai/
  app/
    main.py
  routers/
    genomics_router.py
    chat_router.py
  agents/
    data_ingestion_agent.py
    qc_agent.py
    feature_extraction_agent.py
    ml_prediction_agent.py
    report_generation_agent.py
    rag_retrieval_agent.py
    chatbot_agent.py
  pipeline/
    pipeline_orchestrator.py
  rag/
    vector_store.py
    document_loader.py
    retriever.py
  schemas/
    request_schema.py
    response_schema.py
  utils/
    fastq_parser.py
    sequence_utils.py
    logging_utils.py
  data/
    knowledge_base/
  models/
    trained_models/
  reports/
app/
  main.py
```

## Backward Compatibility
Existing `genomics_ai_system/` modules are preserved. The new platform is added alongside previous code and can coexist.

## Install
```bash
pip install -r requirements.txt
```

## Run (required)
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### 1) FASTQ analysis
`POST /genomics/analyze_fastq`

Response example:
```json
{
  "qc_metrics": {},
  "model_prediction": {},
  "analysis_summary": "",
  "chatbot_explanation": ""
}
```

### 2) Chat over genomic results
`POST /chat/genomics`

Request:
```json
{
  "question": "Explain mutation risk",
  "analysis_summary": "Optional summary"
}
```

Response:
```json
{
  "answer": "AI generated explanation with literature support"
}
```

## Example Commands

### Analyze FASTQ
```bash
curl -X POST "http://127.0.0.1:8000/genomics/analyze_fastq" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_data/demo_reads.fastq"
```

### Ask genomic chat question
```bash
curl -X POST "http://127.0.0.1:8000/chat/genomics" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"question":"Explain mutation risk"}'
```

## Local Pipeline Script
```bash
python scripts/run_local_pipeline.py
```

## Testing
```bash
python -m pytest -q tests/test_pipeline_example.py
```
