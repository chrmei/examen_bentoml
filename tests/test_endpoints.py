"""Comprehensive test suite for admission prediction API endpoints."""

import pytest
import requests
import jwt
import os
import time
from pathlib import Path
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

BASE_URL = "http://localhost:3000"
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "default_secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
API_USERNAME = os.getenv("API_USERNAME", "admin")
API_PASSWORD = os.getenv("API_PASSWORD", "secret123")


@pytest.fixture(scope="module")
def valid_token():
    """Fixture to get a valid JWT token."""
    response = requests.post(
        f"{BASE_URL}/login",
        json={"username": API_USERNAME, "password": API_PASSWORD}
    )
    assert response.status_code == 200
    return response.json().get("token")


@pytest.fixture
def sample_input():
    """Fixture for sample admission input."""
    return {
        "gre_score": 337,
        "toefl_score": 118,
        "university_rating": 4,
        "sop": 4.5,
        "lor": 4.5,
        "cgpa": 9.65,
        "research": 1
    }


@pytest.fixture
def sample_batch_input():
    """Fixture for sample batch input."""
    return {
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
            },
            {
                "gre_score": 310,
                "toefl_score": 105,
                "university_rating": 2,
                "sop": 3.0,
                "lor": 2.5,
                "cgpa": 7.5,
                "research": 0
            }
        ]
    }


# Login API Tests
class TestLoginAPI:
    """Tests for login endpoint."""

    def test_valid_credentials_return_token(self):
        """Test that valid credentials return a JWT token."""
        response = requests.post(
            f"{BASE_URL}/login",
            json={"username": API_USERNAME, "password": API_PASSWORD}
        )
        assert response.status_code == 200
        assert "token" in response.json()

    def test_invalid_credentials_return_401(self):
        """Test that invalid credentials return 401."""
        response = requests.post(
            f"{BASE_URL}/login",
            json={"username": "wrong", "password": "wrong"}
        )
        assert response.status_code == 401


# JWT Authentication Tests
class TestJWTAuth:
    """Tests for JWT authentication middleware."""

    def test_missing_token_returns_401(self, sample_input):
        """Test that missing token returns 401."""
        response = requests.post(f"{BASE_URL}/predict", json=sample_input)
        assert response.status_code == 401

    def test_invalid_token_returns_401(self, sample_input):
        """Test that invalid token returns 401."""
        response = requests.post(
            f"{BASE_URL}/predict",
            headers={"Authorization": "Bearer invalid_token"},
            json=sample_input
        )
        assert response.status_code == 401

    def test_expired_token_returns_401(self, sample_input):
        """Test that expired token returns 401."""
        expired_payload = {
            "sub": API_USERNAME,
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
            "iat": datetime.now(timezone.utc) - timedelta(hours=2)
        }
        expired_token = jwt.encode(expired_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        response = requests.post(
            f"{BASE_URL}/predict",
            headers={"Authorization": f"Bearer {expired_token}"},
            json=sample_input
        )
        assert response.status_code == 401

    def test_valid_token_succeeds(self, valid_token, sample_input):
        """Test that valid token allows access."""
        response = requests.post(
            f"{BASE_URL}/predict",
            headers={"Authorization": f"Bearer {valid_token}"},
            json=sample_input
        )
        assert response.status_code == 200


# Single Prediction API Tests
class TestSinglePrediction:
    """Tests for single prediction endpoint."""

    def test_missing_jwt_returns_401(self, sample_input):
        """Test that missing JWT returns 401."""
        response = requests.post(f"{BASE_URL}/predict", json=sample_input)
        assert response.status_code == 401

    def test_valid_input_returns_prediction(self, valid_token, sample_input):
        """Test that valid input returns prediction."""
        response = requests.post(
            f"{BASE_URL}/predict",
            headers={"Authorization": f"Bearer {valid_token}"},
            json=sample_input
        )
        assert response.status_code == 200
        data = response.json()
        assert "chance_of_admit" in data
        assert 0 <= data["chance_of_admit"] <= 1

    def test_invalid_input_returns_error(self, valid_token):
        """Test that invalid input returns 400."""
        response = requests.post(
            f"{BASE_URL}/predict",
            headers={"Authorization": f"Bearer {valid_token}"},
            json={"invalid_field": "test"}
        )
        assert response.status_code == 400


# Batch Submission Tests
class TestBatchSubmission:
    """Tests for batch submission endpoint."""

    def test_missing_jwt_returns_401(self, sample_batch_input):
        """Test that missing JWT returns 401."""
        response = requests.post(f"{BASE_URL}/batch/submit", json=sample_batch_input)
        assert response.status_code == 401

    def test_valid_batch_submission_returns_job_id(self, valid_token, sample_batch_input):
        """Test that valid batch submission returns job_id."""
        response = requests.post(
            f"{BASE_URL}/batch/submit",
            headers={"Authorization": f"Bearer {valid_token}"},
            json=sample_batch_input
        )
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert "status" in data
        assert data["status"] == "pending"

    def test_empty_batch_returns_error(self, valid_token):
        """Test that empty batch returns validation error."""
        response = requests.post(
            f"{BASE_URL}/batch/submit",
            headers={"Authorization": f"Bearer {valid_token}"},
            json={"inputs": []}
        )
        assert response.status_code == 400

    def test_large_batch_returns_error(self, valid_token):
        """Test that batch exceeding 1000 records returns error."""
        large_batch = {
            "inputs": [
                {
                    "gre_score": 320,
                    "toefl_score": 110,
                    "university_rating": 3,
                    "sop": 3.5,
                    "lor": 3.0,
                    "cgpa": 8.5,
                    "research": 1
                }
            ] * 1001
        }
        response = requests.post(
            f"{BASE_URL}/batch/submit",
            headers={"Authorization": f"Bearer {valid_token}"},
            json=large_batch
        )
        assert response.status_code == 400

    def test_invalid_batch_input_returns_error(self, valid_token):
        """Test that invalid batch input returns error."""
        response = requests.post(
            f"{BASE_URL}/batch/submit",
            headers={"Authorization": f"Bearer {valid_token}"},
            json={"invalid_field": "test"}
        )
        assert response.status_code == 400


# Batch Status Tests
class TestBatchStatus:
    """Tests for batch status endpoint."""

    def test_missing_jwt_returns_401(self):
        """Test that missing JWT returns 401."""
        response = requests.get(f"{BASE_URL}/batch/status/test-job-id")
        assert response.status_code == 401

    def test_invalid_job_id_returns_404(self, valid_token):
        """Test that invalid job_id returns 404."""
        response = requests.get(
            f"{BASE_URL}/batch/status/invalid-job-id-12345",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        assert response.status_code == 404

    def test_check_pending_status(self, valid_token, sample_batch_input):
        """Test checking status of pending job."""
        # Submit batch job
        submit_response = requests.post(
            f"{BASE_URL}/batch/submit",
            headers={"Authorization": f"Bearer {valid_token}"},
            json=sample_batch_input
        )
        assert submit_response.status_code == 200
        job_id = submit_response.json()["job_id"]

        # Check status immediately (should be pending or processing)
        status_response = requests.get(
            f"{BASE_URL}/batch/status/{job_id}",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        assert status_response.status_code == 200
        data = status_response.json()
        assert "job_id" in data
        assert "status" in data
        assert data["status"] in ["pending", "processing", "completed"]

    def test_check_completed_status(self, valid_token, sample_batch_input):
        """Test checking status of completed job."""
        # Submit batch job
        submit_response = requests.post(
            f"{BASE_URL}/batch/submit",
            headers={"Authorization": f"Bearer {valid_token}"},
            json=sample_batch_input
        )
        assert submit_response.status_code == 200
        job_id = submit_response.json()["job_id"]

        # Wait for completion (poll with retry)
        max_attempts = 30
        for attempt in range(max_attempts):
            status_response = requests.get(
                f"{BASE_URL}/batch/status/{job_id}",
                headers={"Authorization": f"Bearer {valid_token}"}
            )
            assert status_response.status_code == 200
            status_data = status_response.json()
            if status_data["status"] == "completed":
                break
            time.sleep(1)

        # Final status check
        status_response = requests.get(
            f"{BASE_URL}/batch/status/{job_id}",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        assert status_response.status_code == 200
        data = status_response.json()
        assert data["status"] == "completed"


# Batch Results Tests
class TestBatchResults:
    """Tests for batch results endpoint."""

    def test_missing_jwt_returns_401(self):
        """Test that missing JWT returns 401."""
        response = requests.get(f"{BASE_URL}/batch/results/test-job-id")
        assert response.status_code == 401

    def test_job_not_found_returns_404(self, valid_token):
        """Test that non-existent job returns 404."""
        response = requests.get(
            f"{BASE_URL}/batch/results/invalid-job-id-12345",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        assert response.status_code == 404

    def test_pending_job_returns_202(self, valid_token, sample_batch_input):
        """Test that pending job returns 202."""
        # Submit batch job
        submit_response = requests.post(
            f"{BASE_URL}/batch/submit",
            headers={"Authorization": f"Bearer {valid_token}"},
            json=sample_batch_input
        )
        assert submit_response.status_code == 200
        job_id = submit_response.json()["job_id"]

        # Try to get results immediately (might be pending or processing)
        results_response = requests.get(
            f"{BASE_URL}/batch/results/{job_id}",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        # Should be 202 if pending/processing, or 200 if already completed
        assert results_response.status_code in [200, 202]

    def test_retrieve_completed_results(self, valid_token, sample_batch_input):
        """Test retrieving results from completed job."""
        # Submit batch job
        submit_response = requests.post(
            f"{BASE_URL}/batch/submit",
            headers={"Authorization": f"Bearer {valid_token}"},
            json=sample_batch_input
        )
        assert submit_response.status_code == 200
        job_id = submit_response.json()["job_id"]

        # Wait for completion
        max_attempts = 30
        for attempt in range(max_attempts):
            status_response = requests.get(
                f"{BASE_URL}/batch/status/{job_id}",
                headers={"Authorization": f"Bearer {valid_token}"}
            )
            assert status_response.status_code == 200
            status_data = status_response.json()
            if status_data["status"] == "completed":
                break
            time.sleep(1)

        # Retrieve results
        results_response = requests.get(
            f"{BASE_URL}/batch/results/{job_id}",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        assert results_response.status_code == 200
        data = results_response.json()
        assert "job_id" in data
        assert "status" in data
        assert data["status"] == "completed"
        assert "results" in data
        assert "total" in data
        assert len(data["results"]) == data["total"]
        assert len(data["results"]) == len(sample_batch_input["inputs"])

    def test_results_format_validation(self, valid_token, sample_batch_input):
        """Test that results have correct format."""
        # Submit batch job
        submit_response = requests.post(
            f"{BASE_URL}/batch/submit",
            headers={"Authorization": f"Bearer {valid_token}"},
            json=sample_batch_input
        )
        assert submit_response.status_code == 200
        job_id = submit_response.json()["job_id"]

        # Wait for completion
        max_attempts = 30
        for attempt in range(max_attempts):
            status_response = requests.get(
                f"{BASE_URL}/batch/status/{job_id}",
                headers={"Authorization": f"Bearer {valid_token}"}
            )
            assert status_response.status_code == 200
            status_data = status_response.json()
            if status_data["status"] == "completed":
                break
            time.sleep(1)

        # Retrieve and validate results
        results_response = requests.get(
            f"{BASE_URL}/batch/results/{job_id}",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        assert results_response.status_code == 200
        data = results_response.json()
        
        # Validate structure
        assert isinstance(data["results"], list)
        for result in data["results"]:
            assert "chance_of_admit" in result
            assert 0 <= result["chance_of_admit"] <= 1


# Batch Workflow Tests
class TestBatchWorkflow:
    """End-to-end tests for complete batch workflow."""

    def test_complete_batch_workflow(self, valid_token, sample_batch_input):
        """Test complete batch workflow: submit → poll → retrieve."""
        # Step 1: Submit batch job
        submit_response = requests.post(
            f"{BASE_URL}/batch/submit",
            headers={"Authorization": f"Bearer {valid_token}"},
            json=sample_batch_input
        )
        assert submit_response.status_code == 200
        submit_data = submit_response.json()
        job_id = submit_data["job_id"]
        assert submit_data["status"] == "pending"

        # Step 2: Poll status until completed
        max_attempts = 30
        completed = False
        for attempt in range(max_attempts):
            status_response = requests.get(
                f"{BASE_URL}/batch/status/{job_id}",
                headers={"Authorization": f"Bearer {valid_token}"}
            )
            assert status_response.status_code == 200
            status_data = status_response.json()
            assert status_data["job_id"] == job_id
            
            if status_data["status"] == "completed":
                completed = True
                break
            elif status_data["status"] == "failed":
                pytest.fail(f"Batch job failed: {status_data}")
            
            time.sleep(1)

        assert completed, "Job did not complete within timeout"

        # Step 3: Retrieve results
        results_response = requests.get(
            f"{BASE_URL}/batch/results/{job_id}",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        assert results_response.status_code == 200
        results_data = results_response.json()
        
        # Step 4: Verify results
        assert results_data["job_id"] == job_id
        assert results_data["status"] == "completed"
        assert len(results_data["results"]) == len(sample_batch_input["inputs"])
        assert results_data["total"] == len(sample_batch_input["inputs"])
        
        # Verify each result has correct format
        for i, result in enumerate(results_data["results"]):
            assert "chance_of_admit" in result
            assert 0 <= result["chance_of_admit"] <= 1

