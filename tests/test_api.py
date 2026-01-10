import pytest
import requests
import jwt
from datetime import datetime, timedelta, timezone

BASE_URL = "http://localhost:3000"
JWT_SECRET = "bentoml_exam_secret_key_2024"
JWT_ALGORITHM = "HS256"

@pytest.fixture(scope="module")
def valid_token():
    response = requests.post(f"{BASE_URL}/login", json={"username": "admin", "password": "secret123"})
    return response.json().get("token")

# JWT Authentication Tests
class TestJWTAuth:
    def test_missing_token_returns_401(self):
        response = requests.post(f"{BASE_URL}/predict", json={
            "gre_score": 320, "toefl_score": 110, "university_rating": 3,
            "sop": 3.5, "lor": 3.0, "cgpa": 8.5, "research": 1
        })
        assert response.status_code == 401

    def test_invalid_token_returns_401(self):
        response = requests.post(f"{BASE_URL}/predict", 
            headers={"Authorization": "Bearer invalid_token"},
            json={"gre_score": 320, "toefl_score": 110, "university_rating": 3,
                  "sop": 3.5, "lor": 3.0, "cgpa": 8.5, "research": 1})
        assert response.status_code == 401

    def test_expired_token_returns_401(self):
        expired_payload = {
            "sub": "admin",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
            "iat": datetime.now(timezone.utc) - timedelta(hours=2)
        }
        expired_token = jwt.encode(expired_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        response = requests.post(f"{BASE_URL}/predict",
            headers={"Authorization": f"Bearer {expired_token}"},
            json={"gre_score": 320, "toefl_score": 110, "university_rating": 3,
                  "sop": 3.5, "lor": 3.0, "cgpa": 8.5, "research": 1})
        assert response.status_code == 401

    def test_valid_token_succeeds(self, valid_token):
        response = requests.post(f"{BASE_URL}/predict",
            headers={"Authorization": f"Bearer {valid_token}"},
            json={"gre_score": 320, "toefl_score": 110, "university_rating": 3,
                  "sop": 3.5, "lor": 3.0, "cgpa": 8.5, "research": 1})
        assert response.status_code == 200

# Login API Tests
class TestLoginAPI:
    def test_valid_credentials_return_token(self):
        response = requests.post(f"{BASE_URL}/login", json={"username": "admin", "password": "secret123"})
        assert response.status_code == 200
        assert "token" in response.json()

    def test_invalid_credentials_return_401(self):
        response = requests.post(f"{BASE_URL}/login", json={"username": "wrong", "password": "wrong"})
        assert response.status_code == 401

# Prediction API Tests
class TestPredictAPI:
    def test_missing_jwt_returns_401(self):
        response = requests.post(f"{BASE_URL}/predict", json={
            "gre_score": 320, "toefl_score": 110, "university_rating": 3,
            "sop": 3.5, "lor": 3.0, "cgpa": 8.5, "research": 1
        })
        assert response.status_code == 401

    def test_valid_input_returns_prediction(self, valid_token):
        response = requests.post(f"{BASE_URL}/predict",
            headers={"Authorization": f"Bearer {valid_token}"},
            json={"gre_score": 337, "toefl_score": 118, "university_rating": 4,
                  "sop": 4.5, "lor": 4.5, "cgpa": 9.65, "research": 1})
        assert response.status_code == 200
        data = response.json()
        assert "chance_of_admit" in data
        assert 0 <= data["chance_of_admit"] <= 1

    def test_invalid_input_returns_error(self, valid_token):
        response = requests.post(f"{BASE_URL}/predict",
            headers={"Authorization": f"Bearer {valid_token}"},
            json={"invalid_field": "test"})
        assert response.status_code == 400

