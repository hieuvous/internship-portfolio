from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_PATH = PROJECT_ROOT / "data" / "processed_job_posts.csv"


st.set_page_config(
    page_title="Vietnam IT Internship Market Dashboard",
    layout="wide"
)


@st.cache_data
def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        st.error(
            "Cannot find data/processed_job_posts.csv. "
            "Please run: python scripts/clean_job_posts.py"
        )
        st.stop()

    df = pd.read_csv(DATA_PATH)

    bool_cols = [col for col in df.columns if col.startswith("skill_")]
    for col in bool_cols:
        if df[col].dtype != bool:
            df[col] = df[col].astype(str).str.lower().isin(["true", "1", "yes"])

    return df


def clean_skill_name(skill_col: str) -> str:
    return skill_col.replace("skill_", "").replace("_", " ").title()


def get_skill_counts(df: pd.DataFrame) -> pd.DataFrame:
    skill_cols = [col for col in df.columns if col.startswith("skill_")]

    if not skill_cols:
        return pd.DataFrame(columns=["skill", "num_jobs"])

    skill_counts = df[skill_cols].sum().sort_values(ascending=False)

    result = skill_counts.reset_index()
    result.columns = ["skill", "num_jobs"]
    result["skill"] = result["skill"].apply(clean_skill_name)

    return result


def show_kpis(df: pd.DataFrame) -> None:
    total_jobs = len(df)
    total_companies = df["company"].nunique() if "company" in df.columns else 0

    sql_rate = df["skill_sql"].mean() * 100 if "skill_sql" in df.columns and total_jobs > 0 else 0
    python_rate = df["skill_python"].mean() * 100 if "skill_python" in df.columns and total_jobs > 0 else 0
    power_bi_rate = df["skill_power_bi"].mean() * 100 if "skill_power_bi" in df.columns and total_jobs > 0 else 0

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Job Posts", total_jobs)
    col2.metric("Companies", total_companies)
    col3.metric("SQL Demand", f"{sql_rate:.1f}%")
    col4.metric("Python Demand", f"{python_rate:.1f}%")
    col5.metric("Power BI Demand", f"{power_bi_rate:.1f}%")


def main() -> None:
    df = load_data()

    st.title("Vietnam IT Internship Market Analysis Dashboard")

    st.markdown(
        """
        This dashboard analyzes IT/Data/AI internship job postings in Vietnam.
        It helps identify common role groups, required skills, and hiring patterns.
        """
    )

    st.sidebar.header("Filters")

    filtered_df = df.copy()

    if "role_group" in df.columns:
        role_options = ["All"] + sorted(df["role_group"].dropna().unique().tolist())
        selected_role = st.sidebar.selectbox("Role Group", role_options)

        if selected_role != "All":
            filtered_df = filtered_df[filtered_df["role_group"] == selected_role]

    if "location" in df.columns:
        location_options = sorted(df["location"].dropna().unique().tolist())
        selected_locations = st.sidebar.multiselect(
            "Location",
            location_options,
            default=location_options
        )

        if selected_locations:
            filtered_df = filtered_df[filtered_df["location"].isin(selected_locations)]

    if "source" in df.columns:
        source_options = sorted(df["source"].dropna().unique().tolist())
        selected_sources = st.sidebar.multiselect(
            "Source",
            source_options,
            default=source_options
        )

        if selected_sources:
            filtered_df = filtered_df[filtered_df["source"].isin(selected_sources)]

    if "company" in df.columns:
        company_options = sorted(df["company"].dropna().unique().tolist())
        selected_companies = st.sidebar.multiselect(
            "Company",
            company_options,
            default=company_options
        )

        if selected_companies:
            filtered_df = filtered_df[filtered_df["company"].isin(selected_companies)]

    st.subheader("Key Metrics")
    show_kpis(filtered_df)

    if len(filtered_df) == 0:
        st.warning("No data available for the selected filters.")
        st.stop()

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Overview", "Skills", "Role Comparison", "Data"]
    )

    with tab1:
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
            title="Number of Job Posts by Role Group",
            text="num_jobs"
        )
        fig_role.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_role, use_container_width=True)

        if len(role_counts) > 0:
            top_role = role_counts.iloc[0]["role_group"]
            top_role_count = role_counts.iloc[0]["num_jobs"]
            st.info(
                f"**Insight:** The most common role group is **{top_role}**, "
                f"with **{top_role_count}** job posts in the current filter."
            )

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
            title="Number of Job Posts by Source",
            text="num_jobs"
        )
        fig_source.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_source, use_container_width=True)

    with tab2:
        st.subheader("Top Required Skills")

        skill_counts = get_skill_counts(filtered_df)
        top_skills = skill_counts.head(15)

        fig_skills = px.bar(
            top_skills,
            x="num_jobs",
            y="skill",
            orientation="h",
            title="Top Required Skills",
            text="num_jobs"
        )
        fig_skills.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_skills, use_container_width=True)

        if len(top_skills) > 0:
            top_skill = top_skills.iloc[0]["skill"]
            top_skill_count = top_skills.iloc[0]["num_jobs"]

            st.info(
                f"**Insight:** The most mentioned skill is **{top_skill}**, "
                f"appearing in **{top_skill_count}** job posts in the current filter."
            )

        st.dataframe(top_skills, use_container_width=True)

    with tab3:
        st.subheader("Skill Demand by Role Group")

        skill_cols = [col for col in filtered_df.columns if col.startswith("skill_")]

        selected_skill_cols = [
            col for col in [
                "skill_sql",
                "skill_python",
                "skill_excel",
                "skill_power_bi",
                "skill_tableau",
                "skill_machine_learning",
                "skill_etl",
                "skill_pytorch",
                "skill_llm",
            ]
            if col in skill_cols
        ]

        if selected_skill_cols:
            role_skill = (
                filtered_df
                .groupby("role_group")[selected_skill_cols]
                .mean()
                .reset_index()
            )

            role_skill_long = role_skill.melt(
                id_vars="role_group",
                var_name="skill",
                value_name="percentage"
            )

            role_skill_long["percentage"] = role_skill_long["percentage"] * 100
            role_skill_long["skill"] = role_skill_long["skill"].apply(clean_skill_name)

            fig_heatmap = px.density_heatmap(
                role_skill_long,
                x="skill",
                y="role_group",
                z="percentage",
                text_auto=".1f",
                title="Skill Demand Percentage by Role Group"
            )

            st.plotly_chart(fig_heatmap, use_container_width=True)

            st.info(
                "**Insight:** This heatmap shows how skill requirements differ by role group. "
                "For example, Data Analyst / BI roles usually emphasize SQL, Excel, and BI tools, "
                "while AI / ML roles tend to emphasize Python and machine learning."
            )

            st.dataframe(role_skill_long, use_container_width=True)

    with tab4:
        st.subheader("Data Preview")

        preview_cols = [
            "job_id",
            "job_title",
            "company",
            "location",
            "source",
            "employment_type",
            "role_group",
            "salary",
            "url",
        ]

        available_cols = [col for col in preview_cols if col in filtered_df.columns]

        st.dataframe(
            filtered_df[available_cols],
            use_container_width=True
        )

        st.download_button(
            label="Download filtered data as CSV",
            data=filtered_df.to_csv(index=False, encoding="utf-8-sig"),
            file_name="filtered_job_posts.csv",
            mime="text/csv"
        )


if __name__ == "__main__":
    main()