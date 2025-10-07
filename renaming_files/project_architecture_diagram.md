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
│  │  ┌─────────────────┐              ┌─────────────────┐                    │   │
│  │  │  main_processor │              │  postman_cli    │                    │   │
│  │  │      .py        │              │      .py        │                    │   │
│  │  │                 │              │                 │                    │   │
│  │  │ • CLI Interface │              │ • CLI Interface │                    │   │
│  │  │ • TS Commands   │              │ • Standalone    │                    │   │
│  │  │ • Batch Process │              │   Operations    │                    │   │
│  │  │ • File Renaming │              │ • Collection    │                    │   │
│  │  │ • Auto Postman  │              │   Management    │                    │   │
│  │  └─────────┬───────┘              └─────────┬───────┘                    │   │
│  └────────────┼─────────────────────────────────┼───────────────────────────┘   │
│               │                                 │                               │
│               │                                 │                               │
│               ▼                                 ▼                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                        CORE PROCESSING LAYER                            │   │
│  │                                                                         │   │
│  │  ┌─────────────────┐              ┌─────────────────┐                    │   │
│  │  │ models_config   │              │ postman_generator│                   │   │
│  │  │      .py        │              │      .py        │                    │   │
│  │  │                 │              │                 │                    │   │
│  │  │ • Configuration │              │ • Collection    │                    │   │
│  │  │   Management    │              │   Generation    │                    │   │
│  │  │ • Model Data    │              │ • JSON Parsing  │                    │   │
│  │  │ • Static Config │              │ • Request       │                    │   │
│  │  │ • Dynamic Config│              │   Creation      │                    │   │
│  │  │ • Fallback      │              │ • Validation     │                    │   │
│  │  └─────────┬───────┘              └─────────────────┘                    │   │
│  │            │                                                           │   │
│  │            ▼                                                           │   │
│  │  ┌─────────────────┐                                                   │   │
│  │  │ dynamic_models   │                                                   │   │
│  │  │      .py         │                                                   │   │
│  │  │                  │                                                   │   │
│  │  │ • Auto-Discovery  │                                                   │   │
│  │  │ • Folder Parsing  │                                                   │   │
│  │  │ • Model Detection │                                                   │   │
│  │  │ • TS Number       │                                                   │   │
│  │  │   Normalization   │                                                   │   │
│  │  │ • Pattern Matching│                                                   │   │
│  │  └─────────────────┘                                                   │   │
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
│  │             │    │             │    │             │    │             │      │
│  │ TS_*_sur/   │    │ TC#ID#edit  │    │ TC#ID#edit  │    │ JSON File   │      │
│  │ regression/ │    │ #code#suffix │    │ #code#LR/NR │    │ Ready for   │      │
│  │             │    │ .json       │    │ /EX.json    │    │ Import      │      │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘      │
│         │                   │                   │                   │          │
│         │                   │                   │                   │          │
│         ▼                   ▼                   ▼                   ▼          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │ Dynamic     │    │ Main        │    │ Destination │    │ Postman     │      │
│  │ Discovery   │    │ Processor   │    │ Folders     │    │ Generator   │      │
│  │             │    │             │    │             │    │             │      │
│  │ • Scan TS   │    │ • Parse     │    │ TS_*_dis/   │    │ • Create    │      │
│  │   folders   │    │   files     │    │ renaming_   │    │   requests  │      │
│  │ • Extract   │    │ • Rename    │    │ jsons/      │    │ • Generate  │      │
│  │   params    │    │ • Move      │    │ regression/ │    │   collection│      │
│  │ • Validate  │    │ • Generate  │    │             │    │ • Save JSON │      │
│  │   paths     │    │   Postman   │    │             │    │             │      │
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
│  │                                                                         │   │
│  │  ┌─────────────────┐              ┌─────────────────┐                  │   │
│  │  │ models_config.py │              │ postman_generator│                  │   │
│  │  │                 │              │      .py        │                  │   │
│  │  │ • get_models_   │              │                 │                  │   │
│  │  │   config()      │              │ • Postman       │                  │   │
│  │  │ • get_model_    │              │   Collection    │                  │   │
│  │  │   by_ts()       │              │   Generator     │                  │   │
│  │  └─────────┬───────┘              └─────────────────┘                  │   │
│  │            │                                                           │   │
│  │            ▼                                                           │   │
│  │  ┌─────────────────┐                                                   │   │
│  │  │ dynamic_models  │                                                   │   │
│  │  │      .py        │                                                   │   │
│  │  │                 │                                                   │   │
│  │  │ • discover_ts_  │                                                   │   │
│  │  │   folders()     │                                                   │   │
│  │  │ • get_model_    │                                                   │   │
│  │  │   by_ts_number()│                                                   │   │
│  │  │ • normalize_ts_ │                                                   │   │
│  │  │   number()      │                                                   │   │
│  │  └─────────────────┘                                                   │   │
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
renaming_postman_collection/
├── 📁 WGS_CSBD/                         # Source TS folders
│   ├── TS_01_Covid_WGS_CSBD_*/sur/regression/
│   ├── TS_02_Laterality_*/sur/regression/
│   ├── TS_03_Revenue_*/sur/regression/
│   └── ... (other TS folders)
│
├── 📁 renaming_jsons/                   # Processed files
│   ├── TS_01_Covid_WGS_CSBD_*/dis/regression/
│   ├── TS_02_Laterality_*/dis/regression/
│   ├── TS_03_Revenue_*/dis/regression/
│   └── ... (renamed JSON files)
│
├── 📁 postman_collections/              # Generated collections
│   ├── TS_01_Covid_Collection/
│   ├── TS_02_Laterality_Collection/
│   ├── TS_03_Revenue_Collection/
│   └── ... (Postman JSON files)
│
├── 🐍 main_processor.py                 # Main orchestrator
├── 🐍 postman_cli.py                    # CLI interface
├── 🐍 models_config.py                  # Configuration manager
├── 🐍 dynamic_models.py                 # Auto-discovery engine
├── 🐍 postman_generator.py              # Collection generator
└── 📄 requirements.txt                  # Dependencies
```

## Command Usage Examples

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            COMMAND USAGE PATTERNS                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  # Main Processor Commands                                                      │
│  python main_processor.py --TS01                    # Process TS01 model       │
│  python main_processor.py --TS07                    # Process TS07 model       │
│  python main_processor.py --all                     # Process all models       │
│  python main_processor.py --list                    # List available models     │
│  python main_processor.py --edit-id rvn001 --code 00W5  # Custom model        │
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
│  5. Output Phase                                                                │
│     Ready-to-import Postman collections in postman_collections/ folder         │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```
