import streamlit as st
import requests

API_BASE = "http://localhost:8000/api/v1" #For demo purpose, we should put it inside env actually

st.set_page_config(page_title="Email Ledger Demo", layout="wide")
st.title("Email Ledger Demo UI")

# Transactions Section
st.header("Transactions")
if st.button("Refresh Transactions") or 'transactions' not in st.session_state:
    try:
        resp = requests.get(f"{API_BASE}/transactions")
        resp.raise_for_status()
        data = resp.json()
        st.session_state['transactions'] = data
    except Exception as e:
        st.error(f"Error fetching transactions: {e}")
        st.session_state['transactions'] = []
data = st.session_state.get('transactions', [])
if data:
    st.dataframe(data)
else:
    st.info("No transactions found.")

# Summary Section
st.header("Summary")
if st.button("Refresh Summary") or 'summary' not in st.session_state:
    try:
        resp = requests.get(f"{API_BASE}/summary")
        resp.raise_for_status()
        st.session_state['summary'] = resp.json()
    except Exception as e:
        st.error(f"Error fetching summary: {e}")
        st.session_state['summary'] = {}
summary = st.session_state.get('summary', {})
if summary:
    st.json(summary)
else:
    st.info("No summary data available.")

# Process Recent Emails Section
st.header("Process Recent Emails")
email_count = st.number_input("Number of recent emails to process", min_value=1, max_value=100, value=10, step=1)
if st.button("Process"):
    try:
        resp = requests.post(f"{API_BASE}/process-recent-emails", params={"email_count": int(email_count)})
        resp.raise_for_status()
        result = resp.json()
        st.success("Processing complete!")
        st.json(result)
    except Exception as e:
        st.error(f"Error processing emails: {e}")
