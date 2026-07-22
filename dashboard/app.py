import streamlit as st
from db import engine
from sqlalchemy import text
import pages.Obzor as page_obzor
import pages.Kompania as page_kompania
import pages.Gipotezy as page_gipotezy
import pages.Gruppy as page_gruppy

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
st.sidebar.caption("ФНС Аналитика — система риск-мониторинга")

pages[sel].render()
