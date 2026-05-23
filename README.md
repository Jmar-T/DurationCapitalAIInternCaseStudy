Markdown
# Dispatch Performance & Client Tracking Pipeline

A lightweight, automated Python data suite that processes raw dispatch logs, applies zero-shot machine learning triage to operational exceptions, and provides an interactive, secure real-time tracking portal for logistics clients.

## 🚀 Getting Started

### Dependencies & Environment Setup
This pipeline utilizes external machine learning frameworks and data analysis toolkits. To ensure all library versions match perfectly without manual troubleshooting, initialize your environment using the provided requirements layout:

1. Clone or download the repository to your machine.
2. Open your terminal in the root directory and install the necessary dependencies via `pip`:
```bash
   pip install -r requirements.txt
```
### Project Structure
├── data/
│   └── dispatch_log_q1(in).csv        # Raw logistics log input
├── src/
│   ├── build_reports.py               # Automated pipeline execution script
│   ├── clean_data.py                  # Core data cleaning & string normalization library
│   └── inquires.py                    # Interactive client tracking portal application
├── models/
│   └── distilbart_zero_shot/          # Local ML cache folder (Excluded from Git tracking)
└── results/
    ├── report_YYYY-MM-DD_to_...       # Automated weekly text outputs
    ├── urgent_actions_YYYY-MM-DD...   # Timestamped critical exception logs
    ├── deferred_actions_YYYY-MM-DD... # Timestamped non-critical exception logs
    └── log_only_records_YYYY-MM-DD... # Timestamped minor operational logs
### Execution
## To process the raw data and generate the weekly performance summaries along with the ML triage outputs:
Bash
  python src/build_reports.py
To launch the client-facing tracking portal:
Bash
  ```python src/inquires.py```
### Core Assumptions & Operational Logic
Real-world dispatch logs contain manual entry noise. To protect the statistical integrity of the weekly reports and ensure reliable customer lookup performance, the application enforces the following explicit design choices:
1. The "Unassigned Driver" Paradox
The raw dataset contains orders with a blank or "UNASSIGNED" driver ID that still register an explicit on-time status (Y/N).
Logic: Rather than discarding these rows, the pipeline preserves them in a distinct UNASSIGNED category. Operational assumptions suggest these represent automated dispatches or third-party couriers missing from the core driver registry.
2. Deterministic Client Identity Consolidation
Due to human typing variations, punctuation, and corporate suffixes, a single business entity often appeared under multiple names (e.g., "Brigham & Women's" vs. "Brigham and Womens", or "LabCorp" vs. "Labcorp Inc").
Logic: Across the raw dataset, exactly 24 unique dirty client name variations were identified. To ensure absolute data precision, the pipeline bypasses unpredictable fuzzy-matching algorithms in favor of a centralized, 100% deterministic hardcoded normalization dictionary inside clean_data.py. This ensures perfect parity between historical reporting files and interactive user input lookups.
3. Ingestion-Layer Filtering of "Clean Runs"
The exception_notes column contains frequent empty cells, which load into dataframes as missing or NaN values.
Logic: The pipeline assumes an empty cell implies a "clean run" (the delivery occurred with zero logistical friction). To maximize operational efficiency and maintain a high Signal-to-Noise Ratio, rows with missing or blank exception notes are completely skipped at the ingestion layer. They are not processed by the machine learning model or written to output logs, focusing 100% of dispatch attention on actual system variances.
4. Categorical Case Standardization
Logging variations like "STAT", "Stat", and "stat" artificially split data into separate columns during database aggregations.
Logic: The pipeline forces service_type variables to lowercase and on_time statuses to uppercase, eliminating duplicate metrics and ensuring clean, consolidated reporting blocks.
5. Step-Based Milestone Status Routing
The dataset does not contain a dedicated "Delivery Status" text column.
Logic: The client tracking portal handles this by evaluating the structural presence of chronological timestamps. An order's current position in the physical world is derived deterministically using the following state hierarchy:
If delivery_time contains a valid timestamp → DELIVERED.
If pickup_time is populated but delivery_time is blank → EN ROUTE.
If dispatch_time is populated but pickup_time is blank → DISPATCHED (Driver assigned, traveling to origin).
6. Client Data Security Gate
To prevent clients from accidentally or intentionally scraping information belonging to other business entities, lookups require a two-factor security validation match.
Logic: A customer query will completely fail with an Access Denied status unless both the client corporate name string (normalized through the clean_data engine) and the precise alphanumeric Order ID string (strictly matching the ORD-XXXXX layout via regular expressions) match a single historical entry.
7. Weight Caching Strategy
Machine learning model weights (model.safetensors) exceed the standard 100 MB GitHub file push limits.
Logic: The codebase is designed to isolate model weights locally inside a tracked .gitignore path (models/). Upon execution, the script checks if the local path exists; if it does not, it securely streams the model from Hugging Face once and builds a permanent local cache, bypassing long initial download sequences on subsequent executions.