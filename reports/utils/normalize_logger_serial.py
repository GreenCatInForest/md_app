import re

# def is_valid_serial(cleaned_serial):
#     """Check if the serial has exactly three digits, a dash, and more digits."""
#     pattern = r'^\d{3}-\d+$'
#     return bool(re.match(pattern, cleaned_serial))

def contains_letters(cleaned_serial):
    """Check if the serial contains any letters."""
    pattern = r'[a-zA-Z]'
    return bool(re.search(pattern, cleaned_serial))

def normalize_logger_serial(serial, dash_position=3):
    """Remove non-numeric characters and reformat the logger serial input."""
    cleaned_serial = re.sub(r'\D', '', serial)
    if len(cleaned_serial) > dash_position:
        cleaned_serial = cleaned_serial[:dash_position] + '-' + cleaned_serial[dash_position:]

    if contains_letters(cleaned_serial):
        raise ValueError("Serial must be numeric.")
    
    return cleaned_serial