from sqlalchemy import create_engine
import pandas as pd
import streamlit as st

DB_URL = "postgresql+psycopg2://podft:podft-secret@localhost:5432/analytics"

@st.cache_data(ttl=300)
def load_company_year():
    return pd.read_sql("SELECT * FROM reporting.rpt_company_year", DB_URL)

@st.cache_data(ttl=300)
def load_anomaly():
    return pd.read_sql("SELECT * FROM reporting.rpt_anomaly", DB_URL)

@st.cache_data(ttl=300)
def load_hypothesis_flags():
    return pd.read_sql("SELECT * FROM reporting.rpt_company_hypothesis_flags", DB_URL)

@st.cache_data(ttl=300)
def load_group_signal():
    return pd.read_sql("SELECT * FROM reporting.rpt_group_signal", DB_URL)

@st.cache_data(ttl=300)
def load_hypothesis_summary():
    return pd.read_sql("SELECT * FROM reporting.rpt_hypothesis_summary", DB_URL)

def load_all():
    return {
        "company_year": load_company_year(),
        "anomaly": load_anomaly(),
        "hypothesis_flags": load_hypothesis_flags(),
        "group_signal": load_group_signal(),
        "hypothesis_summary": load_hypothesis_summary(),
    }
