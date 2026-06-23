import streamlit as st
import pandas as pd

st.title("Vietnam IT Internship Market Analysis Dashboard")

df = pd.read_csv("data/processed_job_posts.csv")

st.write(df.head())