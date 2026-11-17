"""Core data-processing logic for Universal Auditor Data Cleaner."""

import re


def column_letter_to_number(column_letter):
    """Convert Excel column letter to 0-based number. 'auto' returns 'auto'."""
    if not column_letter or str(column_letter).lower() == "auto":
        return "auto"
    letters = re.sub(r"[^A-Za-z]", "", str(column_letter)).upper()
    if not letters:
        return "auto"
    number = 0
    for i, char in enumerate(letters[::-1]):
        number += (ord(char) - 64) * (26 ** i)
    return number - 1


def column_number_to_letter(column_number):
    """Convert 0-based number to Excel column letter."""
    if column_number is None or column_number < 0:
        return ""
    letters = ""
    num = column_number + 1
    while num > 0:
        num, remainder = divmod(num - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


def is_numeric(value):
    try:
        float(str(value).strip().replace(",", "").replace(" ", ""))
        return True
    except (ValueError, TypeError):
        return False


def to_float(value):
    if value is None:
        return 0.0
    text = str(value).strip()
    text = text.replace(" ", "")
    # Handle parentheses as negatives
    if text.startswith("(") and text.endswith(")"):
        text = "-" + text[1:-1]
    # Remove currency symbols and Dr/Cr suffixes
    text = text.replace("$", "").replace("RM", "")
    text = text.replace("Dr", "").replace("Cr", "").replace("dr", "").replace("cr", "")
    text = text.replace(",", "")
    try:
        return float(text)
    except (ValueError, TypeError):
        return 0.0


def is_account_line(text):
    if not text:
        return False
    text_lower = str(text).lower()
    return "account code" in text_lower or ("account" in text_lower and "code" in text_lower)


def extract_account_info(row):
    """Return (code, name) if row contains account information, else (None, None)."""
    row_text = " ".join(str(cell) for cell in row if cell not in (None, ""))

    if is_account_line(row_text):
        match = re.search(r"account\s*code[:\s]*([^\s]+)\s*(.*)", row_text, re.IGNORECASE)
        if match:
            code = match.group(1).strip()
            name = match.group(2).strip()
            if code and any(c.isalnum() for c in code):
                return code, name

    # Look for patterns like 12399-D01 anywhere
    for cell in row:
        cell_str = str(cell).strip() if cell is not None else ""
        if re.match(r"^\d{4,5}-[A-Z]\d{2}$", cell_str):
            return cell_str, "Detected Account"

    return None, None


def _get_cell_value(row, col_index):
    if col_index == "auto" or col_index is None:
        return ""
    if not isinstance(col_index, int) or col_index >= len(row):
        return ""
    value = row[col_index]
    return value if value is not None else ""


def is_transaction_row(date, reference, debit, credit):
    has_date = bool(str(date).strip())
    has_ref = bool(str(reference).strip())
    has_debit = is_numeric(debit) and to_float(debit) > 0
    has_credit = is_numeric(credit) and to_float(credit) > 0
    return (has_date and has_ref) or (has_date and (has_debit or has_credit))


def process_rows(rows, config):
    """Process raw rows into a list of transaction dicts."""
    number_config = {}
    for key, value in config.items():
        if key.startswith("col_"):
            number_config[key] = column_letter_to_number(value)

    processed = []
    current_code = "Unknown"
    current_name = "Unknown Account"

    for row in rows:
        code, name = extract_account_info(row)
        if code:
            current_code = code
            if name:
                current_name = name
            continue

        date_val = _get_cell_value(row, number_config.get("col_date", 0))
        journal_val = _get_cell_value(row, number_config.get("col_journal", 2))
        ref_val = _get_cell_value(row, number_config.get("col_reference", 6))
        desc_val = _get_cell_value(row, number_config.get("col_description", 8))
        debit_val = _get_cell_value(row, number_config.get("col_debit", 22))

        credit_col = number_config.get("col_credit", "auto")
        if credit_col == "auto":
            credit_val = _auto_detect_credit(row, number_config)
        else:
            credit_val = _get_cell_value(row, credit_col)

        balance_col = number_config.get("col_balance_start", 31)
        balance_val = _get_cell_value(row, balance_col)

        if is_transaction_row(date_val, ref_val, debit_val, credit_val):
            processed.append({
                "Account Code": current_code,
                "Account Name": current_name,
                "Date": date_val,
                "Journal": journal_val,
                "Reference": ref_val,
                "Description": desc_val,
                "Debit": debit_val,
                "Credit": credit_val,
                "Balance": balance_val,
            })

    return processed


def _auto_detect_credit(row, number_config):
    skip_cols = set()
    debit_col = number_config.get("col_debit")
    if isinstance(debit_col, int):
        skip_cols.add(debit_col)
    bal_start = number_config.get("col_balance_start")
    bal_end = number_config.get("col_balance_end", bal_start)
    if isinstance(bal_start, int):
        for c in range(bal_start, (bal_end if isinstance(bal_end, int) else bal_start) + 1):
            skip_cols.add(c)

    for col_idx, cell in enumerate(row):
        if col_idx in skip_cols:
            continue
        if is_numeric(cell) and to_float(cell) > 0:
            return cell
    return ""