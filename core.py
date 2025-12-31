import re
import json
import base64
import html
import time
from urllib.parse import quote
from snscrape.modules.telegram import TelegramChannelScraper


_config_cache = {}

def update_cache(channel_name, post_count):
    current_time = time.time()
    target_protocols = {'vless', 'vmess', 'ss', 'trojan'}
    raw_configs = []
    post_counter = 0

    try:
        for post in TelegramChannelScraper(channel_name).get_items():
            if post.content is None:
                continue
            post_counter += 1
            try:
                content = html.unescape(post.content)
            except Exception:
                continue

            for _, config in find_configs(target_protocols, content):
                raw_configs.append(config)

            if post_counter >= post_count:
                break
        
        _config_cache[channel_name] = (current_time, raw_configs)
    except Exception as e:
        print(f"Error scraping {channel_name}: {e}")
        if channel_name in _config_cache:
            return _config_cache[channel_name][1]
            
    return raw_configs

def get_raw_configs(channel_name, post_count):
    if channel_name in _config_cache:
        return _config_cache[channel_name][1]
    return update_cache(channel_name, post_count)

def subscription(channel_name, post_count=55, config_count=25, config_name="@Iranray_VPN | Config"):
    if channel_name is None:
        # Channel name is required
        return 'vless://00000000@noconfigs.xd:200?mode=gun&security=none&encryption=none&type=grpc&serviceName=#Channel name is required'

    result = ''
    config_counter = 0

    raw_configs = get_raw_configs(channel_name, post_count)

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
