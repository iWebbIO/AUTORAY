from flask import Flask, request
from discord import SyncWebhook
from datetime import datetime
import multiprocessing as mp
import core as tvc
import os
import json
import threading
import time
import random
import string
import pytz

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
        "ports": [2873],
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

app = Flask(__name__)

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
                    tvc.subscription(
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
                    tvc.subscription(
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
            tvc.update_cache(i.get("name"), i)
            
            currentdatetime = get_current_time()
            allconfigs += (
                tvc.subscription(
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
                tvc.update_cache(channel.get("name"), channel)
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
    ports = config.get("ports", [2873])
    
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
