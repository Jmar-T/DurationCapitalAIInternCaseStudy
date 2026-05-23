# Dispatch Performance Reporting Pipeline

A lightweight, automated Python data pipeline that processes raw dispatch logs, handles real-world data logging anomalies, and generates structured, weekly operational performance text reports.

## 🚀 Getting Started

### Dependencies
* **Python 3.x** (Core environment)
* All data manipulation is handled via the Python standard library and standard data science packages (`pandas`).

### Project Structure
```plaintext```
├── data/
│   └── dispatch_log_q1(in).csv      # Raw log input
├── src/
│   └── build_reports.py             # Pipeline execution script
└── results/
    └── report_YYYY-MM-DD_to_...     # Automated weekly text outputs

### Execution
* Run the pipeline from the root directory:
```python src/build_reports.py```

### Core Assumptions & Operational Logic

Real-world dispatch logs contain manual entry noise. To protect the statistical integrity of the weekly reports, the pipeline applies the following explicit business logic

1. The "Unassigned Driver" Paradox
The raw dataset contains orders with a blank or "UNASSIGNED" driver ID that still register an explicit on-time status (Y/N).
Logic: Rather than discarding these rows, the pipeline preserves them in a distinct UNASSIGNED category. Operational assumptions suggest these represent automated dispatches or third-party couriers missing from the core driver registry.
2. Deterministic Client Identity Consolidation
Due to human typing variations, punctuation, and corporate suffixes, a single business entity often appeared under multiple names (e.g., "Brigham & Women's" vs. "Brigham and Womens", or "LabCorp" vs. "Labcorp Inc").
Logic: Across the raw dataset, exactly 24 unique dirty client name variations were identified. To ensure absolute data precision, the pipeline bypasses unpredictable fuzzy-matching algorithms in favor of a 100% deterministic, hardcoded normalization dictionary to guarantee perfectly pooled client statistics.
3. Null Exception Values as a "Clean Run"
The exception_notes column contains frequent empty cells, which load into data frames as missing or NaN values.
Logic: The pipeline assumes an empty cell implies a "clean run" (no logistical friction occurred). The logic safely filters out these null fields and whitespace tokens to calculate a precise, non-inflated Exception Volume for each weekly period.
4. Categorical Case Standardization
Logging variations like "STAT", "Stat", and "stat" artificially split the data into separate columns during analysis.
Logic: The pipeline forces service_type to lowercase and on_time statuses to uppercase, ensuring clean, consolidated groups without duplicate categories.