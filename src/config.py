"""Configuration handling for Universal Auditor Data Cleaner."""

import json
import os

DEFAULT_CONFIG = {
    "col_date": "A",
    "col_journal": "C",
    "col_reference": "G",
    "col_description": "I",
    "col_debit": "W",
    "col_credit": "auto",
    "col_balance_start": "AF",
    "col_balance_end": "AF",
    "col_account_code": "E",
    "col_account_name": "K",
}


def load_config(path="auditor_config_universal.json"):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                saved = json.load(f)
            cfg = dict(DEFAULT_CONFIG)
            cfg.update(saved)
            return cfg
        except (OSError, ValueError):
            return dict(DEFAULT_CONFIG)
    return dict(DEFAULT_CONFIG)


def save_config(config, path="auditor_config_universal.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)