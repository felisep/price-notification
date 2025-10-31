# Monitoring Suite

A monorepo containing multiple monitoring projects with shared utilities.

## Projects

### 1. Price Tracker (`projects/price-tracker/`)
Monitors product prices on various websites and sends notifications when prices drop.

### 2. Website Monitor (`projects/website-monitor/`)
Monitors websites for any changes using both content analysis and visual comparison. Perfect for tracking schedule updates, announcements, or any content changes.

## Features

### Website Monitor Features:

- 📸 **Visual Comparison**: Takes screenshots and highlights differences
- 🔍 **Content Monitoring**: Tracks text changes using CSS selectors
- 💬 **Discord Integration**: Send notifications to Discord channels
- ⚙️ **Configurable**: Easy JSON configuration for multiple websites
- 🤖 **GitHub Actions**: Automated monitoring with scheduling

## Quick Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Configure website monitoring:**
   Edit `projects/website-monitor/config.json`:
   ```json
   {
     "websites": [
       {
         "name": "table_tennis_schedule",
         "url": "https://your-table-tennis-site.com/schedule",
         "selectors": {
           "schedule_table": "table.schedule, .schedule",
           "announcements": ".announcements, .news"
         }
       }
     ],
     "discord_webhook": ""
   }
   ```

3. **Set environment variables:**
   ```bash
   export DISCORD_WEBHOOK="https://discord.com/api/webhooks/..."
   ```

4. **Run website monitor:**
   ```bash
   cd projects/website-monitor
   python monitor.py
   ```

## Docker Usage

```bash
# Build image
docker build -t monitoring-suite .

# Run price tracker
docker run -e PROJECT_TYPE=price-tracker \
  -e DISCORD_WEBHOOK="https://discord.com/api/webhooks/..." \
  monitoring-suite

# Run website monitor
docker run -e PROJECT_TYPE=website-monitor \
  -e DISCORD_WEBHOOK="https://discord.com/api/webhooks/..." \
  monitoring-suite
```

## GitHub Actions Setup

The workflow runs automatically:

- **Price Tracker**: Every 4 hours
- **Website Monitor**: Twice daily (9 AM and 6 PM UTC)

### Required GitHub Secrets

- `DISCORD_WEBHOOK`: Discord webhook URL

