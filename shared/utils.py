import re
import hashlib
import os
from typing import Any, Optional


def clean_number(price_str: str) -> str:
    """Clean and extract numbers from price strings."""
    if price_str is None:
        return "0"
    
    # Remove any non-digit characters except decimal points
    cleaned = re.sub(r'[^\d.,]', '', str(price_str))
    
    # Handle European format (comma as decimal separator)
    if ',' in cleaned and '.' in cleaned:
        # Assume comma is thousands separator if both present
        cleaned = cleaned.replace(',', '')
    elif ',' in cleaned:
        # Assume comma is decimal separator if only comma present
        cleaned = cleaned.replace(',', '.')
    
    return cleaned


def calculate_hash(content: str) -> str:
    """Calculate SHA256 hash of content for change detection."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def ensure_directory_exists(directory_path: str) -> None:
    """Create directory if it doesn't exist."""
    os.makedirs(directory_path, exist_ok=True)


def load_previous_hash(file_path: str) -> Optional[str]:
    """Load previously saved hash from file."""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return f.read().strip()
    except Exception as e:
        print(f"Error loading previous hash: {e}")
    return None


def save_hash(file_path: str, content_hash: str) -> bool:
    """Save hash to file."""
    try:
        ensure_directory_exists(os.path.dirname(file_path))
        with open(file_path, 'w') as f:
            f.write(content_hash)
        return True
    except Exception as e:
        print(f"Error saving hash: {e}")
        return False


def has_content_changed(content: str, hash_file_path: str) -> tuple[bool, str]:
    """
    Check if content has changed by comparing hashes.
    Returns (has_changed, new_hash)
    """
    new_hash = calculate_hash(content)
    previous_hash = load_previous_hash(hash_file_path)
    
    if previous_hash is None:
        # First time checking - save hash and return no change
        save_hash(hash_file_path, new_hash)
        return False, new_hash
    
    has_changed = new_hash != previous_hash
    
    if has_changed:
        save_hash(hash_file_path, new_hash)
    
    return has_changed, new_hash