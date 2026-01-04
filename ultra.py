import re
import json
import base64
import html
import time
import socket
import threading
import multiprocessing as mp
import os
import random
import string
import pytz
from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from flask import Flask, request, Response
from discord import SyncWebhook
from snscrape.modules.telegram import TelegramChannelScraper

# -----------------------------------------------------------------------------
# CORE FUNCTIONALITY (formerly core.py)
# -----------------------------------------------------------------------------

_config_cache = {}

def update_cache(channel_name, scrape_config):
    current_time = time.time()
    target_protocols = {'vless', 'vmess', 'ss', 'trojan'}
    raw_configs = []
    post_counter = 0
    seen_configs = set()

    # Determine scraping limits
    # Handle legacy int input or dict input
    if isinstance(scrape_config, int):
        mode = 'count'
        limit_count = scrape_config
        days = 0
        hours = 0
    else:
        mode = scrape_config.get('scrape_mode', 'count')
        limit_count = int(scrape_config.get('scrape_limit', 25))
        days = int(scrape_config.get('scrape_days', 0))
        hours = int(scrape_config.get('scrape_hours', 0))

    cutoff_date = None
    if mode == 'time':
        if days == 0 and hours == 0:
            days = 1  # Default to 1 day if time mode selected but no time given
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days, hours=hours)

    try:
        for post in TelegramChannelScraper(channel_name).get_items():
            post_counter += 1
            
            # Check limits
            if mode == 'time' and cutoff_date:
                if post.date < cutoff_date:
                    break
            elif mode == 'count':
                if post_counter > limit_count:
                    break
            
            # Safety break for time mode to prevent infinite scraping
            if post_counter > 500:
                break

            # Gather text content from post and link previews
            content_sources = []
            if post.content:
                content_sources.append(html.unescape(post.content))
            
            # Feature: Scan link previews for configs
            if post.linkPreview:
                if post.linkPreview.title:
                    content_sources.append(html.unescape(post.linkPreview.title))
                if post.linkPreview.description:
                    content_sources.append(html.unescape(post.linkPreview.description))

            full_text = "\n".join(content_sources)

            for _, config in find_configs(target_protocols, full_text):
                # Feature: Deduplication
                if config not in seen_configs:
                    seen_configs.add(config)
                    raw_configs.append(config)
        
        _config_cache[channel_name] = (current_time, raw_configs)
    except Exception as e:
        print(f"Error scraping {channel_name}: {e}")
        if channel_name in _config_cache:
            return _config_cache[channel_name][1]
            
    return raw_configs

def get_raw_configs(channel_name, scrape_config):
    if channel_name in _config_cache:
        return _config_cache[channel_name][1]
    return update_cache(channel_name, scrape_config)

def subscription(channel_name, channel_config=None, config_count=25, config_name="@Iranray_VPN | Config"):
    if channel_name is None:
        # Channel name is required
        return 'vless://00000000@noconfigs.xd:200?mode=gun&security=none&encryption=none&type=grpc&serviceName=#Channel name is required'

    if channel_config is None:
        channel_config = {'scrape_mode': 'count', 'scrape_limit': 55}

    result = ''
    config_counter = 0

    raw_configs = get_raw_configs(channel_name, channel_config)

    for config in raw_configs:
        final_config = rename_config(config, config_name)
        if final_config == '':
            continue

        result += final_config + '\n'
        config_counter += 1
        if config_counter >= config_count:
            break

    if not result:
        # Invalid channel
        return 'vless://00000000@noconfigs.xd:200?mode=gun&security=none&encryption=none&type=grpc&serviceName=#Invalid Channel'

    return result


def find_configs(target_protocols, text):
    for config_idx, conf in enumerate(re.findall(f'(({"|".join(target_protocols)}):\/\/[^\s]+)', text)):
        config, _ = conf

        if config.count('://') > 1:
            # Handle concatenated configs (e.g. vless://...vless://...)
            temp_config = config
            for proto in target_protocols:
                temp_config = temp_config.replace(f'{proto}://', f'\n{proto}://')
            
            for sub_config in temp_config.split('\n'):
                if sub_config.strip():
                    yield config_idx, clean_config(sub_config.strip())
        else:
            yield config_idx, clean_config(config)

def clean_config(config):
    """Removes common markdown/HTML artifacts from the end of the config."""
    return config.split('<')[0].rstrip('`\'")];,.')

def rename_config(config, config_name):
    protocol = config.split('://')[0]
    if protocol == 'vmess':
        start_index = len(protocol) + 3
        for i in range(len(config), start_index, -1):
            try:
                config_b64 = config[start_index:i]
                # Fix padding
                missing_padding = len(config_b64) % 4
                if missing_padding:
                    config_b64 += '=' * (4 - missing_padding)
                decoded_config = base64.b64decode(config_b64).decode('utf-8')
                parsed_config = json.loads(decoded_config)
                if isinstance(parsed_config, dict):
                    parsed_config['ps'] = config_name
                    stringify_config = json.dumps(parsed_config)
                    encoded_config = base64.b64encode(stringify_config.encode('utf-8')).decode('utf-8')
                    return protocol + '://' + encoded_config
            except:
                continue
        return ''

    else:
        safe_name = quote(config_name)
        if '#' in config:
            hashtag_index = config.index('#')
            return config[:hashtag_index + 1] + safe_name
        else:
            return config + '#' + safe_name

# -----------------------------------------------------------------------------
# HANDLER & DNS FUNCTIONALITY
# -----------------------------------------------------------------------------

config_file = "config.json"

def generate(length):
    characters = string.ascii_letters + string.digits
    password = "".join(random.choice(characters) for _ in range(length))
    return password

def get_current_time():
    # Set the time zone to Iran
    iran_tz = pytz.timezone("Asia/Tehran")

    # Get the current time in Iran
    current_time = datetime.now(iran_tz)

    # Format the time as "Day_Of_the_week Hour:Minute"
    formatted_time = current_time.strftime("%A %H:%M")

    return formatted_time

def load_config():
    default_config = {
        "api_secret": "ql1lGsB7TTO3TOOR2vRjaMgQi2DvmEWtngOkxNtFhTLQaDUne6sZvhRhD0jXUAKC0DtL9EW8fCZO5GdzHaIZyuBM2Re2OdYi",
        "webhook_url": None,
        "keys": [],
        "channels": [],
        "ports": [8083],
        "cache_ttl": 1800
    }
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
        return default_config
    
    with open(config_file, 'r') as f:
        try:
            loaded_config = json.load(f)
            # Ensure all default keys exist in the loaded config
            for key, value in default_config.items():
                if key not in loaded_config:
                    loaded_config[key] = value
            return loaded_config
        except Exception:
            return default_config

def save_config(config):
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)

def sendTo_webhook(msgcontent):
    config = load_config()
    if config.get("webhook_url"):
        try:
            webhook = SyncWebhook.from_url(config["webhook_url"])
            webhook.send(msgcontent)
        except Exception:
            pass

def dns_forward(req_data: bytes, ip: str) -> bytes | None:
    """
    Forwards the raw DNS query to the upstream IP via UDP.
    """
    target = (ip, 53)
    try:
        # Create a UDP socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(2)  # 2 second timeout matching PHP
            sock.sendto(req_data, target)

            # Read response (4096 bytes buffer matching PHP)
            response, _ = sock.recvfrom(4096)
            return response if response else None
    except Exception:
        return None

app = Flask(__name__)

# --- DNS Routes ---

@app.route('/', methods=['GET', 'POST'])
def handle_dns_request():
    req_data = None
    upstream = '1.1.1.1'
    max_size = 1024

    # Handle POST (application/dns-message)
    if request.method == 'POST':
        ctype = request.headers.get('Content-Type', '')
        if ctype.startswith('application/dns-message'):
            req_data = request.get_data()
            # Upstream remains 1.1.1.1

    # Handle GET (dns query parameter)
    elif request.method == 'GET':
        dns_param = request.args.get('dns')
        if dns_param:
            upstream = '1.0.0.1'
            try:
                # Mimic PHP: base64_decode(strtr($_GET['dns'], '-_', '+/'))
                # Python is strict about padding, PHP is not, so we must add padding manually.
                sanitized = dns_param.replace('-', '+').replace('_', '/')
                padding = len(sanitized) % 4
                if padding > 0:
                    sanitized += '=' * (4 - padding)

                req_data = base64.b64decode(sanitized)
            except Exception:
                req_data = None

    # Validation
    if not req_data or len(req_data) > max_size or len(req_data) == 0:
        return Response("Bad Request", status=400, mimetype='text/plain')

    # Forward the request
    res_data = dns_forward(req_data, upstream)

    # Return response
    if res_data:
        return Response(
            res_data,
            status=200,
            mimetype='application/dns-message'
        )
    else:
        return Response("Bad Gateway", status=502, mimetype='text/plain')

# --- AutoRAY Routes ---

@app.route("/createkey")
def createkey():
    config = load_config()
    try:
        if request.args.get("secret") == config["api_secret"]:
            newkey = generate(16)
            config["keys"].append(newkey)
            save_config(config)
            sendTo_webhook(
                f"New key generated! ✅ \nKey: `{newkey}`\n{datetime.now()}"
            )
            # Dynamically generate link based on the current request host
            return f"Subscription created! ✅ \nKey: `{newkey}`\n\nLink: `{request.scheme}://{request.host}/connect?key={newkey}#WebbTVC-vip`"
        else:
            print("AUTH_ERROR /createkey")
    except Exception as e:
        print(e)
        return "Error creating key"


@app.route("/allkeys")
def returnallkeys():
    config = load_config()
    sendTo_webhook("⚠️ Warning!\nThe Allkeys route has been triggered")
    if request.args.get("secret") == config["api_secret"]:
        sendTo_webhook("Access granted ✅\n|")
        return "\n".join(config["keys"])
    else:
        sendTo_webhook("Access denied!\n|")
        return "Access denied"


@app.route("/ping")
def apialiveping():
    sendTo_webhook("Status ping\nReturned `ALIVE`")
    return "ALIVE"


@app.route("/delkey")
def deletekey():
    config = load_config()
    if request.args.get("secret") == config["api_secret"]:
        targetKey = request.args.get("targetkey")
        
        if targetKey in config["keys"]:
            config["keys"].remove(targetKey)
            save_config(config)
            sendTo_webhook(f"Key got removed! ⚠️\nKey: `{targetKey}`\n{datetime.now()}")
            return "SUCCESS"
        return "Nothing removed"


@app.route("/addkey")
def appendkey():
    config = load_config()
    try:
        if request.args.get("secret") == config["api_secret"]:
            target_key = request.args.get("targetkey")
            if not target_key:
                return "Missing target key"
            config["keys"].append(target_key)
            save_config(config)
            sendTo_webhook(
                f"Key got added! ✅\nKey: `{target_key}`\n{datetime.now()}"
            )
            return "SUCCESS"
        return "Access denied"
    except Exception:
        sendTo_webhook(f"Failed to add {request.args.get('targetkey')} to keys")
        return "Failed to add key"


@app.route("/connect")
def sub():
    config = load_config()
    keyslist = config["keys"]
    try:
        rqkey = request.args.get("key")
        if str(rqkey) in list(keyslist):
            allconfigs = ""
            item_list = config["channels"]
            for i in item_list:
                currentdatetime = get_current_time()
                allconfigs += (
                    subscription(
                        channel_name=i.get("name"),
                        channel_config=i,
                        config_count=int(i.get("scrape_limit", i.get("count", 25))),
                        config_name=f"AutoRAY | {currentdatetime}",
                    )
                    + "\n"
                )
            sendTo_webhook(f"\nSuccessful update ✅\nKey: `{rqkey}`\n{datetime.now()}")
            return allconfigs
        else:
            sendTo_webhook(
                f"Failed update ⚠️\nReason: Invalid password\nKey: `{rqkey}`\n_"
            )
            return "vless://00000000@incorrectpasskey.xd:200?mode=gun&security=none&encryption=none&type=grpc&serviceName=#ERR: Invalid key | @Iranray_VPN"
    except Exception as e:
        print(e)
        sendTo_webhook(
            f"Failed update ⚠️\nReason: Internal server error\n{datetime.now()}\n_"
        )
        return "vless://00000000@internalerror.xd:200?mode=gun&security=none&encryption=none&type=grpc&serviceName=#ERR: Internal error | @Iranray_VPN"


@app.route("/custom")
def partnersub():
    config = load_config()
    keyslist = config["keys"]
    try:
        rqkey = request.args.get("key")
        rqname = request.args.get("name")
        if str(rqkey) in list(keyslist):
            allconfigs = ""
            item_list = config["channels"]
            for i in item_list:
                allconfigs += (
                    subscription(
                        channel_name=i.get("name"),
                        channel_config=i,
                        config_count=int(i.get("scrape_limit", i.get("count", 25))),
                        config_name=rqname
                    )
                    + "\n"
                )
            sendTo_webhook(
                f"(CUSTOM) Successful update ✅\nKey: `{rqkey}`\n\n{datetime.now()}\n|"
            )
            return allconfigs
        else:
            sendTo_webhook(
                f"(CUSTOM) Failed update (Partner Route)⚠️\nReason: Invalid password\nKey: `{rqkey}`\n_"
            )
            return "vless://00000000@incorrectpasskey.xd:200?mode=gun&security=none&encryption=none&type=grpc&serviceName=#ERR: Invalid key | @Iranray_VPN"
    except Exception:
        sendTo_webhook(
            f"(CUSTOM) Failed update (Partner Route) ⚠️\nReason: Internal server error\n{datetime.now()}\n_"
        )
        return "vless://00000000@internalerror.xd:200?mode=gun&security=none&encryption=none&type=grpc&serviceName=#ERR: Internal error | @Iranray_VPN"


@app.route("/addchannel")
def addchannel():
    config = load_config()
    if request.args.get("secret") == config["api_secret"]:
        name = request.args.get("name")
        
        # New parameters
        mode = request.args.get("mode", "count") # 'count' or 'time'
        limit = request.args.get("limit", 25)    # Message count limit
        days = request.args.get("days", 0)       # Days to look back
        hours = request.args.get("hours", 0)     # Hours to look back
        
        if not name:
            return "Missing channel name"
            
        try:
            limit = int(limit)
            days = int(days)
            hours = int(hours)
        except ValueError:
            return "Invalid number format"

        for channel in config["channels"]:
            if channel["name"] == name:
                return "Channel already exists"

        new_channel = {
            "name": name,
            "scrape_mode": mode,
            "scrape_limit": limit,
            "scrape_days": days,
            "scrape_hours": hours,
            # Maintain backward compatibility for 'count' key if needed by other tools
            "count": limit 
        }

        config["channels"].append(new_channel)
        save_config(config)
        sendTo_webhook(f"Channel added! ✅\nName: `{name}`\nMode: `{mode}`\n{datetime.now()}")
        return "SUCCESS"
    return "Access denied"


@app.route("/delchannel")
def delchannel():
    config = load_config()
    if request.args.get("secret") == config["api_secret"]:
        name = request.args.get("name")
        if not name:
            return "Missing channel name"
            
        initial_len = len(config["channels"])
        config["channels"] = [c for c in config["channels"] if c["name"] != name]
        
        if len(config["channels"]) < initial_len:
            save_config(config)
            sendTo_webhook(f"Channel removed! ⚠️\nName: `{name}`\n{datetime.now()}")
            return "SUCCESS"
        return "Channel not found"
    return "Access denied"


@app.route("/listchannels")
def listchannels():
    config = load_config()
    if request.args.get("secret") == config["api_secret"]:
        return json.dumps(config["channels"], indent=4)
    return "Access denied"


@app.route("/setwebhook")
def setwebhook():
    config = load_config()
    if request.args.get("secret") == config["api_secret"]:
        url = request.args.get("url")
        if url:
            config["webhook_url"] = url
            save_config(config)
            sendTo_webhook(f"Webhook updated! ✅\n{datetime.now()}")
            return "SUCCESS"
        return "Missing url"
    return "Access denied"


@app.route("/freshconnect")
def fresh_connect():
    config = load_config()
    if request.args.get("secret") == config["api_secret"]:
        allconfigs = ""
        item_list = config["channels"]
        for i in item_list:
            # Force update cache
            update_cache(i.get("name"), i)
            
            currentdatetime = get_current_time()
            allconfigs += (
                subscription(
                    channel_name=i.get("name"),
                    channel_config=i,
                    config_count=int(i.get("scrape_limit", i.get("count", 25))),
                    config_name=f"AutoRAY | {currentdatetime}",
                )
                + "\n"
            )
        sendTo_webhook(f"Fresh configs requested via API! ✅\n{datetime.now()}")
        return allconfigs
    return "Access denied"


def background_cache_updater():
    while True:
        ttl = 1800
        try:
            config = load_config()
            ttl = int(config.get("cache_ttl", 1800))
            for channel in config["channels"]:
                update_cache(channel.get("name"), channel)
        except Exception as e:
            print(f"Background update error: {e}")
        time.sleep(ttl)

# Run the server

## Single port mode (Default)
def startServer(port):
    print(f"Starting server on port {port}")
    updater_thread = threading.Thread(target=background_cache_updater)
    updater_thread.daemon = True
    updater_thread.start()
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    config = load_config()
    ports = config.get("ports", [8083])
    
    if len(ports) == 1:
        startServer(ports[0])
    else:
        processes = []
        for port in ports:
            p = mp.Process(target=startServer, args=(port,))
            p.daemon = True
            p.start()
            processes.append(p)
        
        for p in processes:
            p.join()