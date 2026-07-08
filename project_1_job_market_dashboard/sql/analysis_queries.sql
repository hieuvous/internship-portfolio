-- Query 01: Total job posts
SELECT 
    COUNT(*) AS total_jobs
FROM job_posts;

-- Query 02: Job count by role group
SELECT 
    role_group,
    COUNT(*) AS num_jobs
FROM job_posts
GROUP BY role_group
ORDER BY num_jobs DESC;

-- Query 03: Job count by location
SELECT 
    location,
    COUNT(*) AS num_jobs
FROM job_posts
GROUP BY location
ORDER BY num_jobs DESC;

-- Query 04: Top companies by number of job posts
SELECT 
    company,
    COUNT(*) AS num_jobs
FROM job_posts
GROUP BY company
ORDER BY num_jobs DESC
LIMIT 10;

-- Query 05: Job count by source
SELECT 
    source,
    COUNT(*) AS num_jobs
FROM job_posts
GROUP BY source
ORDER BY num_jobs DESC;

-- Query 06: Skill demand overview
SELECT 
    SUM(skill_sql) AS sql_count,
    SUM(skill_python) AS python_count,
    SUM(skill_excel) AS excel_count,
    SUM(skill_power_bi) AS power_bi_count,
    SUM(skill_tableau) AS tableau_count,
    SUM(skill_machine_learning) AS machine_learning_count,
    SUM(skill_etl) AS etl_count,
    SUM(skill_pytorch) AS pytorch_count,
    SUM(skill_llm) AS llm_count
FROM job_posts;

-- Query 07: SQL and Python demand percentage
SELECT 
    COUNT(*) AS total_jobs,
    SUM(skill_sql) AS sql_jobs,
    ROUND(SUM(skill_sql) * 100.0 / COUNT(*), 2) AS sql_percentage,
    SUM(skill_python) AS python_jobs,
    ROUND(SUM(skill_python) * 100.0 / COUNT(*), 2) AS python_percentage
FROM job_posts;

-- Query 08: Skill profile
SELECT 
    CASE 
        WHEN skill_sql = 1 AND skill_python = 1 THEN 'SQL + Python'
        WHEN skill_sql = 1 THEN 'SQL only'
        WHEN skill_python = 1 THEN 'Python only'
        ELSE 'Neither'
    END AS skill_profile,
    COUNT(*) AS num_jobs
FROM job_posts
GROUP BY skill_profile
ORDER BY num_jobs DESC;

-- Query 09: Top skills using CTE
WITH skill_counts AS (
    SELECT 'SQL' AS skill, SUM(skill_sql) AS num_jobs FROM job_posts
    UNION ALL
    SELECT 'Python', SUM(skill_python) FROM job_posts
    UNION ALL
    SELECT 'Excel', SUM(skill_excel) FROM job_posts
    UNION ALL
    SELECT 'Power BI', SUM(skill_power_bi) FROM job_posts
    UNION ALL
    SELECT 'Tableau', SUM(skill_tableau) FROM job_posts
    UNION ALL
    SELECT 'Machine Learning', SUM(skill_machine_learning) FROM job_posts
    UNION ALL
    SELECT 'ETL', SUM(skill_etl) FROM job_posts
    UNION ALL
    SELECT 'PostgreSQL', SUM(skill_postgresql) FROM job_posts
    UNION ALL
    SELECT 'MySQL', SUM(skill_mysql) FROM job_posts
    UNION ALL
    SELECT 'PyTorch', SUM(skill_pytorch) FROM job_posts
    UNION ALL
    SELECT 'LLM', SUM(skill_llm) FROM job_posts
)
SELECT 
    skill,
    num_jobs
FROM skill_counts
ORDER BY num_jobs DESC;

-- Query 10: Skill demand by role group
SELECT
    role_group,
    COUNT(*) AS total_jobs,
    SUM(skill_sql) AS sql_count,
    ROUND(SUM(skill_sql) * 100.0 / COUNT(*), 2) AS sql_pct,
    SUM(skill_python) AS python_count,
    ROUND(SUM(skill_python) * 100.0 / COUNT(*), 2) AS python_pct,
    SUM(skill_excel) AS excel_count,
    ROUND(SUM(skill_excel) * 100.0 / COUNT(*), 2) AS excel_pct,
    SUM(skill_power_bi) AS power_bi_count,
    ROUND(SUM(skill_power_bi) * 100.0 / COUNT(*), 2) AS power_bi_pct,
    SUM(skill_machine_learning) AS ml_count,
    ROUND(SUM(skill_machine_learning) * 100.0 / COUNT(*), 2) AS ml_pct,
    SUM(skill_etl) AS etl_count,
    ROUND(SUM(skill_etl) * 100.0 / COUNT(*), 2) AS etl_pct
FROM job_posts
GROUP BY role_group
ORDER BY total_jobs DESC;

-- Query 11: Data Analyst / BI jobs requiring SQL or Power BI
SELECT 
    job_title,
    company,
    location,
    salary,
    url
FROM job_posts
WHERE role_group = 'Data Analyst / BI'
  AND (skill_sql = 1 OR skill_power_bi = 1)
ORDER BY company;

-- Query 12: AI / ML jobs requiring Python or Machine Learning
SELECT 
    job_title,
    company,
    location,
    salary,
    url
FROM job_posts
WHERE role_group = 'AI / ML'
  AND (skill_python = 1 OR skill_machine_learning = 1)
ORDER BY company;