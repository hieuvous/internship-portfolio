import pandas as pd
import streamlit as st
import plotly.express as px

# Page config
st.set_page_config(
    page_title="Vietnam IT Internship Market Dashboard",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("data/processed_job_posts.csv")

df = load_data()

# Title
st.title("Vietnam IT Internship Market Analysis Dashboard")

st.markdown("""
This dashboard analyzes Data/AI/BI internship job postings in Vietnam.
It helps identify common role groups, required skills, and hiring patterns.
""")

# Sidebar filters
st.sidebar.header("Filters")

filtered_df = df.copy()

role_options = ["All"] + sorted(df["role_group"].dropna().unique().tolist())
selected_role = st.sidebar.selectbox("Role Group", role_options)

if selected_role != "All":
    filtered_df = filtered_df[filtered_df["role_group"] == selected_role]

location_options = sorted(df["location"].dropna().unique().tolist())
selected_locations = st.sidebar.multiselect(
    "Location",
    location_options,
    default=location_options
)

if selected_locations:
    filtered_df = filtered_df[filtered_df["location"].isin(selected_locations)]

company_options = sorted(df["company"].dropna().unique().tolist())
selected_companies = st.sidebar.multiselect(
    "Company",
    company_options,
    default=company_options
)

if selected_companies:
    filtered_df = filtered_df[filtered_df["company"].isin(selected_companies)]

# KPIs
st.subheader("Key Metrics")

total_jobs = len(filtered_df)
total_companies = filtered_df["company"].nunique()

sql_rate = filtered_df["skill_sql"].mean() * 100 if total_jobs > 0 else 0
python_rate = filtered_df["skill_python"].mean() * 100 if total_jobs > 0 else 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Job Posts", total_jobs)
col2.metric("Companies", total_companies)
col3.metric("SQL Demand", f"{sql_rate:.1f}%")
col4.metric("Python Demand", f"{python_rate:.1f}%")

if total_jobs == 0:
    st.warning("No data available for the selected filters.")
    st.stop()

# Chart 1: role distribution
st.subheader("Job Posts by Role Group")

role_counts = (
    filtered_df["role_group"]
    .value_counts()
    .reset_index()
)

role_counts.columns = ["role_group", "num_jobs"]

fig_role = px.bar(
    role_counts,
    x="num_jobs",
    y="role_group",
    orientation="h",
    title="Number of Job Posts by Role Group"
)

st.plotly_chart(fig_role, use_container_width=True)

if len(role_counts) > 0:
    top_role = role_counts.iloc[0]["role_group"]
    top_role_count = role_counts.iloc[0]["num_jobs"]

    st.info(
        f"The most common role group is **{top_role}**, "
        f"with **{top_role_count}** job posts in the current filter."
    )

# Chart 2: top skills
st.subheader("Top Required Skills")

skill_cols = [col for col in filtered_df.columns if col.startswith("skill_")]

skill_counts = filtered_df[skill_cols].sum().sort_values(ascending=False)

skill_counts_clean = skill_counts.copy()
skill_counts_clean.index = (
    skill_counts_clean.index
    .str.replace("skill_", "", regex=False)
    .str.replace("_", " ", regex=False)
)

top_skills = skill_counts_clean.head(10).reset_index()
top_skills.columns = ["skill", "num_jobs"]

fig_skills = px.bar(
    top_skills,
    x="num_jobs",
    y="skill",
    orientation="h",
    title="Top 10 Required Skills"
)

st.plotly_chart(fig_skills, use_container_width=True)

if len(top_skills) > 0:
    top_skill = top_skills.iloc[0]["skill"]
    top_skill_count = top_skills.iloc[0]["num_jobs"]

    st.info(
        f"The most mentioned skill is **{top_skill}**, "
        f"appearing in **{top_skill_count}** job posts in the current filter."
    )

# Chart 3: source distribution
st.subheader("Job Posts by Source")

source_counts = (
    filtered_df["source"]
    .value_counts()
    .reset_index()
)

source_counts.columns = ["source", "num_jobs"]

fig_source = px.bar(
    source_counts,
    x="num_jobs",
    y="source",
    orientation="h",
    title="Number of Job Posts by Source"
)

st.plotly_chart(fig_source, use_container_width=True)

# Data preview
st.subheader("Data Preview")

preview_cols = [
    "job_title", "company", "location",
    "source", "role_group", "url"
]

available_preview_cols = [col for col in preview_cols if col in filtered_df.columns]

st.dataframe(filtered_df[available_preview_cols], use_container_width=True)