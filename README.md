# BentoML Admission Prediction Service

A machine learning API service that predicts university admission chances using BentoML.

## Project Status

| Component | Status |
|-----------|--------|
| Data Pipeline | Complete |
| Model Training | Complete (R²: 0.82) |
| JWT Authentication | Complete |
| BentoML Service | Complete |
| Batch Processing | Complete |
| Docker Container | Complete |
| Unit Tests | 20+ Passing |

## Workflow

This section describes the complete workflow required to decompress, load, and test the containerized API. **All tests must return PASSED status.**

### Step 1: Decompress the Archive

If the project is delivered as a compressed archive (zip or tar), decompress it first:

```bash
unzip exam_MEISTER.zip
```

### Step 2: Load Docker Image

Load the BentoML Docker image into your local Docker registry:

```bash
docker load -i bento_image.tar
```

### Step 3: Launch Containerized API

**Option A: Using Docker Compose (Recommended)**

```bash
docker-compose up
```

**Option B: Using Docker directly**

```bash
docker run --rm -p 3000:3000 christianm_admission_service:latest
```

**Note:** Keep this terminal window open as the API will be running. Open a new terminal for the next step.

#### Docker Compose Configuration

The `docker-compose.yml` file includes:
- Port mapping: `3000:3000`
- Environment variables from `.env` file
- Healthcheck endpoint: `/healthz`
- Automatic restart policy

To customize environment variables, create a `.env` file or modify `docker-compose.yml`.

### Step 4: Run Unit Tests

In a new terminal window, install test dependencies and run the pytest tests:

```bash
# Install required test dependencies
pip install pytest requests pyjwt python-dotenv

# Run all tests with verbose output
pytest tests/test_endpoints.py -v
```

**Expected Result:** All tests must return **PASSED** status. The test suite includes:
- JWT authentication tests (4 tests)
- Login API tests (2 tests)
- Single prediction API tests (3 tests)
- Batch submission tests (5 tests)
- Batch status tests (3 tests)
- Batch results tests (5 tests)
- Batch workflow tests (1 test)

## Architecture

```
                    ┌─────────────┐
                    │   Client    │
                    │   (HTTP)    │
                    └──────┬──────┘
                           │
                    ┌──────▼──────────────────┐
                    │   BentoML Service       │
                    │   (JWT Protected)       │
                    └──────┬──────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌─────▼─────┐      ┌─────▼──────────┐
   │ /login  │       │ /predict  │      │  Batch API     │
   │ (POST)  │       │  (POST)   │      │  (FastAPI)     │
   │(public) │       │(protected)│      │(protected)     │
   └─────────┘       └─────┬─────┘      └─────┬──────────┘
                            │                  │
                     ┌──────▼──────┐    ┌──────┼──────────────┐
                     │  Runner 1   │    │      │              │
                     │  (Single)  │    │  ┌───▼────────┐    │
                     │             │    │  │/batch/     │    │
                     │max_batch=1  │    │  │  submit    │    │
                     │max_lat=100ms│    │  │  (POST)    │    │
                     └─────────────┘    │  └────────────┘    │
                                        │                    │
                                        │  ┌──────────────┐ │
                                        │  │/batch/status/│ │
                                        │  │  {job_id}    │ │
                                        │  │  (GET)       │ │
                                        │  └──────────────┘ │
                                        │                    │
                                        │  ┌──────────────┐ │
                                        │  │/batch/results/│ │
                                        │  │  {job_id}    │ │
                                        │  │  (GET)       │ │
                                        │  └──────┬───────┘ │
                                        │         │         │
                                        │  ┌──────▼───────┐ │
                                        │  │   Runner 2   │ │
                                        │  │    (Batch)   │ │
                                        │  │              │ │
                                        │  │max_batch=100 │ │
                                        │  │max_lat=1000ms│ │
                                        │  └──────────────┘ │
                                        └────────────────────┘
```

### Dual-Runner Architecture

The service uses two dedicated runners optimized for different use cases:

- **Runner 1 (Single)**: Optimized for low-latency single predictions
  - `max_batch_size=1` - Processes requests immediately
  - `max_latency_ms=100` - Fast response time
  
- **Runner 2 (Batch)**: Optimized for high-throughput batch processing
  - `max_batch_size=100` - Batches multiple requests
  - `max_latency_ms=1000` - Allows batching window for efficiency

## Project Structure

```
.
├── data/
│   ├── raw/admission.csv
│   └── processed/
├── src/
│   ├── auth/jwt_auth.py      # JWT middleware
│   ├── models/
│   │   ├── __init__.py       # Models package
│   │   └── input_model.py    # Pydantic models
│   ├── prepare_data.py       # Data preprocessing
│   ├── train_model.py        # Model training
│   └── service_batch.py      # BentoML service with batch support
├── tests/test_endpoints.py   # Comprehensive test suite
├── docker-compose.yml        # Docker Compose configuration
├── bentofile.yaml            # BentoML config
├── Dockerfile.template       # Custom Docker template
└── bento_image.tar           # Exported Docker image
```



## API Endpoints

### POST /login
Authenticate and receive JWT token.

```bash
curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"secret123"}'
```

Response:
```json
{"token": "eyJhbGciOiJIUzI1NiIs..."}
```

### POST /predict
Get admission prediction (requires JWT).

```bash
curl -X POST http://localhost:3000/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "gre_score": 337,
    "toefl_score": 118,
    "university_rating": 4,
    "sop": 4.5,
    "lor": 4.5,
    "cgpa": 9.65,
    "research": 1
  }'
```

Response:
```json
{"chance_of_admit": 0.958}
```

### POST /batch/submit
Submit a batch prediction job (requires JWT).

```bash
curl -X POST http://localhost:3000/batch/submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "inputs": [
      {
        "gre_score": 337,
        "toefl_score": 118,
        "university_rating": 4,
        "sop": 4.5,
        "lor": 4.5,
        "cgpa": 9.65,
        "research": 1
      },
      {
        "gre_score": 320,
        "toefl_score": 110,
        "university_rating": 3,
        "sop": 3.5,
        "lor": 3.0,
        "cgpa": 8.5,
        "research": 0
      }
    ]
  }'
```

Response:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Batch job submitted successfully"
}
```

### GET /batch/status/{job_id}
Check the status of a batch prediction job (requires JWT).

```bash
curl -X GET http://localhost:3000/batch/status/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer <token>"
```

Response:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed"
}
```

Status values: `pending`, `processing`, `completed`, `failed`

### GET /batch/results/{job_id}
Retrieve batch prediction results (requires JWT).

```bash
curl -X GET http://localhost:3000/batch/results/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer <token>"
```

Response (when completed):
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "results": [
    {"chance_of_admit": 0.958},
    {"chance_of_admit": 0.782}
  ],
  "total": 2
}
```

Response (when still processing):
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "Job is still processing"
}
```
Status code: `202 Accepted`

## Batch Workflow

The batch prediction workflow follows an asynchronous pattern:

1. **Submit Job**: POST to `/batch/submit` with a list of inputs
   - Returns immediately with a `job_id`
   - Job status is `pending`

2. **Poll Status**: GET `/batch/status/{job_id}` to check progress
   - Status transitions: `pending` → `processing` → `completed`
   - Poll until status is `completed` (or `failed`)

3. **Retrieve Results**: GET `/batch/results/{job_id}` when completed
   - Returns all predictions if `completed`
   - Returns `202 Accepted` if still processing

### Example Python Workflow

```python
import requests
import time

BASE_URL = "http://localhost:3000"
token = "your_jwt_token"
headers = {"Authorization": f"Bearer {token}"}

# Step 1: Submit batch job
batch_data = {
    "inputs": [
        {"gre_score": 337, "toefl_score": 118, "university_rating": 4,
         "sop": 4.5, "lor": 4.5, "cgpa": 9.65, "research": 1},
        {"gre_score": 320, "toefl_score": 110, "university_rating": 3,
         "sop": 3.5, "lor": 3.0, "cgpa": 8.5, "research": 0}
    ]
}

response = requests.post(f"{BASE_URL}/batch/submit", json=batch_data, headers=headers)
job_id = response.json()["job_id"]

# Step 2: Poll status until completed
max_attempts = 30
for attempt in range(max_attempts):
    status_response = requests.get(f"{BASE_URL}/batch/status/{job_id}", headers=headers)
    status_data = status_response.json()
    
    if status_data["status"] == "completed":
        break
    elif status_data["status"] == "failed":
        raise Exception(f"Job failed: {status_data}")
    
    time.sleep(1)

# Step 3: Retrieve results
results_response = requests.get(f"{BASE_URL}/batch/results/{job_id}", headers=headers)
results = results_response.json()
print(f"Received {results['total']} predictions")
```

### Batch Limits

- Maximum batch size: **1000 records**
- Empty batches are rejected
- Large batches (>1000) return `400 Bad Request`

## Model Performance

| Metric | Value |
|--------|-------|
| R² Score | 0.8188 |
| RMSE | 0.0609 |
| MAE | 0.0427 |

## Development

### Setup Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Download Dataset

```bash
curl -o data/raw/admission.csv https://assets-datascientest.s3.eu-west-1.amazonaws.com/MLOPS/bentoml/admission.csv
```

### Configure Environment

Create `.env` file:
```
JWT_SECRET_KEY=bentoml_exam_secret_key_2024
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
API_USERNAME=admin
API_PASSWORD=secret123
```

### Prepare Data & Train Model

```bash
python src/prepare_data.py
python src/train_model.py
```

### Build & Containerize

```bash
# Build the Bento
bentoml build

# Containerize the Bento
bentoml containerize admission_service:latest -t admission_service:latest

# Or use the custom tag
bentoml containerize admission_service:latest -t christianm_admission_service:latest
```

### Docker Compose Deployment

```bash
# Start the service
docker-compose up

# Start in detached mode
docker-compose up -d

# Stop the service
docker-compose down

# View logs
docker-compose logs -f
```

### Export Docker Image

```bash
docker save -o bento_image.tar admission_service:latest
# Or
docker save -o bento_image.tar christianm_admission_service:latest
```

### Deploy to BentoCloud

```bash
# Login to BentoCloud (first time only)
bentoml cloud login

# Push the bento
bentoml push admission_service:latest

# Deploy
bentoml deploy admission_service:latest -n admission-service
```

## Input Features

| Feature | Description | Range |
|---------|-------------|-------|
| gre_score | GRE test score | 0-340 |
| toefl_score | TOEFL test score | 0-120 |
| university_rating | University rating | 1-5 |
| sop | Statement of Purpose | 1-5 |
| lor | Letter of Recommendation | 1-5 |
| cgpa | Cumulative GPA | 0-10 |
| research | Research experience | 0 or 1 |

## Test Credentials

- Username: `admin`
- Password: `secret123`
