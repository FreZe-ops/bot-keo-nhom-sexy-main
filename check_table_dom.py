import urllib.request
import json

# Check the table DOM info or active table info
for ns in ['NS1', 'NS2', 'NS3', 'NS4']:
    try:
        url = f'http://127.0.0.1:3201/api/get-active-table?nameService={ns}'
        with urllib.request.urlopen(url, timeout=3) as r:
            print(f"[{ns}]", json.loads(r.read().decode('utf-8')))
    except Exception as e:
        print(f"[{ns}] Error: {e}")
