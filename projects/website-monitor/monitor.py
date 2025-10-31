"""
Website Monitor - Detects changes on web pages and sends notifications
with visual comparison using screenshots and highlighted differences.
"""

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import sys
import json
from datetime import datetime
from typing import Optional, Dict, Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Using system environment variables only.")

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from notifications import send_notification
from utils import has_content_changed, ensure_directory_exists


class WebsiteMonitor:
    def __init__(self, config_file: str = "config.json"):
        """Initialize the website monitor with configuration."""
        self.config = self.load_config(config_file)
        self.screenshots_dir = "screenshots"
        self.data_dir = "data"
        ensure_directory_exists(self.screenshots_dir)
        ensure_directory_exists(self.data_dir)
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file {config_file} not found. Creating default config.")
            default_config = {
                "websites": [
                    {
                        "name": "table_tennis_schedule",
                        "url": "https://example.com/schedule",
                        "selectors": {
                            "main_content": "body",
                            "schedule_table": "table.schedule",
                            "announcements": ".announcements"
                        }
                    }
                ],
                "discord_webhook": ""
            }
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def take_screenshot(self, url: str, output_path: str, full_page: bool = True) -> bool:
        """Take a screenshot of the webpage using Playwright."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url)
                page.wait_for_load_state('networkidle')
                page.screenshot(path=output_path, full_page=full_page)
                browser.close()
            return True
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return False
    
    def compare_screenshots(self, img1_path: str, img2_path: str, diff_path: str) -> tuple[bool, float]:
        """
        Compare two screenshots and create a diff image highlighting changes.
        Returns (has_differences, difference_percentage)
        """
        try:
            # Load images
            img1 = cv2.imread(img1_path)
            img2 = cv2.imread(img2_path)
            
            if img1 is None or img2 is None:
                return False, 0.0
            
            # Resize images to same dimensions if needed
            if img1.shape != img2.shape:
                h, w = min(img1.shape[0], img2.shape[0]), min(img1.shape[1], img2.shape[1])
                img1 = cv2.resize(img1, (w, h))
                img2 = cv2.resize(img2, (w, h))
            
            # Calculate difference
            diff = cv2.absdiff(img1, img2)
            gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            
            # Threshold to get binary image
            _, thresh = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
            
            # Calculate percentage of changed pixels
            total_pixels = thresh.shape[0] * thresh.shape[1]
            changed_pixels = cv2.countNonZero(thresh)
            change_percentage = (changed_pixels / total_pixels) * 100
            
            # Create highlighted diff image
            highlighted = img2.copy()
            
            # Find contours of changed areas
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Draw rectangles around changed areas
            for contour in contours:
                if cv2.contourArea(contour) > 100:  # Filter small changes
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(highlighted, (x, y), (x + w, y + h), (0, 0, 255), 3)
            
            # Save the highlighted diff image
            cv2.imwrite(diff_path, highlighted)
            
            # Consider significant change if more than 0.5% of pixels changed
            has_significant_change = change_percentage > 0.5
            
            return has_significant_change, change_percentage
            
        except Exception as e:
            print(f"Error comparing screenshots: {e}")
            return False, 0.0
    
    def get_page_content(self, url: str, selectors: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Extract content from webpage using specified selectors."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            content = {}
            
            if selectors:
                for name, selector in selectors.items():
                    elements = soup.select(selector)
                    if elements:
                        content[name] = '\n'.join(element.get_text(strip=True) for element in elements)
                    else:
                        content[name] = ""
            else:
                # Default: get all text content
                content['full_page'] = soup.get_text(strip=True)
            
            return content
            
        except Exception as e:
            print(f"Error fetching page content: {e}")
            return {}
    
    def monitor_website(self, website_config: Dict[str, Any]) -> bool:
        """Monitor a single website for changes."""
        name = website_config['name']
        url = website_config['url']
        selectors = website_config.get('selectors', {})
        
        print(f"Monitoring {name} at {url}")
        
        # File paths
        current_screenshot = os.path.join(self.screenshots_dir, f"{name}_current.png")
        previous_screenshot = os.path.join(self.screenshots_dir, f"{name}_previous.png")
        diff_screenshot = os.path.join(self.screenshots_dir, f"{name}_diff.png")
        content_hash_file = os.path.join(self.data_dir, f"{name}_content.hash")
        
        # Get current content
        current_content = self.get_page_content(url, selectors)
        if not current_content:
            print(f"Failed to get content from {url}")
            return False
        
        # Check for content changes
        content_str = json.dumps(current_content, sort_keys=True)
        content_changed, _ = has_content_changed(content_str, content_hash_file)
        
        # Take current screenshot
        screenshot_success = self.take_screenshot(url, current_screenshot)
        
        visual_change_detected = False
        change_percentage = 0.0
        
        # Compare screenshots if previous exists
        if screenshot_success and os.path.exists(previous_screenshot):
            visual_change_detected, change_percentage = self.compare_screenshots(
                previous_screenshot, current_screenshot, diff_screenshot
            )
        
        # Determine if notification should be sent
        should_notify = content_changed or visual_change_detected
        
        if should_notify:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Prepare notification message
            changes = []
            if content_changed:
                changes.append("content changes detected")
            if visual_change_detected:
                changes.append(f"visual changes detected ({change_percentage:.2f}% of page changed)")
            
            message = f"""
🔄 Website Change Detected: {name}

URL: {url}
Time: {timestamp}
Changes: {', '.join(changes)}

Please check the attached screenshot for highlighted differences.
            """.strip()
            
            # Send Discord notification
            success = send_notification(
                message=message,
                webhook_url=self.config.get('discord_webhook') or os.getenv('DISCORD_WEBHOOK'),
                image_path=diff_screenshot if visual_change_detected else current_screenshot
            )
            
            print(f"Change detected for {name}. Notification sent: {success}")
            
            # Move current screenshot to previous for next comparison
            if screenshot_success and os.path.exists(current_screenshot):
                if os.path.exists(previous_screenshot):
                    os.remove(previous_screenshot)
                os.rename(current_screenshot, previous_screenshot)
            
            return success
        else:
            print(f"No changes detected for {name}")
            
            # Move current screenshot to previous for next comparison
            if screenshot_success and os.path.exists(current_screenshot):
                if os.path.exists(previous_screenshot):
                    os.remove(previous_screenshot)
                os.rename(current_screenshot, previous_screenshot)
            
            return True
    
    def run(self):
        """Run monitoring for all configured websites."""
        print(f"Starting website monitoring at {datetime.now()}")
        
        for website in self.config['websites']:
            try:
                self.monitor_website(website)
            except Exception as e:
                print(f"Error monitoring {website.get('name', 'unknown')}: {e}")
        
        print("Website monitoring completed")


if __name__ == "__main__":
    monitor = WebsiteMonitor()
    monitor.run()