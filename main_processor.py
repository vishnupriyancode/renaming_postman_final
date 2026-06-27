#!/usr/bin/env python3
"""
Main Processor - Consolidated file for renaming files and generating Postman collections.
This file combines the functionality of:
- rename_files_with_postman.py (main processing logic)
- process_multiple_models.py (batch processing)
- rename_files.py (simple interface wrapper)

NOTE: File renaming functionality has been moved to rename_files.py module.
This file now imports the renaming functions from that module.

Supports both single model processing and batch processing of multiple models.

SCRIPT FLOW OVERVIEW:
===================
1. FILE RENAMING STAGE: Convert JSON files from old naming convention to new format (via rename_files.py)
2. POSTMAN GENERATION STAGE: Create Postman collections for API testing
3. BATCH PROCESSING STAGE: Handle multiple models simultaneously
4. COMMAND LINE INTERFACE STAGE: Provide user-friendly CLI for different operations
"""

import os
import re
import shutil
import sys
import subprocess
import argparse
import json
from pathlib import Path
from dotenv import load_dotenv
from postman_generator import PostmanCollectionGenerator
from report_generate import ExcelReportGenerator, TimingTracker, get_excel_reporter, create_excel_reporter_for_model_type
from rename_files import rename_files, extract_model_info_from_directory

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Optional report generation - gracefully handle if report_generate.py is missing or disabled
# Check .env file for ENABLE_REPORT_GENERATION setting (default: True)
# Set to 'false', 'False', '0', or comment out the line to disable
REPORT_GENERATION_ENABLED = os.getenv('ENABLE_REPORT_GENERATION', 'true').lower() in ('true', '1', 'yes', 'on')

# Postman generation per TS collection - from .env (default: True for each)
# Set to 'false' to disable Postman generation for that collection type
def _postman_enabled_for_collection(collection_key: str) -> bool:
    env_key = f"ENABLE_POSTMAN_{collection_key.upper()}"
    return os.getenv(env_key, 'true').lower() in ('true', '1', 'yes', 'on')

POSTMAN_ENABLED_MODEL_1 = _postman_enabled_for_collection("MODEL_1")
try:
    from report_generate import (
        extract_model_name_from_source_dir,
        generate_timing_report_for_model,
        generate_json_renaming_timing_report,
        generate_excel_timing_report,
        create_excel_reporter_for_processing,
        create_excel_reporter_for_batch_processing
    )
except ImportError:
    # Report generation module not available - create dummy functions
    REPORT_GENERATION_ENABLED = False
    def extract_model_name_from_source_dir(source_dir):
        return "Unknown"
    def generate_timing_report_for_model(model_config, model_type):
        pass
    def generate_json_renaming_timing_report(timing_data, model_config, model_type, total_time):
        pass
    def generate_excel_timing_report(excel_reporter, model_type=None):
        return None
    def create_excel_reporter_for_processing(model_type=None):
        return get_excel_reporter()
    def create_excel_reporter_for_batch_processing(model_type=None):
        return get_excel_reporter()

from refdb_change import load_default_values, process_directory, is_refdb_model_enabled
from pathlib import Path
import re


# NOTE: Renaming functionality has been moved to rename_files.py
# The rename_files() function and related helper functions are now imported from that module.


def process_multiple_models(models_config, generate_postman=True, model_type=None):
    """
    STAGE 3: BATCH PROCESSING FUNCTION
    =================================
    Process multiple models with their respective configurations.
    This function handles batch processing of multiple TS models simultaneously.
    
    PROCESSING FLOW:
    1. Iterate through each model configuration
    2. Call rename_files() for each model
    3. Track success/failure for each model
    4. Provide comprehensive summary report
    5. Generate Excel timing report
    
    Args:
        models_config: List of dictionaries containing model configurations
        generate_postman: Whether to generate Postman collections for each model
    
    Example models_config:
    [
        {
            "edit_id": "rvn001",
            "code": "00W5",
            "source_dir": "source_folder/model_1/Model_01_sample_model_1_M000001_00W04_sur/payloads/regression",
            "dest_dir": "renaming_jsons/model_1/Model_01_sample_model_1_M000001_00W04_dis/payloads/regression",
            "postman_collection_name": "Model_01_sample_Collection"
        },
        {
            "edit_id": "rvn002", 
            "code": "00W6",
            "source_dir": "source_folder/model_1/Model_02_sample_model_1_M000002_00W06_sur/payloads/regression",
            "dest_dir": "renaming_jsons/model_1/Model_02_sample_model_1_M000002_00W06_dis/payloads/regression",
            "postman_collection_name": "Model_02_sample_Collection"
        }
    ]
    """
    
    # STAGE 3.1: BATCH PROCESSING INITIALIZATION
    # ==========================================
    print("Starting Multi-Model Processing")
    print("=" * 80)
    
    # Initialize Excel reporter session (only if report generation is enabled)
    excel_reporter = None
    if REPORT_GENERATION_ENABLED:
        excel_reporter = create_excel_reporter_for_batch_processing(model_type)
    
    total_processed = 0
    successful_models = []
    failed_models = []
    
    # STAGE 3.2: MODEL ITERATION LOOP
    # ===============================
    for i, model_config in enumerate(models_config, 1):
        edit_id = model_config.get("edit_id")
        code = model_config.get("code")
        source_dir = model_config.get("source_dir")
        dest_dir = model_config.get("dest_dir")
        postman_collection_name = model_config.get("postman_collection_name")
        
        print(f"\nProcessing Model {i}/{len(models_config)}")
        print(f"   Edit ID: {edit_id}")
        print(f"   Code: {code}")
        print(f"   Source: {source_dir}")
        print(f"   Destination: {dest_dir}")
        print("-" * 60)
        
        try:
            # Process the model
            renamed_files = rename_files(
                edit_id=edit_id,
                code=code,
                source_dir=source_dir,
                dest_dir=dest_dir,
                generate_postman=generate_postman,
                postman_collection_name=postman_collection_name,
                postman_file_name=model_config.get("postman_file_name"),
                excel_reporter=excel_reporter,
                ts_number=model_config.get("ts_number"),
            )
            
            if renamed_files:
                print(f"SUCCESS Model {edit_id}_{code}: Successfully processed {len(renamed_files)} files")
                successful_models.append({
                    "edit_id": edit_id,
                    "code": code,
                    "files_count": len(renamed_files),
                    "files": renamed_files
                })
                total_processed += len(renamed_files)
            else:
                print(f"WARNING  Model {edit_id}_{code}: No files were processed")
                failed_models.append({
                    "edit_id": edit_id,
                    "code": code,
                    "reason": "No files found or processed"
                })
                
        except Exception as e:
            print(f"ERROR Model {edit_id}_{code}: Failed with error - {e}")
            failed_models.append({
                "edit_id": edit_id,
                "code": code,
                "reason": str(e)
            })
    
    # STAGE 3.3: BATCH PROCESSING SUMMARY
    # ==================================
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY PROCESSING SUMMARY")
    print("=" * 80)
    print(f"Total models processed: {len(models_config)}")
    print(f"Successful models: {len(successful_models)}")
    print(f"Failed models: {len(failed_models)}")
    print(f"Total files processed: {total_processed}")
    
    if successful_models:
        print(f"\nSUCCESS SUCCESSFUL MODELS:")
        for model in successful_models:
            print(f"   - {model['edit_id']}_{model['code']}: {model['files_count']} files")
    
    if failed_models:
        print(f"\nERROR FAILED MODELS:")
        for model in failed_models:
            print(f"   - {model['edit_id']}_{model['code']}: {model['reason']}")
    
    print("\nTARGET All models processed!")
    
    # Generate Excel timing report (only if report generation is enabled and reporter exists)
    if REPORT_GENERATION_ENABLED and excel_reporter:
        generate_excel_timing_report(excel_reporter, model_type=model_type)
    
    return successful_models, failed_models




def main():
    """
    STAGE 4: COMMAND LINE INTERFACE FUNCTION
    =======================================
    Main function with comprehensive command line interface.
    This function provides the CLI for users to interact with the script.
    
    CLI FEATURES:
    1. Process specific TS models (model_1)
    2. Process all discovered models
    3. List available models
    4. Custom parameter processing
    5. Skip Postman generation option
    6. Generate timing reports for specific models
    
    PROCESSING FLOW:
    1. Parse command line arguments
    2. Load model configurations
    3. Handle different processing modes
    4. Execute file renaming and Postman generation
    5. Provide comprehensive feedback
    """
    
    # STAGE 4.1: ARGUMENT PARSER SETUP
    # ================================
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Main Processor - Rename files and generate Postman collections for TS models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process model_1 models (use --TSXX format)
  python main_processor.py --model_1 --TS01    # Process TS01 model
  python main_processor.py --model_1 --TS02    # Process TS02 model
  python main_processor.py --model_1 --TS07    # Process TS07 model

  # Process all discovered models
  python main_processor.py --model_1 --all     # Process all discovered model_1 models

  # List available models
  python main_processor.py --list    # List all available TS models

  # Generate timing reports for specific models
  python main_processor.py --model_1 --TS01 --list

  # Postman generation: controlled by .env (ENABLE_POSTMAN_MODEL_1)

  # Process with custom parameters
  python main_processor.py --edit-id M000001 --code 00W04 --source-dir custom/path
        """
    )
    
    parser.add_argument("--model_1", action="store_true",
                       help="Process model_1 models (required for TS model processing)")

    parser.add_argument("--all", action="store_true",
                       help="Process all discovered models")
    parser.add_argument("--list", action="store_true",
                       help="List all available TS models")
    parser.add_argument("--no-report", action="store_true",
                       help="Disable Excel report generation (skip timing reports)")
    parser.add_argument("--refdb", action="store_true",
                       help="Apply refdb value replacement for refdb-specific models")
    
    # Add custom parameter arguments
    parser.add_argument("--edit-id", type=str, help="Custom edit ID (e.g., rvn001)")
    parser.add_argument("--code", type=str, help="Custom code (e.g., 00W5)")
    parser.add_argument("--source-dir", type=str, help="Custom source directory path")
    parser.add_argument("--dest-dir", type=str, help="Custom destination directory path")
    parser.add_argument("--collection-name", type=str, help="Custom Postman collection name")
    
    # Parse arguments and handle unknown arguments for --TSXX pattern
    args, unknown_args = parser.parse_known_args()

    if not args.model_1 and args.list:
        args.model_1 = True

    try:
        from dynamic_models import normalize_ts_number
    except ImportError:
        def normalize_ts_number(ts_number_raw: str) -> str:
            ts_num = int(ts_number_raw)
            if 1 <= ts_num <= 9:
                return f"{ts_num:02d}"
            elif 10 <= ts_num <= 99:
                return f"{ts_num:02d}"
            elif 100 <= ts_num <= 999:
                return f"{ts_num:03d}"
            return ts_number_raw

    ts_models = []
    legacy_prefixes = ("--MODEL_2", "--MODEL_3")
    for arg in unknown_args:
        upper = arg.upper()
        for prefix in legacy_prefixes:
            if upper.startswith(prefix):
                print(f"ERROR: Legacy flag '{arg}' is no longer supported.")
                print(f"       Use --model_1 --TS## instead (e.g. python main_processor.py --model_1 --TS01)")
                sys.exit(1)

    if args.model_1:
        for arg in unknown_args:
            if arg.startswith('--TS') and len(arg) > 4:
                ts_number_str = arg[4:]
                if ts_number_str.isdigit():
                    ts_number = normalize_ts_number(ts_number_str)
                    ts_models.append(ts_number)
                    print(f"[INFO] Detected TS{ts_number_str} for model_1 processing (maps to TS{ts_number})")

    args.ts_models = ts_models

    # STAGE 4.2: MODEL CONFIGURATION LOADING
    # ======================================
    # Load model configurations with dynamic discovery (model_1 only)
    try:
        from models_config import get_models_config, get_model_by_ts, STATIC_MODELS_CONFIG
        models_config = get_models_config(use_dynamic=True, use_model_1_destination=args.model_1)
        print("Configuration loaded with dynamic discovery")
    except ImportError as e:
        print(f"Error: {e}")
        print("Please ensure models_config.py and dynamic_models.py exist.")
        sys.exit(1)
    
    # STAGE 4.3: LIST MODE HANDLING
    # =============================
    # Handle --list option
    if args.list:
        # Timing report generation is handled via --TSXX patterns
        
        # Regular list mode - show available models
        try:
            from dynamic_models import print_nested_models_display
            print_nested_models_display()
        except ImportError:
            print("\nINFO AVAILABLE TS MODELS")
            print("=" * 50)
            if models_config:
                for model in models_config:
                    print(f"TS_{model['ts_number']}: {model['edit_id']}_{model['code']}")
                    print(f"  FOLDER Source: {model['source_dir']}")
                    print(f"  FOLDER Dest:   {model['dest_dir']}")
                    print()
            else:
                print("No TS models found")
        sys.exit(0)
    
    # STAGE 4.4: CUSTOM PARAMETER HANDLING
    # ====================================
    # Handle custom parameters
    if args.edit_id and args.code:
        print(f"\nTOOL Processing custom model: {args.edit_id}_{args.code}")
        print("=" * 60)
        
        try:
            renamed_files = rename_files(
                edit_id=args.edit_id,
                code=args.code,
                source_dir=args.source_dir,
                dest_dir=args.dest_dir,
                generate_postman=True,
                postman_collection_name=args.collection_name
            )
            
            if renamed_files:
                print(f"SUCCESS Custom model {args.edit_id}_{args.code}: Successfully processed {len(renamed_files)} files")
            else:
                print(f"WARNING  Custom model {args.edit_id}_{args.code}: No files were processed")
                
        except Exception as e:
            print(f"ERROR Custom model {args.edit_id}_{args.code}: Failed with error - {e}")
            sys.exit(1)
        
        sys.exit(0)
    
    # STAGE 4.5: MODEL SELECTION LOGIC
    # ================================
    # Determine which models to process
    models_to_process = []

    if hasattr(args, 'ts_models') and args.ts_models:
        if not args.model_1:
            print("ERROR Error: --model_1 flag is required for TS model processing!")
            print("\nPlease use the --model_1 flag with TS model commands:")
            for ts_num in args.ts_models:
                print(f"  python main_processor.py --model_1 --TS{ts_num}")
            sys.exit(1)

        for ts_number_str in args.ts_models:
            matched = [model for model in models_config if model.get("ts_number") == ts_number_str]
            if matched:
                models_to_process.extend(matched)
                folder_types = [m.get("folder_type", "regression") for m in matched]
                print(f"[INFO] Added {len(matched)} TS{ts_number_str} model(s) to processing queue: {', '.join(folder_types)}")
            else:
                print(f"ERROR Error: TS{ts_number_str} model not found!")
                print(f"Available models: {[m.get('ts_number') for m in models_config]}")

    if args.all:
        if not args.model_1:
            print("ERROR Error: --model_1 flag is required for --all processing!")
            print("  python main_processor.py --model_1 --all")
            sys.exit(1)
        models_to_process = models_config
        print(f"SUCCESS Processing all {len(models_config)} discovered models")

    if not models_to_process:
        print("ERROR Error: No model specified!")
        print("\nPlease specify which model to process:")
        print("  --model_1 --TS01    Process TS01 model")
        print("  --model_1 --TS02    Process TS02 model")
        print("  --model_1 --all     Process all discovered model_1 models")
        print("  --list              List all available TS models")
        print("\nUse --help for more information.")
        sys.exit(1)

    model_type = "model_1" if args.model_1 else None
    postman_enabled_for_type = POSTMAN_ENABLED_MODEL_1 if args.model_1 else True
    generate_postman = postman_enabled_for_type
    if not postman_enabled_for_type and model_type:
        print(f"[INFO] Postman generation is DISABLED for {model_type} (from .env: ENABLE_POSTMAN_MODEL_1=false)")

    # Check if report generation is disabled via command line or .env file
    enable_reporting = REPORT_GENERATION_ENABLED and not args.no_report
    
    # Create separate Excel reporter for this model type (only if reporting is enabled)
    excel_reporter = None
    if enable_reporting:
        excel_reporter = create_excel_reporter_for_processing(model_type)
        env_setting = os.getenv('ENABLE_REPORT_GENERATION', 'true')
        print(f"[INFO] Report generation is ENABLED (from .env: ENABLE_REPORT_GENERATION={env_setting})")
    else:
        if args.no_report:
            print("[INFO] Report generation is DISABLED (--no-report flag)")
        elif not REPORT_GENERATION_ENABLED:
            env_setting = os.getenv('ENABLE_REPORT_GENERATION', 'not set')
            if env_setting.lower() in ('false', '0', 'no', 'off'):
                print(f"[INFO] Report generation is DISABLED (from .env: ENABLE_REPORT_GENERATION={env_setting})")
            else:
                print("[INFO] Report generation is DISABLED (report_generate.py not available)")
    
    print(f"\nSTARTING Processing {len(models_to_process)} model(s)...")
    print("=" * 60)
    
    total_processed = 0
    successful_models = []
    
    for i, model_config in enumerate(models_to_process, 1):
        edit_id = model_config["edit_id"]
        code = model_config["code"]
        source_dir = model_config["source_dir"]
        dest_dir = model_config["dest_dir"]
        postman_collection_name = model_config["postman_collection_name"]
        ts_number = model_config.get("ts_number", "??")
        
        print(f"\nINFO Processing Model {i}/{len(models_to_process)}: TS_{ts_number} ({edit_id}_{code})")
        print("-" * 40)
        
        try:
            renamed_files = rename_files(
                edit_id=edit_id,
                code=code,
                source_dir=source_dir,
                dest_dir=dest_dir,
                generate_postman=generate_postman,
                postman_collection_name=postman_collection_name,
                postman_file_name=model_config.get('postman_file_name'),
                excel_reporter=excel_reporter,
                ts_number=model_config.get('ts_number'),
            )
            
            # Apply refdb value replacement if --refdb flag is set
            if args.refdb and renamed_files:
                print(f"\nINFO Applying refdb value replacement for TS_{ts_number}...")
                try:
                    refdb_model = "model_1" if model_type == "model_1" else None

                    if refdb_model and not is_refdb_model_enabled(refdb_model):
                        print(f"INFO Refdb is disabled for {refdb_model} (check ENABLE_REFDB_MODEL_1 in .env). Skipping refdb replacement.")
                    elif refdb_model:
                        refdb_replacements = load_default_values(refdb_model)
                        dest_path = Path(dest_dir)
                        if dest_path.exists():
                            successful_refdb, failed_refdb = process_directory(
                                directory=dest_path,
                                replacements=refdb_replacements,
                                recursive=True,
                                backup=False,
                                model=refdb_model
                            )
                            if successful_refdb > 0:
                                print(f"SUCCESS Refdb: Successfully processed {successful_refdb} file(s) with refdb values")
                            if failed_refdb > 0:
                                print(f"WARNING Refdb: {failed_refdb} file(s) failed refdb processing")
                        else:
                            print(f"WARNING Refdb: Destination directory not found: {dest_dir}")
                    else:
                        print(f"WARNING Refdb: Model type '{model_type}' is not a refdb-supported model")
                except Exception as refdb_error:
                    print(f"WARNING Refdb processing failed: {refdb_error}")
                    # Continue with normal processing even if refdb fails
            
            if renamed_files:
                print(f"SUCCESS Model TS_{ts_number} ({edit_id}_{code}): Successfully processed {len(renamed_files)} files")
                successful_models.append({
                    "ts_number": ts_number,
                    "edit_id": edit_id,
                    "code": code,
                    "files_count": len(renamed_files)
                })
                total_processed += len(renamed_files)
            else:
                print(f"WARNING  Model TS_{ts_number} ({edit_id}_{code}): No files were processed")
                
        except Exception as e:
            print(f"ERROR Model TS_{ts_number} ({edit_id}_{code}): Failed with error - {e}")
    
    # STAGE 4.7: FINAL SUMMARY REPORT
    # ===============================
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY PROCESSING SUMMARY")
    print("=" * 60)
    print(f"Models processed: {len(models_to_process)}")
    print(f"Successful models: {len(successful_models)}")
    print(f"Total files processed: {total_processed}")
    
    if successful_models:
        print(f"\nSUCCESS SUCCESSFUL MODELS:")
        for model in successful_models:
            print(f"   - TS_{model['ts_number']} ({model['edit_id']}_{model['code']}): {model['files_count']} files")
        
        if generate_postman:
            print(f"\nCOLLECTION POSTMAN COLLECTIONS GENERATED:")
            print("To use these collections:")
            print("1. Open Postman")
            print("2. Click 'Import'")
            print("3. Select the collection files from 'postman_collections' folder")
            print("4. Start testing your APIs!")
    
    if total_processed > 0:
        print(f"\nCELEBRATION Successfully processed {total_processed} files!")
        print("Files are now ready for API testing with Postman.")
        
        # Generate Excel timing report for single model processing (only if enabled)
        if enable_reporting and excel_reporter:
            generate_excel_timing_report(excel_reporter, model_type=model_type)
    else:
        print("\nERROR No files were processed.")


if __name__ == "__main__":
    main()
