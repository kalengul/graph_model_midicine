#!/usr/bin/env python3
import sys
import urllib.request
import urllib.error

URL = "http://localhost:8000/health/"
TIMEOUT = 3

try:
    with urllib.request.urlopen(URL, timeout=TIMEOUT) as response:
        if response.getcode() == 200:
            sys.exit(0)
        else:
            print(f"Status code is not 200: {response.getcode()}", file=sys.stderr)
            sys.exit(1)
            
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} {e.reason}", file=sys.stderr)
    sys.exit(1)
except urllib.error.URLError as e:
    print(f"Connection Error: {e.reason}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Unexpected Error: {e}", file=sys.stderr)
    sys.exit(1)

