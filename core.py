import re
import json
import base64
import html
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from snscrape.modules.telegram import TelegramChannelScraper


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
