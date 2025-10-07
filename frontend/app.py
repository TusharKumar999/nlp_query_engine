# frontend/app.py
"""
Streamlit frontend:
 - Upload PDF (optional)
 - Run queries (normal and hybrid)
 - Show cache status, backend+frontend response times
 - Display results uniformly as a styled DataFrame
"""

import streamlit as st
import pandas as pd
import requests
import time
from io import BytesIO

st.set_page_config(page_title="NLP Query Engine", layout="wide")
st.title("NLP Query Engine")

BACKEND = "http://127.0.0.1:8000"

# PDF upload
st.subheader("Upload PDF (optional)")
uploaded_file = st.file_uploader("Choose a PDF to upload", type=["pdf"])
if uploaded_file is not None:
    st.info(f"Uploading '{uploaded_file.name}' ...")
    file_bytes = uploaded_file.getvalue()
    files = {"file": (uploaded_file.name, BytesIO(file_bytes), "application/pdf")}
    try:
        r = requests.post(f"{BACKEND}/upload_pdf/", files=files, timeout=30)
        if r.status_code == 200:
            data = r.json()
            st.success(f"Uploaded: {data.get('filename')} (parsed {data.get('parsed_count')} records)")
        else:
            st.error(f"Upload failed: {r.status_code}")
    except Exception as e:
        st.error(f"Upload error: {e}")

# Query section
st.subheader("Run Query")
query = st.text_input("Enter your query here (e.g., 'list employees', 'count employees', 'department IT')")

if st.button("Run Query"):
    if not query.strip():
        st.warning("Please enter a query.")
    else:
        start_front = time.time()
        try:
            resp = requests.post(f"{BACKEND}/api/query", json={"q": query}, timeout=30)
            front_elapsed = round((time.time() - start_front) * 1000, 2)
            if resp.status_code != 200:
                st.error(f"Backend error: {resp.status_code}")
            else:
                data = resp.json()
                st.markdown(f"**Query:** {data.get('query')}")
                st.markdown(f"**Cache:** {data.get('cache')}")
                st.markdown(f"**Backend response time:** {data.get('response_time_ms')} ms")
                st.markdown(f"**Frontend measured time:** {front_elapsed} ms")

                results = data.get("result", [])

                if not results:
                    st.info("No detailed results found.")
                else:
                    df = pd.DataFrame(results)

                    # Reorder to show employee columns first if present
                    employee_cols = ["id", "name", "department", "designation", "salary", "joining_date"]
                    cols = [c for c in employee_cols if c in df.columns] + [c for c in df.columns if c not in employee_cols]
                    if cols:
                        df = df[cols]

                    st.success(f"Total rows: {len(df)}")
                    st.dataframe(df.style.set_properties(**{
                        "background-color": "#f0f8ff",
                        "color": "#00008B",
                        "border-color": "white",
                        "font-size": "14px",
                        "text-align": "center"
                    }), height=380)
        except Exception as e:
            st.error(f"Error contacting backend: {e}")
