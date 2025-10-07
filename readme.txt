🧠 NLP Query Engine — Complete Setup Guide
🚀 Overview

This project is a Smart NLP Query Engine that supports:

✅ Normal Queries (like “count employees”, “list all IT department employees”)

🤖 Hybrid Queries (mix of natural and structured queries)

📄 PDF Upload Support — Extracts data from uploaded PDFs and allows querying on it

⚡ Fast Response Time displayed on frontend

💾 Cache System (HIT / MISS) for performance tracking

🧮 Styled Table Output for better readability

🏗️ Project Structure
nlp_query_engine_submit/
│
├── backend/
│   ├── main.py
│   ├── data/
│   ├── uploads/
│   └── requirements.txt
│
├── frontend/
│   ├── app.py
│   └── pages/
│
└── README.md

⚙️ Backend Setup
1️⃣ Navigate to backend folder
cd backend

2️⃣ Create and activate virtual environment
For Windows PowerShell:
python -m venv venv
.\venv\Scripts\Activate.ps1

For CMD:
python -m venv venv
venv\Scripts\activate

3️⃣ Install dependencies
pip install fastapi uvicorn python-multipart pandas PyPDF2

4️⃣ Run the backend server

Make sure main.py contains:

from fastapi import FastAPI
app = FastAPI()


Then run:

uvicorn main:app --reload


If running from root directory:

uvicorn backend.main:app --reload


Backend will start at:
👉 http://127.0.0.1:8000

🖥️ Frontend Setup
1️⃣ Navigate to frontend folder
cd ../frontend

2️⃣ Install Streamlit and dependencies
pip install streamlit pandas requests


If any extra package missing:

pip install streamlit-extras

3️⃣ Run the frontend app
streamlit run app.py


Frontend will start at:
👉 http://localhost:8501

🔁 Full Workflow

Run backend → uvicorn main:app --reload

Run frontend → streamlit run app.py

Upload PDF file (optional)

Enter your normal or hybrid query

See instant output with:

Cache info (HIT / MISS)

Response time

Table view results

🧩 PDF Query Example

Upload a PDF like:

Employee_Name | Department | Salary
Ravi           IT           50000
Sneha          HR           60000


Then query:

list all employees in IT department


→ Output: List of employees from IT department with salaries.

🧠 Troubleshooting
Error	Solution
Error loading ASGI app	Make sure app = FastAPI() exists in main.py
No module named 'PyPDF2'	Run pip install PyPDF2
streamlit_extras not found	Run pip install streamlit-extras
Access denied while activating venv	Run PowerShell as Administrator
No detailed results found	Check PDF format or ensure backend connected properly