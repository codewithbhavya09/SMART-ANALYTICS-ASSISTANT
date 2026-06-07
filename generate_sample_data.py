"""
generate_sample_data.py
=======================
Utility script that creates a rich sample CSV file for testing
the Smart Analytics Assistant without needing a real dataset.

Run:
    python generate_sample_data.py

Output:
    sample_data.csv  (500 rows, mixed column types)
"""

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
n = 500

departments = ["Engineering", "Marketing", "Sales", "HR", "Finance", "Operations"]
cities = ["New York", "San Francisco", "Chicago", "Austin", "Boston", "Seattle", "Denver"]
statuses = ["Active", "Inactive", "Pending", "Suspended"]

df = pd.DataFrame(
    {
        "employee_id": range(1001, 1001 + n),
        "name": [f"Employee_{i}" for i in range(n)],
        "age": rng.integers(22, 65, n),
        "salary": rng.normal(75_000, 20_000, n).round(2),
        "bonus": rng.exponential(5_000, n).round(2),
        "years_experience": rng.integers(0, 40, n),
        "performance_score": rng.uniform(1, 10, n).round(2),
        "department": rng.choice(departments, n),
        "city": rng.choice(cities, n),
        "status": rng.choice(statuses, n, p=[0.75, 0.10, 0.10, 0.05]),
        "remote_work": rng.choice([True, False], n, p=[0.45, 0.55]),
        "hire_date": pd.date_range("2010-01-01", periods=n, freq="D")
        .to_series()
        .sample(n, replace=True, random_state=42)
        .values,
    }
)

# Introduce some missing values
for col in ["salary", "bonus", "performance_score", "city"]:
    mask = rng.random(n) < 0.05  # ~5 % missing
    df.loc[mask, col] = np.nan

# Introduce some duplicates
dup_rows = df.sample(10, random_state=1)
df = pd.concat([df, dup_rows], ignore_index=True)

# Shuffle
df = df.sample(frac=1, random_state=99).reset_index(drop=True)

df.to_csv("sample_data.csv", index=False)
print(f"✅ sample_data.csv created — {len(df):,} rows × {len(df.columns)} columns")
