import re
import json
from pathlib import Path
from datetime import datetime, timezone

import modules.actions as actions

def apply_schema(raw_section: dict, schema: dict) -> dict:
    """
    Returns a dict with target field names populated from raw data,
    or None if the label isn't present.
    """
    result = {}
    for field_name, label in schema.items():
        result[field_name] = raw_section.get(label)
    return result

def make_model_key(model_title: str) -> str:
    ''' Converts model title to a standardized model key'''
    if not model_title:
        return None
    s = model_title.lower()
    s = re.sub(r'[^a-z0-9]+', '_', s)
    s = s.strip('_')
    return s

def current_timestamp() -> str:
    '''Returns the UTC timestamp format'''
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def load_json_list(path: str) -> list:
    """
    Load a JSON file containing a list.
    If it doesn't exist, return an empty list.
    """
    p = Path(path)
    if not p.exists():
        return []
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_json_list(path: str, rows: list):
    """
    Save a list back to JSON, creating directories if needed.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

def append_json_row(path: str, row: dict):
    """
    Append a row dict to a JSON list file (create file if needed).
    """
    rows = load_json_list(path)
    rows.append(row)
    save_json_list(path, rows)

def add_metadata(data, model_title):
    ''' Adds some standard metadata fields to the data dictionary'''
    enriched = data.copy()
    enriched['model_key'] = make_model_key(model_title)
    enriched['model_name'] = model_title
    enriched['scrape_timestamp'] = current_timestamp()
    return enriched

def summary_pipeline(driver, SUMMARY_SCHEMA, title, path = "data/summary.json" ):
    ''' Pipeline to extract, transform, and load summary stats'''
    stats  = actions.get_model_card_stats(driver)
    stats_staging = add_metadata(stats, title)
    stats_final = apply_schema(stats_staging, SUMMARY_SCHEMA)

    stats_summary = load_json_list(path)
    append_json_row(path, stats_final)

    print(f'Appended summary data {title} to {path}')

    return None

def accordion_section_pipeline(driver, sections, SCHEMA, title):
    ''' Pipeline to extract, transform, and load accordion section features'''
    for section_name in sections:

        section_name_slug = re.sub(r'[^a-z0-9]+', '_', section_name.lower()).strip('_')

        features = actions.get_features(driver, section=section_name)
        features_staging = add_metadata(features, title)
        features_final = apply_schema(features_staging, SCHEMA[section_name_slug])

        path = f"../data/{section_name_slug}.json"

        feature_data = load_json_list(path)

        append_json_row(path, features_final)

        print(f'Appended {section_name} data {title} to {path}')

    return None