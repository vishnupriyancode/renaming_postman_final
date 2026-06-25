#!/usr/bin/env python3
"""
Dynamic model discovery system for TS folders.
Automatically detects Model_XX_* and TS_XX_* folders under source_folder/model_1.
"""

import os
import re
import glob
from typing import List, Dict, Optional


def normalize_ts_number(ts_number_raw: str) -> str:
    """
    Normalize TS number to handle different digit patterns.

    Examples:
        "1" -> "01", "01" -> "01", "10" -> "10", "100" -> "100"
    """
    ts_num = int(ts_number_raw)

    if 1 <= ts_num <= 9:
        return f"{ts_num:02d}"
    elif 10 <= ts_num <= 99:
        return f"{ts_num:02d}"
    elif 100 <= ts_num <= 999:
        return f"{ts_num:03d}"
    return ts_number_raw


def generate_postman_collection_name(ts_number: str) -> str:
    """Generate Postman collection name based on TS number."""
    return f"ts_{ts_number}_collection"


def format_ts_argument(ts_number: str) -> str:
    """Format TS number for command line arguments."""
    ts_num = int(ts_number)

    if 1 <= ts_num <= 9:
        return f"{ts_num:02d}"
    elif 10 <= ts_num <= 99:
        return f"{ts_num:02d}"
    elif 100 <= ts_num <= 999:
        return f"{ts_num:03d}"
    return ts_number


def discover_ts_folders(base_dir: str = ".", use_model_1_destination: bool = False) -> List[Dict]:
    """
    Discover model folders under base_dir and extract model parameters.
    Supports Model_XX_* and TS_XX_* naming under source_folder/model_1.

    Args:
        base_dir: Base directory to search for model folders
        use_model_1_destination: If True, place outputs under renaming_jsons/model_1

    Returns:
        List of model configuration dicts
    """
    models = []

    def get_folders_from_patterns(patterns):
        all_folders = []
        for pattern in patterns:
            all_folders.extend(glob.glob(pattern))
        return list(dict.fromkeys(all_folders))

    patterns = [
        os.path.join(base_dir, "Model_*"),
        os.path.join(base_dir, "TS_*"),
    ]
    ts_folders_list = get_folders_from_patterns(patterns)
    valid_suffixes = ("_sur", "_payloads_sur", "_ayloads_sur")
    ts_folders = [
        f for f in ts_folders_list
        if os.path.isdir(f) and f.endswith(valid_suffixes)
    ]

    print(f"Scanning for model folders in: {base_dir}")
    print(f"Found {len(ts_folders)} model folders")

    folder_patterns = [
        r'Model_(\d{1,3})_(.+?)_model_1_([A-Za-z0-9]+)_([A-Za-z0-9]+)_(sur|payloads_sur|ayloads_sur)$',
        r'TS_(\d{1,3})_(.+?)_model_1_([A-Za-z0-9]+)_([A-Za-z0-9]+)_(sur|payloads_sur|ayloads_sur)$',
        r'Model_(\d{1,3})_(.+?)_([A-Za-z0-9]+)_([A-Za-z0-9]+)_(sur|payloads_sur|ayloads_sur)$',
        r'TS_(\d{1,3})_(.+?)_([A-Za-z0-9]+)_([A-Za-z0-9]+)_(sur|payloads_sur|ayloads_sur)$',
    ]

    for folder_path in ts_folders:
        folder_name = os.path.basename(folder_path)

        match = None
        for pattern in folder_patterns:
            match = re.match(pattern, folder_name)
            if match:
                break

        if not match:
            print(f"Warning: Could not parse folder name: {folder_name}")
            continue

        ts_number_raw, model_name, edit_id, code = match.groups()[:4]
        ts_number = normalize_ts_number(ts_number_raw)

        payloads_path = os.path.join(folder_path, "payloads")
        has_payloads_structure = os.path.exists(payloads_path)

        if has_payloads_structure:
            regression_path = os.path.join(payloads_path, "regression")
            smoke_path = os.path.join(payloads_path, "smoke")
            has_regression = os.path.exists(regression_path)
            has_smoke = os.path.exists(smoke_path)

            if not has_regression and not has_smoke:
                print(f"Warning: Neither regression nor smoke folders found in {folder_name}/payloads")
                continue

            folder_configs = []
            if has_regression:
                folder_configs.append(("regression", regression_path))
            if has_smoke:
                folder_configs.append(("smoke", smoke_path))
        else:
            regression_path = os.path.join(folder_path, "regression")
            if not os.path.exists(regression_path):
                print(f"Warning: Regression folder not found in {folder_name}")
                continue
            folder_configs = [("regression", regression_path)]

        if "_payloads_sur" in folder_name:
            dest_folder_name = folder_name.replace("_payloads_sur", "_payloads_dis")
        elif "_ayloads_sur" in folder_name:
            dest_folder_name = folder_name.replace("_ayloads_sur", "_payloads_dis")
        elif "_sur" in folder_name:
            dest_folder_name = folder_name.replace("_sur", "_dis")
        else:
            dest_folder_name = folder_name

        for folder_type, source_path in folder_configs:
            if use_model_1_destination:
                if has_payloads_structure:
                    dest_dir = os.path.join("renaming_jsons", "model_1", dest_folder_name, "payloads", folder_type)
                else:
                    dest_dir = os.path.join("renaming_jsons", "model_1", dest_folder_name, folder_type)
            else:
                if has_payloads_structure:
                    dest_dir = os.path.join("renaming_jsons", dest_folder_name, "payloads", folder_type)
                else:
                    dest_dir = os.path.join("renaming_jsons", dest_folder_name, folder_type)

            model_slug = model_name.replace(' ', '_').replace('-', '_').lower()
            base_collection_name = f"Model_{ts_number}_{model_name}_Collection"
            base_file_name = f"{model_slug}_model_1_{edit_id}_{code}"

            if folder_type == "smoke":
                postman_collection_name = base_collection_name
                postman_file_name = f"{base_file_name}_smoke.json"
            else:
                postman_collection_name = base_collection_name
                postman_file_name = f"{base_file_name}_regression.json"

            model_config = {
                "ts_number": ts_number,
                "ts_number_raw": ts_number_raw,
                "edit_id": edit_id,
                "code": code,
                "source_dir": source_path,
                "dest_dir": dest_dir,
                "postman_collection_name": postman_collection_name,
                "postman_file_name": postman_file_name,
                "folder_name": folder_name,
                "folder_type": folder_type,
            }

            models.append(model_config)
            print(f"Discovered: TS_{ts_number} ({edit_id}_{code}) [{folder_type}] [Raw: {ts_number_raw}]")

    return models


def get_model_by_ts_number(ts_number: str, base_dir: str = ".") -> Optional[Dict]:
    """Get model configuration for a specific TS number."""
    models = discover_ts_folders(base_dir)
    normalized_input = normalize_ts_number(ts_number)

    for model in models:
        if model["ts_number"] == normalized_input:
            return model

    return None


def get_all_models(base_dir: str = ".") -> List[Dict]:
    """Get all discovered model configurations."""
    return discover_ts_folders(base_dir)


def validate_model_config(model: Dict) -> bool:
    """Validate that a model configuration has all required fields and paths exist."""
    required_fields = ["ts_number", "edit_id", "code", "source_dir", "dest_dir"]

    for field in required_fields:
        if field not in model:
            print(f"Missing required field: {field}")
            return False

    if not os.path.exists(model["source_dir"]):
        print(f"Source directory does not exist: {model['source_dir']}")
        return False

    return True


def print_discovered_models(models: List[Dict]):
    """Print a formatted list of discovered models."""
    if not models:
        print("No TS models discovered")
        return

    print(f"\nDISCOVERED TS MODELS ({len(models)} found)")
    print("=" * 60)

    for i, model in enumerate(models, 1):
        print(f"{i}. TS_{model['ts_number']}: {model['edit_id']}_{model['code']}")
        print(f"   Source: {model['source_dir']}")
        print(f"   Dest:   {model['dest_dir']}")
        print(f"   Collection: {model['postman_collection_name']}")
        print()


def print_nested_models_display():
    """Display all models in a nested structure for model_1."""
    print("\n" + "=" * 80)
    print("NESTED MODEL STRUCTURE")
    print("=" * 80)

    model_1_models = discover_ts_folders("source_folder/model_1", use_model_1_destination=True)

    print(f"Total Models Found: {len(model_1_models)}")
    print("=" * 80)

    if model_1_models:
        print(f"\nMODEL_1 MODELS ({len(model_1_models)} models)")
        print("-" * 50)
        for i, model in enumerate(model_1_models, 1):
            ts_number = model['ts_number']
            edit_id = model['edit_id']
            code = model['code']
            collection_name = model['postman_collection_name']
            print(f"  {i:2d}. TS_{ts_number:02s} | {collection_name}")
            print(f"      |- Edit ID: {edit_id}")
            print(f"      |- Code: {code}")
            print(f"      `- Collection: {collection_name}")
            print()
    else:
        print(f"\nMODEL_1 MODELS (0 models)")
        print("-" * 50)
        print("   No model_1 models found")

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"model_1 Models: {len(model_1_models)}")
    print(f"Total Models: {len(model_1_models)}")
    print("=" * 80)


if __name__ == "__main__":
    print("Testing Dynamic Model Discovery")
    print("=" * 50)

    print_nested_models_display()

    print("\n" + "=" * 50)
    print("TRADITIONAL DISPLAY")
    print("=" * 50)

    models = discover_ts_folders()
    print_discovered_models(models)

    if models:
        first_model = models[0]
        ts_number = first_model["ts_number"]
        print(f"Testing lookup for TS_{ts_number}...")

        found_model = get_model_by_ts_number(ts_number)
        if found_model:
            print(f"Found model: {found_model['edit_id']}_{found_model['code']}")
        else:
            print(f"Model not found for TS_{ts_number}")
