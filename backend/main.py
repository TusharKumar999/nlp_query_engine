# backend/main.py
"""
Final backend for NLP Query Engine with:
 - PDF upload (save + extract + parse employee-like records)
 - /api/query endpoint: supports normal & hybrid & document queries
 - returns uniform results (list of dicts), cache info, backend response time in ms
"""

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import uuid
import os
from typing import List, Dict, Any
import PyPDF2
import re

app = FastAPI(title="NLP Query Engine")

# CORS for local frontend (change in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload directory
UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory storage of uploaded PDFs (text + parsed structured rows)
# Each item: {id, filename, saved_as, text, parsed_records}
uploaded_pdfs: List[Dict[str, Any]] = []

# Built-in structured employee DB
employees_db: List[Dict[str, Any]] = [
    {"id": 1, "name": "John Doe", "department": "IT"},
    {"id": 2, "name": "Jane Smith", "department": "HR"},
    {"id": 3, "name": "Alice Kumar", "department": "IT"},
    {"id": 4, "name": "Bob Verma", "department": "Finance"},
]

# Simple cache: maps normalized query -> results list
cache: Dict[str, List[Dict[str, Any]]] = {}

class QueryRequest(BaseModel):
    q: str

def extract_text_from_pdf_bytes(bytes_data: bytes) -> str:
    """
    Extract text from PDF bytes using PyPDF2.
    Returns joined text from all pages.
    """
    from io import BytesIO
    stream = BytesIO(bytes_data)
    try:
        reader = PyPDF2.PdfReader(stream)
    except Exception:
        return ""
    texts = []
    for page in reader.pages:
        try:
            page_text = page.extract_text()
            if page_text:
                texts.append(page_text)
        except Exception:
            continue
    return "\n".join(texts)

def parse_employee_records_from_text(text: str) -> List[Dict[str, Any]]:
    """
    Parse structured employee-like records from text.
    Looks for blocks with 'Department:', 'Employee Name:', 'Designation:', 'Salary:', 'Joining Date:'.
    Returns list of dicts with keys id,name,department,designation,salary,joining_date where available.
    """
    records = []
    # Split text into blocks by double-newline or "Department:" occurrences
    # We'll use a regex to find blocks starting with "Department:" and capture following lines
    # Normalize line endings
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return records

    # Reconstruct into blocks whenever a line starts with "Department:"
    blocks = []
    current = []
    for ln in lines:
        if re.match(r'(?i)^department\s*[:\-]', ln):  # new block
            if current:
                blocks.append("\n".join(current))
            current = [ln]
        else:
            current.append(ln)
    if current:
        blocks.append("\n".join(current))

    # If no 'Department:' tokens, try to chunk every 6 lines as fallback
    if not blocks:
        chunks = [lines[i:i+6] for i in range(0, len(lines), 6)]
        blocks = ["\n".join(c) for c in chunks]

    # For each block extract fields
    for blk in blocks:
        rec = {}
        # department
        m = re.search(r'(?i)department\s*[:\-]\s*(.+)', blk)
        if m:
            rec['department'] = m.group(1).strip()
        # name
        m = re.search(r'(?i)employee\s*name\s*[:\-]\s*(.+)', blk)
        if m:
            rec['name'] = m.group(1).strip()
        # designation
        m = re.search(r'(?i)designation\s*[:\-]\s*(.+)', blk)
        if m:
            rec['designation'] = m.group(1).strip()
        # salary (digits, commas)
        m = re.search(r'(?i)salary\s*[:\-]\s*([\d,]+)', blk)
        if m:
            rec['salary'] = m.group(1).strip()
        # joining date
        m = re.search(r'(?i)joining\s*date\s*[:\-]\s*(.+)', blk)
        if m:
            rec['joining_date'] = m.group(1).strip()

        # Require at least name+department to consider it a valid parsed record
        if rec.get('name') and rec.get('department'):
            # assign new id that doesn't clash with employees_db ids
            rec['id'] = max([e['id'] for e in employees_db] + [0]) + len(records) + 1
            records.append(rec)

    return records

def find_pdf_snippets_for_query(query: str, context_chars: int = 120) -> List[Dict[str, str]]:
    """
    Search all uploaded_pdfs' text for the query (case-insensitive).
    Return list of {"document_name": ..., "snippet": ...}
    """
    q = query.lower().strip()
    snippets = []
    for pdf in uploaded_pdfs:
        text = (pdf.get("text") or "").lower()
        idx = text.find(q)
        if idx != -1:
            start = max(0, idx - context_chars)
            end = min(len(text), idx + len(q) + context_chars)
            orig = pdf.get("text", "")
            snippet = orig[start:end].replace("\n", " ").strip()
            snippets.append({"document_name": pdf.get("filename"), "snippet": snippet})
    return snippets

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Save PDF, extract text, parse structured records (if any), and store in memory.
    """
    contents = await file.read()
    unique_name = f"{uuid.uuid4().hex}_{file.filename}"
    save_path = os.path.join(UPLOAD_DIR, unique_name)
    with open(save_path, "wb") as f:
        f.write(contents)

    # Extract text
    extracted_text = extract_text_from_pdf_bytes(contents)

    # Parse structured employee records (best-effort)
    parsed = parse_employee_records_from_text(extracted_text)

    # store
    uploaded_pdfs.append({
        "id": uuid.uuid4().hex,
        "filename": file.filename,
        "saved_as": unique_name,
        "text": extracted_text,
        "parsed_records": parsed
    })

    return {"status": "success", "filename": file.filename, "saved_as": unique_name, "parsed_count": len(parsed), "total_pdfs": len(uploaded_pdfs)}

@app.post("/api/query")
def api_query(request: QueryRequest):
    """
    Unified query endpoint:
    - Searches structured DB (employees_db + parsed PDF records) for normal/hybrid queries
    - Also searches PDF text to return snippet rows (document_name, snippet)
    - Returns uniform list-of-dicts results
    """
    q = request.q.strip()
    low = q.lower()
    start = time.time()

    # Cache lookup
    cache_key = low
    if cache_key in cache:
        elapsed = round((time.time() - start) * 1000, 2)
        return {"query": q, "cache": "HIT", "response_time_ms": elapsed, "result": cache[cache_key]}

    # Build combined structured row list: base employees_db + parsed records from PDFs
    combined_structured = list(employees_db)  # copy
    for pdf in uploaded_pdfs:
        parsed = pdf.get("parsed_records", [])
        if parsed:
            # assign ids so they don't conflict (they already have ids set during parse)
            combined_structured.extend(parsed)

    results: List[Dict[str, Any]] = []

    # 1) Exact-like normal queries
    if low == "list employees" or low.startswith("list employees"):
        results = combined_structured
    elif low == "count employees" or low.startswith("count employees"):
        results = [{"total": len(combined_structured)}]
    else:
        # 2) Department / hybrid style: look for 'department' keyword or 'employees in <dept>'
        if "department" in low or "employees in" in low or "in the" in low:
            # try to match known department names from combined_structured
            known_depts = set([str(e.get("department", "")).lower() for e in combined_structured if e.get("department")])
            matched = []
            for d in known_depts:
                if d and d in low:
                    for emp in combined_structured:
                        if str(emp.get("department", "")).lower() == d:
                            matched.append(emp)
            # fallback: if phrase 'employees in <token>' style
            if not matched:
                m = re.search(r'employees in ([a-zA-Z &]+)', low)
                if m:
                    token = m.group(1).strip()
                    for emp in combined_structured:
                        if token in str(emp.get("department", "")).lower():
                            matched.append(emp)
            results = matched

    # 3) PDF text search for snippets (always run and append after structured rows)
    doc_snips = find_pdf_snippets_for_query(low)

    # Combine results: structured first, document snippet rows after
    combined_output: List[Dict[str, Any]] = []
    if results:
        combined_output.extend(results)
    if doc_snips:
        for s in doc_snips:
            combined_output.append({"document_name": s["document_name"], "snippet": s["snippet"]})

    if not combined_output:
        combined_output = [{"info": f"No detailed results found for: '{q}'"}]

    # Cache & return
    cache[cache_key] = combined_output
    elapsed = round((time.time() - start) * 1000, 2)
    return {"query": q, "cache": "MISS", "response_time_ms": elapsed, "result": combined_output}
