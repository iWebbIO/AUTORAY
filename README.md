# AutoRAY - A new Era of VPNs
### What is AutoRAY?
- AutoRAY is a python program that connects to the Telegram API and helps you scrape V2ray configurations and pack them into a subscription (Flask Route/HTTP Response)
### What is it exactly?
- Clients like [V2rayNG](https://github.com/2dust/v2rayNG) and [Hiddify](https://github.com/hiddify/hiddify-next) let you add subscriptions, This way you can provide the v2ray configs to your client without the need to leave the app.
- AutoRAY saves a ton of time by doing the "finding the configs" process automatically.

### How can i use it?
- You have two options, use the community servers OR self-host your own Autoray server

# Community servers
- You can find community links and server in [autoray-community-servers](https://github.com/iWebbIO/Autoray-public-servers)

# Host it yourself! **(Linux DEB)**
### Step 1: Download `dashboard.py`
- Run the following command to download the `dashboard.py` file<br>
This script will help you install AutoRAY
<br>`wget https://github.com/iWebbIO/AUTORAY/releases/download/v2.0.1-STABLE/dashboard.py`
### Step 2: Update & Upgrade packages using `APT` and install `python3`
- `sudo apt update && sudo apt upgrade -y && sudo apt install python3 python3-pip`
### Step 3: Run `dashboard.py`
- To install AutoRAY you have to Run the `dashboard.py` script<br>
- Make sure you are in the dorectory where you downloaded the fle before running this command
`python3 dashboard.py`
### Step 4: Go through the installation process
### Step 5: Set up Channels, Keys and discord webhook
- Change your directory to the location that you installed AutoRAY and locate the `Settings` folder
- Insert your Telegram channel IDs in the `channels` file and put your API Access keys in the `keys` file
To setup Discord webhooks and log activity on your AutoRAY server visit [How to connect AutoRAY to a Discord Webhook](https://github.com/iWebbIO/AUTORAY/wiki/Connect-AutoRAY-to-a-Discord-webhook)

### Step 6:
- After the installation is complete and the settings are configured, Run the `AutoRAYhandler.py` file by running ```python3 AutoRAYhandler.py```

# Connect to your server
- to connect to your AutoRAY server, simply use the template below:<br>
`http://ServerIP:Port/connect?key=YOURKEY`
### What do these mean?
- `ServerIP`: Replace with the IP of your server
- `Port`: Replace with your server's port (Default: 2873)
- `YOURKEY`: One of the Api Access keys that you inserted into the `/Settings/keys` file

For example i have a server that has an IPv4 address (123.456.789.123)
and i Run the Autoray server on it and i put a key named `free` in the keys file
This would be the URL i'd have to connect to:
`http:123.456.789.123:2873/connect?key=FREE`

Remember that the program is case-sensitive and when you choose a key like `hGhKsoiU` you'll have to put the exact same thing when connecting to your server
