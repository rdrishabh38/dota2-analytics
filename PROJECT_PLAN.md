# Project Design: Dota 2 Analytics Hub

## 1. Project Overview

### Vision
To create a personal Dota 2 analytics tool that allows a player to download, analyze, and visualize their performance and behavior data over time. The project will support **multiple Steam accounts (profiles)**, allowing users to manage data from different sources seamlessly. The project will start by focusing on the **Behavior Score and Conduct Summary** and will be designed to be easily expandable.

### Core Features
- **Multi-Profile Support**: Manage and download data for multiple Steam accounts within the same application.
- **Automated Data Ingestion**: A script to fetch all available conduct summary data for the selected profile.
- **Intelligent Syncing**: The downloader will perform a full historical download on the first run and efficient, incremental syncs on subsequent runs to only fetch new data.
- **Data Processing**: A separate script to parse the raw data, clean it, and structure it into a usable format.
- **Data Isolation**: All raw and processed data for each profile is stored in separate, dedicated directories.

---

## 2. System Architecture & Profile Management

The core two-phase architecture remains, but it will now operate within the context of an **active profile** selected in the configuration.

### Profile Switching
The user can switch between profiles by changing the `active_profile` value in the `config.json` file. The scripts will read this value on startup to determine which profile's cookies and data directories to use.

### Updated Configuration (`config.json`)
The configuration will be updated to hold a list of profiles, each with a unique name and its own set of cookies.

```json
{
  "active_profile": "Main_Account",
  "profiles": [
    {
      "profile_name": "Main_Account",
      "cookies": {
        "sessionid": "SESSIONID_FOR_MAIN_ACCOUNT",
        "steamLoginSecure": "STEAMLOGINSECURE_FOR_MAIN"
      }
    },
    {
      "profile_name": "Smurf_Account",
      "cookies": {
        "sessionid": "SESSIONID_FOR_SMURF_ACCOUNT",
        "steamLoginSecure": "STEAMLOGINSECURE_FOR_SMURF"
      }
    }
  ],
  "max_retries": 5,
  "initial_backoff_seconds": 5
}
```

### Data Storage Layer & Directory Structure
To ensure **data isolation**, the project will create a parent directory for each profile. All data related to that profile will be stored inside it.

```
.
├── data/
│   ├── Main_Account/
│   │   ├── raw_conduct_summary/
│   │   │   └── ...json files...
│   │   └── conduct_summary.csv
│   └── Smurf_Account/
│       ├── raw_conduct_summary/
│       │   └── ...json files...
│       └── conduct_summary.csv
├── download_data.py
├── process_data.py
└── config.json
```
---

## 3. Data Model and Flow

The data flow remains the same conceptually but is now scoped to the active profile.

**Profile-Aware Data Flow**:
`Select Active Profile` → `Use Profile's Cookies` → `Steam API` → `Save to Profile's Raw JSON Folder` → `Process Profile's Raw Files` → `Save to Profile's Processed CSV` → `UI Displays Profile's Data`

### Processed Data Schema
The schema for the `conduct_summary.csv` file remains unchanged. Each profile will have its own version of this file.

| Column Name             | Data Type | Description                                        |
| ----------------------- | --------- | -------------------------------------------------- |
| `MatchID`               | Integer   | The unique ID for the conduct summary report.      |
| `SummaryDate`           | Datetime  | The date and time the summary was generated.       |
| `BehaviorScore`         | Integer   | Your behavior score at the end of this period.     |
| ...                     | ...       | (Other columns as previously defined)              |

---

## 4. Component Design (Profile-Aware)

Both scripts will be modified to first determine the active profile before executing their main logic.

### Component 1: The Downloader (`download_data.py`)

1.  **Initialization**:
    - Reads `config.json`.
    - Gets the `active_profile` name (e.g., "Main_Account").
    - Finds the corresponding profile object in the `profiles` list.
    - Loads the cookies for **only that profile**.
    - Constructs the correct data path (e.g., `data/Main_Account/raw_conduct_summary/`).
2.  **Execution**:
    - The rest of the historical and incremental load logic proceeds as previously designed, but using the specific cookies and saving files to the specific directory of the active profile.

### Component 2: The Processor (`process_data.py`)

1.  **Initialization**:
    - Reads `config.json` to find the `active_profile`.
    - Constructs the path to the profile's raw data directory (e.g., `data/Main_Account/raw_conduct_summary/`).
    - Determines the output path for the processed CSV file (e.g., `data/Main_Account/conduct_summary.csv`).
2.  **Execution**:
    - The processing logic remains the same, but it reads from and writes to the directories corresponding to the active profile.

---

## 5. Project Roadmap

- **Milestone 1: Core Data Pipeline (Profile-Aware)**
    - [ ] Task 1: Update `config.json` to the new profile list structure.
    - [ ] Task 2: Implement the **profile-aware** `download_data.py` script.
    - [ ] Task 3: Implement the **profile-aware** `process_data.py` script.
    - [ ] Task 4: Test the full pipeline with at least two profiles.

- **Milestone 2: Basic Visualization (Frontend)**
    - [ ] Task 5: Create a Streamlit application (`app.py`).
    - [ ] Task 6: Add a dropdown menu to the UI to select and switch between profiles dynamically.
    - [ ] Task 7: Display the behavior score chart and data table for the selected profile.

- **Milestone 3: Expansion**
    - [ ] Task 8: Identify and integrate the next data source (e.g., match history), ensuring it also follows the profile-based directory structure.
