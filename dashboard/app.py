import streamlit as st
from db import engine
from sqlalchemy import text
import page_obzor
import page_kompania
import page_gipotezy
import page_gruppy

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
    "Обзор": page_obzor,
    "Компания": page_kompania,
    "Гипотезы": page_gipotezy,
    "Группы": page_gruppy,
}

sel = st.sidebar.radio("Дашборд", list(pages.keys()))
st.sidebar.markdown("---")
st.sidebar.caption("ФНС Аналитика — риск-мониторинг")

pages[sel]
