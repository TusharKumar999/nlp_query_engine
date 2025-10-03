# backend/main.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import pandas as pd
import os
from typing import Optional

app = FastAPI(title="NLP Query Engine")

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory cache
cache = {}

# Simulated database
employees_db = [
    {"id": 1, "name": "John Doe", "department": "IT"},
    {"id": 2, "name": "Jane Smith", "department": "HR"},
    {"id": 3, "name": "Alice Kumar", "department": "IT"},
    {"id": 4, "name": "Bob Verma", "department": "Finance"}
]

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class QueryRequest(BaseModel):
    q: str
    hybrid: Optional[bool] = False

@app.post("/api/query")
def run_query(request: QueryRequest):
    """Process normal or hybrid query"""
    query = request.q.strip().lower()
    start_time = time.time()

    # Check cache
    cache_key = f"{query}_{request.hybrid}"
    if cache_key in cache:
        response_time = time.time() - start_time
        return {"query": query, "cache": "HIT", "response_time": round(response_time,3), "result": cache[cache_key]}

    # Normal query simulation
    results = []
    if "count employees" in query:
        results = [{"total": len(employees_db)}]
    elif "list employees" in query:
        results = employees_db
    elif "department" in query:  # hybrid query simulation
        for emp in employees_db:
            if emp["department"].lower() in query:
                results.append(emp)

    cache[cache_key] = results
    response_time = time.time() - start_time
    return {"query": query, "cache": "MISS", "response_time": round(response_time,3), "result": results}

@app.post("/api/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """Save uploaded PDF on backend"""
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)
    return {"filename": file.filename, "message": "File uploaded successfully"}
