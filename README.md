# DNA Sequence Analysis AI System

Production-ready **Agentic Genomic AI Platform** for FASTQ ingestion, QC, feature extraction, genomic ML prediction, variant risk analysis, report generation, RAG retrieval, and chatbot explanation.

## Project Name
**DNA Sequence Analysis AI Backend**

## Agentic Pipeline
Data Ingestion Agent → QC Analysis Agent → Feature Extraction Agent → ML Prediction Agent → Genomic Variant Agent → Report Generation Agent → Knowledge Retrieval Agent → Chatbot Explanation Agent

## Modular Architecture

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
    variant_analysis_agent.py
    report_generation_agent.py
    rag_retrieval_agent.py
    chatbot_agent.py
  pipeline/
    pipeline_orchestrator.py
  models/
    trained_models/
    splice_detection_model.py
    cancer_expression_model.py
    variant_risk_model.py
    tf_binding_model.py
    gene_network_gnn.py
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
  reports/
app/
  main.py
```

## Backward Compatibility
Existing `genomics_ai_system/` modules and routes remain in the repository. The new `agentic_genomic_ai/` stack is additive.

## Install
```bash
pip install -r requirements.txt
```

## Run
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### POST `/genomics/analyze_fastq`
Upload FASTQ and execute the full agentic pipeline.

Response example:
```json
{
  "qc_metrics": {},
  "model_predictions": {},
  "variant_risk": {},
  "analysis_summary": "",
  "chatbot_explanation": ""
}
```

### POST `/chat/genomics`
Ask genomic questions backed by retrieved knowledge context.

Request:
```json
{
  "question": "Explain variant pathogenicity",
  "analysis_summary": "Optional summary"
}
```

Response:
```json
{
  "answer": "AI explanation supported by genomic literature"
}
```

## Example Commands

```bash
curl -X POST "http://127.0.0.1:8000/genomics/analyze_fastq" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_data/demo_reads.fastq"
```

```bash
curl -X POST "http://127.0.0.1:8000/chat/genomics" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"question":"Explain mutation risk"}'
```

## Local Validation
```bash
python scripts/run_local_pipeline.py
python -m pytest -q tests/test_pipeline_example.py
```
