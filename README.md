# AUTORAY

AUTORAY is a specialized VPN subscription manager and aggregator built with Python and Flask. It automates the process of scraping V2Ray, Xray, Trojan, and Shadowsocks configurations from Telegram channels, aggregates them, and serves them via managed subscription links.

## Features

- **Automated Scraping**: Uses `snscrape` to fetch fresh configurations from specified Telegram channels.
- **Protocol Support**: Parses and cleans `vless`, `vmess`, `trojan`, and `ss` (Shadowsocks) links.
- **Subscription Management**: Secure access via generated keys.
- **Smart Caching**: Background caching system to ensure low-latency responses and reduce scraping overhead.
- **Discord Integration**: Sends real-time notifications (new keys, errors, status updates) to a Discord Webhook.
- **Multi-Port Support**: Capable of running on multiple ports simultaneously using multiprocessing.
- **Dynamic Renaming**: Automatically renames configurations with timestamps or custom tags for better organization.

## Prerequisites

- Python 3.8+
- `pip` (Python Package Installer)

## Installation

1.  **Clone the repository** (or download the source):
    ```bash
    git clone <repository-url>
    cd AUTORAY
    ```

2.  **Install dependencies**:
    ```bash
    pip install flask discord.py snscrape pytz
    ```

## Configuration

Upon the first run, the application will generate a `config.json` file.

**Default Configuration:**
```json
{
    "api_secret": "ql1lGsB7TTO3TOOR2vRjaMgQi2DvmEWtngOkxNtFhTLQaDUne6sZvhRhD0jXUAKC0DtL9EW8fCZO5GdzHaIZyuBM2Re2OdYi",
    "webhook_url": null,
    "keys": [],
    "channels": [],
    "ports": [2873],
    "cache_ttl": 1800
}
```

- **api_secret**: The master key for administrative API actions. **Change this immediately for security.**
- **webhook_url**: URL for Discord Webhook notifications.
- **channels**: List of Telegram channels to scrape.
- **ports**: Ports the server will listen on.
- **cache_ttl**: Time-to-live for cached configs in seconds (default: 30 minutes).

## Usage

Start the server:
```bash
python handler.py
```

### API Endpoints

#### User Routes
- **Get Subscription**:
  `GET /connect?key=<USER_KEY>`
  Returns the subscription body containing all scraped configs.

- **Partner/Custom Subscription**:
  `GET /custom?key=<USER_KEY>&name=<CUSTOM_NAME>`
  Returns configs renamed with the provided `<CUSTOM_NAME>`.

- **Ping**:
  `GET /ping`
  Returns `ALIVE` status.

#### Admin Routes (Requires `secret`)

- **Create Key**:
  `GET /createkey?secret=<API_SECRET>`
  Generates a new user key and returns the subscription link.

- **Add Channel**:
  `GET /addchannel?secret=<API_SECRET>&name=<CHANNEL_ID>&count=<LIMIT>`
  Adds a Telegram channel to the scraper.
  - `name`: Channel username (without @).
  - `count`: Max configs to fetch (default: 25).

- **Remove Channel**:
  `GET /delchannel?secret=<API_SECRET>&name=<CHANNEL_ID>`

- **Set Webhook**:
  `GET /setwebhook?secret=<API_SECRET>&url=<WEBHOOK_URL>`

- **Force Refresh**:
  `GET /freshconnect?secret=<API_SECRET>`
  Forces a cache update and returns fresh configs.

- **List Channels**:
  `GET /listchannels?secret=<API_SECRET>`

## Disclaimer
This tool is for educational purposes only.