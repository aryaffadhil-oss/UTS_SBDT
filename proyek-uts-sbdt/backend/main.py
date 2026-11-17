import os
import json
import joblib
import psycopg2
from psycopg2.extras import RealDictCursor
import jwt
from jwt import PyJWKClient
from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel

app = FastAPI(title="SBDT Distributed Inference API")

# Konfigurasi Environment
DB_PRIMARY_URL = os.getenv("DB_PRIMARY_URL", "postgresql://postgres:postgres@db-primary:5432/sbdt_db")
DB_REPLICA_URL = os.getenv("DB_REPLICA_URL", "postgresql://postgres:postgres@db-replica:5432/sbdt_db")
KEYCLOAK_JWKS_URL = os.getenv("KEYCLOAK_JWKS_URL", "http://keycloak:8080/realms/sbdt-realm/protocol/openid-connect/certs")

# Load ML Model
artifact = joblib.load("model.joblib")
ml_model = artifact["model"]
target_names = artifact["target_names"]

# JWKS Client untuk validasi signature token secara terdistribusi
jwks_client = PyJWKClient(KEYCLOAK_JWKS_URL)

class PredictRequest(BaseModel):
    features: list[float]  # Contoh: [5.1, 3.5, 1.4, 0.2]

def verify_jwt(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Format header Authorization harus Bearer <token>")
    token = authorization.split(" ")[1]
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_aud": False}
        )
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token JWT tidak valid: {str(e)}")

@app.post("/predict")
def predict(req: PredictRequest, user: dict = Depends(verify_jwt)):
    if len(req.features) != 4:
        raise HTTPException(status_code=400, detail="Input features harus berisi 4 angka desimal.")
    
    # 1. Eksekusi Inferensi Model ML
    pred_idx = ml_model.predict([req.features])[0]
    pred_label = target_names[pred_idx]

    # 2. WRITE ROUTING -> Simpan hasil ke Node Primary Database
    conn = psycopg2.connect(DB_PRIMARY_URL)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO inference_history (user_sub, username, input_features, prediction)
        VALUES (%s, %s, %s, %s) RETURNING id, created_at;
        """,
        (user.get("sub"), user.get("preferred_username", "unknown"), json.dumps(req.features), pred_label)
    )
    inserted = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    return {
        "status": "success",
        "routed_to": "PRIMARY_DB (WRITE)",
        "id": inserted[0],
        "prediction": pred_label,
        "timestamp": inserted[1]
    }

@app.get("/history")
def get_history(user: dict = Depends(verify_jwt)):
    # READ ROUTING -> Query riwayat dialihkan otomatis ke Node Read-Replica Database
    conn = psycopg2.connect(DB_REPLICA_URL, cursor_factory=RealDictCursor)
    cur = conn.cursor()
    cur.execute("SELECT * FROM inference_history ORDER BY id DESC LIMIT 20;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return {
        "status": "success",
        "routed_to": "READ_REPLICA_DB (READ)",
        "total": len(rows),
        "data": rows
    }