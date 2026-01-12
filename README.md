# BentoML Admission Prediction Service

A machine learning API service that predicts university admission chances using BentoML.

## Project Status

| Component | Status |
|-----------|--------|
| Data Pipeline | Complete |
| Model Training | Complete (R²: 0.82) |
| JWT Authentication | Complete |
| BentoML Service | Complete |
| Docker Container | Complete |
| Unit Tests | 9/9 Passing |

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

Run the containerized API service:

```bash
docker run --rm -p 3000:3000 christianm_admission_service:latest
```

**Note:** Keep this terminal window open as the API will be running. Open a new terminal for the next step.

### Step 4: Run Unit Tests

In a new terminal window, install test dependencies and run the pytest tests:

```bash
# Install required test dependencies
pip install pytest requests pyjwt python-dotenv

# Run all tests with verbose output
pytest tests/test_api.py -v
```

**Expected Result:** All 9 tests must return **PASSED** status. The test suite includes:
- JWT authentication tests (4 tests)
- Login API tests (2 tests)
- Prediction API tests (3 tests)

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Client    │───▶│  BentoML Service │───▶│ Linear Regression│
│  (HTTP)     │     │  (JWT Protected) │     │     Model        │
└─────────────┘     └──────────────────┘     └──────────────────┘
                           │
                    ┌──────┴──────┐
                    │             │
                  /login        /predict
                 (public)      (protected)
```

## Project Structure

```
.
├── data/
│   ├── raw/admission.csv
│   └── processed/
├── src/
│   ├── auth/jwt_auth.py      # JWT middleware
│   ├── prepare_data.py       # Data preprocessing
│   ├── train_model.py        # Model training
│   └── service.py            # BentoML service
├── tests/test_api.py         # Unit tests
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
bentoml build
bentoml containerize admission_service:latest -t christianm_admission_service:latest
```

### Export Docker Image

```bash
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
