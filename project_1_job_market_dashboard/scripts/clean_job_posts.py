from pathlib import Path
import csv
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_PATH = PROJECT_ROOT / "data" / "raw_job_posts.csv"
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed_job_posts.csv"


REQUIRED_COLUMNS = [
    "job_id",
    "job_title",
    "company",
    "location",
    "source",
    "employment_type",
    "role_group",
    "salary",
    "description",
    "requirements",
    "skills_text",
    "posted_date",
    "url",
]


SKILL_PATTERNS = {
    "sql": ["sql"],
    "python": ["python"],
    "excel": ["excel", "spreadsheet", "google sheets"],
    "power_bi": ["power bi", "powerbi", "power-bi"],
    "tableau": ["tableau"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "scikit_learn": ["scikit-learn", "sklearn", "scikit learn"],
    "machine_learning": ["machine learning", "ml model", "classification", "regression"],
    "deep_learning": ["deep learning", "neural network", "cnn", "rnn", "transformer"],
    "etl": ["etl", "elt", "data pipeline", "pipeline"],
    "postgresql": ["postgresql", "postgres"],
    "mysql": ["mysql"],
    "mongodb": ["mongodb", "mongo"],
    "spark": ["spark", "pyspark"],
    "pytorch": ["pytorch", "torch"],
    "tensorflow": ["tensorflow"],
    "hugging_face": ["hugging face", "transformers"],
    "dashboard": ["dashboard", "reporting", "report", "bi report"],
    "data_visualization": ["data visualization", "visualization", "data viz", "chart"],
    "airflow": ["airflow"],
    "aws": ["aws", "amazon web services"],
    "gcp": ["gcp", "google cloud"],
    "llm": ["llm", "large language model", "prompt engineering", "agent"],
}


LABEL_MAPPING = {
    "Data analyst": "Data Analyst / BI",
    "data analyst": "Data Analyst / BI",
    "DA": "Data Analyst / BI",
    "BI": "Data Analyst / BI",
    "AI/ML": "AI / ML",
    "AI - ML": "AI / ML",
    "Data engineering": "Data Engineer",
    "BA": "Business Analyst",
}


def repair_bad_csv_rows(path: Path) -> pd.DataFrame:
    """
    Reads a CSV file and repairs rows where location contains an unquoted comma.
    Example bad row:
    JD017,...,Hà Nội, Hồ Chí Minh,TopCV,...

    Expected schema has 13 columns.
    If a row has 14 columns, we merge columns 3 and 4 as location.
    """
    rows = []

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        expected_len = len(header)

        if header != REQUIRED_COLUMNS:
            print("Warning: header is different from expected schema.")
            print("Current header:", header)

        for line_num, row in enumerate(reader, start=2):
            if len(row) == expected_len:
                rows.append(row)
            elif len(row) == expected_len + 1:
                # Common case: location has one unquoted comma.
                repaired = row[:3] + [row[3].strip() + ", " + row[4].strip()] + row[5:]
                rows.append(repaired)
                print(f"Repaired row {line_num}: merged location columns.")
            else:
                raise ValueError(
                    f"Cannot repair row {line_num}. "
                    f"Expected {expected_len} columns, got {len(row)} columns.\n"
                    f"Row: {row}"
                )

    return pd.DataFrame(rows, columns=header)


def normalize_text_series(series: pd.Series) -> pd.Series:
    return (
        series
        .fillna("")
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )


def contains_any_pattern(text: str, patterns: list[str]) -> bool:
    text = str(text).lower()
    return any(pattern.lower() in text for pattern in patterns)


def main() -> None:
    if not RAW_PATH.exists():
        raise FileNotFoundError(f"Cannot find raw data file: {RAW_PATH}")

    df = repair_bad_csv_rows(RAW_PATH)

    df.columns = df.columns.str.strip().str.lower()

    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    text_cols = [
        "job_id",
        "job_title",
        "company",
        "location",
        "source",
        "employment_type",
        "role_group",
        "salary",
        "description",
        "requirements",
        "skills_text",
        "posted_date",
        "url",
    ]

    for col in text_cols:
        df[col] = normalize_text_series(df[col])

    df["location"] = df["location"].replace("", "Unknown")
    df["salary"] = df["salary"].replace("", "Not specified")
    df["role_group"] = df["role_group"].replace("", "Software / Other")
    df["role_group"] = df["role_group"].replace(LABEL_MAPPING)

    before = len(df)

    df = df.drop_duplicates(
        subset=["job_title", "company", "url"],
        keep="first"
    )

    after = len(df)

    df["full_text"] = (
        df["job_title"] + " " +
        df["description"] + " " +
        df["requirements"] + " " +
        df["skills_text"]
    ).str.lower()

    for skill_name, patterns in SKILL_PATTERNS.items():
        df[f"skill_{skill_name}"] = df["full_text"].apply(
            lambda text: contains_any_pattern(text, patterns)
        )

    skill_cols = [col for col in df.columns if col.startswith("skill_")]

    print("Raw rows:", before)
    print("Rows after duplicate removal:", after)
    print("Removed duplicates:", before - after)
    print()
    print("Role distribution:")
    print(df["role_group"].value_counts())
    print()
    print("Top skills:")
    print(df[skill_cols].sum().sort_values(ascending=False).head(15))

    df.to_csv(PROCESSED_PATH, index=False, encoding="utf-8-sig")

    print()
    print(f"Processed data saved to: {PROCESSED_PATH}")


if __name__ == "__main__":
    main()