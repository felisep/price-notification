import requests
import os
import json
from typing import Optional


def send_discord_message(message: str, webhook_url: str, file_path: Optional[str] = None) -> bool:
    """Send a message to Discord via webhook with optional file attachment."""
    try:
        if file_path and os.path.exists(file_path):
            # Send message with file attachment
            with open(file_path, 'rb') as f:
                files = {
                    'file': (os.path.basename(file_path), f, 'image/png')
                }
                data = {
                    'content': message
                }
                response = requests.post(webhook_url, data=data, files=files)
        else:
            # Send message without file
            data = {"content": message}
            response = requests.post(webhook_url, json=data)
        
        response.raise_for_status()
        return True
        
    except requests.RequestException as e:
        print(f"Failed to send Discord message: {e}")
        return False
    except Exception as e:
        print(f"Error sending Discord message: {e}")
        return False


def send_notification(
    message: str,
    webhook_url: Optional[str] = None,
    image_path: Optional[str] = None
) -> bool:
    """Send notification via Discord webhook."""
    
    # Get webhook URL from parameter or environment
    webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK")
    
    if not webhook_url:
        print("Discord webhook URL not provided. Set DISCORD_WEBHOOK environment variable.")
        return False
    
    return send_discord_message(message, webhook_url, image_path)