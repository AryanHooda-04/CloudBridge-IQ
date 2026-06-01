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
AUTH_SECRET_KEY=replace_with_a_random_session_secret
AUTH_ADMIN_IDENTITIES=aryan,aryan.a,aryan hooda,aryanhooda-04,aryanhooda04
AUTH_ARCHITECT_IDENTITIES=aryan,aryan.a,aryan hooda,aryanhooda-04,aryanhooda04
AUTH_ADMIN_PASSWORD=
AUTH_DEFAULT_ROLE=reviewer
AUTH_SESSION_HOURS=8
```

`SSL_OPENAI=insecure` disables TLS certificate verification for OpenAI calls. Use it only in environments that require it, such as corporate SSL interception setups.

Without an API key, the application still runs and uses deterministic fallback detection for local development, but image-only diagrams will have low-confidence results.

`AUTH_ADMIN_IDENTITIES` and `AUTH_ARCHITECT_IDENTITIES` control who receives elevated access. By default, Aryan identities are assigned admin and architect capabilities. Other signed-in users are constrained to reviewer or viewer access.

## Run

```bash
uvicorn app.main:app --reload
```

Open the browser UI at `http://127.0.0.1:8000`.

Open the generated API docs at `http://127.0.0.1:8000/docs`.

## Deploy Free On Render

This project is ready to deploy on Render as a Docker Web Service. The included `Dockerfile` installs Python dependencies plus Graphviz and Poppler system packages for diagram rendering and PDF image conversion.

### 1. Push The Repo To GitHub

Commit and push the latest project files to GitHub. Do not commit `.env`.

### 2. Create A Render Web Service

In Render:

```text
New -> Web Service -> Connect GitHub repository
```

Recommended settings:

```text
Name: cloudbridge-iq
Runtime: Docker
Branch: main
Root Directory: cloud_migration_agent
Instance Type: Free
Health Check Path: /health
```

If your GitHub repository root is already this `cloud_migration_agent` folder, leave **Root Directory** empty.

### 3. Add Render Environment Variables

Add these in the Render service dashboard:

```env
OPENAI_API_KEY=your_openai_api_key
MODEL_NAME=gpt-4.1
VISION_MODEL_NAME=gpt-4.1
SSL_OPENAI=insecure
AUTH_ADMIN_PASSWORD=your_admin_password
AUTH_SECRET_KEY=generate_a_long_random_value
AUTH_DEFAULT_ROLE=reviewer
AUTH_SESSION_HOURS=8
```

`SSL_OPENAI=insecure` is included because this project is expected to run behind an environment that requires TLS verification bypass for OpenAI calls.

### 4. Deploy

Click:

```text
Manual Deploy -> Deploy latest commit
```

After deployment, open:

```text
https://<your-render-service>.onrender.com
```

Render free services can sleep after inactivity, so the first request after idle may take longer.

### Optional Blueprint Deploy

The included `render.yaml` can also be used as a Render Blueprint. It defines a free Docker web service, health check path, and required secret placeholders.

### Local Docker Smoke Test

You can test the container locally before pushing:

```bash
docker build -t cloudbridge-iq .
docker run --rm -p 10000:10000 --env-file .env cloudbridge-iq
```

Then open `http://127.0.0.1:10000`.

## Web UI

The app includes a local UI for testing and using the migration agent:

- Upload an image or PDF architecture diagram.
- Sign in with local RBAC. Aryan receives admin and architect access; other users enter as reviewer or viewer.
- Set source and target providers.
- Add migration intent and comma-separated goals.
- Run the assessment against `POST /analyze-migration`.
- Review the generated report, architecture diagram, service mappings, risks, costs, and decision gate.
- Copy the report or download PDF, Markdown, and rendered target diagram PNG output.

## Auth And RBAC

The local development build includes signed HTTP-only session cookies and role-based API protection.

Roles:

- `admin`: full access, including architect review, approval, assessment execution, exports, and admin capabilities.
- `architect`: full assessment and architect review access, excluding admin-only ownership.
- `reviewer`: can run assessments, save local review state, comment, ask the agent, and export.
- `viewer`: read-only access to available assessment views and exports.

Protected APIs:

- `POST /analyze-migration` and `POST /rebuild-assessment` require `can_assess`.
- `POST /download-report-pdf`, `POST /download-aws-diagram`, and `POST /ask-migration-agent` require `can_view`.

Login endpoints:

- `POST /auth/login`
- `GET /auth/me`
- `POST /auth/logout`

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
  -b cookies.txt \
  -F "file=@azure-architecture.png" \
  -F "source_provider=azure" \
  -F "target_provider=aws" \
  -F "migration_intent=We are migrating this from Azure to AWS." \
  -F "goals=reduce operations,modernize application hosting,improve disaster recovery"
```

Authenticate first when calling protected APIs directly:

```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d "{\"display_name\":\"Aryan\",\"email\":\"aryan.a\",\"requested_role\":\"reviewer\"}"
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
  -b cookies.txt \
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
- `diagrams`
- `graphviz`
- `pdf2image`

Recommended next improvement packages:

- `opencv-python` for image cleanup, thresholding, resizing, and preprocessing before vision analysis.
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
- Auth is local signed-cookie RBAC for development. Production deployments should replace the local login with enterprise SSO such as Microsoft Entra ID, Okta, or another OIDC provider.

## Future Improvements

- Improve PDF page rasterization controls and multi-page vision analysis.
- Add image preprocessing with OpenCV if diagrams need resizing, denoising, or contrast cleanup before vision analysis.
- Expand YAML mappings for more managed services, edge cases, and multi-cloud patterns.
- Add optional image-based AWS diagram generation with `diagrams` and Graphviz.
- Integrate cost modeling, migration wave planning, and dependency graph analysis.
- Replace local RBAC with SSO-backed users, groups, audit events, and server-side assessment storage.
- Add authentication, request persistence, background jobs, and report export formats.
