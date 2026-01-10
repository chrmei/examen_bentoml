import bentoml
import numpy as np
from pydantic import BaseModel
from starlette.responses import JSONResponse
from src.auth.jwt_auth import JWTAuthMiddleware, create_token, validate_credentials

class LoginRequest(BaseModel):
    username: str
    password: str

class AdmissionInput(BaseModel):
    gre_score: float
    toefl_score: float
    university_rating: float
    sop: float
    lor: float
    cgpa: float
    research: int

@bentoml.service(name="admission_service")
class AdmissionService:
    model_ref = bentoml.models.get("admission_model:latest")
    
    def __init__(self):
        self.model = bentoml.sklearn.load_model(self.model_ref)
    
    @bentoml.api(route="/login")
    def login(self, username: str, password: str):
        if validate_credentials(username, password):
            return {"token": create_token(username)}
        return JSONResponse({"error": "Invalid credentials"}, status_code=401)
    
    @bentoml.api(route="/predict")
    def predict(self, gre_score: float, toefl_score: float, university_rating: float,
                sop: float, lor: float, cgpa: float, research: int) -> dict:
        features = np.array([[gre_score, toefl_score, university_rating, sop, lor, cgpa, research]])
        prediction = self.model.predict(features)
        return {"chance_of_admit": float(prediction[0])}

AdmissionService.add_asgi_middleware(JWTAuthMiddleware)
