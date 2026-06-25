#!/usr/bin/env python3
"""
Postman Collection Generator - Creates Postman v2.1.0 API collections from JSON payload files.
Used by main_processor.py, rename_files.py, and postman_cli.py.
"""

import json
import re
from pathlib import Path


META_TRANSID_MODEL_1 = "20220117181853TMBL20359Cl893580999"
META_SRC_ENVRMT = "IMSH"


class PostmanCollectionGenerator:
    """Generates Postman collections from JSON payload files in a source directory."""

    def __init__(self, source_dir=None, output_dir=None):
        self.source_dir = Path(source_dir) if source_dir else None
        self.output_dir = Path(output_dir) if output_dir else Path("postman_collections")

    def _default_meta_transid(self):
        return META_TRANSID_MODEL_1

    def _collect_json_files(self, directory=None):
        """Collect all .json files under directory (default: self.source_dir)."""
        root = Path(directory) if directory else self.source_dir
        if not root or not root.exists():
            return []
        files = []
        for path in root.rglob("*.json"):
            if path.is_file():
                files.append(path)
        return sorted(files)

    def _build_request_headers(self, json_data):
        """Build Postman request headers; use meta-transid from file or default."""
        meta_transid = (
            json_data.get("meta-transid")
            if isinstance(json_data, dict)
            else None
        )
        if not meta_transid:
            meta_transid = self._default_meta_transid()
        meta_src = (
            json_data.get("meta-src-envrmt", META_SRC_ENVRMT)
            if isinstance(json_data, dict)
            else META_SRC_ENVRMT
        )
        return [
            {"key": "Content-Type", "value": "application/json", "type": "text"},
            {"key": "meta-transid", "value": meta_transid, "type": "text"},
            {"key": "meta-src-envrmt", "value": meta_src, "type": "text"},
        ]

    def generate_postman_collection(self, collection_name, custom_filename=None, **_kwargs):
        """
        Generate a single Postman collection from all JSON files in self.source_dir.
        Returns the path to the written collection file, or None on failure.
        """
        if not self.source_dir or not self.source_dir.exists():
            return None
        json_files = self._collect_json_files()
        if not json_files:
            return None
        slug = re.sub(r"[^\w\-]", "_", collection_name).strip("_")
        filename = custom_filename if custom_filename else f"{slug}.json"
        return self._write_collection(
            collection_name=collection_name,
            json_files=json_files,
            output_filename=filename,
        )

    def _write_collection(self, collection_name, json_files, output_filename, collection_folder=None):
        """Build Postman collection dict and write to output_dir / collection_folder / output_filename."""
        display_name = Path(output_filename).stem if output_filename else collection_name
        url_raw = "{{baseUrl}}/api/validate/{{tc_id}}"
        url_path = ["api", "validate", "{{tc_id}}"]
        variables = [
            {"key": "baseUrl", "value": "http://localhost:3000", "type": "string"},
            {"key": "tc_id", "value": "", "type": "string"},
        ]
        items = []
        for jpath in json_files:
            try:
                with open(jpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError):
                continue
            name = jpath.stem
            headers = self._build_request_headers(data)
            raw_body = json.dumps(data, indent=2, ensure_ascii=False)
            request = {
                "method": "POST",
                "header": headers,
                "url": {
                    "raw": url_raw,
                    "host": ["{{baseUrl}}"],
                    "path": url_path,
                },
                "body": {"mode": "raw", "raw": raw_body, "options": {"raw": {"language": "json"}}},
            }
            items.append({"name": name, "request": request})

        collection = {
            "info": {
                "name": display_name,
                "description": f"API collection for {display_name} test cases",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            },
            "item": items,
            "variable": variables,
        }

        if collection_folder:
            folder_name = re.sub(r"[^\w\-]", "_", collection_folder).strip("_")
        else:
            folder_name = re.sub(r"[^\w\-]", "_", display_name).strip("_")
        out_dir = self.output_dir / folder_name
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / output_filename
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(collection, f, indent=2, ensure_ascii=False)
        return str(out_path)

    def generate_collection_for_directory(self, directory):
        """Generate a collection for a specific directory. Returns path to collection file or None."""
        if not directory:
            return None
        dir_path = Path(directory)
        if not dir_path.is_absolute() and self.source_dir:
            dir_path = self.source_dir / directory
        if not dir_path.exists():
            return None
        json_files = self._collect_json_files(str(dir_path))
        if not json_files:
            return None
        collection_name = dir_path.name
        slug = re.sub(r"[^\w\-]", "_", collection_name).strip("_")
        filename = f"{slug}.json"
        return self._write_collection(
            collection_name=collection_name,
            json_files=json_files,
            output_filename=filename,
        )

    def generate_all_collections(self):
        """Generate collections for all directories under source_dir that contain JSON files."""
        if not self.source_dir or not self.source_dir.exists():
            return {}
        results = {}
        seen_dirs = set()
        for path in self.source_dir.rglob("*.json"):
            parent = path.parent
            key = str(parent)
            if key in seen_dirs:
                continue
            json_files = self._collect_json_files(key)
            if not json_files:
                continue
            seen_dirs.add(key)
            name = Path(key).name
            slug = re.sub(r"[^\w\-]", "_", name).strip("_")
            out_path = self._write_collection(
                collection_name=name,
                json_files=json_files,
                output_filename=f"{slug}.json",
            )
            if out_path:
                results[name] = out_path
        return results

    def list_available_directories(self):
        """List directories under source_dir that contain at least one JSON file."""
        if not self.source_dir or not self.source_dir.exists():
            return []
        dirs = set()
        for path in self.source_dir.rglob("*.json"):
            if path.is_file():
                dirs.add(str(path.parent))
        return sorted(dirs)

    def get_directory_stats(self, directory):
        """Return stats for a directory."""
        if not directory:
            return {"error": "No directory specified"}
        dir_path = Path(directory)
        if not dir_path.is_absolute() and self.source_dir:
            dir_path = self.source_dir / directory
        if not dir_path.exists():
            return {"error": f"Directory not found: {dir_path}"}
        json_files = self._collect_json_files(str(dir_path))
        if not json_files:
            return {"error": "No JSON files found", "total_files": 0, "suffixes": [], "edit_ids": [], "eob_codes": [], "file_types": []}
        suffixes = set()
        edit_ids = set()
        eob_codes = set()
        for p in json_files:
            suffixes.add(p.suffix)
            stem = p.stem
            parts = re.split(r"[#_]", stem)
            for part in parts:
                if part and re.match(r"^[A-Z0-9]{6,}$", part) and "TC" not in part.upper():
                    edit_ids.add(part)
                if re.match(r"^00W\d{2}$", part):
                    eob_codes.add(part)
        return {
            "total_files": len(json_files),
            "file_types": list(suffixes),
            "suffixes": list(suffixes),
            "edit_ids": list(edit_ids),
            "eob_codes": list(eob_codes),
        }

    def validate_collection(self, collection_path):
        """Validate a Postman collection file."""
        path = Path(collection_path)
        result = {"valid": False, "errors": [], "warnings": [], "stats": {}}
        if not path.exists():
            result["errors"].append(f"File not found: {path}")
            return result
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            result["errors"].append(f"Invalid JSON: {e}")
            return result
        except OSError as e:
            result["errors"].append(str(e))
            return result
        if not isinstance(data, dict):
            result["errors"].append("Root must be a JSON object")
            return result
        if "info" not in data:
            result["errors"].append("Missing 'info'")
        if "item" not in data:
            result["errors"].append("Missing 'item'")
        else:
            result["stats"]["items"] = len(data["item"]) if isinstance(data["item"], list) else 0
        result["valid"] = len(result["errors"]) == 0
        return result
