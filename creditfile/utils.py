# Created 2023-10-11


import re
import unicodedata
from numbers import Number


def notna(x):
    'Checks if value is observed.'
    return x == x and x is not None
    
def isna(x):
    'Complement to notna.'
    return not notna(x)
    
def force_numeric(num, error_value=float('nan')):
    'Force an object to a numerical type.'
    if isinstance(num, Number) and notna(num):
        return num
    elif isinstance(num, str):
        num = re.sub(r'[^0-9.\-]', '', num)
        try:
            return float(num)
        except ValueError:
            return error_value
    else:
        return error_value
        
def normalize_text(text):
    'Normalize text to ascii.'
    normalized = (
        unicodedata.normalize('NFKD', text)
        .encode('ascii', errors='ignore')
        .decode('utf-8')
        .lower()
    )
    normalized = re.sub(r'[\.\,\-\/\(\)\s]+', ' ', normalized).strip()
    normalized = re.sub(r'[^a-z0-9 ]', '', normalized)
    return normalized