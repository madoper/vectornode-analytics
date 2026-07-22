import streamlit as st
from db import engine
from sqlalchemy import text
from modules import obzor as page_obzor
from modules import kompania as page_kompania
from modules import gipotezy as page_gipotezy
from modules import gruppy as page_gruppy

st.set_page_config(
    page_title="ФНС Аналитика",
    page_icon="static/logo.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
except Exception as e:
    st.error(f"Нет подключения к БД: {e}")
    st.stop()

pages = {
    "Обзор": _page_obzor,
    "Компания": _page_kompania,
    "Гипотезы": _page_gipotezy,
    "Группы": _page_gruppy,
}

sel = st.sidebar.radio("Дашборд", list(pages.keys()))
st.sidebar.markdown("---")
st.sidebar.caption("ФНС Аналитика — риск-мониторинг")

pages[sel]
