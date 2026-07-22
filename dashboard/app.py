import streamlit as st
from db import engine
from sqlalchemy import text

st.set_page_config(
    page_title="ФНС Аналитика",
    page_icon="static/logo.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.markdown("# ФНС Аналитика")
st.sidebar.caption("Система риск-мониторинга")

try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    st.success("✅ Подключение к БД установлено")
except Exception as e:
    st.error(f"⚠️ Нет подключения к БД: {e}")

st.info("Выберите дашборд в боковом меню слева")
