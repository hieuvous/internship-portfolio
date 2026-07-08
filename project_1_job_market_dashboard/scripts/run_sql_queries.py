from pathlib import Path
import sqlite3
import re
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_PATH = PROJECT_ROOT / "database" / "job_market.db"
SQL_PATH = PROJECT_ROOT / "sql" / "analysis_queries.sql"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "sql_results"


def split_sql_queries(sql_text: str) -> list[tuple[str, str]]:
    """
    Splits SQL file into named queries.
    Query name is taken from comments like:
    -- Query 01: Total job posts
    """
    pattern = r"--\s*(Query\s+\d+:\s*.+)"
    parts = re.split(pattern, sql_text)

    queries = []

    if len(parts) < 3:
        raw_queries = [q.strip() for q in sql_text.split(";") if q.strip()]
        return [(f"query_{i+1:02d}", q + ";") for i, q in enumerate(raw_queries)]

    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        query = parts[i + 1].strip()

        if query:
            query = query.rstrip(";") + ";"
            safe_name = (
                title.lower()
                .replace(":", "")
                .replace(" ", "_")
                .replace("/", "_")
            )
            safe_name = re.sub(r"[^a-z0-9_]+", "", safe_name)
            queries.append((safe_name, query))

    return queries


def main() -> None:
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Cannot find database: {DATABASE_PATH}\n"
            "Run scripts/create_database.py first."
        )

    if not SQL_PATH.exists():
        raise FileNotFoundError(f"Cannot find SQL file: {SQL_PATH}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    sql_text = SQL_PATH.read_text(encoding="utf-8")
    queries = split_sql_queries(sql_text)

    conn = sqlite3.connect(DATABASE_PATH)

    for name, query in queries:
        try:
            result_df = pd.read_sql_query(query, conn)
            output_path = OUTPUT_DIR / f"{name}.csv"
            result_df.to_csv(output_path, index=False, encoding="utf-8-sig")

            print(f"Saved: {output_path}")
            print(result_df.head())
            print("-" * 80)

        except Exception as exc:
            print(f"Failed query: {name}")
            print(query)
            print("Error:", exc)
            print("-" * 80)

    conn.close()


if __name__ == "__main__":
    main()