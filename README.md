# Cloud Migration Assessment Agent

Production-oriented Python starter project for an AI-powered cloud migration assessment agent. The API accepts an architecture diagram, infers source cloud services, maps them to target cloud services, proposes a target architecture for AWS, Azure, or Google Cloud, renders Mermaid output, and returns a structured migration assessment report.

Primary example: upload an Azure architecture diagram and set `migration_intent` to `We are migrating this from Azure to AWS.`

## Stack

- FastAPI backend API
- LangGraph workflow orchestration
- LangChain and `langchain-openai` model integration
- Pydantic structured data models
- OpenAI vision-capable model for diagram understanding
- Mermaid architecture diagram output
- PDF export using ReportLab
- YAML-based service equivalence mappings
- Pytest coverage for mapping, Mermaid, and report generation

Optional image-based diagram rendering can use `diagrams` and Graphviz.

## Setup

```bash
cd cloud_migration_agent
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS/Linux, activate with:

```bash
source .venv/bin/activate
```

## Environment

Copy the example environment file and set your OpenAI key:

```bash
cp .env.example .env
```

```env
OPENAI_API_KEY=your_api_key_here
MODEL_NAME=gpt-4.1
VISION_MODEL_NAME=gpt-4.1
SSL_OPENAI=insecure
POPPLER_PATH=C:\Tools\poppler\poppler-26.02.0\Library\bin
GRAPHVIZ_DOT=C:\Tools\Graphviz-15.0.0-win64\bin\dot.exe
```

`SSL_OPENAI=insecure` disables TLS certificate verification for OpenAI calls. Use it only in environments that require it, such as corporate SSL interception setups.

Without an API key, the application still runs and uses deterministic fallback detection for local development, but image-only diagrams will have low-confidence results.

## Run

```bash
uvicorn app.main:app --reload
```

Open the browser UI at `http://127.0.0.1:8000`.

Open the generated API docs at `http://127.0.0.1:8000/docs`.

## Web UI

The app includes a local UI for testing and using the migration agent:

- Upload an image or PDF architecture diagram.
- Set source and target providers.
- Add migration intent and comma-separated goals.
- Run the assessment against `POST /analyze-migration`.
- Review the generated report, Mermaid diagram, service mappings, and raw JSON.
- Copy the report or download PDF, Markdown, JSON, and rendered target diagram PNG output.

## API

### `POST /analyze-migration`

Form fields:

- `file`: uploaded image or PDF architecture diagram
- `source_provider`: optional, default `auto`
- `target_provider`: optional, default `aws`
- `migration_intent`: optional text
- `goals`: optional comma-separated text

Example:

```bash
curl -X POST "http://127.0.0.1:8000/analyze-migration" \
  -F "file=@azure-architecture.png" \
  -F "source_provider=azure" \
  -F "target_provider=aws" \
  -F "migration_intent=We are migrating this from Azure to AWS." \
  -F "goals=reduce operations,modernize application hosting,improve disaster recovery"
```

Example response shape:

```json
{
  "markdown_report": "# Migration Assessment Snapshot\n...",
  "mermaid_diagram": "graph TD\n    Users[\"Users\"] --> ...",
  "source_architecture": {
    "provider": "azure",
    "summary": "Detected Azure application architecture...",
    "components": [],
    "relationships": [],
    "assumptions": [],
    "missing_information": []
  },
  "target_architecture": {
    "provider": "aws",
    "summary": "Proposed AWS architecture...",
    "components": [],
    "relationships": [],
    "design_notes": []
  },
  "service_mappings": [],
  "final_verdict": {
    "recommendation": "conditionally_recommended",
    "reasoning": "The migration is feasible, but should proceed after validation...",
    "confidence": 0.78
  }
}
```

### `POST /download-report-pdf`

Converts the current Markdown assessment into a PDF download.

```bash
curl -X POST "http://127.0.0.1:8000/download-report-pdf" \
  -H "Content-Type: application/json" \
  -d "{\"filename\":\"migration-assessment.pdf\",\"markdown_report\":\"# Migration Assessment Snapshot\"}" \
  --output migration-assessment.pdf
```

### `POST /download-aws-diagram`

Converts the proposed target architecture into a PNG. AWS targets use the optional `diagrams` and Graphviz renderer where available; Azure and Google Cloud targets use the clean provider-neutral Pillow renderer.
If the Graphviz `dot` executable is not available on PATH, AWS diagrams also fall back to the Pillow-rendered PNG.

## Packages to Install for the Improved App

Install the project requirements first:

```bash
pip install -r requirements.txt
```

Core packages already used by the app:

- `fastapi`
- `uvicorn`
- `python-multipart`
- `python-dotenv`
- `pydantic`
- `langchain`
- `langchain-openai`
- `langgraph`
- `pillow`
- `pypdf`
- `pyyaml`
- `networkx`
- `jinja2`
- `reportlab`
- `pytest`

Recommended next improvement packages:

- `pdf2image` for converting PDF architecture pages to images before vision analysis.
- `opencv-python` for image cleanup, thresholding, resizing, and preprocessing before vision analysis.
- `diagrams` and `graphviz` for image-based AWS architecture diagrams. Install the Graphviz system executable too if you want official AWS icon rendering rather than the built-in Pillow fallback.
- `httpx` for richer API and integration tests.
- `pytest-asyncio` for async workflow tests.

Recommended system tools:

- Poppler, commonly required by `pdf2image`.
- Graphviz, required for the `diagrams` package to render architecture images.

## Workflow

The LangGraph workflow uses these nodes:

1. `ingest_diagram`
2. `detect_source_architecture`
3. `map_services`
4. `generate_target_architecture`
5. `generate_mermaid_diagram`
6. `generate_migration_strategy`
7. `generate_report`
8. `generate_final_verdict`

## Tests

```bash
pytest
```

## Known Limitations

- Diagram vision quality depends on the configured OpenAI vision-capable model and input image clarity.
- PDF ingestion extracts embedded text and can render sparse PDFs to images for OpenAI vision analysis when Poppler is available.
- Local text extraction from images is intentionally not included; image understanding is handled by the configured OpenAI vision model.
- Cost estimates are qualitative. Production use should integrate measured utilization and pricing APIs.
- Service mappings now cover common Azure, AWS, and Google Cloud directions, but each mapping still needs architect validation for production workloads.
- The AWS architecture generator uses opinionated production defaults; Azure and Google Cloud targets use provider-native generic foundations that should be adapted to organizational landing zone standards.

## Future Improvements

- Improve PDF page rasterization controls and multi-page vision analysis.
- Add image preprocessing with OpenCV if diagrams need resizing, denoising, or contrast cleanup before vision analysis.
- Expand YAML mappings for more managed services, edge cases, and multi-cloud patterns.
- Add optional image-based AWS diagram generation with `diagrams` and Graphviz.
- Integrate cost modeling, migration wave planning, and dependency graph analysis.
- Add authentication, request persistence, background jobs, and report export formats.
