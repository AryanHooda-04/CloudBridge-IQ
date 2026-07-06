FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    SSL_OPENAI=insecure \
    PORT=10000

WORKDIR /app

# graphviz powers the optional diagrams renderer; poppler enables PDF page
# conversion for image-only architecture PDFs.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        graphviz \
        poppler-utils \
        fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

COPY app ./app
COPY samples/architecture_diagrams ./samples/architecture_diagrams

EXPOSE 10000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
