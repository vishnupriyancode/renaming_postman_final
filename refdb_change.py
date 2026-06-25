#!/usr/bin/env python3
"""
refdb_change.py - Replace specific values in JSON files with user-provided values

This module provides refdb value replacement functionality for refdb-specific models.
It is primarily used by main_processor.py when the --refdb flag is specified.

Values are loaded from `refdb_values.json` for model_1.
"""

import json
import os
import sys
import argparse
import re
from pathlib import Path
from typing import Dict, Optional

try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=_env_path)
except ImportError:
    pass

if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

REFDB_TS_NUMBERS = {
    "model_1": ["47", "59", "75"],
}


def _is_refdb_model_enabled(model: str) -> bool:
    """Return True if refdb processing is enabled for this model (from .env)."""
    env_keys = {
        "model_1": "ENABLE_REFDB_MODEL_1",
    }
    key = env_keys.get(model)
    if not key:
        return True
    return os.getenv(key, "true").lower() in ("true", "1", "yes", "on")


def is_refdb_model_enabled(model: str) -> bool:
    """Public helper: return True if refdb is enabled for this model."""
    return _is_refdb_model_enabled(model)


REFDB_TS_NUMBERS_EFFECTIVE = {
    k: v for k, v in REFDB_TS_NUMBERS.items() if _is_refdb_model_enabled(k)
}


def load_default_values(model: str, config_file: Optional[Path] = None) -> Dict[str, str]:
    """Load default values from JSON configuration file for model_1."""
    if model != "model_1":
        print(f"Error: Only model_1 is supported; got '{model}'")
        sys.exit(1)

    if config_file is None:
        script_dir = Path(__file__).parent
        config_file = script_dir / "refdb_values.json"

    required_keys = ["HCID", "PAT_BRTH_DT", "PAT_FRST_NME", "PAT_LAST_NM", "PROV_TAX_ID", "BILLG_NPI", "NAT_EA2_RNDR_NPI"]
    template_config = {
        "model_1": {k: "" for k in required_keys},
    }

    if not config_file.exists():
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(template_config, f, indent=2, ensure_ascii=False)
            print(f"Created config file template: {config_file}")
            print("Please fill in the values for model_1 in the config file and run the script again.")
            sys.exit(1)
        except Exception as e:
            print(f"Error: Cannot create config file {config_file}: {e}")
            sys.exit(1)

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        if not isinstance(config_data, dict):
            print(f"Error: Config file {config_file} must contain a JSON object with model keys.")
            sys.exit(1)

        if "model_1" not in config_data:
            print(f"Error: Model 'model_1' not found in {config_file}")
            print(f"Available models: {', '.join(config_data.keys())}")
            sys.exit(1)

        values = config_data["model_1"]
        if not isinstance(values, dict):
            print(f"Error: Model 'model_1' in {config_file} must contain a JSON object.")
            sys.exit(1)

        missing_keys = set(required_keys) - set(values.keys())
        if missing_keys:
            print(f"Error: Missing required keys for model_1 in {config_file}: {', '.join(missing_keys)}")
            sys.exit(1)

        empty_keys = [key for key, value in values.items() if not value or (isinstance(value, str) and value.strip() == "")]
        if empty_keys:
            print(f"Warning: Empty values found for model_1 in {config_file} for: {', '.join(empty_keys)}")
            print("These fields will not be replaced in target JSON files.")

        print(f"Loaded default values for model_1 from: {config_file}")
        return values

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {config_file}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Cannot read {config_file}: {e}")
        sys.exit(1)


DEFAULT_VALUES = {}


def get_user_input(default_values: Dict[str, str]) -> Dict[str, str]:
    """Prompt user for replacement values interactively."""
    replacements = {}
    print("\n" + "="*60)
    print("JSON Value Replacement Tool")
    print("="*60)
    print("\nEnter new values for each field (press Enter to keep default):\n")
    for key, default_value in default_values.items():
        user_input = input(f"{key} (default: {default_value}): ").strip()
        replacements[key] = user_input if user_input else default_value
    return replacements


def replace_values_in_json(data: dict, replacements: Dict[str, str]) -> tuple[dict, int]:
    """Recursively search and replace values in JSON data structure."""
    count = 0
    if isinstance(data, dict):
        for key, value in data.items():
            if key in replacements:
                if isinstance(value, str):
                    data[key] = replacements[key]
                    count += 1
                    print(f"  Replaced {key}: '{value}' -> '{replacements[key]}'")
            elif isinstance(value, (dict, list)):
                sub_data, sub_count = replace_values_in_json(value, replacements)
                data[key] = sub_data
                count += sub_count
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                sub_data, sub_count = replace_values_in_json(item, replacements)
                data[i] = sub_data
                count += sub_count
    return data, count


def extract_ts_number_from_path(file_path: Path, model: str) -> Optional[str]:
    """Extract TS number from file path for model_1 folders (Model_XX_ or TS_XX_)."""
    if model != "model_1":
        return None
    path_str = str(file_path)
    for pattern in (r'Model_(\d{1,3})_', r'TS_(\d{1,3})_'):
        match = re.search(pattern, path_str)
        if match:
            return match.group(1)
    return None


def validate_refdb_model(file_path: Path, model: str) -> bool:
    """Validate if the file path belongs to a refdb-specific model."""
    ts_number = extract_ts_number_from_path(file_path, model)
    if ts_number is None:
        return False
    if model in REFDB_TS_NUMBERS_EFFECTIVE:
        return ts_number in REFDB_TS_NUMBERS_EFFECTIVE[model]
    return False


def process_json_file(file_path: Path, replacements: Dict[str, str], backup: bool = True, model: str = None) -> bool:
    """Process a single JSON file and replace values."""
    if not model:
        print(f"  ✗ Error: Model parameter is required for refdb processing")
        return False

    if not validate_refdb_model(file_path, model):
        ts_number = extract_ts_number_from_path(file_path, model)
        refdb_models = REFDB_TS_NUMBERS_EFFECTIVE.get(model, [])
        if ts_number:
            print(f"  ⚠ Skipping {file_path.name}: Model_{ts_number} is not a refdb-specific model")
            print(f"     Refdb models for {model}: Model_{', Model_'.join(refdb_models) if refdb_models else 'None configured'}")
        else:
            print(f"  ⚠ Skipping {file_path.name}: Could not determine TS number from path")
            print(f"     Expected path pattern: Model_XX_* or TS_XX_*")
        return False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if backup:
            backup_path = file_path.with_suffix(file_path.suffix + '.bak')
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"  Backup created: {backup_path}")

        print(f"\nProcessing: {file_path}")
        modified_data, count = replace_values_in_json(data, replacements)

        if count > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(modified_data, f, indent=2, ensure_ascii=False)
            print(f"  ✓ Successfully replaced {count} value(s)")
            return True
        print(f"  ⚠ No matching fields found to replace")
        return False

    except json.JSONDecodeError as e:
        print(f"  ✗ Error: Invalid JSON in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error processing {file_path}: {e}")
        return False


def process_directory(directory: Path, replacements: Dict[str, str],
                      recursive: bool = True, backup: bool = True, model: str = None) -> tuple[int, int]:
    """Process all JSON files in a directory."""
    if not model:
        print(f"Error: Model parameter is required for refdb processing")
        return 0, 1

    successful = 0
    failed = 0
    skipped = 0
    pattern = "**/*.json" if recursive else "*.json"
    json_files = list(directory.glob(pattern))

    if not json_files:
        print(f"No JSON files found in {directory}")
        return 0, 0

    print(f"\nFound {len(json_files)} JSON file(s) to process...")
    refdb_models = REFDB_TS_NUMBERS_EFFECTIVE.get(model, [])
    is_refdb_dir = validate_refdb_model(directory, model)

    if not is_refdb_dir:
        ts_number = extract_ts_number_from_path(directory, model)
        if ts_number:
            print(f"\n⚠ Warning: Directory does not appear to be a refdb-specific model (Model_{ts_number})")
            print(f"   Refdb models for {model}: Model_{', Model_'.join(refdb_models) if refdb_models else 'None configured'}")
        else:
            print(f"\n⚠ Warning: Could not determine TS number from directory path")
            print(f"   Expected path pattern: Model_XX_* or TS_XX_*")
        print("   Processing files individually - only refdb-specific files will be processed...\n")

    for json_file in json_files:
        result = process_json_file(json_file, replacements, backup, model)
        if result is True:
            successful += 1
        elif result is False:
            ts_number = extract_ts_number_from_path(json_file, model)
            if ts_number and ts_number not in refdb_models:
                skipped += 1
            failed += 1

    if skipped > 0:
        print(f"\n{'='*60}")
        print(f"Summary: {successful} successful, {failed} failed ({skipped} skipped - not refdb models)")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print(f"Summary: {successful} successful, {failed} failed")
        print(f"{'='*60}")

    return successful, failed


def main():
    """Main function to handle command-line arguments and execute replacements."""
    parser = argparse.ArgumentParser(
        description='Replace specific values in JSON files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples (Recommended - Use main_processor.py):
    python main_processor.py --model_1 --TS47 --refdb
    python main_processor.py --model_1 --TS59 --refdb

Standalone Usage:
    python refdb_change.py --model model_1 --no-interactive -d path/to/directory

Note: Only refdb-specific model_1 TS numbers are processed.
      Update REFDB_TS_NUMBERS in refdb_change.py to add more models.
        """
    )

    parser.add_argument('-f', '--file', type=str, help='Path to a specific JSON file to process')
    parser.add_argument('-d', '--directory', type=str, help='Path to directory containing JSON files')
    parser.add_argument('-r', '--recursive', action='store_true', default=True,
                        help='Process subdirectories recursively (default: True)')
    parser.add_argument('--no-recursive', dest='recursive', action='store_false',
                        help='Do not process subdirectories')
    parser.add_argument('--hcid', type=str, help='New value for HCID')
    parser.add_argument('--pat-brth-dt', type=str, dest='pat_brth_dt', help='New value for PAT_BRTH_DT')
    parser.add_argument('--pat-frst-nme', type=str, dest='pat_frst_nme', help='New value for PAT_FRST_NME')
    parser.add_argument('--pat-last-nm', type=str, dest='pat_last_nm', help='New value for PAT_LAST_NM')
    parser.add_argument('--prov-tax-id', type=str, dest='prov_tax_id', help='New value for PROV_TAX_ID')
    parser.add_argument('--billg-npi', type=str, dest='billg_npi', help='New value for BILLG_NPI')
    parser.add_argument('--nat-ea2-rndr-npi', type=str, dest='nat_ea2_rndr_npi',
                        help='New value for NAT_EA2_RNDR_NPI')
    parser.add_argument('--no-backup', action='store_true', help='Do not create backup files')
    parser.add_argument('--no-interactive', action='store_true',
                        help='Skip interactive input (use defaults or command-line values)')
    parser.add_argument('--config', type=str,
                        help='Path to JSON configuration file with default values (default: refdb_values.json)')
    parser.add_argument('--model', type=str, required=True,
                        choices=['model_1'],
                        help='Model type: model_1 (required)')

    args = parser.parse_args()
    config_path = Path(args.config) if args.config else None
    DEFAULT_VALUES = load_default_values(args.model, config_path)

    refdb_models = REFDB_TS_NUMBERS_EFFECTIVE.get(args.model, [])
    if refdb_models:
        print(f"\n{'='*60}")
        print(f"REFDB-SPECIFIC MODEL PROCESSING")
        print(f"{'='*60}")
        print(f"Model: {args.model}")
        print(f"Refdb-specific TS numbers: Model_{', Model_'.join(refdb_models)}")
        print(f"\n⚠ IMPORTANT: Only files from these refdb-specific models will be processed.")
        print(f"   Path patterns: Model_XX_* or TS_XX_*")
        print(f"   All other files will be skipped.\n")
    else:
        print(f"\n{'='*60}")
        print(f"WARNING: No refdb-specific models configured for '{args.model}'")
        print(f"{'='*60}")
        print("Please update REFDB_TS_NUMBERS in refdb_change.py to add refdb models.")
        print("To enable, set ENABLE_REFDB_MODEL_1=true in .env")
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            print("Exiting...")
            sys.exit(1)

    replacements = {}
    arg_mapping = {
        'hcid': 'HCID',
        'pat_brth_dt': 'PAT_BRTH_DT',
        'pat_frst_nme': 'PAT_FRST_NME',
        'pat_last_nm': 'PAT_LAST_NM',
        'prov_tax_id': 'PROV_TAX_ID',
        'billg_npi': 'BILLG_NPI',
        'nat_ea2_rndr_npi': 'NAT_EA2_RNDR_NPI'
    }

    for arg_key, json_key in arg_mapping.items():
        arg_value = getattr(args, arg_key, None)
        if arg_value:
            replacements[json_key] = arg_value

    filtered_defaults = {k: v for k, v in DEFAULT_VALUES.items() if v and str(v).strip()}

    if not replacements and not args.no_interactive:
        replacements = get_user_input(filtered_defaults)
        replacements = {k: v for k, v in replacements.items() if v and str(v).strip()}
    elif not replacements:
        replacements = filtered_defaults.copy()
        if replacements:
            print("\nUsing default values from config file:")
            for key, value in replacements.items():
                print(f"  {key}: {value}")
        else:
            print("\nError: No valid values found in config file. Please fill in the values.")
            sys.exit(1)
    else:
        for key, default_value in filtered_defaults.items():
            if key not in replacements:
                replacements[key] = default_value
        replacements = {k: v for k, v in replacements.items() if v and str(v).strip()}
        if replacements:
            print("\nUsing replacement values:")
            for key, value in replacements.items():
                print(f"  {key}: {value}")
        else:
            print("\nError: No valid replacement values specified.")
            sys.exit(1)

    backup = not args.no_backup

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            sys.exit(1)
        success = process_json_file(file_path, replacements, backup, args.model)
        sys.exit(0 if success else 1)

    elif args.directory:
        dir_path = Path(args.directory)
        if not dir_path.exists():
            print(f"Error: Directory not found: {dir_path}")
            sys.exit(1)
        successful, failed = process_directory(dir_path, replacements, args.recursive, backup, args.model)
        sys.exit(0 if failed == 0 else 1)

    else:
        current_dir = Path.cwd()
        print(f"\nNo file or directory specified. Processing current directory: {current_dir}")
        successful, failed = process_directory(current_dir, replacements, args.recursive, backup, args.model)
        sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
