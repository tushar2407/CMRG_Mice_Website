import re

def extract_number(filename):
    match = re.search(r'group_(\d+)\.json', filename)
    if match:
        return int(match.group(1))
    return None