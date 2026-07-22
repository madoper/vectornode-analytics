import streamlit as st
import time

st.set_page_config(page_title="TEST", layout="wide")

st.title("Hello World")
st.write("Time:", time.time())
st.write("If you can read this, Streamlit works")

st.sidebar.write("Sidebar test:", time.time())
