import AutoRAYcore as tvc
import functions
import multiprocessing as mp
from discord import SyncWebhook
from flask import Flask, request, render_template_string
import os
from datetime import datetime
import pytz
from datetime import datetime
webhook = SyncWebhook.from_url("DiscordWebhookUrl")



def get_iran_time():
    # Set the time zone to Iran
    iran_tz = pytz.timezone('Asia/Tehran')
    
    # Get the current time in Iran
    current_time = datetime.now(iran_tz)
    
    # Format the time as "Day_Of_the_week Hour:Minute"
    formatted_time = current_time.strftime("%A %H:%M")
    
    return formatted_time
app = Flask(__name__)

# Decorator to check if the request is from localhost
import random, string

apiSecret = "ql1lGsB7TTO3TOOR2vRjaMgQi2DvmEWtngOkxNtFhTLQaDUne6sZvhRhD0jXUAKC0DtL9EW8fCZO5GdzHaIZyuBM2Re2OdYi"

        #Public route
@app.route('/createkey')
def createkey():
    try:
        if request.args.get("pass") == apiSecret:
            newkey = functions.generate(16)
            with open("keys.txt", "a") as f:
                f.write(newkey + "\n")
            f.close()
            webhook.send(f"New key generated! :white_check_mark: \nKey: `{newkey}`\n{datetime.now()}")
            #return f"Subscription created! :white_check_mark: \nKey: `{newkey}`\n\nMain links:\nNormal: `http://moriw.net.eu.org:2052/connect?key={newkey}#WebbTVC-vip`\nTunneled: `http://tunnel.moriw.net.eu.org:2052/connect?key={newkey}#WebbTVC-vip`\n\nBackup Link: `http://free-01.duckhost.pro:8428/connect?key={newkey}#WebbTVC-vip`"
            return f"Subscription created! ✅ \nKey: `{newkey}`\n\nLink: `http://85.232.241.109:53275/connect?key={newkey}#WebbTVC-vip`\nBackup Link: `http://85.232.241.109:7242/connect?key={newkey}#WebbTVC-vip`"
        else:
            request.abort(404)
    except:
        request.abort(404)
@app.route("/allkeys")
def seeallkeysapi():
    webhook.send("⚠️Warning!\nThe Allkeys route has been triggered")
    if request.args.get("key") == apiSecret:
        webhook.send("Access granted :white_check_mark: \n_")
        allkeycontent = ""
        with open("keys.txt", "r") as f:
            apiReturnContent = f.readlines()
        for i in apiReturnContent:
            allkeycontent += i
        return allkeycontent
    else:
        webhook.send("Access denied!  <@&1197993368270143568>  \n_")
@app.route('/ping')
def apialiveping():
    try:
        if request.args.get('key') == apiSecret:
            webhook.send("Status ping: SUCCUSS")
            return "ALIVE"
        else:
            webhook.send("Status ping: INVALID_AUTH")
    except:
        webhook.send("Status ping: INTERNAL_ERR")
@app.route('/delkey')
def deletekeyfromfile():
    if request.args.get('key') == apiSecret:
        with open("keys.txt", "r") as f:
            keyslist = [line.strip() for line in f]
            f.close()
        targetKey = request.args.get('tkey')
        restKeys = []
        resultcode = "Nothing removed"
        for i in keyslist:
            if not i == targetKey:
                restKeys.append(i)
            else:
                resultcode = "SUCCUSS"
                webhook.send(f"Key got removed! ⚠️\nKey: `{i}`\n{datetime.now}")
        with open("keys.txt", "w") as f:
            for i in restKeys:
                f.write(f"{i}\n")
            f.close()
        return resultcode
@app.route('/addkey')
def addnewkey():
    try:
        if request.args.get('key') == apiSecret:
            with open("keys.txt", "a") as f:
                f.write(request.args.get('tkey') + "\n")
                f.close()
            webhook.send(f"Key got added!  <:yes:1197990451484053615> \nKey: `{request.args.get('tkey')}`\n{datetime.now}")
            return "SUCCUSS"
    except:
        return "Failed to add key"
        webhook.send(f"Failed to add {request.args.get('key')} to .KEYS")
@app.route('/connect')
def sub():
    with open("keys.txt", "r") as f:
        keyslist = [line.strip() for line in f]  # This removes any trailing newline characters
    try:
        rqkey = request.args.get("key")
        if str(rqkey) in list(keyslist):
            allconfigs = ""
            with open("channels.txt", "r") as file:
                item_list = [line.strip().split() for line in file]

            item_list = [[channel_id, int(count)] for channel_id, count in item_list]
            for i in item_list:
                irancurrenttimeday = get_iran_time()
                allconfigs += tvc.subscription(channel_name=i[0], config_count=i[1], config_name=f"@IranRAY_vpn | {irancurrenttimeday}") + "\n"
            webhook.send(f"\nSuccussful update\nKey: `{rqkey}`\n{datetime.now()}")
            return allconfigs
        else:
            webhook.send(f"Failed update ⚠️\nReason: Invalid password\nKey: `{rqkey}`\n_")
            return "vless://00000000@incorrectpasskey.xd:200?mode=gun&security=none&encryption=none&type=grpc&serviceName=#ERR: Invalid key | @Iranray_VPN"
    except:
        webhook.send("Failed update ⚠️\nReason: Internal server error\n{datetime.now()}\n_")
        return "vless://00000000@internalerror.xd:200?mode=gun&security=none&encryption=none&type=grpc&serviceName=#ERR: Internal error | @Iranray_VPN"
@app.route('/partner')
def partnersub():
    with open("keys.txt", "r") as f:
        keyslist = [line.strip() for line in f]  # This removes any trailing newline characters
    try:
        rqkey = request.args.get("key")
        rqname = request.args.get("name")
        if str(rqkey) in list(keyslist):
            allconfigs = ""
            with open("channels.txt", "r") as file:
                item_list = [line.strip().split() for line in file]

            item_list = [[channel_id, int(count)] for channel_id, count in item_list]
            for i in item_list:
                allconfigs += tvc.subscription(channel_name=i[0], config_count=i[1], config_name=rqname) + "\n"
            webhookpartner.send(f"\nSuccussful update\nKey: `{rqkey}`\n\n{datetime.now()}\n|")
            return allconfigs
        else:
            webhookpartner.send(f"Failed update (Partner Route)⚠️\nReason: Invalid password\nKey: `{rqkey}`\n_")
            return "vless://00000000@incorrectpasskey.xd:200?mode=gun&security=none&encryption=none&type=grpc&serviceName=#ERR: Invalid key | @Iranray_VPN"
    except:
        webhookpartner.send("Failed updat (Partner Route)e ⚠️\nReason: Internal server error\n{datetime.now()}\n_")
        return "vless://00000000@internalerror.xd:200?mode=gun&security=none&encryption=none&type=grpc&serviceName=#ERR: Internal error | @Iranray_VPN"
@app.route('/miner')
def minrsub():
    minerconfigs = tvc.subscription(channel_name="iranrayminer", config_count=15, config_name="W ? B B | Iranray Miner 1.0")
    return minerconfigs

#if __name__ == '__main__':
#    app.run(host="0.0.0.0", port=2052)
def startServer(port):
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    print('Main Line Starting')
    p = mp.Process(target=startServer, args=(7242,))
    p.daemon = True
    p.start()
    p1 = mp.Process(target=startServer, args=(53275,))
    p1.daemon = True
    p1.start()
    p.join()
    p1.join()