from flask import Flask, request, render_template_string
from discord import SyncWebhook
from datetime import datetime
import multiprocessing as mp
import AutoRAYcore as tvc
import random, string
import functions as extra
import pytz
import os

settingsdir = "Settings"
keysfile_path = "keys"
channelsfile_path = "channels"
webhook = None # Put your discord webhook url here
apiSecret = "ql1lGsB7TTO3TOOR2vRjaMgQi2DvmEWtngOkxNtFhTLQaDUne6sZvhRhD0jXUAKC0DtL9EW8fCZO5GdzHaIZyuBM2Re2OdYi"
os.chdir(settingsdir)
def sendTo_webhook(msgcontent):
    if webhook != None:
        webhook.send(msgcontent)
app = Flask(__name__)

@app.route("/createkey")
def createkey():
    try:
        if request.args.get("secret") == apiSecret:
            newkey = extra.generate(16)
            with open(keysfile_path, "a") as f:
                f.write(newkey + "\n")
            f.close()
            sendTo_webhook(
                f"New key generated! Ã¢Å“â€¦ \nKey: `{newkey}`\n{datetime.now()}"
            )
            # return f"Subscription created! Ã¢Å“â€¦ \nKey: `{newkey}`\n\nMain links:\nNormal: `http://moriw.net.eu.org:2052/connect?key={newkey}#WebbTVC-vip`\nTunneled: `http://tunnel.moriw.net.eu.org:2052/connect?key={newkey}#WebbTVC-vip`\n\nBackup Link: `http://free-01.duckhost.pro:8428/connect?key={newkey}#WebbTVC-vip`"
            return f"Subscription created! Ã¢Å“â€¦ \nKey: `{newkey}`\n\nLink: `http://85.232.241.109:53275/connect?key={newkey}#WebbTVC-vip`\nBackup Link: `http://85.232.241.109:7242/connect?key={newkey}#WebbTVC-vip`"
        else:
            print("AUTH_ERROR /createkey")
    except Exception as e:
        print(e)


@app.route("/allkeys")
def returnallkeys():
    sendTo_webhook("Ã¢Å¡Â Ã¯Â¸Â Warning!\nThe Allkeys route has been triggered")
    if request.args.get("key") == apiSecret:
        sendTo_webhook("Access granted Ã¢Å“â€¦\n|")
        allkeycontent = ""
        with open(keysfile_path, "r") as f:
            apiReturnContent = f.readlines()
        for i in apiReturnContent:
            allkeycontent += i
        return allkeycontent
    else:
        sendTo_webhook("Access denied!\n|")


@app.route("/ping")
def apialiveping():
    sendTo_webhook("Status ping\nReturned `ALIVE`")
    return "ALIVE"


@app.route("/delkey")
def deletekey():
    if request.args.get("secret") == apiSecret:
        with open(keysfile_path, "r") as f:
            keyslist = [line.strip() for line in f]
            f.close()
        targetKey = request.args.get("targetkey")
        restKeys = []
        resultcode = "Nothing removed"
        for i in keyslist:
            if not i == targetKey:
                restKeys.append(i)
            else:
                resultcode = "SUCCUSS"
                sendTo_webhook(f"Key got removed! Ã¢Å¡Â Ã¯Â¸Â\nKey: `{i}`\n{datetime.now()}")
        with open(keysfile_path, "w") as f:
            for i in restKeys:
                f.write(f"{i}\n")
            f.close()
        return resultcode


@app.route("/addkey")
def appendkey():
    try:
        if request.args.get("secret") == apiSecret:
            with open(keysfile_path, "a") as f:
                f.write(request.args.get("targetkey") + "\n")
                f.close()
            sendTo_webhook(
                f"Key got added! Ã¢Å“â€¦\nKey: `{request.args.get('tkey')}`\n{datetime.now()}"
            )
            return "SUCCUSS"
    except:
        return "Failed to add key"
        sendTo_webhook(f"Failed to add {request.args.get('key')} to ")


@app.route("/connect")
def sub():
    with open(keysfile_path, "r") as f:
        keyslist = [line.strip() for line in f]
    try:
        rqkey = request.args.get("key")
        if str(rqkey) in list(keyslist):
            allconfigs = ""
            with open(channelsfile_path, "r") as file:
                item_list = [line.strip().split() for line in file]

            item_list = [[channel_id, int(count)] for channel_id, count in item_list]
            for i in item_list:
                currentdatetime = extra.get_current_time()
                allconfigs += (
                    tvc.subscription(
                        channel_name=i[0],
                        config_count=i[1],
                        config_name=f"AutoRAY | {currentdatetime}",
                    )
                    + "\n"
                )
            sendTo_webhook(f"\nSuccussful update Ã¢Å“â€¦\nKey: `{rqkey}`\n{datetime.now()}")
            return allconfigs
        else:
            sendTo_webhook(
                f"Failed update Ã¢Å¡Â Ã¯Â¸Â\nReason: Invalid password\nKey: `{rqkey}`\n_"
            )
            return "vless://00000000@incorrectpasskey.xd:200?mode=gun&security=none&encryption=none&type=grpc&serviceName=#ERR: Invalid key | @Iranray_VPN"
    except Exception as e:
        print(e)
        sendTo_webhook(
            "Failed update Ã¢Å¡Â Ã¯Â¸Â\nReason: Internal server error\n{datetime.now()}\n_"
        )
        return "vless://00000000@internalerror.xd:200?mode=gun&security=none&encryption=none&type=grpc&serviceName=#ERR: Internal error | @Iranray_VPN"


@app.route("/custom")
def partnersub():
    with open(keysfile_path, "r") as f:
        keyslist = [line.strip() for line in f]
    try:
        rqkey = request.args.get("key")
        rqname = request.args.get("name")
        if str(rqkey) in list(keyslist):
            allconfigs = ""
            with open(channelsfile_path, "r") as file:
                item_list = [line.strip().split() for line in file]

            item_list = [[channel_id, int(count)] for channel_id, count in item_list]
            for i in item_list:
                allconfigs += (
                    tvc.subscription(
                        channel_name=i[0], config_count=i[1], config_name=rqname
                    )
                    + "\n"
                )
            sendTo_webhook(
                f"(CUSTOM) Succussful update Ã¢Å“â€¦\nKey: `{rqkey}`\n\n{datetime.now()}\n|"
            )
            return allconfigs
        else:
            sendTo_webhook(
                f"(CUSTOM) Failed update (Partner Route)Ã¢Å¡Â Ã¯Â¸Â\nReason: Invalid password\nKey: `{rqkey}`\n_"
            )
            return "vless://00000000@incorrectpasskey.xd:200?mode=gun&security=none&encryption=none&type=grpc&serviceName=#ERR: Invalid key | @Iranray_VPN"
    except:
        sendTo_webhook(
            "(CUSTOM) Failed update (Partner Route)e Ã¢Å¡Â Ã¯Â¸Â\nReason: Internal server error\n{datetime.now()}\n_"
        )
        return "vless://00000000@internalerror.xd:200?mode=gun&security=none&encryption=none&type=grpc&serviceName=#ERR: Internal error | @Iranray_VPN"


# Run the server

## Single port mode (Default)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2873)
# ---------
## Use the following code to run the AutoRAY server on multiple ports
# def startServer(port):
#     print(f"Starting server on port {port}")
#     app.run(host="0.0.0.0", port=port)
# if __name__ == "__main__":
#     print("Main Line Starting")
#     p = mp.Process(target=startServer, args=(7242,))
#     p.daemon = True
#     p.start()
#     p1 = mp.Process(target=startServer, args=(53275,))
#     p1.daemon = True
#     p1.start()
#     p.join()
#     p1.join()
