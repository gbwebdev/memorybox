import unicodedata

def remove_accents(input_str):
    # Normalize the string to decomposed form (NFD)
    nfkd_form = unicodedata.normalize('NFD', input_str)
    
    # Filter out combining characters (accents, etc.)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])