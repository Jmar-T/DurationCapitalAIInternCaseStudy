# Dispatch Performance & Client Tracking Pipeline

A lightweight, automated Python data suite that processes raw dispatch logs, applies zero-shot machine learning triage to operational exceptions, and provides an interactive, secure real-time tracking portal for logistics clients.

## Getting Started

### Dependencies & Environment Setup
This pipeline utilizes external machine learning frameworks and data analysis toolkits. To ensure all library versions match perfectly without manual troubleshooting, initialize your environment using the provided requirements layout:

1. Clone or download the repository to your machine.
2. Open your terminal in the root directory and install the necessary dependencies via `pip`:
   ```bash
   pip install -r requirements.txt

### Project Structure

```Plaintext
├── data/
│   ├── dispatch_log_q1(in).csv        # Raw logistics log input
│   ├── local_client_notes.csv         # Local operational notes cache (Git ignored)
│   └── local_driver_notes.csv         # Local operator tribal knowledge (Git ignored)
├── src/
│   ├── build_reports.py               # Automated pipeline execution script
│   ├── clean_data.py                  # Core data cleaning & string normalization library
│   ├── inquires.py                    # Interactive client tracking portal application
│   └── operator_notes.py              # Standalone tribal knowledge management engine
├── models/
│   └── distilbart_zero_shot/          # Local ML cache folder (Excluded from Git tracking)
└── results/
    ├── report_YYYY-MM-DD_to_...       # Automated weekly text outputs
    ├── urgent_actions_YYYY-MM-DD...   # Timestamped critical exception logs
    ├── deferred_actions_YYYY-MM-DD... # Timestamped non-critical exception logs
    └── log_only_records_YYYY-MM-DD... # Timestamped minor operational logs
```
### Execution

To process raw logs and generate weekly performance metrics with ML triage output files:

```Bash
python src/build_reports.py
```
To launch the client-facing tracking portal:
```Bash
python src/inquires.py
```
To launch the internal operator notes and tribal knowledge management system:
```Bash
python src/operator_notes.py
```
To triage the exception notes:
```Bash
python src/exception_triage.py
```
 Core Operational Logic & Assumptions
Real-world dispatch logs contain manual entry noise. To protect the statistical integrity of the analytics, the system applies the following explicit data processing logic:
1. The "Unassigned Driver" Paradox
The raw dataset contains orders with an "UNASSIGNED" driver ID that still register an explicit on-time status (Y/N).
Logic: Rather than discarding these rows, the pipeline preserves them in a distinct UNASSIGNED category. Operational assumptions suggest these represent automated dispatches or third-party couriers missing from the core driver registry.
2. Deterministic Client Identity Consolidation
Due to human typing variations, punctuation, and corporate suffixes, a single business entity often appeared under multiple names (e.g., "Brigham & Women's" vs. "Brigham and Womens").
Logic: Across the raw dataset, exactly 24 unique dirty client name variations were identified. To ensure absolute data precision, the pipeline uses a 100% deterministic hardcoded normalization dictionary inside clean_data.py. This ensures perfect parity between historical reporting files and interactive user input lookups.
3. Ingestion-Layer Filtering of "Clean Runs"
The exception_notes column contains frequent empty cells, which load into dataframes as missing or NaN values.
Logic: The pipeline assumes an empty cell implies a "clean run" (the delivery occurred with zero logistical friction). Rows with missing or blank exception notes are completely skipped at the ingestion layer. They are not processed by the machine learning model or written to output logs, focusing 100% of dispatch attention on actual system variances.
4. Step-Based Milestone Status Routing
The dataset does not contain a dedicated "Delivery Status" text column.
Logic: The client tracking portal handles this by evaluating the structural presence of chronological timestamps. An order's current position in the physical world is derived deterministically using the following state hierarchy:
If delivery_time contains a valid timestamp → DELIVERED.
If pickup_time is populated but delivery_time is blank → EN ROUTE.
If dispatch_time is populated but pickup_time is blank → DISPATCHED (Driver assigned, traveling to origin).