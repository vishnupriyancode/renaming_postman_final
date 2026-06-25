# Postman Collection Generator - Project Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           POSTMAN COLLECTION GENERATOR SYSTEM                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                           USER INTERFACES                                │   │
│  │                                                                         │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │   │
│  │  │ main_processor  │  │ postman_cli     │  │ Support Tools   │            │   │
│  │  │      .py        │  │      .py        │  │                 │            │   │
│  │  │ • CLI Interface │  │ • CLI Interface │  │ auto_edit_      │            │   │
│  │  │ • TS Commands   │  │ • Standalone    │  │   processor.py  │            │   │
│  │  │ • Batch Process │  │   Operations    │  │ • edits_list    │            │   │
│  │  │ • File Renaming │  │ • Collection    │  │   .xlsx → config│            │   │
│  │  │ • Auto Postman  │  │   Management    │  │                 │            │   │
│  │  │ • --refdb       │  │                 │  │                 │            │   │
│  │  └─────────┬───────┘  └─────────┬───────┘  └─────────────────┘            │   │
│  │            │                    │                                            │   │
│  └────────────┼────────────────────┼───────────────────────────────────────────┘   │
│               │                                 │                               │
│               │                                 │                               │
│               ▼                                 ▼                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                        CORE PROCESSING LAYER                            │   │
│  │                                                                         │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │   │
│  │  │ models_config   │  │ rename_files.py │  │ postman_generator│        │   │
│  │  │      .py        │  │                 │  │      .py         │        │   │
│  │  │ • Configuration │  │ • File Renaming │  │ • Collection     │        │   │
│  │  │   Management    │  │ • Header/Footer │  │   Generation     │        │   │
│  │  │ • Model Data    │  │   Transform     │  │ • JSON Parsing   │        │   │
│  │  │ • Static Config │  │ • KEY_CHK_CDN   │  │ • Request        │        │   │
│  │  │ • Dynamic Config│  │   Generation    │  │   Creation       │        │   │
│  │  │ • Fallback      │  │ • Model Info    │  │ • Validation     │        │   │
│  │  └─────────┬───────┘  │   Extraction    │  └─────────────────┘        │   │
│  │            │          └─────────────────┘                              │   │
│  │            │                                                           │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │   │
│  │  │ dynamic_models  │  │ report_generate │  │ refdb_change.py │        │   │
│  │  │      .py        │  │      .py        │  │                 │        │   │
│  │  │ • Auto-Discovery│  │ • Timing Track  │  │ • RefDB Value    │        │   │
│  │  │ • Folder Parsing│  │ • Excel Reports │  │   Replacement    │        │   │
│  │  │ • Model Detect. │  │ • Performance   │  │ • HCID, NPI,     │        │   │
│  │  │ • TS Number     │  │   Metrics       │  │   PAT_* etc.     │        │   │
│  │  │   Normalization │  │ • Statistics    │  │ • refdb_values   │        │   │
│  │  │ • Pattern Match │  │ • Batch Reports │  │   .json          │        │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘        │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                DATA FLOW                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │   Source    │    │   File      │    │  Renamed    │    │  Postman    │      │
│  │  Folders    │───▶│  Renaming   │───▶│   Files     │───▶│ Collection  │      │
│  │             │    │(rename_     │    │             │    │             │      │
│  │ TS_*_sur/   │    │ files.py)   │    │ TC#ID#edit  │    │ JSON File   │      │
│  │ regression/ │    │             │    │ #code#LR/NR │    │ Ready for   │      │
│  │             │    │ • Transform │    │ /EX.json    │    │ Import      │      │
│  └─────────────┘    │ • Rename   │    └──────┬──────┘    └─────────────┘      │
│         │            │ • Move     │           │ (optional)                     │
│         │            └─────────────┘           │ --refdb                        │
│         │                                      ▼                                │
│         │                               ┌─────────────┐                         │
│         │                               │ refdb_      │                         │
│         │                               │ change.py   │                         │
│         │                               │ Value       │                         │
│         │                               │ replacement │                         │
│         │                               └─────────────┘                         │
│         │                   │                   │                   │          │
│         │                   │                   │                   │          │
│         ▼                   ▼                   ▼                   ▼          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │ Dynamic     │    │ Main        │    │ Destination │    │ Postman     │      │
│  │ Discovery   │    │ Processor   │    │ Folders     │    │ Generator   │      │
│  │             │    │             │    │             │    │             │      │
│  │ • Scan TS   │    │ • Orchestr. │    │ TS_*_dis/   │    │ • Create    │      │
│  │   folders   │    │ • Coordinate│    │ renaming_   │    │   requests  │      │
│  │ • Extract   │    │ • Timing   │    │ jsons/      │    │ • Generate  │      │
│  │   params    │    │ • Reports  │    │ regression/ │    │   collection│      │
│  │ • Validate  │    │             │    │             │    │ • Save JSON │      │
│  │   paths     │    │             │    │             │    │             │      │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘      │
│         │                   │                   │                   │          │
│         │                   │                   │                   │          │
│         ▼                   ▼                   ▼                   ▼          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │ Excel       │    │ Timing      │    │ Reports     │    │ Analytics   │      │
│  │ Reports     │    │ Tracking    │    │ Generation  │    │ & Stats     │      │
│  │             │    │             │    │             │    │             │      │
│  │ • XLSX      │    │ • Track     │    │ • Generate  │    │ • Metrics   │      │
│  │ • Timing    │    │   Operations│    │   Reports   │    │ • Breakdowns │      │
│  │ • Stats     │    │ • Performance│   │ • Batch     │    │ • Summary   │      │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘      │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## File Dependencies

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            DEPENDENCY GRAPH                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  main_processor.py                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │   │
│  │  │ models_config.py│  │ rename_files.py │  │ postman_generator│        │   │
│  │  │ • get_models_   │  │ • rename_files()│  │      .py         │        │   │
│  │  │   config()      │  │ • extract_      │  │ • Postman        │        │   │
│  │  │ • get_model_    │  │   model_info()  │  │   Collection     │        │   │
│  │  │   by_ts()       │  │ • transform_    │  │   Generator      │        │   │
│  │  └─────────┬───────┘  │   headers()     │  └─────────────────┘        │   │
│  │            │          └─────────────────┘                              │   │
│  │            ▼                                                            │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │   │
│  │  │ dynamic_models  │  │ report_generate │  │ refdb_change.py │        │   │
│  │  │      .py        │  │      .py        │  │                 │        │   │
│  │  │ • discover_ts_  │  │ • TimingTracker │  │ • load_default_  │        │   │
│  │  │   folders()     │  │ • ExcelReport   │  │   values()       │        │   │
│  │  │ • get_model_    │  │ • get_excel_    │  │ • process_      │        │   │
│  │  │   by_ts_number()│  │   reporter()    │  │   directory()    │        │   │
│  │  │ • normalize_ts_ │  │ • generate_     │  │ • is_refdb_      │        │   │
│  │  │   number()      │  │   timing_report │  │   model_enabled()│        │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘        │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  postman_cli.py                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │  ┌─────────────────┐                                                   │   │
│  │  │ postman_generator│                                                   │   │
│  │  │      .py        │                                                   │   │
│  │  │                 │                                                   │   │
│  │  │ • Postman       │                                                   │   │
│  │  │   Collection    │                                                   │   │
│  │  │   Generator     │                                                   │   │
│  │  └─────────────────┘                                                   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
renaming_files/                           # Project root
├── 📁 model_1/                         # Source TS folders (and model_4, GBDF_*)
│   ├── TS_*_*/sur/regression/ | smoke/
│   └── ... (other TS folders)
│
├── 📁 renaming_jsons/                   # Processed files
│   ├── TS_*_*/dis/regression/ | smoke/
│   └── ... (renamed JSON files)
│
├── 📁 postman_collections/               # Generated collections
│   └── ... (Postman JSON files per TS)
│
├── 📁 reports/                           # Timing/Excel reports (optional)
│   └── collection_reports/
│
├── 📁 Docs/                              # Documentation
│
├── 🐍 main_processor.py                  # Main orchestrator (CLI, batch, --refdb)
├── 🐍 rename_files.py                   # File renaming module
├── 🐍 postman_cli.py                     # CLI for Postman operations
├── 🐍 postman_generator.py               # Collection generator
├── 🐍 models_config.py                  # Configuration manager
├── 🐍 dynamic_models.py                  # Auto-discovery engine
├── 🐍 report_generate.py                # Timing + Excel report generation
├── 🐍 refdb_change.py                    # RefDB value replacement (--refdb)
├── 🐍 auto_edit_processor.py            # edits_list.xlsx → models_config
├── 📄 refdb_values.json                  # RefDB replacement values
├── 📄 edits_list.xlsx                    # Edit list for config automation
├── 📄 .env / .env.example                # ENABLE_* flags, paths
└── 📄 requirements.txt                   # Dependencies
```

## Command Usage Examples

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            COMMAND USAGE PATTERNS                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  # Main Processor Commands                                                      │
│  python main_processor.py --model_1 --CSBDTS01     # Process TS01 model_1   │
│  python main_processor.py --model_1 --CSBDTS07     # Process TS07 model_1   │
│  python main_processor.py --model_1 --GBDTS47      # Process TS47 GBDF MCR   │
│  python main_processor.py --model_1 --GBDTS139     # Process TS139 GBDF GRS  │
│  python main_processor.py --wgs_nyk --NYKTS130       # Process TS130 WGS_NYK   │
│  python main_processor.py --model_1 --all          # Process all model_1    │
│  python main_processor.py --list                    # List available models   │
│  python main_processor.py --model_1 --CSBDTS46 --refdb  # RefDB value replace │
│  python main_processor.py --wgs_nyk --NYKTS123 --refdb   # RefDB (WGS_NYK)    │
│                                                                                 │
│  # Postman CLI Commands                                                         │
│  python postman_cli.py generate --collection-name "TestCollection"              │
│  python postman_cli.py generate-all               # Generate all collections   │
│  python postman_cli.py list-directories           # List available dirs        │
│  python postman_cli.py stats --directory "TS_01_*" # Show directory stats     │
│  python postman_cli.py validate --collection-path "path/to/collection.json"     │
│                                                                                 │
│  # Standalone Generator                                                         │
│  python postman_generator.py --source-dir "renaming_jsons"                     │
│  python postman_generator.py --directory "TS_01_*" --collection-name "Test"    │
│                                                                                 │
│  # Support / Config Automation                                                  │
│  python auto_edit_processor.py              # Update config from edits_list   │
│  python refdb_change.py --help              # Standalone RefDB (see module)   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## File Naming Convention

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            FILENAME CONVENTION                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Input Format (Source):                                                         │
│  TC#01_12345#deny.json          →  TC#01_12345#rvn001#00W5#LR.json             │
│  TC#01_12345#bypass.json        →  TC#01_12345#rvn001#00W5#NR.json             │
│  TC#01_12345#market.json        →  TC#01_12345#rvn001#00W5#EX.json             │
│                                                                                 │
│  Output Format (Destination):                                                   │
│  TC#01_12345#rvn001#00W5#LR.json  (Limited Response)                          │
│  TC#01_12345#rvn001#00W5#NR.json  (No Response)                               │
│  TC#01_12345#rvn001#00W5#EX.json  (Exception)                                 │
│                                                                                 │
│  Where:                                                                         │
│  • TC = Test Case                                                              │
│  • 01_12345 = Test Case ID                                                     │
│  • rvn001 = Edit ID                                                            │
│  • 00W5 = EOB Code                                                             │
│  • LR/NR/EX = Response Type                                                    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Process Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              PROCESS FLOW                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  1. Discovery Phase                                                             │
│     dynamic_models.py → Scan folders → Extract parameters → Validate paths     │
│                                                                                 │
│  2. Configuration Phase                                                        │
│     models_config.py → Load configs → Provide to main_processor.py              │
│                                                                                 │
│  3. Processing Phase                                                           │
│     main_processor.py → Parse files → Rename files → Move to destination       │
│                                                                                 │
│  4. Generation Phase                                                            │
│     postman_generator.py → Create requests → Generate collection → Save JSON   │
│                                                                                 │
│  5. (Optional) RefDB Phase                                                      │
│     When --refdb: refdb_change.py → Replace HCID, NPI, PAT_* etc. in JSONs     │
│     Uses refdb_values.json; enabled per model via .env (ENABLE_REFDB_*)        │
│                                                                                 │
│  6. Output Phase                                                                │
│     Ready-to-import Postman collections in postman_collections/ folder          │
│     Reports in reports/collection_reports/ when report generation enabled       │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```
