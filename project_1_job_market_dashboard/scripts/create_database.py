from pathlib import Path
import sqlite3
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_PATH = PROJECT_ROOT / "data" / "processed_job_posts.csv"
DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_PATH = DATABASE_DIR / "job_market.db"


def main() -> None:
    if not PROCESSED_PATH.exists():
        raise FileNotFoundError(
            f"Cannot find processed data: {PROCESSED_PATH}\n"
            "Run scripts/clean_job_posts.py first."
        )

    DATABASE_DIR.mkdir(exist_ok=True)

    df = pd.read_csv(PROCESSED_PATH)

    conn = sqlite3.connect(DATABASE_PATH)

    df.to_sql("job_posts", conn, if_exists="replace", index=False)

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM job_posts;")
    total_rows = cursor.fetchone()[0]

    conn.close()

    print(f"Database created at: {DATABASE_PATH}")
    print(f"Table created: job_posts")
    print(f"Total rows inserted: {total_rows}")


if __name__ == "__main__":
    main()