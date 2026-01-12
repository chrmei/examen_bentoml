"""BentoML service with dual runners for single and batch predictions."""

import bentoml
import numpy as np
import uuid
import threading
import time
from typing import Dict, List
from starlette.responses import JSONResponse
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.models.input_model import (
    AdmissionInput,
    BatchAdmissionInput,
    AdmissionOutput,
    BatchJobResponse,
    BatchStatusResponse,
    BatchResultsResponse,
    LoginRequest,
)
from src.auth.jwt_auth import JWTAuthMiddleware, create_token, validate_credentials, verify_token

# Thread-safe job storage (module-level)
jobs: Dict[str, Dict] = {}
jobs_lock = threading.Lock()

# Create FastAPI app for GET endpoints
fastapi_app = FastAPI()
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token from FastAPI dependency."""
    token = credentials.credentials
    try:
        payload = verify_token(token)
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def process_batch_job(service_instance, job_id: str, inputs: List[AdmissionInput]) -> None:
    """Process batch job asynchronously."""
    try:
        with jobs_lock:
            jobs[job_id]["status"] = "processing"
        
        # Convert inputs to numpy array (N x 7)
        features = np.array([
            [
                inp.gre_score,
                inp.toefl_score,
                inp.university_rating,
                inp.sop,
                inp.lor,
                inp.cgpa,
                inp.research
            ]
            for inp in inputs
        ])
        
        # Run batch prediction using batch model
        predictions = service_instance.batch_model.predict(features)
        
        # Convert predictions to output format
        results = [
            AdmissionOutput(chance_of_admit=float(pred))
            for pred in predictions
        ]
        
        # Store results
        with jobs_lock:
            jobs[job_id]["status"] = "completed"
            jobs[job_id]["results"] = results
            jobs[job_id]["completed_at"] = time.time()
    
    except Exception as e:
        # Handle errors
        with jobs_lock:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = str(e)
            jobs[job_id]["completed_at"] = time.time()


@bentoml.service(name="admission_service")
@bentoml.mount_asgi_app(fastapi_app)
class AdmissionService:
    """BentoML service with dual model instances for single and batch predictions."""
    
    # Model reference
    model_ref = bentoml.sklearn.get("admission_model:latest")
    
    def __init__(self):
        # Load model instances directly (compatible with production)
        # Using separate instances to simulate dual-runner architecture
        self.single_model = bentoml.sklearn.load_model(self.model_ref)
        self.batch_model = bentoml.sklearn.load_model(self.model_ref)
    
    @bentoml.api(route="/login")
    def login(self, username: str, password: str):
        """Authenticate and receive JWT token."""
        if validate_credentials(username, password):
            return {"token": create_token(username)}
        return JSONResponse({"error": "Invalid credentials"}, status_code=401)
    
    @bentoml.api(route="/predict")
    def predict(self, gre_score: float, toefl_score: float, university_rating: float,
                sop: float, lor: float, cgpa: float, research: int) -> dict:
        """Get single admission prediction."""
        # Convert input to numpy array
        features = np.array([[gre_score, toefl_score, university_rating, sop, lor, cgpa, research]])
        
        # Run prediction using single model
        prediction = self.single_model.predict(features)
        
        return {"chance_of_admit": float(prediction[0])}
    
    @bentoml.api(route="/batch/submit")
    def batch_submit(self, inputs: List[dict]) -> dict:
        """Submit batch prediction job."""
        # Validate and convert input
        try:
            # Convert dict list to AdmissionInput objects
            admission_inputs = [AdmissionInput(**inp) for inp in inputs]
            batch_input = BatchAdmissionInput(inputs=admission_inputs)
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=400)
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Initialize job in storage
        with jobs_lock:
            jobs[job_id] = {
                "status": "pending",
                "results": [],
                "created_at": time.time(),
                "inputs": batch_input.inputs
            }
        
        # Process batch asynchronously in background thread
        thread = threading.Thread(target=process_batch_job, args=(self, job_id, batch_input.inputs))
        thread.daemon = True
        thread.start()
        
        return {
            "job_id": job_id,
            "status": "pending",
            "message": "Batch job submitted successfully"
        }


# FastAPI routes for GET endpoints
@fastapi_app.get("/batch/status/{job_id}")
async def batch_status_get(job_id: str, current_user: dict = Depends(get_current_user)):
    """Check batch job status (GET endpoint)."""
    # Get service instance - we'll need to access it differently
    # For now, we'll use the module-level functions
    with jobs_lock:
        if job_id not in jobs:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job = jobs[job_id]
        return {
            "job_id": job_id,
            "status": job["status"]
        }


@fastapi_app.get("/batch/results/{job_id}")
async def batch_results_get(job_id: str, current_user: dict = Depends(get_current_user)):
    """Retrieve batch prediction results (GET endpoint)."""
    with jobs_lock:
        if job_id not in jobs:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job = jobs[job_id]
        status = job["status"]
        
        if status == "completed":
            results = job.get("results", [])
            # Convert Pydantic models to dict
            results_dict = []
            for r in results:
                if hasattr(r, 'model_dump'):
                    results_dict.append(r.model_dump())
                elif hasattr(r, 'dict'):
                    results_dict.append(r.dict())
                else:
                    results_dict.append(r)
            return {
                "job_id": job_id,
                "status": status,
                "results": results_dict,
                "total": len(results)
            }
        elif status in ["pending", "processing"]:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                content={
                    "job_id": job_id,
                    "status": status,
                    "message": "Job is still processing"
                },
                status_code=202
            )
        elif status == "failed":
            error_msg = job.get("error", "Unknown error")
            raise HTTPException(
                status_code=500,
                detail={
                    "job_id": job_id,
                    "status": status,
                    "error": error_msg
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Unknown status: {status}"
            )


# Add JWT authentication middleware
AdmissionService.add_asgi_middleware(JWTAuthMiddleware)

# Export service instance for bentofile.yaml
svc = AdmissionService

