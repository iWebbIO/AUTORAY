# AUTORAY Documentation

**AUTORAY** is a robust, Python-based VPN subscription aggregator and manager. It automates the collection of proxy configurations (V2Ray, Xray, Trojan, Shadowsocks) from public Telegram channels and serves them through secure, managed subscription links.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Scraping Engine](#scraping-engine)
5. [API Reference](#api-reference)
6. [Deployment](#deployment)

---

## 1. System Architecture

AUTORAY is built using **Flask** and operates on a multi-process architecture to handle high concurrency.

- **Core Engine (`core.py`)**: Handles the interaction with Telegram using `snscrape`. It parses messages, extracts proxy links using regex, cleans them, and standardizes them.
- **Request Handler (`handler.py`)**: The Flask web server that exposes API endpoints. It manages authentication, configuration persistence, and response generation.
- **Caching System**: To prevent rate-limiting from Telegram and ensure fast response times, scraped configs are cached in memory. A background thread refreshes this cache based on the `cache_ttl` setting.
- **Notification System**: Integrated with Discord Webhooks to provide real-time alerts for administrative actions and errors.

---

## 2. Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python Package Manager)

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository_url>
   cd AUTORAY
   ```

2. **Install Dependencies**:
   ```bash
   pip install flask discord.py snscrape pytz
   ```

3. **First Run**:
   Start the application to generate the default configuration file.
   ```bash
   python handler.py
   ```

---

## 3. Configuration

The application is controlled by `config.json` located in the root directory.

### Structure

```json
{
    "api_secret": "YOUR_ADMIN_SECRET_KEY",
    "webhook_url": "YOUR_DISCORD_WEBHOOK_URL",
    "keys": ["user_key_1", "user_key_2"],
    "channels": [
        {
            "name": "channel_username",
            "scrape_mode": "time",
            "scrape_days": 1,
            "scrape_limit": 25
        }
    ],
    "ports": [2873],
    "cache_ttl": 1800
}
```

### Parameters

| Parameter | Description |
| :--- | :--- |
| `api_secret` | Master key for accessing Admin API routes. **Change immediately.** |
| `webhook_url` | Discord Webhook URL for system notifications. Set to `null` to disable. |
| `keys` | List of valid user authentication keys for generating subscriptions. |
| `channels` | List of Telegram channels to scrape. See Channel Object below. |
| `ports` | Array of ports the server will listen on (e.g., `[80, 2052, 2082]`). |
| `cache_ttl` | Time in seconds before the background thread refreshes channel data (Default: 1800s / 30m). |

### Channel Object

Each entry in the `channels` list controls how a specific Telegram channel is scraped.

- **`name`**: The Telegram username (without `@`).
- **`scrape_mode`**:
  - `"count"`: Scrapes the last `X` messages.
  - `"time"`: Scrapes messages from the last `X` days/hours.
- **`scrape_limit`**: Used in `count` mode. The number of messages to fetch.
- **`scrape_days`**: Used in `time` mode.
- **`scrape_hours`**: Used in `time` mode.

---

## 4. Scraping Engine

The scraping logic is defined in `core.py`.

### Supported Protocols
AUTORAY extracts and parses the following protocols:
- `vless://`
- `vmess://` (Includes Base64 decoding and JSON repacking for renaming)
- `trojan://`
- `ss://` (Shadowsocks)

### Features
- **Link Preview Scanning**: The scraper looks inside the text content of the message **and** the link preview metadata (title/description) to find hidden configs.
- **Deduplication**: Identical configs found within the same scrape session are removed.
- **Safety Limits**: In `time` mode, a hard limit of 500 posts is enforced to prevent infinite loops on very active channels.
- **Dynamic Renaming**: All configs are renamed to include the aggregator's signature or a custom partner name.

---

## 5. API Reference

### User Endpoints
*Publicly accessible routes requiring a valid User Key.*

#### 1. Get Subscription
Fetches the aggregated list of proxies.
- **URL**: `/connect`
- **Method**: `GET`
- **Params**: `key` (User Key)
- **Response**: Plain text list of config links.

#### 2. Custom/Partner Subscription
Fetches proxies with a custom name tag (useful for resellers or specific devices).
- **URL**: `/custom`
- **Method**: `GET`
- **Params**:
  - `key`: User Key
  - `name`: Custom string to append to config names.

#### 3. Ping
Health check endpoint.
- **URL**: `/ping`
- **Response**: `ALIVE`

---

### Admin Endpoints
*Protected routes requiring the `api_secret`.*

#### 1. Create Key
Generates a new random user key.
- **URL**: `/createkey`
- **Params**: `secret`

#### 2. Add Channel
Adds a new source channel to the scraper.
- **URL**: `/addchannel`
- **Params**:
  - `secret`: API Secret
  - `name`: Channel username
  - `mode`: `count` or `time` (Default: `count`)
  - `limit`: Message count (Default: 25)
  - `days`: Lookback days (Default: 0)
  - `hours`: Lookback hours (Default: 0)

#### 3. Remove Channel
- **URL**: `/delchannel`
- **Params**: `secret`, `name`

#### 4. Force Refresh
Forces an immediate cache update for all channels.
- **URL**: `/freshconnect`
- **Params**: `secret`

#### 5. Set Webhook
Updates the Discord notification URL.
- **URL**: `/setwebhook`
- **Params**: `secret`, `url`

---

## 6. Deployment

### Multi-Port Support
AUTORAY utilizes Python's `multiprocessing` to bind to multiple ports simultaneously. This is useful for bypassing firewalls that may block specific ports.

To configure, edit the `ports` array in `config.json`:
```json
"ports": [80, 443, 2053]
```

### Background Caching
A daemon thread runs in the background (per process) to keep the cache warm. This ensures that when a user requests `/connect`, the server serves data from RAM immediately rather than waiting for the scraper to fetch data from Telegram.