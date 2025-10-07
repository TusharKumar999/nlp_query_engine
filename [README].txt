[**README**]

markdown
NLP Query Engine – FastAPI + Streamlit

 Objective
Create a query engine that returns employee data via backend API and displays it in a polished frontend table.  
Supports **normal keyword queries** as well as **hybrid queries** (keyword + project substring search).



 Tools & Modules
- Python 3.x
- FastAPI
- Uvicorn
- Streamlit
- Requests
- Pandas



Folder Structure

nlp_query_engine_submit/
│
├── backend/
│   ├── main.py                # Backend code with normal + hybrid query support
│   └── README_BACKEND.txt     # Optional: backend run instructions
│
├── frontend/
│   ├── app.py                 # Streamlit frontend UI
│   └── README_FRONTEND.txt    # Optional: frontend run instructions
│
└── README.md                  # This documentation file



 Backend Instructions (Load & Run)
1. Open PowerShell / Terminal in **backend folder**:  


cd C:\Users\Admin\Desktop\nlp_query_engine_submit\backend


2. Activate virtual environment (if exists):

.\venv\Scripts\Activate.ps1

> Tip: If activation fails, run:

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

3. Install required modules:

pip install fastapi uvicorn

4. Run backend server:

uvicorn main:app --reload

5. Test backend endpoints in browser:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
> You should see `/api/query` endpoint ready for queries.


 Frontend Instructions (Load & Run)
1. Open PowerShell / Terminal in **frontend folder**:  


cd C:\Users\Admin\Desktop\nlp_query_engine_submit\frontend


2. Install required modules:


pip install streamlit requests pandas


3. Run frontend UI:


streamlit run app.py


4. Open browser:


[http://localhost:8502](http://localhost:8502)


> Query box will appear, and results table will show both **normal and hybrid query results**.


 Features
- **Count Employees:** Returns total number of employees.  
- **List Employees:** Displays all employee details in a table.  
- **Department Filter:** Returns employees by department (`IT`, `HR`, `Finance`).  
- **Hybrid Queries:** Combination of keyword + project substring match.  
  - Example: `"IT AI"` → employees in IT department working on AI projects.  
- **Polished Table:** Styled table with total results count and scrollable height.  
- **Error Handling:**  
  - `404` → Endpoint not found  
  - `422` → Missing query parameter  
  - Empty results → Displays “No detailed results found”  



 Test Queries

| Query Type | Example Queries | Expected Behavior |
|------------|----------------|-----------------|
| Normal     | `count employees` | Total employees count |
| Normal     | `list employees` | Full employee table |
| Normal     | `department IT`  | Table of IT employees only |
| Hybrid     | `IT AI`          | IT employees working on AI projects |
| Hybrid     | `HR Recruitment` | HR employees working on Recruitment projects |
| Hybrid     | `Finance Accounts` | Finance employees with Accounts project |


 Notes
- **Backend must run before frontend**, otherwise frontend will show connection errors.  
- Queries are **case-insensitive**, extra spaces ignored.  
- Hybrid queries use **substring matching** for demo purposes.  
- **No external API keys required**.  



 Final Submission Checklist
- [x] Backend working with normal + hybrid queries ✅  
- [x] Frontend polished + table view ✅  
- [x] Queries tested ✅  
- [x] Error handling verified ✅  
- [x] Documentation complete ✅    



**All paths, commands, and instructions are provided for Windows PowerShell.**  
Keep the folder structure intact for smooth running of backend + frontend.
Thank you.

