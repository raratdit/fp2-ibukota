
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Your Data", layout="wide")

st.title("📊 Your Data")

# Path ke file
file_path = os.path.join("assets", "data_penduduk_indonesia.csv")

# Cek apakah file ada
if os.path.exists(file_path):
    df = pd.read_csv(file_path)
    st.dataframe(df, use_container_width=True)
else:
    st.error(f"File '{file_path}' tidak ditemukan. Pastikan file tersedia.")
