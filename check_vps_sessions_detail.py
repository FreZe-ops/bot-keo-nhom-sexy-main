import urllib.request
import json

port = 3201
for path in ['/api/current-table', '/api/tables']:
    try:
        url = f'http://127.0.0.1:{port}{path}'
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=3) as res:
            data = json.loads(res.read().decode('utf-8'))
            print(f"=== {path} ===")
            print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error {path}: {e}")

# Check occupied tables on server.js
for ns in ['NS1', 'NS2', 'NS3', 'NS4', 'NS5']:
    try:
        url = f'http://127.0.0.1:{port}/api/current-table?nameService={ns}'
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=3) as res:
            data = json.loads(res.read().decode('utf-8'))
            print(f"[{ns}] -> {data}")
    except Exception as e:
        print(f"[{ns}] Error: {e}")
