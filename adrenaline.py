#!/usr/bin/env python3

import sys
import os
import re
import requests
from urllib.parse import urlparse
import colorama
colorama.init()


# Suppress only the single InsecureRequestWarning from urllib3 needed for `verify=False`
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Import logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0'

def main():
    """
    Fetches a URL, extracts relative hrefs, saves them, and checks their headers.
    """
    target_url = sys.argv[1]

    if target_url == '-h':
        print('\nAdrenaline v0.9\nUsage: python3 adrenaline.py <url>\n\nCreated by Gabriel H. @weekndr_sec\nhttps://github.com/ndr-repo | http://weekndr.me')
        sys.exit(0)
    else:
        pass

    try:
        parsed_url = urlparse(target_url)
        domain = parsed_url.netloc
        if not domain:
            raise ValueError("Invalid URL provided. Could not determine domain.")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    output_dir = "log/hrefTrace"
    os.makedirs(output_dir, exist_ok=True)
    log_file_path = os.path.join(output_dir, f"{domain}.txt")

    try:
        headers = {'User-Agent': USER_AGENT}
        # Replicates curl -L (allow_redirects=True) and -k (verify=False)
        response = requests.get(target_url, headers=headers, verify=False, allow_redirects=True, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}", file=sys.stderr)
        sys.exit(1)

    # This regex finds any path inside double quotes that starts with a forward slash.
    regex = r'"(\/[a-zA-Z0-9\-._~%|&\'()*+,;=:@\/]+)"'
    
    # Find all unique paths and sort them
    relative_paths = sorted(list(set(re.findall(regex, response.text))))
    print()
    logging.info("[adr] - Banner grabbing via GET request...")
    banners = os.path.join(output_dir, str(f"{domain}_banners.txt"))
    for path in relative_paths:
        full_url = f"https://{domain}{path}"
        try:
            get_response = requests.get(full_url, headers=headers, verify=False, allow_redirects=True, timeout=10)
            for key, value in get_response.headers.items():        
                bannerlog = str(banners)
                with open(bannerlog,  "w") as l:
                    l.write(f"{full_url}: {key}: {value}")
        except requests.RequestException as e:
            print(f"Error checking {full_url}: {e}", file=sys.stderr)
        if len(f"{path}") > 2:
            logging.info(str(f'[adr/hrefTrace/banner] - GET {path} - {get_response.status_code} {get_response.reason} - {get_response.headers.get("Content-Type")}'))
    
    logging.info(str(f"[adr] - Found {len(relative_paths)} unique relative paths. Saving to directory: {output_dir}"))
    print(colorama.Fore.RED + '\nAdrenaline v0.9\nCreated by Gabriel H. @weekndr_sec\nhttps://github.com/ndr-repo | http://weekndr.me' + colorama.Style.RESET_ALL)

    with open(log_file_path, 'w') as f:
        for path in relative_paths:
            f.write(f"{path}\n")
        
if __name__ == "__main__":
    main()
