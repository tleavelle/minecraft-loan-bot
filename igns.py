# igns.py

def load_igns(filename="igns.txt"):
    with open(filename, "r") as f:
        return sorted({line.strip() for line in f if line.strip()}, key=str.lower)

def is_valid_ign(ign, igns_set):
    return ign in igns_set
