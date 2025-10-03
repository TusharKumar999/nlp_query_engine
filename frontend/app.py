# frontend/app.py
import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="NLP Query Engine", layout="wide")

st.title("NLP Query Engine")
st.write("Enter your query and see results from the backend in a polished table format.")

# --- Query Input ---
query = st.text_input("Enter your query here:")
hybrid_query = st.checkbox("Hybrid Query (optional)")

# --- PDF Upload ---
uploaded_file = st.file_uploader("Upload PDF (optional)", type=["pdf"])
if uploaded_file:
    files = {"file": uploaded_file.getvalue()}
    try:
        res = requests.post("http://127.0.0.1:8000/api/upload_pdf/", files={"file": uploaded_file})
        if res.status_code == 200:
            st.success(f"Uploaded: {uploaded_file.name}")
        else:
            st.error("PDF upload failed!")
    except Exception as e:
        st.error(f"PDF upload error: {e}")

# --- Run Query ---
if st.button("Run Query"):
    if not query.strip():
        st.warning("Please enter a query.")
    else:
        try:
            start_frontend = time.time()
            payload = {"q": query, "hybrid": hybrid_query}
            response = requests.post("http://127.0.0.1:8000/api/query", json=payload)
            frontend_time = round(time.time() - start_frontend, 3)

            if response.status_code == 200:
                data = response.json()
                results_list = data.get("result", [])

                st.markdown(f"**Cache:** {data.get('cache', 'N/A')} | **Backend response time:** {data.get('response_time', 'N/A')}s | **Frontend time:** {frontend_time}s")

                if not results_list:
                    st.info("No detailed results found.")
                else:
                    df = pd.DataFrame(results_list)
                    st.success(f"Total results: {len(results_list)}")
                    st.dataframe(df.style.set_properties(**{
                        'background-color': '#f0f8ff',
                        'color': '#00008B',
                        'border-color': 'white',
                        'font-size': '14px',
                        'text-align': 'center'
                    }), height=300)
            else:
                st.error(f"Backend error: {response.status_code}")
        except Exception as e:
            st.error(f"Error connecting to backend: {e}")
