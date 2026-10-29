import os
from dotenv import load_dotenv
load_dotenv()

def require(name):
    value = os.getenv(name)
    if not value or value == "replace_me":
        raise ValueError(f"Set {name} in .env")
    return value
