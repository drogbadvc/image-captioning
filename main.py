import streamlit as st
from views.dashboard import dashboard

st.set_page_config(page_title="Analyzing and Quickview Link Weights", layout="wide")


def view():
    dashboard()


view()
