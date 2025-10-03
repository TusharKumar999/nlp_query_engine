from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

# -----------------------
# Dummy employees data
# -----------------------
employees = [
    {"id": 1, "name": "John Doe", "department": "IT", "projects": "AI, ML"},
    {"id": 2, "name": "Jane Smith", "department": "HR", "projects": "Recruitment"},
    {"id": 3, "name": "Alice Kumar", "department": "IT", "projects": "Web, AI"},
    {"id": 4, "name": "Bob Verma", "department": "Finance", "projects": "Accounts"}
]

# -----------------------
# API endpoint with hybrid query
# -----------------------
@app.get("/api/query")
def query(q: str):
    q_lower = q.lower()
    
    # count employees
    if "count employees" in q_lower:
        total = len(employees)
        return JSONResponse(content={"query": q, "cache": "HIT", "result": [{"total": total}]})
    
    # list all employees
    elif "list employees" in q_lower:
        return JSONResponse(content={"query": q, "cache": "HIT", "result": employees})
    
    # department filter (keyword)
    elif "department" in q_lower:
        dep_name = q_lower.replace("department", "").strip().lower()
        filtered = [e for e in employees if e["department"].lower() == dep_name]
        return JSONResponse(content={"query": q, "cache": "HIT", "result": filtered})
    
    # Hybrid-like search: keyword + project substring match
    else:
        # Example: "IT AI" → filter department "IT" + project contains "AI"
        words = q_lower.split()
        filtered = employees
        
        # Check if any department keyword exists
        for word in words:
            # filter by department
            filtered = [e for e in filtered if word in e["department"].lower() or word in e["name"].lower() or word in e["projects"].lower()]
        
        return JSONResponse(content={"query": q, "cache": "HIT", "result": filtered})
