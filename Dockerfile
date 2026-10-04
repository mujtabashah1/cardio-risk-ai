FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 API_HOST=0.0.0.0 API_PORT=8000 LOG_LEVEL=INFO
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*
COPY requirements-api.txt ./
RUN python -m pip install --no-cache-dir -r requirements-api.txt
COPY api/ ./api/
COPY src/__init__.py ./src/__init__.py
COPY src/inference/ ./src/inference/
COPY src/models/__init__.py src/models/config.py src/models/estimators.py src/models/preprocessing.py ./src/models/
COPY src/data/__init__.py src/data/mappings.py ./src/data/
COPY models/heart_disease_pipeline.joblib models/feature_schema.json models/model_metadata.json models/model_version.txt models/threshold_profiles.json ./models/
COPY data/processed/data_dictionary.csv ./data/processed/data_dictionary.csv
COPY reports/deployment/model_integrity.json ./reports/deployment/model_integrity.json
COPY tests/fixtures/golden_predictions.json ./tests/fixtures/golden_predictions.json
RUN useradd --create-home --uid 10001 appuser
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/ready', timeout=3)"
CMD ["python", "-m", "api"]
