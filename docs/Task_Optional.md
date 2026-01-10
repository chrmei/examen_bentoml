# BentoML Challenge

## Part 2: Admission Prediction Service with BentoML 🚀

**Difficulty:** ⭐️⭐️⭐️⭐️⭐️ (Optional Part)

For the validation of your exam, you are not required to complete this part (you can ignore it to focus on the mandatory part). However, by choosing to complete it, you have the opportunity to implement a real-world production case.

> [!IMPORTANT]
> This challenge requires extra effort. You will need to research the **BentoML Documentation** to deepen your understanding of the library.

---

## 2.1 Project Context

A university wants to automate its admission process by deploying an ML model via an API. The model, trained in the previous part of the project, predicts a student's chances of admission based on various academic metrics.

---

## 2.2 Global Architecture

Below is the architecture you will implement:

```text
┌─────────────────┐      ┌──────────────┐      ┌─────────────┐
│   Client HTTP   │─────>│  API Service │─────>│  Runner 1   │
│    (Tests)      │      │   (BentoML)  │      │ (Single)    │
└─────────────────┘      │              │      └─────────────┘
                         │              │      ┌─────────────┐
                         │              │─────>│  Runner 2   │
                         │              │      │  (Batch)    │
                         └──────────────┘      └─────────────┘

```

### Advantages of this Architecture:

* **Separation of Responsibilities:** The HTTP client handles requests, the API Service handles routing, and Runners execute the processing.
* **Flexibility and Scalability:** Easily add new Runners or scale horizontally.
* **Resource Optimization:** Dedicated runners for single (latency-sensitive) vs. batch (throughput-sensitive) requests.
* **Isolation and Maintenance:** Components can be updated independently.
* **Performance:** Batch processing optimizes performance for large data volumes.

---

## 2.3 Project Structure

We recommend the following organization:

```text
project/
├── src/
│   ├── auth/
│   │   └── jwt_auth.py        # JWT authentication functions
│   ├── models/
│   │   └── input_model.py     # Pydantic validation models
│   └── service_batch.py       # Main BentoML service
├── tests/
│   └── test_endpoints.py      # Endpoint tests
├── bentofile.yml             # BentoML configuration
└── docker-compose.yml        # Docker configuration

```

---

## 2.4 Challenge Steps

### 1. Development Environment

Create a virtual environment and install the necessary dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install bentoml pandas scikit-learn pydantic pyjwt pytest requests

```

*Tip: Use a `requirements.txt` file to manage these dependencies.*

### 2. Data Models

Define your Pydantic models in `src/models/input_model.py`:

```python
from pydantic import BaseModel

class AdmissionInput(BaseModel):
    gre_core: int
    toefl_score: int
    university_rating: int
    sop: float
    lor: float
    cgpa: float
    research: int

# 🎯 Challenge: Complete this file with models for batch predictions!

```

### 3. JWT Authentication

Implement the logic in `src/auth/jwt_auth.py`:

```python
import jwt
from starlette.middleware.base import BaseHTTPMiddleware

JWT_SECRET_KEY = "your_secret_key"
JWT_ALGORITHM = "HS256"

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # 🔍 To implement:
        # 1. Check token in "Authorization" header
        # 2. Verify "Bearer <token>" format
        # 3. Handle errors (missing, invalid, or expired tokens)
        return await call_next(request)

```

### 4. Main Service

In `service_batch.py`, configure your runners and API endpoints:

```python
import bentoml
from bentoml.io import JSON
from src.models.input_model import AdmissionInput
from src.auth.jwt_auth import JWTAuthMiddleware

# Runners configuration
runner1 = bentoml.sklearn.get("admission_lr:latest").to_runner()
# ... [Add runner2 for batch with the same model]

# Service with authentication
svc = bentoml.Service("admission_service", runners=[runner1])
svc.add_middleware(JWTAuthMiddleware)

# Example endpoint
@svc.api(input=JSON(pydantic_model=AdmissionInput))
def predict(input_data):
    # To implement!
    pass

```

### 5. Deployment Configuration

#### `bentofile.yml`

```yaml
service: "src.service_batch:svc"
description: "Admission Prediction Service"
python:
  packages:
    - numpy
    - pandas
    - scikit-learn
    - pyjwt
    # Complete the list!

```

#### `docker-compose.yml`

```yaml
version: "3"
services:
  api:
    image: admission_service:latest
    ports:
      - "3000:3000"
    # 🔍 Hint: Consider API/runners separation and env variables.

```

---

## 2.5 Help and Resources

### Batch Workflow Logic

```text
┌──────────┐       ┌───────────┐      ┌──────────┐
│ Job      │──────>│  Status   │─────>│ Results  │
│Submission│       │"pending"  │      │          │
└──────────┘       └───────────┘      └──────────┘
     │                   ▲                  ▲
     │                   │                  │
     └───────────────────┴──────────────────┘
         Polling status until completion

```

### Evaluation Criteria

| Category | Criteria | Status |
| --- | --- | --- |
| **Functionality** | Operational service, Batch handling, JWT Auth | ✅ |
| **Code** | Clear structure, Error handling, Passing tests | ✅ |
| **Deployment** | `bentofile` config, Docker functional | ✅ |
| **Bonus** | Monitoring, Documentation, Additional tests | ⭐ |

---

## 2.6 Optional Part Deliverables

If you choose to complete this part, please provide an archive containing:

1. **README.md**: Detailed documentation with commands to build the Bento, build the Docker image, launch the architecture, and run tests.
2. **Project Files**:
* `mandatory_part/` ...
* `optional_part/`
* `src/` (auth, models, service)
* `tests/`
* `bentofile.yml`
* `docker-compose.yml`

🎉 **Congratulations on reaching the end of the challenge!** 🎉
