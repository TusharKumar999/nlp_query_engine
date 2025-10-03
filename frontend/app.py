import streamlit as st
import requests
import pandas as pd

# -----------------------
# Page config & CSS
# -----------------------
st.set_page_config(page_title="NLP Query Engine", layout="wide", page_icon="🧠")

st.markdown("""
<style>
.big-font { font-size:22px !important; color: #00BFFF; font-weight: bold; }
.error-font { color: #FF4500; font-weight: bold; }
.info-font { color: #FFA500; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">NLP Query Engine</p>', unsafe_allow_html=True)
st.write("Enter your query and see results from the backend in a polished table format.")

# -----------------------
# Layout
# -----------------------
col1, col2 = st.columns([2,3])

with col1:
    query = st.text_input("Enter your query here:")
    search_btn = st.button("Search")

with col2:
    result_placeholder = st.empty()

# -----------------------
# Backend call function
# -----------------------
def get_results(query_text):
    backend_url = f"http://127.0.0.1:8000/api/query?q={query_text}"  # endpoint + q parameter

    try:
        with st.spinner('Fetching results from backend... ⏳'):
            response = requests.get(backend_url)
            
            if response.status_code == 404:
                st.markdown('<p class="error-font">Error 404: Endpoint not found! Check backend URL.</p>', unsafe_allow_html=True)
                return None
            elif response.status_code == 422:
                st.markdown('<p class="error-font">Error 422: Missing or invalid query parameter!</p>', unsafe_allow_html=True)
                return None
            elif response.status_code != 200:
                st.markdown(f'<p class="error-font">Backend returned {response.status_code}: {response.text}</p>', unsafe_allow_html=True)
                return None
            
            data = response.json()
            return data
    except Exception as e:
        st.markdown(f'<p class="error-font">Error connecting to backend: {e}</p>', unsafe_allow_html=True)
        return None

# -----------------------
# On Search
# -----------------------
if search_btn:
    if query.strip() == "":
        st.markdown('<p class="error-font">Query cannot be empty!</p>', unsafe_allow_html=True)
    else:
        data = get_results(query)
        if data:
            # === FIXED: Safe parsing for all backend responses ===
            results_list = data.get("result", [])

            if not results_list:
                st.markdown('<p class="info-font">No detailed results found.</p>', unsafe_allow_html=True)
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
